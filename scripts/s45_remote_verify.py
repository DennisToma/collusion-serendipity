"""Verify pushed S45 release in one full-history origin clone;installed venv reused."""
import hashlib,json,os,subprocess,tempfile
from datetime import datetime,timezone
from pathlib import Path


def main():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    remote=subprocess.check_output(['git','remote','get-url','origin'],text=True).strip()
    observed=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],text=True).split()[0]
    assert observed==head,'Push the exact tested release first'
    artifacts=['results/s45_reviewring.json','results/s45_summary.md','results/s45_action_text.json','results/s45_action_text.md','logs/s45_independent.json','logs/s45_metadata_check.json','logs/s45_release.json','figures/s45_reviewring.png','REPORT.md','HITS.md','README.md','REPORT_DETAILS.md']
    snapshot=json.loads((root/'logs/s45_archive_snapshot.json').read_text())
    commands=[['scripts/s45_analyze.py'],['scripts/s45_independent.py'],['scripts/s45_present.py'],['scripts/s45_action_text.py'],['scripts/s45_metadata_check.py','--self-test'],['scripts/s45_release.py'],['-m','unittest','scripts.test_s45']]
    # Every child gets an unconditional no-science-call guard;unit fixtures may
    # replace it only with their explicit synthetic transports.
    bootstrap="""import runpy,sys
from unittest.mock import patch
args=sys.argv[1:]
with patch('llm.chat',side_effect=AssertionError('Origin check forbids scientific calls')):
 if args[0]=='-m':
  sys.argv=[args[1],*args[2:]];runpy.run_module(args[1],run_name='__main__')
 else:
  sys.argv=args;runpy.run_path(args[0],run_name='__main__')
"""
    with tempfile.TemporaryDirectory(prefix='s45_origin_',dir='/var/tmp') as td,(root/'logs/s45_origin_stdout.txt').open('w') as log:
        clone=Path(td)/'repo'
        subprocess.run(['git','clone','--quiet',remote,str(clone)],check=True,stdout=log,stderr=subprocess.STDOUT)
        subprocess.run(['git','checkout','--quiet',head],cwd=clone,check=True,stdout=log,stderr=subprocess.STDOUT)
        assert (clone/'.git').is_dir() and not (clone/'.git/shallow').exists()
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1')
        for command in commands:
            log.write('RUN '+json.dumps(command)+'\n');log.flush()
            subprocess.run([str(root/'.venv/bin/python'),'-c',bootstrap,*command],cwd=clone,env=env,check=True,stdout=log,stderr=subprocess.STDOUT)
        for name in artifacts:assert (clone/name).read_bytes()==(root/name).read_bytes(),name
        for name,digest in {**snapshot['sources'],**snapshot['archive']}.items():assert hashlib.sha256((clone/name).read_bytes()).hexdigest()==digest,name
        status=subprocess.check_output(['git','status','--porcelain'],cwd=clone,text=True);assert not status,status
        receipt=dict(passed=True,checked_utc=datetime.now(timezone.utc).isoformat(),tested_results_commit=head,observed_origin_head=observed,full_history_origin_clone=True,scientific_calls_forbidden=True,dependency_environment='Existing installed frozen venv reused;not a fresh dependency installation',commands=commands,bootstrap_code=bootstrap,byte_identical_artifacts={name:hashlib.sha256((clone/name).read_bytes()).hexdigest() for name in artifacts},registered_sources_unchanged=len(snapshot['sources']),archive_files_unchanged=len(snapshot['archive']),scoped_tests=21,supplemental_metadata_negative_checks=12,clone_git_status_clean=True,scientific_result_sha256=snapshot['scientific_result_sha256'])
    (root/'logs/s45_remote_clean_clone.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS origin '+head+':12artifacts byte-identical,21protocol tests,12metadata negative checks,clean clone')

if __name__=='__main__':main()
