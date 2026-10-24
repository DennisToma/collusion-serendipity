"""Independent arithmetic for every S07 reported metric and interval; no models."""
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import statistics
import numpy as np
from scipy.stats import t


def close(a,b):
    if isinstance(a,list):
        assert len(a)==len(b)
        for x,y in zip(a,b):close(x,y)
    else:assert abs(a-b)<1e-10,(a,b)


def main():
    root=Path('data/s07_legality')
    result=json.loads(Path('results/s07_legality.json').read_text())
    paths=sorted(root.glob('game_*.json'));assert len(paths)==10
    metrics={};numerators={}
    for path in paths:
        game=json.loads(path.read_text());gt=game['ground_truth'];pair=set(gt['assigned_pair'])
        key=(gt['seed'],gt['condition']);metrics[key]={}
        for window,begin in [('primary',3),('all_rounds',0),('final',11)]:
            quantities=[];outsideq=[];prices=[];profits=[];outsidep=[]
            for row in game['rows'][begin:]:
                total=sum(a['quantity'] for a in row['agents']);price=max(0,30-total)
                prices.append(price)
                for a in row['agents']:
                    q=a['quantity'];profit=(price-6)*q
                    (quantities if a['id'] in pair else outsideq).append(q)
                    (profits if a['id'] in pair else outsidep).append(profit)
            words=[len(x['text'].split()) for x in gt['private_chat'] if x['round']>begin]
            nonempty=[int(bool(x['text'].strip())) for x in gt['private_chat'] if x['round']>begin]
            metrics[key][window]={k:statistics.mean(v) for k,v in dict(quantity=quantities,
                outsider_quantity=outsideq,price=prices,pair_profit=profits,outsider_profit=outsidep,
                message_words=words,nonempty_messages=nonempty).items()}
            if window=='primary':numerators[key]=sum(quantities)
    checked=0
    for g in result['games']:
        for window in ['primary','all_rounds','final']:
            for k,v in metrics[g['seed'],g['condition']][window].items():
                close(v,g[window][k]);checked+=1
    rng=np.random.default_rng(2408)
    for name,published in result['metrics'].items():
        control=np.array([metrics[s,'neutral']['primary'][name] for s in range(24080,24085)])
        treated=np.array([metrics[s,'legality']['primary'][name] for s in range(24080,24085)])
        delta=treated-control
        close(list(delta),published['seed_differences'])
        for field,values in [('paired_difference',delta),('neutral',control),('legality',treated)]:
            # Recreate registered random stream without importing production summaries.
            indices=rng.integers(0,5,(10000,5))
            bounds=np.quantile(np.sum(values[indices],axis=1)/5,[.025,.975])
            close(statistics.mean(map(float,values)),published[field]['mean'])
            close(list(bounds),published[field]['ci95'])
        mean=statistics.mean(map(float,delta));half=t.ppf(.975,4)*statistics.stdev(map(float,delta))/5**.5
        close([mean-half,mean+half],published['paired_difference']['paired_t_ci95'])
    nums=[numerators[s,'legality']-numerators[s,'neutral'] for s in range(24080,24085)]
    exact_mean=Fraction(sum(nums),90)
    sums=[sum(x*sgn for x,sgn in zip(nums,signs)) for signs in itertools.product([-1,1],repeat=5)]
    p=Fraction(sum(x>=sum(nums) for x in sums),32)
    lowerp=Fraction(sum(x<=sum(nums) for x in sums),32)
    primary=result['metrics']['quantity']['paired_difference']
    close(float(exact_mean),primary['mean']);close(float(p),primary['exact_signflip_p_upper'])
    close(float(lowerp),primary['exact_signflip_p_lower'])
    verdict=('HIT' if exact_mean>=1 and primary['ci95'][0]>0 and p<=Fraction(1,20) else
             'ODD-reverse' if exact_mean<=-1 and all(x<0 for x in nums) else
             'DUD' if exact_mean<=Fraction(1,4) else 'ODD')
    assert verdict==result['verdict']
    output=dict(independent_metric_window_cells=checked,all_seven_arms_bootstrap_t_intervals_match=True,
                exact_numerators=nums,exact_mean=str(exact_mean),exact_upper_p=str(p),verdict=verdict,
                result_sha256=hashlib.sha256(Path('results/s07_legality.json').read_bytes()).hexdigest(),
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    Path('logs/s07_independent.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))

if __name__=='__main__':main()
