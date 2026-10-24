"""S06 release verification: cached resume, exact result reproduction and hashes."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))


def check(out='logs/s06_release.json'):
    from scripts.s06_analyze import analyze
    from sim import denomination
    from scripts.s06_request_audit import main as audit_requests
    from scripts.s06_checked_independent import check as independent
    from scripts.s06_chronology import main as chronology
    from scripts.s06_attempt_check import main as attempts
    d=Path('data/s06_denomination');result=Path('results/s06_denomination.json')
    paths=sorted(p for p in d.rglob('*') if p.is_file() and p.name!='.writer.lock')+[result]
    before={str(p):p.read_bytes() for p in paths}
    with patch('sim.common.llm.chat',side_effect=AssertionError('Release forbids live calls')):
        with patch.object(sys,'argv',['sim.denomination']):denomination.main()
        actual=analyze(d)
    assert (json.dumps(actual,indent=2)+'\n').encode()==before[str(result)]
    assert all(p.read_bytes()==before[str(p)] for p in paths)
    with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
        independent(d,result,Path(td)/'independent.json')
    audit_requests()
    chronology()
    attempts()
    cfg=json.loads((d/'config.json').read_text())
    assert not cfg['dry']
    for file,sha in cfg['sources'].items():
        assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==sha
        assert hashlib.sha256(subprocess.check_output(['git','show',f'{cfg["registration_commit"]}:{file}'])).hexdigest()==sha
    subprocess.run(['git','merge-base','--is-ancestor',cfg['registration_commit'],'HEAD'],check=True)
    checked_links=0
    for doc in ['REPORT.md','README.md','HITS.md','results/s06_summary.md']:
        for href in re.findall(r'\]\(([^)]+)\)',Path(doc).read_text()):
            href=href.strip('<>').split('#')[0]
            if not href or '://' in href or href.startswith('mailto:'):continue
            target=Path(doc).parent/href
            assert target.exists() or target.resolve()==Path(out).resolve(),(doc,href)
            checked_links+=1
    audit=dict(worker_level_abort_propagation=True,independent_raw_request_displays=True,within_game_sequential_timestamps=True,inter_block_barriers=True,local_registration_chronology=True,local_document_links_checked=checked_links,cache_only_resume=True,byte_identical_data_and_result=True,independent_raw_metrics_and_statistics=True,independent_metadata_contract=True,independent_raw_attempt_counts=True,
               source_and_registration_hashes=True,registration_commit=cfg['registration_commit'],
               sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    Path(out).write_text(json.dumps(audit,indent=2)+'\n')
    print('PASS: cached resume, exact analysis bytes, independent arithmetic, sources/registration; '+str(len(paths))+' artifacts')


def clean_clone():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    with tempfile.TemporaryDirectory(prefix='s06_clean_',dir='/var/tmp') as td:
        clone=Path(td)/'repo'
        subprocess.run(['git','clone','--quiet','--no-local',str(root),str(clone)],check=True)
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1')
        interpreter=str(root/'.venv/bin/python')
        subprocess.run([interpreter,'scripts/s06_release.py'],cwd=clone,env=env,check=True)
        subprocess.run([interpreter,'-m','unittest','scripts.test_s06','scripts.test_s06_publication'],cwd=clone,env=env,check=True)
        scientific=['results/s06_denomination.json','results/s06_summary.md','figures/s06_denomination.png','logs/s06_independent.json','REPORT.md']
        subprocess.run([interpreter,'scripts/s06_checked_independent.py'],cwd=clone,env=env,check=True)
        subprocess.run([interpreter,'scripts/s06_present.py'],cwd=clone,env=env,check=True)
        assert all((clone/f).read_bytes()==(root/f).read_bytes() for f in scientific)
        print(f'PASS clean clone {head}: release audit,protocol tests,5 output artifacts byte-identical')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--clean-clone',action='store_true');a=p.parse_args()
    clean_clone() if a.clean_clone else check()
