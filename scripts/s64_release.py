"""Full offline S64 archive reproduction; never permits live calls."""
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
from scripts.s64_analyze import analyze
from scripts.s64_independent import verify as checked_verify


def check():
    paths=list(Path('data/s64_memory_retention').rglob('*'))
    original={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file() and p.name!='.writer.lock'}
    with patch('sim.common_memory.llm.chat',side_effect=AssertionError('Release forbids model calls')):
        with contextlib.redirect_stdout(io.StringIO()):result=analyze('data/s64_memory_retention')
        expected=json.dumps(result,indent=2)+'\n';assert expected==Path('results/s64_memory_retention.json').read_text()
        independent=checked_verify('data/s64_memory_retention','results/s64_memory_retention.json')
        assert independent==json.loads(Path('logs/s64_independent.json').read_text())
        from sim.memory_retention import main as resume
        with patch.object(sys,'argv',['sim.memory_retention']),contextlib.redirect_stdout(io.StringIO()):resume()
    for p,digest in original.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest,p
    from scripts.s64_present import main as render
    with tempfile.TemporaryDirectory(prefix='s64_render_',dir='/var/tmp') as td:
        destination=Path(td)
        (destination/'results').mkdir();(destination/'figures').mkdir()
        (destination/'results/s64_memory_retention.json').write_text(expected)
        (destination/'data').mkdir()
        (destination/'data/s64_memory_retention').symlink_to(Path('data/s64_memory_retention').resolve(),target_is_directory=True)
        with contextlib.chdir(destination),contextlib.redirect_stdout(io.StringIO()):
            render()
            from scripts.s64_action_text import main as action_text
            action_text()
        for name in ['results/s64_summary.md','figures/s64_memory.png','results/s64_action_text.json','results/s64_action_text.md']:
            assert (destination/name).read_bytes()==Path(name).read_bytes(),'Rendered artifact mismatch: '+name
    from scripts.s64_publish import apply as publication_check
    publication=publication_check(True)
    links=0
    for doc in ['REPORT.md','README.md','HITS.md','REPORT_DETAILS.md','results/s64_summary.md','results/s64_action_text.md']:
        for link in re.findall(r'\]\(([^)]+)\)',Path(doc).read_text()):
            href=link.strip('<>').split('#')[0]
            if not href or '://' in href:continue
            assert (Path(doc).parent/href).exists(),(doc,href)
            links+=1
    receipt=dict(passed=True,local_links_checked=links,source_entries=len(result and json.loads(Path('data/s64_memory_retention/config.json').read_text())['sources']),
                 all_key_replay=True,canonical_result_byte_identical=True,cached_resume_byte_identical=True,
                 independent=independent,publication=publication,rendered_artifacts=4,result_sha256=hashlib.sha256(expected.encode()).hexdigest())
    Path('logs/s64_release.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));return receipt

def clean_clone():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    artifacts=['results/s64_memory_retention.json','results/s64_summary.md','logs/s64_independent.json','figures/s64_memory.png','REPORT.md','HITS.md','README.md','REPORT_DETAILS.md','results/s64_action_text.json','results/s64_action_text.md','logs/s64_release.json']
    with tempfile.TemporaryDirectory(prefix='s64_clean_',dir='/var/tmp') as td:
        clone=Path(td)/'repo'
        remote=subprocess.check_output(['git','remote','get-url','origin'],text=True).strip()
        subprocess.run(['git','clone','--quiet',remote,str(clone)],check=True)
        subprocess.run(['git','checkout','--quiet',head],cwd=clone,check=True)
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1')
        commands=[['scripts/s64_release.py'],['-m','unittest','scripts.test_s64'],['scripts/s64_independent.py'],['scripts/s64_present.py']]
        for command in commands:subprocess.run([str(root/'.venv/bin/python'),*command],cwd=clone,env=env,check=True)
        for name in artifacts:assert (clone/name).read_bytes()==(root/name).read_bytes(),name
        assert subprocess.check_output(['git','status','--porcelain'],cwd=clone,text=True)==''
        receipt=dict(passed=True,commit=head,clone_source='origin',clone_clean=True,dependency_environment='Existing venv with frozen dependencies',
                     byte_identical_artifacts={name:hashlib.sha256((clone/name).read_bytes()).hexdigest() for name in artifacts},commands=commands)
    Path('logs/s64_clean_clone.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS clean clone '+head+': eleven byte-identical artifacts')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--clean-clone',action='store_true');a=p.parse_args()
    clean_clone() if a.clean_clone else check()
