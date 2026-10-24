"""S31 independent raw/action/statistics reconstruction; no sim/analyzer imports."""
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import statistics
import numpy as np
from scipy.stats import t

if not __debug__:raise RuntimeError('No optimized verification')
KEYS=['worker_earnings','offered_wage','employer_profit','tie_rate','stage_regret']

def unique(pairs):
    obj={}
    for k,v in pairs:
        if k in obj:raise ValueError('Duplicate key')
        obj[k]=v
    return obj

def accepted(text):
    try:
        obj=json.loads(text,object_pairs_hook=unique,parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite')))
        if type(obj) is not dict or set(obj)!={'wage','reasoning','note'}:return None
        if type(obj['wage']) is not int or not 0<=obj['wage']<=20:return None
        if type(obj['reasoning']) is not str or type(obj['note']) is not str:return None
        return obj
    except (ValueError,TypeError):return None

def payoff(ws,i):
    return F(20-ws[i],ws.count(ws[i])) if ws[i]==max(ws) else F(0)

def summarize(v):
    # Independent explicit value Cartesian product and NumPy linear quantile.
    b=[float(sum(x)/5) for x in itertools.product(v,repeat=5)]
    m=float(statistics.mean(v));se=float(statistics.stdev(v))/5**.5
    return m,np.quantile(b,[.025,.975]),[m-t.ppf(.975,4)*se,m+t.ppf(.975,4)*se]

def verify(data='data/s31_labor',result='results/s31_labor.json'):
    d=Path(data);r=json.loads(Path(result).read_text());cfg=json.loads((d/'config.json').read_text())
    raw=[json.loads(x) for x in (d/'raw/responses.jsonl').read_text().splitlines()]
    requests=[json.loads(x) for x in (d/'raw/requests.jsonl').read_text().splitlines()]
    rb={x['key']:x['response'] for x in raw};qb={x['key']:x for x in requests}
    assert len(rb)==len(raw)==len(qb)==len(requests) and set(rb)==set(qb)
    for key,q in qb.items():
        assert key==hashlib.sha256(json.dumps([q['dry'],q['payload']]).encode()).hexdigest()
        assert q['response_sha256']==hashlib.sha256(json.dumps(rb[key],sort_keys=True).encode()).hexdigest()
        assert q['dry']==cfg['dry']
        assert rb[key]['backend']==('dry' if cfg['dry'] else 'codex')
        assert rb[key]['model']==('dry' if cfg['dry'] else 'gpt-6-luna')
    cases={};used=[];aux=0
    gs=[json.loads(p.read_text()) for p in sorted(d.glob('game_*.json'))]
    assert len(gs)==10
    for g in gs:
        gt=g['ground_truth'];s,c=gt['seed'],gt['condition'];active=[a['id'] for a in g['rows'][0]['agents']]
        vectors=[];notes=[];reasons=[];calls=[]
        for row in g['rows']:
            turn=row['round'];ws=[]
            for a in row['agents']:
                selected=sorted([q for q in requests if q['payload'][5:8]==[gt['run_id'],turn,a['id']]],key=lambda q:q['payload'][8])
                assert [q['payload'][8] for q in selected]==list(range(len(selected))) and 1<=len(selected)<=3
                for q in selected:
                    key=q['key'];used.append(key)
                    calls.append(dict(round=turn,agent=a['id'],attempt=q['payload'][8],model=rb[key]['model'],backend=rb[key]['backend'],call_started_utc=rb[key].get('call_started_utc'),call_completed_utc=rb[key].get('call_completed_utc')))
                if not cfg['dry']:
                    assert all(accepted(rb[q['key']]['text']) is None for q in selected[:-1]),'Discarded valid response'
                    assert accepted(rb[selected[-1]['key']]['text']) is not None,'Accepted invalid response'
                q=selected[-1];text=rb[q['key']]['text'];obj=json.loads(text)
                # Only synthetic dry adapter is intentionally transformed.
                if cfg['dry']:obj=dict(wage=obj['quantity'],note='dry note',reasoning='dry')
                assert obj['wage']==a['price'];ws.append(obj['wage'])
                visible=notes if c=='shared' else [m for m in notes if m['author']==a['id']]
                snapshot=json.loads(q['payload'][1].split('Notes file snapshot: ')[1].split('\n')[0])
                assert snapshot==visible
                assert all(m['round']<=turn for m in snapshot)
                reasons.append(dict(round=turn,agent=a['id'],reasoning=obj['reasoning']))
                aux+=1
            pay=[payoff(ws,i) for i in range(2)]
            assert row['market']==dict(worker_earnings=max(ws),productivity=20,labor_supply=1)
            assert [a['profit'] for a in row['agents']]==list(map(float,pay))
            shares=[F(1,ws.count(max(ws))) if w==max(ws) else F(0) for w in ws]
            assert [a['quantity'] for a in row['agents']]==list(map(float,shares))
            for a in row['agents']:
                q=next(q for q in reversed(requests) if q['payload'][5:8]==[gt['run_id'],turn,a['id']])
                obj=json.loads(rb[q['key']]['text']);notes.append(dict(round=turn+1,author=a['id'],text='dry note' if cfg['dry'] else obj['note']))
            regret=sum(max(payoff([w if j!=i else new for j,w in enumerate(ws)],i) for new in range(21))-pay[i] for i in range(2))/2
            vectors.append([F(max(ws)),F(sum(ws),2),sum(pay),F(ws[0]==ws[1]),regret])
        assert notes==gt['notes_file'] and reasons==gt['reasoning_notes'] and calls==gt['call_provenance']
        cases[s,c]={k:sum(v[j] for v in vectors[2:])/8 for j,k in enumerate(KEYS)}
    assert len(used)==len(set(used))==len(raw) and set(used)==set(rb)
    assert set(cases)==set(itertools.product(range(24560,24565),['self','shared']))
    cells=summaries=signsets=0
    reports={(x['seed'],x['condition']):x['primary'] for x in r['games']}
    assert set(reports)==set(cases) and r['primary_contrast']=='self minus shared'
    for case,vs in cases.items():
        for k,v in vs.items():assert reports[case][k]==float(v);cells+=1
    for k in KEYS:
        no=[cases[s,'self'][k] for s in range(24560,24565)];yes=[cases[s,'shared'][k] for s in range(24560,24565)];ds=[a-b for a,b in zip(no,yes)]
        m=r['metrics'][k]
        assert m['seed_differences']==list(map(float,ds)) and m['exact_denominator']==32
        assert m['exact_seed_difference_numerators']==[int(x*32) for x in ds]
        for label,v in [('self',no),('shared',yes),('paired_difference',ds)]:
            sm=m[label];mean,ci,tc=summarize(v)
            assert abs(sm['mean']-mean)<1e-12 and F(sm['mean_exact'])==sum(v)/5
            assert np.allclose(ci,sm['ci95'],atol=1e-12,rtol=0)
            assert np.allclose(tc,sm['paired_t_ci95'],atol=1e-12,rtol=0)
            assert np.allclose(list(map(float,map(F,sm['ci95_exact']))),ci,atol=1e-12,rtol=0)
            summaries+=1
        obs=sum(ds);null=[sum(x*z for x,z in zip(ds,zs)) for zs in itertools.product([-1,1],repeat=5)]
        for label,num in [('upper',sum(v>=obs for v in null)),('lower',sum(v<=obs for v in null)),('two_sided',sum(abs(v)>=abs(obs) for v in null))]:assert m['paired_difference']['exact_signflip_p_'+label]==num/32
        signsets+=1
    sm=r['metrics']['worker_earnings']['paired_difference'];mean=F(sm['mean_exact']);lo,hi=map(F,sm['ci95_exact'])
    profit=sum(cases[s,'shared']['employer_profit']-cases[s,'self']['employer_profit'] for s in range(24560,24565))/5
    assert profit==mean==F(r['shared_minus_self_profit_exact'])
    verdict='HIT' if mean>=2 and lo>0 and sm['exact_signflip_p_upper']<=.05 and profit>0 else ('DUD' if mean<=F(1,2) or hi<2 else 'ODD')
    assert verdict==r['verdict']
    return dict(passed=True,metric_cells=cells,bootstrap_and_t_summaries=summaries,sign_sets=signsets,raw_keys=len(used),notes_and_reasons=aux,verdict=verdict,primary_mean=float(mean),primary_ci=sm['ci95'],upper_p=sm['exact_signflip_p_upper'],result_sha256=hashlib.sha256(Path(result).read_bytes()).hexdigest())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s31_labor');p.add_argument('--result',default='results/s31_labor.json');p.add_argument('--out',default='logs/s31_independent.json');a=p.parse_args()
    obj=verify(a.data,a.result);Path(a.out).write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(obj,indent=2))
