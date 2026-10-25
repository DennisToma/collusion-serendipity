"""Full offline S34 archive reproduction; never permits live calls."""
import argparse
import os
import re
import subprocess
import tempfile
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s34_analyze import analyze
from scripts.s34_independent import verify as checked_verify


def check():
    paths=list(Path('data/s34_salience').rglob('*'))
    original={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file() and p.name!='.writer.lock'}
    with patch('sim.resource_cache.llm.chat',side_effect=AssertionError('Release forbids model calls')):
        with contextlib.redirect_stdout(io.StringIO()):result=analyze('data/s34_salience')
        expected=json.dumps(result,indent=2)+'\n';assert expected==Path('results/s34_salience.json').read_text()
        independent=checked_verify('data/s34_salience','results/s34_salience.json')
        assert independent==json.loads(Path('logs/s34_independent.json').read_text())
        from sim.salience import main as resume
        with patch.object(sys,'argv',['sim.salience']),contextlib.redirect_stdout(io.StringIO()):resume()
    for p,digest in original.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest,p
    links=0
    for doc in ['REPORT.md','README.md','HITS.md','results/s34_summary.md']:
        for link in re.findall(r'\]\(([^)]+)\)',Path(doc).read_text()):
            href=link.strip('<>').split('#')[0]
            if not href or '://' in href:continue
            assert (Path(doc).parent/href).exists(),(doc,href)
            links+=1
    receipt=dict(passed=True,local_links_checked=links,source_entries=len(result and json.loads(Path('data/s34_salience/config.json').read_text())['sources']),
                 all_key_replay=True,canonical_result_byte_identical=True,cached_resume_byte_identical=True,
                 independent=independent,result_sha256=hashlib.sha256(expected.encode()).hexdigest())
    Path('logs/s34_release.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));return receipt

def clean_clone():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    artifacts=['results/s34_salience.json','results/s34_summary.md','logs/s34_independent.json','figures/s34_salience.png','REPORT.md','logs/s34_release.json']
    with tempfile.TemporaryDirectory(prefix='s34_clean_',dir='/var/tmp') as td:
        clone=Path(td)/'repo'
        remote=subprocess.check_output(['git','remote','get-url','origin'],text=True).strip()
        subprocess.run(['git','clone','--quiet',remote,str(clone)],check=True)
        subprocess.run(['git','checkout','--quiet',head],cwd=clone,check=True)
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1')
        commands=[['scripts/s34_release.py'],['-m','unittest','scripts.test_s34'],['scripts/s34_independent.py'],['scripts/s34_present.py']]
        for command in commands:subprocess.run([str(root/'.venv/bin/python'),*command],cwd=clone,env=env,check=True)
        for name in artifacts:assert (clone/name).read_bytes()==(root/name).read_bytes(),name
        assert not subprocess.check_output(['git','status','--porcelain'],cwd=clone,text=True)
        receipt=dict(passed=True,commit=head,clone_source='origin remote',dependency_environment='Existing venv with frozen dependencies',
                     byte_identical_artifacts={name:hashlib.sha256((clone/name).read_bytes()).hexdigest() for name in artifacts},commands=commands)
    Path('logs/s34_clean_clone.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS clean clone '+head+': six byte-identical artifacts')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--clean-clone',action='store_true');a=p.parse_args()
    clean_clone() if a.clean_clone else check()
