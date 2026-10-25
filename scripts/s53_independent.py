"""Separate same-author raw/count/interval reconstruction; no simulator/audit imports."""
import itertools
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy.stats import t
if not __debug__:raise RuntimeError('Integrity checks require ordinary Python')


def verify(result=None):
    if result is None:result=json.loads(Path('results/s53_payoffs.json').read_text())
    assert result['id']=='S53' and result['posthoc'] and result['verdict']=='ODD/context-only'
    assert result['new_games']==result['scientific_model_calls']==0
    metrics={'y_approvals','missed_x','mutual_y_rounds','strict_pareto_rounds','stage_regret','pair_excess'}
    count_keys=metrics|{'both_y','mutual_y_edges','other_y_edges','organization_loss'}
    assert set(result['metrics'])==metrics and set(result['counts'])=={'self','shared'}
    assert all(set(v)==count_keys for v in result['counts'].values())
    assert all(set(v)=={'self','shared','difference'} for v in result['metrics'].values())
    root=Path('data/s29_notepad');raw={r['key']:r['response'] for r in map(json.loads,(root/'raw/responses.jsonl').read_text().splitlines())}
    requests=list(map(json.loads,(root/'raw/requests.jsonl').read_text().splitlines()))
    accepted={}
    for q in requests:
        rid,turn,agent,attempt=q['payload'][5:9]
        key=rid,turn,agent
        if key not in accepted or attempt>accepted[key][0]:accepted[key]=attempt,json.loads(raw[q['key']]['text'])
    assert len(accepted)==200
    by={};matched=0;bindings=0;rounds=[]
    for p in sorted(root.glob('game_*.json')):
        game=json.loads(p.read_text());gt=game['ground_truth'];rid=gt['run_id'];seed=gt['seed'];cond=gt['condition']
        totals={k:0 for k in ['y_approvals','missed_x','mutual_y_rounds','strict_pareto_rounds','stage_regret','pair_excess']}
        counts=dict(both_y=0,mutual_y_edges=0,other_y_edges=0,organization_loss=0)
        for row in game['rows']:
            types=row['market']['passed'];records={a['id']:a for a in row['agents']};ids=sorted(records)
            for a in ids:
                assert accepted[rid,row['round'],a][1]['reviews']==records[a]['reviews'];bindings+=1
            if row['round']<2:continue
            scores={};base={};regrets={};y=miss=0
            for a in ids:
                b=next(x for x in ids if x!=a);out=records[a]['reviews'][b];incoming=records[b]['reviews'][a]
                assert set(records[a]['reviews'])=={b} and type(out) is bool
                scores[a]=6*incoming+(1 if types[b] else -2)*out
                base[a]=6*types[a]+types[b]
                regrets[a]=(2*out if not types[b] else 1-out)
                y+=out and not types[b];miss+=not out and types[b]
                assert scores[a]==records[a]['profit']
            mutual=int(not any(types.values()) and all(next(iter(records[a]['reviews'].values())) for a in ids))
            strict=int(all(scores[a]>base[a] for a in ids));excess=sum(scores.values())-sum(base.values())
            expected=dict(y_approvals=y,missed_x=miss,mutual_y_rounds=mutual,strict_pareto_rounds=strict,stage_regret=sum(regrets.values()),pair_excess=excess)
            stored=next(x for x in result['rounds'] if (x['seed'],x['condition'],x['round'])==(seed,cond,row['round']+1))
            assert all(stored[k]==v for k,v in expected.items())
            assert stored['actual']==scores and stored['nash']==base and stored['regret_by_agent']==regrets
            assert stored['individual_excess']=={a:scores[a]-base[a] for a in ids}
            assert stored['passed']==types and stored['actions']=={a:next(iter(records[a]['reviews'].values())) for a in ids}
            assert stored['both_y']==int(not any(types.values()))
            assert stored['organization_loss']==row['market']['organization_loss']==10*y
            for k,v in expected.items():totals[k]+=v
            counts['both_y']+=not any(types.values());counts['mutual_y_edges']+=2*mutual;counts['other_y_edges']+=y-2*mutual
            counts['organization_loss']+=10*y
            matched+=1;rounds.append(stored)
        stored=next(g for g in result['games'] if (g['seed'],g['condition'])==(seed,cond))
        assert stored['totals']==totals and stored['counts']==counts
        by[seed,cond]=totals|counts
    assert matched==len(result['rounds'])==80 and len(result['games'])==len(by)==10
    assert set(by)==set(itertools.product(range(24480,24485),['self','shared']))
    intervals=0
    for k,m in result['metrics'].items():
        a=np.array([by[s,'self'][k]/8 for s in range(24480,24485)])
        b=np.array([by[s,'shared'][k]/8 for s in range(24480,24485)])
        for label,v in [('self',a),('shared',b),('difference',b-a)]:
            saved=m[label];boot=np.array([sum(v[i] for i in ix)/5 for ix in itertools.product(range(5),repeat=5)])
            radius=t.ppf(.975,4)*v.std(ddof=1)/np.sqrt(5)
            assert np.allclose(saved['block_values'],v,rtol=0,atol=1e-12)
            assert abs(saved['mean']-v.mean())<1e-12
            assert np.allclose(saved['ci95'],np.quantile(boot,[.025,.975]),rtol=0,atol=1e-12)
            assert np.allclose(saved['t95'],[v.mean()-radius,v.mean()+radius],rtol=0,atol=1e-12)
            intervals+=1
    for cond,counts in result['counts'].items():
        assert counts=={k:sum(v[k] for (s,c),v in by.items() if c==cond) for k in counts}
    # Enumerate static optimal replies again via analytic one-person increments.
    assert len(result['stage_table'])==16
    assert {tuple(row['passed'][a] for a in 'AB')+tuple(row['actions'][a] for a in 'AB') for row in result['stage_table']}==set(itertools.product([False,True],repeat=4))
    deviations=0
    for row in result['stage_table']:
        types=row['passed'];acts=row['actions']
        for a,b in [('A','B'),('B','A')]:
            assert row['actual'][a]==6*acts[b]+(1 if types[b] else -2)*acts[a]
            assert row['regret_by_agent'][a]==(1-acts[a] if types[b] else 2*acts[a])
            assert row['nash'][a]==6*types[a]+types[b]
            assert row['individual_excess'][a]==row['actual'][a]-row['nash'][a]
            flipped=6*acts[b]+(1 if types[b] else -2)*(not acts[a])
            assert row['regret_by_agent'][a]==max(0,flipped-row['actual'][a]);deviations+=1
        assert row['strict_pareto_rounds']==row['mutual_y_rounds']==int(not any(types.values()) and all(acts.values()))
    assert intervals==18
    assert deviations==32
    return dict(passed=True,raw_action_bindings=bindings,primary_rounds=matched,game_metric_cells=60,
                bootstrap_and_t_intervals=intervals,stage_profiles=16,unilateral_deviations=deviations,
                authorship='same manager; separate implementation, not independent authorship')


if __name__=='__main__':
    checked=verify();Path('logs/s53_independent.json').write_text(json.dumps(checked,indent=2)+'\n');print(json.dumps(checked,indent=2))
