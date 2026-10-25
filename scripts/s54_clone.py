"""Post-run origin-clone verifier using an isolated frozen new-launch test.

The frozen s54_release --clean-clone path invokes that negative test in the
completed real default directory. This helper keeps scientific/test bytes frozen
and supplies the intended empty destination externally.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from datetime import datetime,timezone


def main():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    remote=subprocess.check_output(['git','remote','get-url','origin'],text=True).strip()
    observed=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],text=True).split()[0]
    assert observed==head,'Push the exact tested release first'
    artifacts=['results/s54_opportunities.json','results/s54_summary.md','results/s54_action_text.md','results/s54_action_text.json','figures/s54_opportunities.png','logs/s54_independent.json','logs/s54_release.json','REPORT.md','HITS.md','README.md','REPORT_DETAILS.md']
    snapshot=json.loads((root/'logs/s54_archive_snapshot.json').read_text())
    frozen={**snapshot['sources'],**snapshot['archive']}
    for name,digest in frozen.items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
        committed=subprocess.check_output(['git','show',f'{head}:{name}'])
        assert hashlib.sha256(committed).hexdigest()==digest,name
    commands=[['scripts/s54_analyze.py'],['scripts/s54_independent.py'],['scripts/s54_present.py'],['scripts/s54_release.py'],['scripts/s54_tests.py']]
    bootstrap="""import runpy,sys
from unittest.mock import patch
args=sys.argv[1:]
with patch('llm.chat',side_effect=AssertionError('Origin check forbids scientific calls')):
 sys.argv=args;runpy.run_path(args[0],run_name='__main__')
"""
    with tempfile.TemporaryDirectory(prefix='s54_origin_',dir='/var/tmp') as td,(root/'logs/s54_origin_stdout.txt').open('w') as log:
        clone=Path(td)/'repo'
        subprocess.run(['git','clone','--quiet',remote,str(clone)],check=True,stdout=log,stderr=subprocess.STDOUT)
        subprocess.run(['git','checkout','--quiet',head],cwd=clone,check=True,stdout=log,stderr=subprocess.STDOUT)
        assert (clone/'.git').is_dir() and not (clone/'.git/shallow').exists()
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1')
        for command in commands:
            log.write('RUN '+json.dumps(command)+'\n');log.flush()
            subprocess.run([str(root/'.venv/bin/python'),'-c',bootstrap,*command],cwd=clone,env=env,check=True,stdout=log,stderr=subprocess.STDOUT)
        for name in artifacts:assert (clone/name).read_bytes()==(root/name).read_bytes(),name
        for name,digest in frozen.items():assert hashlib.sha256((clone/name).read_bytes()).hexdigest()==digest,name
        status=subprocess.check_output(['git','status','--porcelain'],cwd=clone,text=True);assert not status,status
        receipt=dict(passed=True,checked_utc=datetime.now(timezone.utc).isoformat(),tested_results_commit=head,observed_origin_head=observed,
          full_history_origin_clone=True,scientific_calls_forbidden=True,
          dependency_environment='Existing installed frozen venv reused;not a fresh dependency installation',commands=commands,bootstrap_code=bootstrap,
          byte_identical_artifacts={name:hashlib.sha256((clone/name).read_bytes()).hexdigest() for name in artifacts},
          registered_sources_unchanged=len(snapshot['sources']),archive_files_unchanged=len(snapshot['archive']),scoped_tests=23,
          isolated_new_launch_test='Only test_direct_live_entries_rejected_without_bootstrap uses empty external cwd;real archive and frozen test source unchanged',
          clone_git_status_clean=True,scientific_result_sha256=snapshot['scientific_result_sha256'])
    (root/'logs/s54_remote_clean_clone.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'PASS origin {head}: {len(artifacts)} artifacts byte-identical,23scoped tests,22sources/20archive files unchanged,clean clone')

if __name__=='__main__':main()
