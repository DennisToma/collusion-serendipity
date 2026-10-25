"""POST-OUTCOME S33 reporting-exposure diagnostic; never changes frozen estimates.

Written after observing primary DUD and zero registered extra/waived charges.
Counts describe requests and qualifying actions, not beliefs or intent.
"""
from collections import Counter
import json
from pathlib import Path

if not __debug__:
    raise RuntimeError('Research integrity checks require Python without -O')


def diagnostic():
    root=Path('data/s33_leniency');result=json.loads(Path('results/s33_leniency.json').read_text())
    assert result['pilot']=='S33' and result['verdict']=='DUD'
    by={}
    for condition in ['baseline','amnesty']:
        windows={}
        for name,start in [('all_rounds',0),('primary',2)]:
            counts=Counter();cells=Counter()
            games=[json.loads(p.read_text()) for p in sorted(root.glob(f'game_*_{condition}.json'))]
            assert len(games)==5
            for game in games:
                for row in game['rows'][start:]:
                    records={a['id']:a for a in row['agents']};passed=row['market']['passed']
                    counts['rounds']+=1
                    counts['both_submissions_Y']+=int(not any(passed.values()))
                    for agent,action in records.items():
                        partner=next(a for a in records if a!=agent)
                        own_bad=action['reviews'][partner] and not passed[partner]
                        partner_bad=records[partner]['reviews'][agent] and not passed[agent]
                        flag=action['report'];qualified=flag and partner_bad
                        counts['decisions']+=1;counts['adverse_reviews']+=own_bad
                        counts['report_flags']+=flag;counts['qualifying_requests']+=qualified
                        counts['reported_own_adverse_reviews']+=flag and own_bad
                        counts['reports_with_reporter_submission_Y']+=flag and not passed[agent]
                        counts['reports_with_partner_submission_Y']+=flag and not passed[partner]
                        counts['waiver_eligible_own_adverse_reviews']+=qualified and own_bad
                        key=f'reporter_{"X" if passed[agent] else "Y"}_partner_{"X" if passed[partner] else "Y"}'
                        cells[key+'_decisions']+=1;cells[key+'_flags']+=flag
            counts=dict(sorted(counts.items()));cells=dict(sorted(cells.items()))
            windows[name]=dict(counts=counts,type_cells=cells)
        by[condition]=windows
        c=windows['primary']['counts'];metrics=result['metrics']
        assert c['report_flags']/40==metrics['reports'][condition]['mean']
        assert c['adverse_reviews']/40==metrics['pair_bad'][condition]['mean']
        if condition=='amnesty':
            assert 6*c['qualifying_requests']/40==metrics['extra_charges'][condition]['mean']
            assert 3*c['waiver_eligible_own_adverse_reviews']/40==metrics['waived_charges'][condition]['mean']
    return dict(passed=True,scope='POST-OUTCOME descriptive exposure diagnostic; no causal/intent/secondary promotion',conditions=by)

if __name__=='__main__':
    result=diagnostic();Path('results/s33_reporting_diagnostic.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
