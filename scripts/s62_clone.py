"""Post-outcome origin-clone proof,including all S62 presentation artifacts."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


def main():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    remote=subprocess.check_output(['git','remote','get-url','origin'],text=True).strip()
    observed=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],text=True).split()[0]
    assert head==observed,'Push results before origin verification'
    artifacts=['results/s62_notepad_qwen.json','results/s62_summary.md','logs/s62_independent.json',
               'figures/s62_notepad.png','REPORT.md','logs/s62_release.json','results/s62_action_text.json',
               'results/s62_action_text.md','REPORT_DETAILS.md','README.md','HITS.md','logs/s62_document_check.json','logs/s62_probe_check.json']
    commands=[['scripts/s62_probe_check.py'],['scripts/s62_release.py'],['-m','unittest','scripts.test_s62'],['scripts/s62_independent.py'],
              ['scripts/s62_present.py'],['scripts/s62_action_text.py'],['scripts/s62_integrate.py']]
    launcher="""import runpy,sys
from unittest.mock import patch
args=sys.argv[1:]
with patch('llm.chat',side_effect=AssertionError('Origin proof forbids scientific calls')):
 if args[0]=='-m':
  sys.argv=[args[1],*args[2:]];runpy.run_module(args[1],run_name='__main__')
 else:
  sys.argv=args;runpy.run_path(args[0],run_name='__main__')
"""
    with tempfile.TemporaryDirectory(prefix='s62_origin_',dir='/var/tmp') as td:
        clone=Path(td)/'repo'
        subprocess.run(['git','clone','--quiet',remote,str(clone)],check=True)
        subprocess.run(['git','checkout','--quiet',head],cwd=clone,check=True)
        assert not (clone/'.git/shallow').exists()
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1')
        for command in commands:
            subprocess.run([str(root/'.venv/bin/python'),'-c',launcher,*command],cwd=clone,env=env,check=True)
        for name in artifacts:assert (clone/name).read_bytes()==(root/name).read_bytes(),name
        assert not subprocess.check_output(['git','status','--porcelain'],cwd=clone,text=True)
        receipt=dict(passed=True,commit=head,observed_origin_head=observed,full_history_origin_clone=True,
                     scientific_calls_forbidden=True,clone_git_status_clean=True,
                     dependency_environment='Existing frozen installed venv;not a fresh dependency installation',
                     byte_identical_artifacts={name:hashlib.sha256((clone/name).read_bytes()).hexdigest() for name in artifacts},
                     commands=commands,scoped_tests=16)
    Path('logs/s62_remote_clean_clone.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'PASS origin clone {head}: {len(artifacts)} byte-identical artifacts;16 scoped tests;clean clone')

if __name__=='__main__':main()
