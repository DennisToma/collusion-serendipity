"""Frozen S25 assigned-order comparison; empirical source-block uncertainty."""
import argparse
from fractions import Fraction
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s25_replay import validate,write,VIEWS,schedule
from scripts.s21_analyze import summary,verdict


def analyze(directory='data/s25_order',allow_dry=False):
    cfg,cases,rows=validate(directory,allow_dry)
    lookup={(r['case_id'],r['view']):r for r in rows};records=[]
    for c in cases:
        record=dict(case_id=c['case_id'],seed=c['seed'],source_run=c['source_run'],author=c['author'],
                    reviewer=c['reviewer'],archived_approval=c['truth'],views={})
        for v in VIEWS:
            parsed=lookup[c['case_id'],v]['parsed']
            order=list(parsed)
            record['views'][v]=dict(approved=parsed['reviews'][c['author']],reviews=parsed['reviews'],
                                   field_order=order,order_compliant=order==({'action_first':['reviews','reasoning','note'],
                                                                           'reason_first':['reasoning','reviews','note']}[v]))
        records.append(record)
    seeds=sorted({c['seed'] for c in cases})
    def values(view,field):return [Fraction(sum(r['views'][view][field] for r in records if r['seed']==s),2) for s in seeds]
    metrics={v:{f:summary(values(v,f)) for f in ['approved','order_compliant']} for v in VIEWS}
    counts={v:{f:sum(r['views'][v][f] for r in records) for f in ['approved','order_compliant']} for v in VIEWS}
    contrasts={f:summary([a-b for a,b in zip(values('action_first',f),values('reason_first',f))]) for f in ['approved','order_compliant']}
    return dict(pilot='S25',dry=cfg['dry'],n_cases=10,n_source_blocks=5,model=cfg['model'],backend=cfg['backend'],
                tuning_attempts=0,first_arm_counts={v:sum(arms[0]==v for b in schedule(cases) for cid,arms in b) for v in VIEWS},primary='approved',verdict=verdict(contrasts['approved']),
                metrics=metrics,contrasts=contrasts,counts=counts,cases=records)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s25_order');p.add_argument('--out',default='results/s25_order.json');p.add_argument('--allow-dry',action='store_true');a=p.parse_args()
    obj=analyze(a.data,a.allow_dry)
    if obj['dry'] and Path(a.out).resolve()==Path('results/s25_order.json').resolve():raise ValueError('Cannot publish dry data')
    write(a.out,obj);print({k:obj[k] for k in ['verdict','counts','contrasts']})
