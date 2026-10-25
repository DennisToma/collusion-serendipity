"""Separate raw/exact S56 reconstruction; no production metric imports."""
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import itertools
import json
import random
from pathlib import Path
import statistics
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy.stats import t

if not __debug__:raise RuntimeError('Integrity checks require ordinary Python')
KEYS=['payment','pair_profit','above_nash','payment_excess','pair_joint_regret','outsider_regret','coalition_stable','strict_pair_improvement']

@lru_cache(None)
def payoff(a,b,c):
    offers=[a,b,c];winning=min(offers);count=sum(x==winning for x in offers)
    return [Q(winning-6,count) if x==winning else Q(0) for x in offers]

@lru_cache(None)
def pair_rewards(c):return [payoff(a,b,c) for a in range(6,21) for b in range(6,21)]

@lru_cache(None)
def cell(a,b,c):
    p=payoff(a,b,c);joint=max(x[0]+x[1] for x in pair_rewards(c))-p[0]-p[1]
    outsider=max(payoff(a,b,z)[2] for z in range(6,21))-p[2]
    gains=any(x[0]>p[0] and x[1]>p[1] for x in pair_rewards(c))
    vals=[Q(min(a,b,c)),p[0]+p[1],Q(min(a,b,c)>7),Q(max(min(a,b,c)-7,0)),joint,outsider,Q(joint==0 and outsider==0),Q(gains)]
    regrets=[]
    for i in range(3):
        opts=[]
        for z in range(6,21):
            bs=[a,b,c];bs[i]=z;opts.append(payoff(*bs)[i])
        regrets.append(max(opts)-p[i])
    return dict(zip(KEYS,vals)),p,regrets

def validate_summary(v,r):
    if list(map(str,v))!=r['block_values_exact']:raise ValueError('Block values differ')
    mean=statistics.mean(v);boot=sorted(statistics.mean(x) for x in itertools.product(v,repeat=5));bounds=[]
    for prob in [Q(1,40),Q(39,40)]:
        idx=prob*3124;left=int(idx);weight=idx-left
        bounds.append(boot[left]+weight*(boot[min(left+1,3124)]-boot[left]))
    if str(mean)!=r['mean_exact'] or list(map(str,bounds))!=r['ci95_exact']:raise ValueError('Exact summary differs')
    se=float(statistics.stdev(v))/5**.5;radius=float(t.ppf(.975,4))*se
    if not np.allclose([float(mean),*map(float,bounds),float(mean)-radius,float(mean)+radius],
                       [r['mean'],*r['ci95'],*r['t95']],rtol=0,atol=1e-12):raise ValueError('Float summary differs')

def raw_bindings():
    root=Path('data/s14_tender');requests=[json.loads(s) for s in (root/'raw/requests.jsonl').read_text().splitlines()];responses=[json.loads(s) for s in (root/'raw/responses.jsonl').read_text().splitlines()]
    cache={r['key']:r['response'] for r in responses};lookup={};used=set();bindings=0
    assert len(cache)==len(responses)==len(requests)
    for r in requests:
        key=r['key'];payload=r['payload'];assert r['dry'] is False
        assert key==hashlib.sha256(json.dumps([r['dry'],payload]).encode()).hexdigest()
        assert r['response_sha256']==hashlib.sha256(json.dumps(cache[key],sort_keys=True).encode()).hexdigest()
        ident=tuple(payload[5:9]);assert ident not in lookup;lookup[ident]=(key,cache[key])
    for path in sorted(root.glob('game_*.json')):
        g=json.loads(path.read_text());gt=g['ground_truth'];provs=gt['call_provenance']
        assert gt['assigned_pair']==random.Random(gt['seed']).sample(list('ABC'),2)
        assert len(g['rows'])==12 and [row['round'] for row in g['rows']]==list(range(12))
        for rec in provs:
            ident=(gt['run_id'],rec['round'],rec['agent'],rec['attempt']);key,response=lookup[ident];used.add(key)
            for k in ['call_started_utc','call_completed_utc','model','backend']:assert response[k]==rec[k]
        for row in g['rows']:
            for agent in row['agents']:
                ps=[p for p in provs if p['round']==row['round'] and p['agent']==agent['id']];last=max(p['attempt'] for p in ps)
                _,response=lookup[(gt['run_id'],row['round'],agent['id'],last)];action=json.loads(response['text'])
                assert type(action['bid']) is int and action['bid']==agent['price'];bindings+=1
    assert used==set(cache) and bindings==360
    return dict(raw_bindings=bindings,raw_requests=len(requests))

