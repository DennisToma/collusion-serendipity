"""Independent raw-game S11 metrics/statistics: no production metric helpers."""
import argparse
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import statistics
import numpy as np
from scipy.stats import t as student_t


def game_metrics(g,start):
    records=[]
    rows=g['rows']
    for i in range(start,12):
        row=rows[i];qs=[a['quantity'] for a in row['agents']]
        price=max(0,30-sum(qs));profits=[(price-6)*q for q in qs]
        assert price==row['market']['price']
        assert profits==[a['profit'] for a in row['agents']]
        stage=[];lag=[];changes=[]
        for j,q in enumerate(qs):
            rivals=sum(qs)-q
            vals=[(max(0,30-rivals-v)-6)*v for v in range(13)]
            stage.append(max(vals)-vals[q])
            if i:
                prev=[a['quantity'] for a in rows[i-1]['agents']]
                rivals=sum(prev)-prev[j]
                vals=[(max(0,30-rivals-v)-6)*v for v in range(13)]
                lag.append(max(vals)-vals[q]);changes.append(abs(q-prev[j]))
        avg=lambda v:F(sum(v),len(v)) if v else None
        records.append(dict(quantity=avg(qs),price=F(price),profit=avg(profits),
                            actual_stage_regret=avg(stage),lag_conditional_regret=avg(lag),
                            distance_nash=avg([abs(q-6) for q in qs]),absolute_change=avg(changes),
                            all_equal=F(int(len(set(qs))==1))))
    return {k:sum(v[k] for v in records if v[k] is not None)/sum(v[k] is not None for v in records) for k in records[0]}


def check(directory,result_path,out):
    d=Path(directory);res=json.loads(Path(result_path).read_text())
    games=[json.loads(p.read_text()) for p in sorted(d.glob('game_*.json'))]
    assert len(games)==10
    by={};cells=0
    for g in games:
        gt=g['ground_truth'];seed=gt['seed'];cond=gt['condition']
        row=next(r for r in res['games'] if r['seed']==seed and r['condition']==cond)
        for label,start in [('primary',3),('all_rounds',0),('final',11)]:
            vals=game_metrics(g,start)
            for k,v in vals.items():
                assert abs(float(v)-row[label][k])<1e-12,(seed,cond,label,k)
                cells+=1
            if label=='primary':by[seed,cond]=vals
        for t in range(12):
            visible=t if cond=='immediate' else max(0,t-1)
            for j,a in enumerate('ABC'):
                table=gt['tables'][t]['delivered'][a]
                if visible:
                    qs=[b['quantity'] for b in g['rows'][visible-1]['agents']]
                    rivals=sum(qs)-qs[j]
                    assert table==[dict(quantity=q,own_profit=(max(0,30-rivals-q)-6)*q) for q in range(13)]
                else:assert table is None
    seeds=range(24110,24115);rng=np.random.default_rng(2411);intervals=0
    def summary(vals,reported):
        nonlocal intervals
        a=np.array(list(map(float,vals)))
        boots=a[rng.integers(0,5,(10000,5))].mean(axis=1)
        assert abs(float(np.mean(a))-reported['mean'])<1e-12
        assert np.allclose(np.quantile(boots,[.025,.975]),reported['ci95'],atol=1e-12,rtol=0)
        intervals+=1
    for k,r in res['metrics'].items():
        im=[by[s,'immediate'][k] for s in seeds];de=[by[s,'delayed'][k] for s in seeds]
        delta=[a-b if k=='absolute_change' else b-a for a,b in zip(im,de)]
        assert np.allclose(list(map(float,delta)),r['seed_differences'],atol=1e-12,rtol=0)
        summary(delta,r['paired_difference']);summary(im,r['immediate']);summary(de,r['delayed'])
        sd=statistics.stdev(delta);mean=statistics.mean(delta)
        ci=[float(mean)+sign*student_t.ppf(.975,4)*float(sd)/5**.5 for sign in [-1,1]]
        assert np.allclose(ci,r['paired_difference']['paired_t_ci95'],atol=1e-12,rtol=0)
    primary=res['metrics']['absolute_change'];ds=[by[s,'immediate']['absolute_change']-by[s,'delayed']['absolute_change'] for s in seeds]
    nums=[int(v*27) for v in ds];assert all(F(n,27)==v for n,v in zip(nums,ds))
    assert nums==primary['exact_seed_difference_numerators']
    null=[sum(n*sign for n,sign in zip(nums,signs)) for signs in itertools.product([-1,1],repeat=5)]
    upper=sum(v>=sum(nums) for v in null)/32;lower=sum(v<=sum(nums) for v in null)/32
    p=primary['paired_difference'];assert upper==p['exact_signflip_p_upper'];assert lower==p['exact_signflip_p_lower']
    m=statistics.mean(ds)
    verdict=('HIT' if m>=1 and p['ci95'][0]>0 and upper<=.05 else
             'ODD-reverse' if m<=-1 and all(v<0 for v in ds) else 'DUD' if m<=F(1,4) else 'ODD')
    assert verdict==res['verdict']
    exact_boot=[float(sum(sample)/5) for sample in itertools.product(ds,repeat=5)]
    raw=[d/'raw/responses.jsonl',d/'raw/requests.jsonl']
    output=dict(independent_metric_cells=cells,bootstrap_intervals=intervals,paired_t_intervals=len(res['metrics']),
                primary_numerators=nums,primary_mean=float(m),upper_p=upper,lower_p=lower,verdict=verdict,
                exact_3125_bootstrap_ci95=np.quantile(exact_boot,[.025,.975]).tolist(),
                sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in raw+[Path(result_path)]})
    Path(out).write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s11_delay');p.add_argument('--result',default='results/s11_delay.json');p.add_argument('--out',default='logs/s11_independent.json');a=p.parse_args();check(a.data,a.result,a.out)
