"""Cache-only release and optional fresh remote clone reproduction."""
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))


def check():
    from scripts.s58_replay import analyze,run
    from scripts.s58_independent import verify
    from scripts.s58_present import render,report_row
    from scripts.s58_action_text import export
    directory=Path('data/s58_history')
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.rglob('*') if p.is_file() and p.name!='.writer.lock'}
    artifacts=['results/s58_history.json','results/s58_summary.md','figures/s58_history.png','results/s58_action_text.md','REPORT.md']
    saved={p:Path(p).read_bytes() for p in artifacts}
    with patch('scripts.s58_replay.chat',side_effect=AssertionError('Model calls forbidden')):
        r=analyze(directory);assert report_row(r) in Path('REPORT.md').read_text()
        assert json.dumps(r,indent=2)+'\n'==Path(artifacts[0]).read_text()
        independent=verify();assert independent==json.loads(Path('logs/s58_independent.json').read_text())
        with contextlib.redirect_stdout(io.StringIO()):run(directory)
        render();export()
    assert all(Path(p).read_bytes()==b for p,b in saved.items())
    assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.rglob('*') if p.is_file() and p.name!='.writer.lock'}
    links=0
    for doc in ['REPORT.md','README.md','HITS.md','results/s58_summary.md']:
        for link in re.findall(r'\]\(([^)]+)\)',Path(doc).read_text()):
            href=link.strip('<>').split('#')[0]
            if not href or '://' in href:continue
            assert (Path(doc).parent/href).exists(),(doc,href)
            links+=1
    receipt=dict(passed=True,raw_archive_files=len(before),model_calls_forbidden=True,
                 scientific_and_rendered_artifacts_byte_identical=True,local_links_checked=links,independent=independent)
    Path('logs/s58_release.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt


def clean_clone():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    remote=subprocess.check_output(['git','remote','get-url','origin'],text=True).strip()
    artifacts=['results/s58_history.json','results/s58_summary.md','figures/s58_history.png','logs/s58_independent.json','logs/s58_release.json','results/s58_action_text.md','REPORT.md']
    with tempfile.TemporaryDirectory(prefix='s58_remote_',dir='/var/tmp') as td:
        clone=Path(td)/'repo';subprocess.run(['git','clone','--quiet',remote,str(clone)],check=True)
        subprocess.run(['git','checkout','--quiet',head],cwd=clone,check=True)
        commands=[['scripts/s58_replay.py','--analyze'],['scripts/s58_independent.py'],['scripts/s58_present.py'],['scripts/s58_action_text.py'],['scripts/s58_release.py'],['-m','unittest','scripts.test_s58']]
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1')
        for args in commands:subprocess.run([str(root/'.venv/bin/python'),*args],cwd=clone,env=env,check=True)
        for name in artifacts:assert (clone/name).read_bytes()==(root/name).read_bytes(),name
        assert not subprocess.check_output(['git','status','--porcelain'],cwd=clone,text=True)
        receipt=dict(passed=True,commit=head,clone_source='origin remote',dependency_environment='Existing venv with frozen dependencies;not fresh install',commands=commands,
                     byte_identical_artifacts={p:hashlib.sha256((clone/p).read_bytes()).hexdigest() for p in artifacts})
    Path('logs/s58_remote_clean_clone.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS remote clean clone '+head)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--clean-clone',action='store_true');a=p.parse_args();clean_clone() if a.clean_clone else print(json.dumps(check(),indent=2))
