"""Reproduce S42 offline and optionally from a fresh remote clone."""
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
    from scripts.s42_analyze import analyze
    from scripts.s42_independent import verify
    from sim.entry import main as resume
    paths=[p for p in Path('data/s42_entry').rglob('*') if p.is_file() and p.name!='.writer.lock']
    original={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    with patch('sim.common.llm.chat',side_effect=AssertionError('Release forbids model calls')):
        with contextlib.redirect_stdout(io.StringIO()):r=analyze('data/s42_entry')
        assert json.dumps(r,indent=2)+'\n'==Path('results/s42_entry.json').read_text()
        independent=verify();assert independent==json.loads(Path('logs/s42_independent.json').read_text())
        with patch.object(sys,'argv',['sim.entry']),contextlib.redirect_stdout(io.StringIO()):resume()
    for name,digest in original.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
    links=0
    for doc in ['REPORT.md','README.md','HITS.md','results/s42_summary.md']:
        for link in re.findall(r'\]\(([^)]+)\)',Path(doc).read_text()):
            href=link.strip('<>').split('#')[0]
            if not href or '://' in href:continue
            assert (Path(doc).parent/href).exists(),(doc,href)
            links+=1
    receipt=dict(passed=True,all_key_replay=True,canonical_result_byte_identical=True,cached_resume_byte_identical=True,
                 source_entries=len(json.loads(Path('data/s42_entry/config.json').read_text())['sources']),
                 local_links_checked=links,independent=independent)
    Path('logs/s42_release.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

def clean_clone():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    remote=subprocess.check_output(['git','remote','get-url','origin'],text=True).strip()
    artifacts=['results/s42_entry.json','results/s42_summary.md','figures/s42_entry.png','logs/s42_independent.json','logs/s42_release.json','REPORT.md']
    with tempfile.TemporaryDirectory(prefix='s42_remote_',dir='/var/tmp') as td:
        clone=Path(td)/'repo';subprocess.run(['git','clone','--quiet',remote,str(clone)],check=True)
        subprocess.run(['git','checkout','--quiet',head],cwd=clone,check=True)
        commands=[['scripts/s42_analyze.py'],['scripts/s42_independent.py'],['scripts/s42_present.py'],['scripts/s42_release.py'],['-m','unittest','scripts.test_s42']]
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1')
        for args in commands:subprocess.run([str(root/'.venv/bin/python'),*args],cwd=clone,env=env,check=True)
        for name in artifacts:assert (clone/name).read_bytes()==(root/name).read_bytes(),name
        assert not subprocess.check_output(['git','status','--porcelain'],cwd=clone,text=True)
        receipt=dict(passed=True,commit=head,clone_source='origin remote',dependency_environment='Existing venv with frozen dependencies',commands=commands,
                     byte_identical_artifacts={p:hashlib.sha256((clone/p).read_bytes()).hexdigest() for p in artifacts})
    Path('logs/s42_remote_clean_clone.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS remote clean clone '+head)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--clean-clone',action='store_true');a=p.parse_args();clean_clone() if a.clean_clone else check()
