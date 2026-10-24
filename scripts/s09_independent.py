"""Independent outcome arithmetic; does not invoke production metric/statistic helpers."""
import hashlib
import itertools
import json
from pathlib import Path
import statistics
import sys
import numpy as np
from scipy.stats import t
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

def verify(directory='data/s09_replay',result_path='results/s09_replay.json'):
    d=Path(directory);res=json.loads(Path(result_path).read_text());by={};cells=0
    for record in res['games']:
        seed,cond=record['seed'],record['condition']
        game=json.loads((d/f'game_{seed}_{cond}.json').read_text())
        pair=game['ground_truth']['assigned_pair']
        for name,lo,hi in [('primary',6,12),('fork',6,7),('final',11,12)]:
            rows=game['rows'][lo:hi]
            inside=[a for r in rows for a in r['agents'] if a['id'] in pair]
            outside=[a for r in rows for a in r['agents'] if a['id'] not in pair]
            msgs=[m for m in game['ground_truth']['private_chat'] if lo < m['round'] <= hi]
            values={'quantity':statistics.mean(a['quantity'] for a in inside),
                'outsider_quantity':statistics.mean(a['quantity'] for a in outside),
                'price':statistics.mean(r['market']['price'] for r in rows),
                'pair_profit':statistics.mean(a['profit'] for a in inside),
                'outsider_profit':statistics.mean(a['profit'] for a in outside),
                'message_words':statistics.mean(len(m['text'].split()) for m in msgs),
                'nonempty_messages':statistics.mean(bool(m['text'].strip()) for m in msgs)}
            for key,val in values.items():
                assert abs(val-record[name][key])<1e-12
                cells+=1
            by[seed,cond,name]=values
        for row in game['rows']:
            price=max(0,30-sum(a['quantity'] for a in row['agents']))
            assert price==row['market']['price']
            assert all(a['profit']==(price-6)*a['quantity'] for a in row['agents'])
    rng=np.random.default_rng(2409);seeds=list(range(24080,24085));intervals=0
    def check_stats(values,reported):
        nonlocal intervals
        a=np.array(values,dtype=float)
        draws=rng.integers(0,5,(10000,5))
        boot=np.quantile(np.mean(a[draws],axis=1),[.025,.975])
        assert abs(float(np.mean(a))-reported['mean'])<1e-12
        assert np.allclose(boot,reported['ci95'],rtol=0,atol=1e-12)
        intervals+=1
    for metric,stat in res['metrics'].items():
        retain=[by[s,'retain','primary'][metric] for s in seeds]
        erase=[by[s,'erase','primary'][metric] for s in seeds]
        diff=[b-a for a,b in zip(retain,erase)]
        check_stats(diff,stat['paired_difference'])
        check_stats(retain,stat['retain']);check_stats(erase,stat['erase'])
        half=t.ppf(.975,4)*statistics.stdev(diff)/(5**.5)
        assert np.allclose([statistics.mean(diff)-half,statistics.mean(diff)+half],stat['paired_difference']['paired_t_ci95'],rtol=0,atol=1e-12)
    nums=[]
    for seed in seeds:
        totals=[]
        for cond in ['retain','erase']:
            g=json.loads((d/f'game_{seed}_{cond}.json').read_text());pair=g['ground_truth']['assigned_pair']
            totals.append(sum(a['quantity'] for r in g['rows'][6:] for a in r['agents'] if a['id'] in pair))
        nums.append(totals[1]-totals[0])
    primary=res['metrics']['quantity']
    assert nums==primary['exact_seed_difference_numerators']
    null=[sum(x*y for x,y in zip(nums,sign)) for sign in itertools.product([-1,1],repeat=5)]
    upper=sum(x>=sum(nums) for x in null)/32
    assert upper==primary['paired_difference']['exact_signflip_p_upper']
    from fractions import Fraction
    mean=Fraction(sum(nums),60)
    verdict=('HIT' if mean>=1 and primary['paired_difference']['ci95'][0]>0 and upper<=.05 else
             'ODD-reverse' if mean<=-1 and all(x<0 for x in nums) else 'ODD' if mean<=-1 else 'DUD' if mean<=Fraction(1,4) else 'ODD')
    assert verdict==res['verdict']
    fork=[by[s,'erase','fork']['quantity']-by[s,'retain','fork']['quantity'] for s in seeds]
    outsider=[by[s,'erase','fork']['outsider_quantity']-by[s,'retain','fork']['outsider_quantity'] for s in seeds]
    assert outsider==res['fork_outsider_seed_differences']
    assert statistics.mean(outsider)==res['fork_outsider_mean_difference']
    check_stats(fork,res['fork_quantity_difference'])
    assert fork==res['fork_seed_differences']
    assert statistics.mean(abs(x) for x in fork)==res['fork_mean_absolute_difference']
    return dict(metric_window_cells=cells,bootstrap_intervals=intervals,paired_t_intervals=7,
                exact_numerators=nums,exact_primary_mean=float(mean),exact_upper_p=upper,verdict=verdict,
                result_sha256=hashlib.sha256(Path(result_path).read_bytes()).hexdigest())

if __name__=='__main__':
    out=verify(*sys.argv[1:])
    Path('logs/s09_independent.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
