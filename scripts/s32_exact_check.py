"""Post-outcome exact-number companion; original frozen scientific files unchanged.

The original independent verifier first binds game metric cells to raw decisions.
This companion then checks rational means/bounds with exact equality,without
reusing the scientific analyzer or its bootstrap implementation.
"""
import argparse
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s32_independent import verify


def exact_numbers(result):
    cells={(g['seed'],g['condition']):g['primary'] for g in result['games']}
    seeds=range(24600,24605);checked=0
    for key in ['resource_payment','offered_rate','firm_profit','tie_rate','stage_regret']:
        human=[F(str(cells[s,'human'][key])) for s in seeds]
        compute=[F(str(cells[s,'compute'][key])) for s in seeds]
        assert all((v*32).denominator==1 for v in human+compute)
        differences=[a-b for a,b in zip(human,compute)]
        for label,values in [('human',human),('compute',compute),('paired_difference',differences)]:
            claimed=result['metrics'][key][label]
            distribution=sorted(sum(sample,F(0))/5 for sample in itertools.product(values,repeat=5))
            actual=[]
            for probability in [F(1,40),F(39,40)]:
                rank=probability*(5**5-1);lower=rank.numerator//rank.denominator;weight=rank-lower
                actual.append(distribution[lower]+weight*(distribution[lower+1]-distribution[lower]))
            assert F(claimed['mean_exact'])==sum(values)/5,'Exact mean mismatch'
            assert claimed['mean']==float(sum(values)/5),'Encoded mean mismatch'
            assert list(map(F,claimed['ci95_exact']))==actual,'Exact rational bootstrap mismatch'
            assert claimed['ci95']==list(map(float,actual)),'Encoded bootstrap mismatch'
            checked+=1
    return checked


def check(data='data/s32_resource',result='results/s32_resource.json'):
    bound=verify(data,result)
    assert bound['passed'] and bound['metric_cells']==50
    r=json.loads(Path(result).read_text());n=exact_numbers(r)
    return dict(passed=True,scope='POST-OUTCOME companion; exact rational equality after original independent raw-cell binding',
                exact_summaries=n,raw_bound_metric_cells=bound['metric_cells'],
                result_sha256=hashlib.sha256(Path(result).read_bytes()).hexdigest())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s32_resource');p.add_argument('--result',default='results/s32_resource.json');p.add_argument('--out',default='logs/s32_exact_check.json');a=p.parse_args()
    obj=check(a.data,a.result);Path(a.out).write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(obj,indent=2))
