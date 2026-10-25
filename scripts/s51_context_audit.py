"""Pre-outcome census of retained historical policy cues, not outcome selection."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import subprocess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import s51_replay as s


def audit():
    cases=s.select_cases()['cases'];rows=[]
    for c in cases:
        before,marker,tail=c['original_prompt'].partition('\nNotes file snapshot: ')
        notes,ending,after=tail.partition('\nReturn strict JSON only')
        assert marker and ending
        # Public numeric scores/charges stay intact. No textual old-policy rule
        # occurs outside the dated historical notes in these source requests.
        for term in ['3-point','bonus -2']:
            assert term not in before+after
        baseline=s.request(c,'baseline');strong=s.request(c,'strong')
        assert '3-point' not in strong['system'] and 'bonus -2' not in strong['system']
        assert strong['prompt']==baseline['prompt']
        assert c['original_system'].endswith(' ')
        parsed=json.loads(notes)
        rows.append(dict(case_id=c['case_id'],round_1based=c['turn']+1,own_status=c['own_status'],
                         historical_notes_with_3point_text=sum('3-point' in n['text'] for n in parsed)))
    subprocess.run(['git','check-ignore','--quiet','data/s51_penalty/.writer.lock'],cwd=s.ROOT,check=True)
    return dict(passed=True,cases_sha256=s.digest(s.ROOT/'data/s51_cases.json'),
                n_cases=len(rows),own_status_counts=dict(Counter(r['own_status'] for r in rows)),
                cases_with_historical_3point_text=sum(r['historical_notes_with_3point_text']>0 for r in rows),
                textual_old_policy_outside_notes=False,writer_lock_gitignored=True,
                interpretation='Dated notes retain old policy by design; current-policy system notice overrides it, with possible cue interference.',cases=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='logs/s51_context_audit.json');a=p.parse_args()
    r=audit();Path(a.out).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
