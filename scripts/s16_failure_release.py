"""Release checks for the failed S16 run, including a clean-clone reproduction."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_failure_audit import audit


def check(out='logs/s16_release.json'):
    result=Path('results/s16_failure.json');actual=audit()
    assert result.read_bytes()==(json.dumps(actual,indent=2)+'\n').encode(),'Failure result differs from canonical reconstruction'
    assert not Path('results/s16_tender.json').exists(),'No scientific result may be published for the failed dataset'
    links=0
    for doc in ['REPORT.md','README.md','HITS.md','results/s16_summary.md']:
        for target in re.findall(r'\]\(([^)]+)\)',Path(doc).read_text()):
            href=target.strip('<>').split('#')[0]
            if not href or '://' in href:continue
            assert (Path(doc).parent/href).exists() or (Path(doc).parent/href).resolve()==Path(out).resolve(),(doc,href)
            links+=1
    output=dict(status='failed pilot; no scientific effect estimate',all_key_cached_prefix_replay=True,independent_saved_history_snapshot_audit=True,
                scientific_sources_unchanged=True,source_count=actual['scientific_sources_verified'],responses=actual['responses'],accepted_decisions=actual['accepted_decisions'],
                rejected_responses=actual['rejected_responses'],complete_games=actual['complete_games'],failed_analysis_and_live_resume_blocked=True,
                retained_evidence_byte_identical=True,links_checked=links,registration_commit=actual['registration_commit'],failure_result_sha256=hashlib.sha256(result.read_bytes()).hexdigest(),
                postfailure_audit_source_sha256=hashlib.sha256(Path('scripts/s16_failure_audit.py').read_bytes()).hexdigest())
    Path(out).write_text(json.dumps(output,indent=2)+'\n');print('PASS failed S16 release: exact173-key reconstruction, no effect estimate');return output


def clean_clone():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    with tempfile.TemporaryDirectory(prefix='s16_failure_clean_',dir='/var/tmp') as td:
        clone=Path(td)/'repo';subprocess.run(['git','clone','--quiet','--no-local',str(root),str(clone)],check=True)
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1');py=str(root/'.venv/bin/python')
        for command in [['scripts/s16_failure_release.py'],['-m','unittest','scripts.test_s16','scripts.test_s16_failure'],['scripts/s16_failure_audit.py'],['scripts/s16_failure_present.py']]:
            subprocess.run([py,*command],cwd=clone,env=env,check=True)
        artifacts=['results/s16_failure.json','results/s16_summary.md','figures/s16_failure.png','REPORT.md']
        assert all((clone/f).read_bytes()==(root/f).read_bytes() for f in artifacts)
        print(f'PASS clean clone {head}: failed-protocol checks and {len(artifacts)} byte-identical outputs')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--clean-clone',action='store_true');a=p.parse_args();clean_clone() if a.clean_clone else check()
