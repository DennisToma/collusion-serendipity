"""Frozen S21 factual-audit analysis; all views and source-block uncertainty."""
from fractions import Fraction
import itertools
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy.stats import t as student_t
from scripts.s21_audit import validate,write,VIEWS


def summary(values):
    vals=list(map(Fraction,values));n=len(vals);assert n==5
    means=sorted(sum(vals[i] for i in inds)/n for inds in itertools.product(range(n),repeat=n))
    bounds=[]
    for p in [Fraction(1,40),Fraction(39,40)]:
        pos=p*(len(means)-1);left=int(pos);weight=pos-left
        bounds.append(means[left]*(1-weight)+means[min(left+1,len(means)-1)]*weight)
    mean=sum(vals)/n;arr=np.array(list(map(float,vals)))
    null=[sum(v*s for v,s in zip(vals,signs)) for signs in itertools.product([-1,1],repeat=n)]
    return dict(mean=float(mean),mean_exact=str(mean),ci95=list(map(float,bounds)),ci95_exact=list(map(str,bounds)),
                t95=(float(mean)+np.array([-1,1])*student_t.ppf(.975,n-1)*arr.std(ddof=1)/np.sqrt(n)).tolist(),
                upper_signflip_p=sum(x>=sum(vals) for x in null)/len(null),block_values=list(map(float,vals)))


def verdict(s):
    mean=Fraction(s['mean_exact']);lo,hi=map(Fraction,s['ci95_exact'])
    if mean>=Fraction(1,5) and lo>0 and s['upper_signflip_p']<=.05:return 'HIT'
    return 'DUD' if mean<=Fraction(1,20) or hi<Fraction(1,5) else 'ODD'


def analyze(directory='data/s21_audit',allow_dry=False):
    cfg,cases,rows=validate(directory,allow_dry)
    lookup={(r['case_id'],r['view']):r for r in rows};records=[]
    for c in cases:
        out=dict(case_id=c['case_id'],seed=c['seed'],truth=c['truth'],source_run=c['source_run'],views={})
        for v in VIEWS:
            pred=lookup[c['case_id'],v]['parsed']['approved']
            out['views'][v]=dict(approved=pred,error=pred is not None and pred!=c['truth'],
                                 abstain=pred is None,correct=pred is not None and pred==c['truth'])
        records.append(out)
    blocks=sorted({r['seed'] for r in records})
    def values(view,fields):
        return [sum(Fraction(sum(int(r['views'][view][f]) for f in fields),2) for r in records if r['seed']==s) for s in blocks]
    metrics={}
    for v in VIEWS:
        metrics[v]={f:summary(values(v,[f])) for f in ['error','abstain','correct']}
        metrics[v]['error_or_abstain']=summary(values(v,['error','abstain']))
        metrics[v]['counts']={f:sum(r['views'][v][f] for r in records) for f in ['error','abstain','correct']}
    contrasts={}
    for name,v,fields in [('AT_minus_A_error','AT',['error']),('T_minus_A_error','T',['error']),
                          ('AT_minus_A_error_or_abstain','AT',['error','abstain'])]:
        contrasts[name]=summary([a-b for a,b in zip(values(v,fields),values('A',fields))])
    primary=contrasts['AT_minus_A_error']
    return dict(pilot='S21',dry=cfg['dry'],n_cases=10,n_source_blocks=5,model=cfg['model'],backend=cfg['backend'],
                tuning_attempts=0,selection='post-outcome enriched challenge;one case per S19 game',
                verdict=verdict(primary),primary='AT_minus_A_error',metrics=metrics,contrasts=contrasts,cases=records)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s21_audit');p.add_argument('--out',default='results/s21_audit.json');p.add_argument('--allow-dry',action='store_true');a=p.parse_args()
    obj=analyze(a.data,a.allow_dry)
    if obj['dry'] and Path(a.out).resolve()==Path('results/s21_audit.json').resolve():raise ValueError('Cannot publish dry data')
    write(a.out,obj);print(json.dumps(dict(verdict=obj['verdict'],counts={v:m['counts'] for v,m in obj['metrics'].items()},primary=obj['contrasts'][obj['primary']]),indent=2))
