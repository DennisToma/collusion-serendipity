"""POST-OUTCOME release coordinator; includes the descriptive reporting companion.

This does not alter the20 registered sources, frozen estimates or verdict.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


def clean_clone():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    remote=subprocess.check_output(['git','remote','get-url','origin'],text=True).strip()
    commands=[['scripts/s33_analyze.py'],['scripts/s33_independent.py'],['scripts/s33_present.py'],['scripts/s33_reporting_diagnostic.py'],['scripts/s33_release.py'],['scripts/run_tests.py']]
    artifacts=['results/s33_leniency.json','results/s33_summary.md','results/s33_reporting_diagnostic.json','logs/s33_independent.json','logs/s33_release.json','figures/s33_leniency.png','REPORT.md']
    with tempfile.TemporaryDirectory(prefix='s33_remote_',dir='/var/tmp') as td:
        clone=Path(td)/'repo';subprocess.run(['git','clone','--quiet',remote,str(clone)],check=True)
        subprocess.run(['git','checkout','--quiet',head],cwd=clone,check=True)
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1')
        for command in commands:subprocess.run([str(root/'.venv/bin/python'),*command],cwd=clone,env=env,check=True,capture_output=True)
        for name in artifacts:
            if (clone/name).read_bytes()!=(root/name).read_bytes():raise RuntimeError('Clone artifact drift:'+name)
        if subprocess.check_output(['git','status','--porcelain'],cwd=clone,text=True):raise RuntimeError('Clone dirty after reproduction')
        receipt=dict(passed=True,commit=head,clone_source='origin remote',commands=commands,
                     dependency_environment='Existing frozen venv reused; no fresh dependency installation',
                     byte_identical_artifacts={name:hashlib.sha256((clone/name).read_bytes()).hexdigest() for name in artifacts})
    Path('logs/s33_remote_clean_clone.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS remote clone '+head+': seven artifacts byte-identical and clone clean')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--clean-clone',action='store_true',required=True);p.parse_args();clean_clone()
