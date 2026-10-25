"""Reproduce S38 offline and optionally from a fresh remote clone."""
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
    from scripts.s38_analyze import analyze
    from scripts.s38_independent import verify
    from scripts.s38_exact_check import check as check_exact
    from sim.horizon import main as resume
    paths=[p for p in Path('data/s38_horizon').rglob('*') if p.is_file() and p.name!='.writer.lock']
    original={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    with patch('sim.common.llm.chat',side_effect=AssertionError('Release forbids model calls')):
        with contextlib.redirect_stdout(io.StringIO()):r=analyze('data/s38_horizon')
        assert json.dumps(r,indent=2)+'\n'==Path('results/s38_horizon.json').read_text()
        independent=verify();assert independent==json.loads(Path('logs/s38_independent.json').read_text())
        exact=check_exact();assert exact==json.loads(Path('logs/s38_exact_check.json').read_text())
        with patch.object(sys,'argv',['sim.horizon']),contextlib.redirect_stdout(io.StringIO()):resume()
    for name,digest in original.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
    links=0
    for doc in ['REPORT.md','README.md','HITS.md','results/s38_summary.md']:
        for link in re.findall(r'\]\(([^)]+)\)',Path(doc).read_text()):
            href=link.strip('<>').split('#')[0]
            if not href or '://' in href:continue
            assert (Path(doc).parent/href).exists(),(doc,href)
            links+=1
    receipt=dict(passed=True,all_key_replay=True,canonical_result_byte_identical=True,cached_resume_byte_identical=True,
                 source_entries=len(json.loads(Path('data/s38_horizon/config.json').read_text())['sources']),
                 local_links_checked=links,independent=independent,exact_companion=exact)
    Path('logs/s38_release.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

def clean_clone():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    remote=subprocess.check_output(['git','remote','get-url','origin'],text=True).strip()
    artifacts=['results/s38_horizon.json','results/s38_summary.md','figures/s38_horizon.png','logs/s38_independent.json','logs/s38_release.json','logs/s38_exact_check.json','REPORT.md']
    with tempfile.TemporaryDirectory(prefix='s38_remote_',dir='/var/tmp') as td:
        clone=Path(td)/'repo';subprocess.run(['git','clone','--quiet',remote,str(clone)],check=True)
        subprocess.run(['git','checkout','--quiet',head],cwd=clone,check=True)
        commands=[['scripts/s38_analyze.py'],['scripts/s38_independent.py'],['scripts/s38_exact_check.py'],['scripts/s38_present.py'],['scripts/s38_release.py'],['-m','unittest','scripts.test_s38']]
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1')
        for args in commands:subprocess.run([str(root/'.venv/bin/python'),*args],cwd=clone,env=env,check=True)
        for name in artifacts:assert (clone/name).read_bytes()==(root/name).read_bytes(),name
        assert not subprocess.check_output(['git','status','--porcelain'],cwd=clone,text=True)
        receipt=dict(passed=True,commit=head,clone_source='origin remote',dependency_environment='Existing venv with frozen dependencies',commands=commands,
                     byte_identical_artifacts={p:hashlib.sha256((clone/p).read_bytes()).hexdigest() for p in artifacts})
    Path('logs/s38_remote_clean_clone.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS remote clean clone '+head)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--clean-clone',action='store_true');a=p.parse_args();clean_clone() if a.clean_clone else check()
