"""Independent exact rational reconstruction; no production sim/metric imports."""
import argparse
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import statistics
import numpy as np
from scipy.stats import t as student_t

if not __debug__:
    raise RuntimeError('Research integrity checks require Python without -O')

KEYS=['payment','pair_profit','outsider_profit','pair_bid','outsider_bid','pair_share','tie','winner_change','stage_regret']

def auction(bs):
    low=min(bs);n=bs.count(low)
    sh=[F(1,n) if b==low else F(0) for b in bs]
    return low,sh,[(low-6)*v for v in sh]


def game_values(g,start):
    pair=g['ground_truth']['assigned_pair'];by={k:[] for k in KEYS}
    for t in range(start,12):
        row=g['rows'][t];bs=[a['price'] for a in row['agents']]
        low,shares,profits=auction(bs)
        assert row['market']['payment']==low
        assert list(map(float,shares))==[a['quantity'] for a in row['agents']]
        assert list(map(float,profits))==[a['profit'] for a in row['agents']]
        pp=[i for i,a in enumerate('ABC') if a in pair];o=next(i for i,a in enumerate('ABC') if a not in pair)
        regret=[]
        for i in range(3):
            rewards=[auction([b if j!=i else q for j,b in enumerate(bs)])[2][i] for q in range(6,21)]
            regret.append(max(rewards)-profits[i])
        w={i for i,s in enumerate(shares) if s}
        prev={i for i,a in enumerate(g['rows'][t-1]['agents']) if a['quantity']>0} if t else None
        vals=[F(low),sum(profits[i] for i in pp),profits[o],F(sum(bs[i] for i in pp),2),F(bs[o]),sum(shares[i] for i in pp),F(len(w)>1),F(w!=prev) if t else None,sum(regret)/3]
        for k,v in zip(KEYS,vals):
            if v is not None:by[k].append(v)
    return {k:sum(v)/len(v) for k,v in by.items()}