def verify(r):
    assert r['id']=='S56' and r['posthoc'] is True and r['verdict']=='ODD/context-only'
    assert r['new_games']==r['scientific_model_calls']==r['tuning_attempts']==0 and r['n_blocks']==5 and r['primary_rounds']=='4..12'
    assert set(r['metrics'])==set(KEYS)
    reports={(g['seed'],g['condition']):g for g in r['games']};records={(g['seed'],g['condition'],g['round']):g for g in r['rounds']}
    expected=set(itertools.product(range(24200,24205),['none','private']));assert len(reports)==len(r['games'])==10 and set(reports)==expected
    assert len(records)==len(r['rounds'])==90 and set(records)=={(s,c,t) for s,c in expected for t in range(4,13)}
    bound=raw_bindings();by={};totals={c:{k:Q(0) for k in KEYS} for c in ['none','private']}
    for path in sorted(Path('data/s14_tender').glob('game_*.json')):
        g=json.loads(path.read_text());gt=g['ground_truth'];s,c=gt['seed'],gt['condition'];pair=gt['assigned_pair'];assert len(pair)==2 and len(set(pair))==2 and set(pair)<set('ABC')
        outside=next(a for a in 'ABC' if a not in pair);order=pair+[outside];acc={k:Q(0) for k in KEYS}
        for raw in g['rows'][3:12]:
            bids={a['id']:a['price'] for a in raw['agents']};assert set(bids)==set('ABC');bs=[bids[a] for a in order];vals,p,regrets=cell(*bs)
            archived_profits={a['id']:a['profit'] for a in raw['agents']}
            assert list(map(float,p))==[archived_profits[a] for a in order]
            saved=records[s,c,raw['round']+1]
            assert saved==dict(seed=s,condition=c,round=raw['round']+1,agent_order=order,bids=bs,metrics={k:str(v) for k,v in vals.items()},profits=list(map(str,p)),individual_regrets=list(map(str,regrets)))
            for k in KEYS:acc[k]+=vals[k]
        saved=reports[s,c];assert saved==dict(seed=s,condition=c,totals_exact={k:str(v) for k,v in acc.items()},means_exact={k:str(v/9) for k,v in acc.items()})
        by[s,c]={k:v/9 for k,v in acc.items()}
        for k,v in acc.items():totals[c][k]+=v
    assert {c:{k:str(v) for k,v in d.items()} for c,d in totals.items()}==r['totals']
    for k in KEYS:
        a=[by[s,'none'][k] for s in range(24200,24205)];b=[by[s,'private'][k] for s in range(24200,24205)]
        for label,vals in [('none',a),('private',b),('difference',[y-x for x,y in zip(a,b)])]:validate_summary(vals,r['metrics'][k][label])
    nash=[];stable=[];strict=0
    for bs in itertools.product(range(6,21),repeat=3):
        vals,_,regrets=cell(*bs)
        if sum(regrets)==0:nash.append(list(bs))
        if vals['coalition_stable']==1:stable.append(list(bs))
        strict+=int(vals['strict_pair_improvement'])
    census=dict(profiles=3375,nash_profiles=nash,nash_payments=sorted({min(bs) for bs in nash}),pair_singleton_stable_profiles=stable,stable_payments=sorted({min(bs) for bs in stable}),strict_pair_improvement_profiles=strict)
    assert census==r['census']
    return dict(passed=True,scope='Independent raw bid/provenance/payoff/statistic reconstruction; full prompt/history/retry eligibility and registration binding require production S14 replay and S56 manifest checks',rounds=90,game_cells=80,bootstrap_and_t_summaries=24,enumerated_profiles=3375,**bound)

if __name__=='__main__':
    r=json.loads(Path('results/s56_coalitions.json').read_text());output=verify(r)
    Path('logs/s56_independent.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n');print(json.dumps(output,indent=2))
