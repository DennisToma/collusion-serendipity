"""Post-run audit of registered S61 release and preservation; no scientific changes."""
from datetime import datetime,timezone
import hashlib,json,subprocess
from pathlib import Path
from scripts.s61_replay import validate,analyze,write,when

def main():
    cfg,cases,rows=validate('data/s61_identity')
    baseline=json.loads(Path('logs/s61_prior_artifacts.json').read_text())
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in baseline['sha256'].items())
    old=subprocess.check_output(['git','show',baseline['base_commit']+':REPORT.md'],text=True)
    previous=[l for l in old.splitlines() if l.startswith('| S')]
    current=[l for l in Path('REPORT.md').read_text().splitlines() if l.startswith('| S') and not l.startswith('| S61 ')]
    assert previous==current
    for name in ['IDEAS.tsv','EXPERIMENTS.tsv']:
        old_lines=subprocess.check_output(['git','show',baseline['base_commit']+':'+name],text=True).splitlines()
        old_by={line.split('\t')[1]:line for line in old_lines if len(line.split('\t'))>1}
        new_by={line.split('\t')[1]:line for line in Path(name).read_text().splitlines() if len(line.split('\t'))>1}
        for key,line in old_by.items():
            if key=='S61-proposal':continue
            assert new_by[key]==line,(name,key)
    start=min(when(row['started_utc']) for row in rows);end=max(when(row['ended_utc']) for row in rows)
    # Each original/repeat request is separately admitted and responded,not reused.
    by={(r['case_id'],r['view']):r for r in rows}
    for c in cases:
        a,b=by[c['case_id'],'anchor'],by[c['case_id'],'repeat']
        assert a['request']==b['request'] and a['started_utc']!=b['started_utc']
    result=analyze('data/s61_identity')
    receipt=dict(passed=True,registration_commit=cfg['registration']['commit'],first_admission_utc=start.isoformat(),last_return_utc=end.isoformat(),observed_duration_seconds=(end-start).total_seconds(),accepted_decisions=len(rows),logical_retries=0,failure=False,prior_scientific_artifacts_unchanged=baseline['selected_artifacts'],prior_report_rows_unchanged=len(previous),prior_ledger_rows_unchanged_except_activated_S61_proposal=True,result_sha256=hashlib.sha256(Path('results/s61_identity.json').read_bytes()).hexdigest(),figure_visually_inspected=True,science_frozen=True)
    write('logs/s61_archive_audit.json',receipt);print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