def check(data,result,out):
    d=Path(data);rp=Path(result);r=json.loads(rp.read_text());cfg=json.loads((d/'config.json').read_text())
    assert r['pilot']=='S16' and r['primary_metric']=='payment' and r['primary_contrast']==r['secondary_contrast']=='shared minus self'
    assert r['n_games']==10 and r['n_seed_blocks']==5 and r['primary_rounds']=='4..12' and r['tuning_attempts']==0
    assert r['model']==cfg['model']=='gpt-6-luna' and r['backend']==cfg['backend']=='codex' and r['dry']==cfg['dry']
    assert list(r['metrics'])==KEYS
    expected=set(itertools.product(range(24240,24245),['self','shared']))
    reports={(g['seed'],g['condition']):g for g in r['games']};assert len(reports)==len(r['games'])==10 and set(reports)==expected
    gs=[json.loads(p.read_text()) for p in sorted(d.glob('game_*.json'))]
    assert len(gs)==10 and {(g['ground_truth']['seed'],g['ground_truth']['condition']) for g in gs}==expected
    by={};cells=0
    for g in gs:
        gt=g['ground_truth'];key=gt['seed'],gt['condition']
        for label,start in [('primary',3),('all_rounds',0),('final',11)]:
            vals=game_values(g,start)
            for k,v in vals.items():assert abs(float(v)-reports[key][label][k])<1e-12;cells+=1
            if label=='primary':by[key]=vals
    note_counts={};retry_roles={c:{'pair':0,'outsider':0} for c in ['self','shared']}
    for c in ['self','shared']:
        es=[e for g in gs if g['ground_truth']['condition']==c for e in g['ground_truth']['notes_file']]
        av=[e for e in es if e['round']<12]
        note_counts[c]=dict(written=len(es),nonempty=sum(bool(e['text'].strip()) for e in es),available_entries=len(av),nonempty_available_entries=sum(bool(e['text'].strip()) for e in av),available_entry_reader_slots=len(av)*(1 if c=='self' else 2),history_entry_appearances=sum(12-e['round'] for e in es)*(1 if c=='self' else 2))
    requests=[json.loads(l) for l in (d/'raw/requests.jsonl').read_text().splitlines()]
    responses=[json.loads(l) for l in (d/'raw/responses.jsonl').read_text().splitlines()]
    assert len(responses)==len(requests)==r['cached_responses']
    pair_by={g['ground_truth']['run_id']:g['ground_truth']['assigned_pair'] for g in gs}
    for row in requests:
        payload=row['payload'];rid=payload[5];c=rid.split('_')[-1]
        if payload[8]>0:retry_roles[c]['pair' if payload[7] in pair_by[rid] else 'outsider']+=1
    assert r['descriptives']==dict(notes=note_counts,retries_by_arm_role=retry_roles)
    rng=np.random.default_rng(2424);intervals=0
    def summary(v,reported):
        nonlocal intervals
        a=np.asarray(list(map(float,v)))
        bootstrap_indices=rng.integers(0,5,(10000,5))
        b=a[bootstrap_indices].mean(axis=1)
        assert abs(float(a.mean())-reported['mean'])<1e-12
        assert np.allclose(np.quantile(b,[.025,.975]),reported['ci95'],rtol=0,atol=1e-12)
        if 'ci95_exact' in reported:
            exact_sums=sorted(sum(v[int(i)] for i in inds) for inds in bootstrap_indices)
            bounds=[]
            for prob in [F(1,40),F(39,40)]:
                pos=prob*9999;j=int(pos);w=pos-j
                bounds.append((exact_sums[j]*(1-w)+exact_sums[min(j+1,9999)]*w)/5)
            assert list(map(str,bounds))==reported['ci95_exact']
        intervals+=1
    for k,m in r['metrics'].items():
        no=[by[s,'self'][k] for s in range(24240,24245)];pr=[by[s,'shared'][k] for s in range(24240,24245)];ds=[p-n for p,n in zip(pr,no)]
        assert np.allclose(list(map(float,ds)),m['seed_differences'],rtol=0,atol=1e-12)
        summary(ds,m['paired_difference']);summary(no,m['self']);summary(pr,m['shared'])
        mean=float(statistics.mean(ds));se=float(statistics.stdev(ds))/5**.5
        assert np.allclose([mean-student_t.ppf(.975,4)*se,mean+student_t.ppf(.975,4)*se],m['paired_difference']['paired_t_ci95'],rtol=0,atol=1e-12)
    p=r['metrics']['payment'];ds=[by[s,'shared']['payment']-by[s,'self']['payment'] for s in range(24240,24245)]
    nums=[int(v*9) for v in ds];assert all(F(n,9)==v for n,v in zip(nums,ds));assert p['exact_denominator']==9 and nums==p['exact_seed_difference_numerators']
    null=[sum(n*z for n,z in zip(nums,zs)) for zs in itertools.product([-1,1],repeat=5)]
    observed=sum(nums);sm=p['paired_difference']
    for name,count in [('upper',sum(v>=observed for v in null)),('lower',sum(v<=observed for v in null)),('two_sided',sum(abs(v)>=abs(observed) for v in null))]:assert sm[f'exact_signflip_p_{name}']==count/32
    mean=sum(ds)/5;profit=sum(by[s,'shared']['pair_profit']-by[s,'self']['pair_profit'] for s in range(24240,24245))/5
    lo,hi=map(F,sm['ci95_exact'])
    verdict='HIT' if mean>=1 and lo>0 and sm['exact_signflip_p_upper']<=.05 and profit>0 else ('DUD' if mean<=F(1,4) or hi<1 else 'ODD')
    assert r['pair_profit_gate_exact']==str(profit)
    assert r['verdict']==verdict
    boot=[float(sum(v)/5) for v in itertools.product(ds,repeat=5)]
    output=dict(independent_metric_cells=cells,bootstrap_intervals=intervals,paired_t_intervals=len(KEYS),primary_numerators=nums,primary_mean=float(mean),upper_p=sm['exact_signflip_p_upper'],pair_profit_difference=float(profit),verdict=verdict,exact_3125_bootstrap_ci95=np.quantile(boot,[.025,.975]).tolist(),result_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
    Path(out).write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2));return output

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s16_tender');p.add_argument('--result',default='results/s16_tender.json');p.add_argument('--out',default='logs/s16_independent.json');a=p.parse_args();check(a.data,a.result,a.out)
