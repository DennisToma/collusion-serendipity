"""Full offline S60 archive reproduction; never permits live calls."""
if not __debug__:raise RuntimeError('Research integrity checks require Python without -O')
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
from scripts.s60_analyze import analyze
from scripts.s60_independent import verify as checked_verify


def check():
    paths=list(Path('data/s60_author_bonus').rglob('*'))
    original={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file() and p.name!='.writer.lock'}
    with patch('sim.resource_cache.llm.chat',side_effect=AssertionError('Release forbids model calls')):
        with contextlib.redirect_stdout(io.StringIO()):result=analyze('data/s60_author_bonus')
        expected=json.dumps(result,indent=2)+'\n';assert expected==Path('results/s60_author_bonus.json').read_text()
        independent=checked_verify('data/s60_author_bonus','results/s60_author_bonus.json')
        assert independent==json.loads(Path('logs/s60_independent.json').read_text())
        from sim.author_bonus import main as resume
        with patch.object(sys,'argv',['sim.author_bonus']),contextlib.redirect_stdout(io.StringIO()):resume()
    for p,digest in original.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest,p
    links=0
    for doc in ['REPORT.md','README.md','HITS.md','results/s60_summary.md']:
        for link in re.findall(r'\]\(([^)]+)\)',Path(doc).read_text()):
            href=link.strip('<>').split('#')[0]
            if not href or '://' in href:continue
            assert (Path(doc).parent/href).exists(),(doc,href)
            links+=1
    receipt=dict(passed=True,local_links_checked=links,source_entries=len(result and json.loads(Path('data/s60_author_bonus/config.json').read_text())['sources']),
                 all_key_replay=True,canonical_result_byte_identical=True,cached_resume_byte_identical=True,
                 independent=independent,result_sha256=hashlib.sha256(expected.encode()).hexdigest())
    Path('logs/s60_release.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));return receipt

def clean_clone():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    artifacts=['results/s60_author_bonus.json','results/s60_summary.md','logs/s60_independent.json','figures/s60_author_bonus.png','results/s60_action_text.md','results/s60_action_text.json','logs/s60_release.json']
    with tempfile.TemporaryDirectory(prefix='s60_clean_',dir='/var/tmp') as td:
        clone=Path(td)/'repo'
        remote=subprocess.check_output(['git','remote','get-url','origin'],text=True).strip()
        observed=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],text=True).split()[0]
        assert observed==head,'Push the exact tested release first'
        subprocess.run(['git','clone','--quiet',remote,str(clone)],check=True)
        subprocess.run(['git','checkout','--quiet',head],cwd=clone,check=True)
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1')
        commands=[['scripts/s60_release.py'],['-m','unittest','scripts.test_s60'],['scripts/s60_independent.py'],['scripts/s60_present.py']]
        bootstrap="import runpy,sys\nfrom unittest.mock import patch\nargs=sys.argv[1:]\nwith patch('llm.chat',side_effect=AssertionError('Origin check forbids scientific calls')):\n if args[0]=='-m':\n  sys.argv=[args[1],*args[2:]];runpy.run_module(args[1],run_name='__main__')\n else:\n  sys.argv=args;runpy.run_path(args[0],run_name='__main__')\n"
        for command in commands:subprocess.run([str(root/'.venv/bin/python'),'-c',bootstrap,*command],cwd=clone,env=env,check=True)
        assert not (clone/'.git/shallow').exists()
        status=subprocess.check_output(['git','status','--porcelain'],cwd=clone,text=True);assert not status,status
        for name in artifacts:assert (clone/name).read_bytes()==(root/name).read_bytes(),name
        receipt=dict(passed=True,commit=head,observed_origin_head=observed,full_history_origin_clone=True,scientific_calls_forbidden=True,clone_git_status_clean=True,dependency_environment='Existing venv with frozen dependencies',
                     byte_identical_artifacts={name:hashlib.sha256((clone/name).read_bytes()).hexdigest() for name in artifacts},commands=commands)
    Path('logs/s60_remote_clean_clone.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS clean clone '+head+': byte-identical artifacts')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--clean-clone',action='store_true');a=p.parse_args()
    clean_clone() if a.clean_clone else check()
