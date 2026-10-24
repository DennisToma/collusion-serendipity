"""Independent S21 raw-answer/count/statistics reconstruction, no production analysis imports."""
import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import statistics
import numpy as np
from scipy.stats import t


def check(directory,result_path):
    d=Path(directory);cases=json.loads((d/'cases.json').read_text())['cases']
    raw=[json.loads(s) for s in (d/'responses.jsonl').read_text().splitlines()]
    result=json.loads(Path(result_path).read_text());assert len(raw)==30
    assert result['pilot']=='S21' and result['primary']=='AT_minus_A_error'
    assert result['model']=='gpt-6.1-sol' and result['backend']=='codex' and result['tuning_attempts']==0
    assert result['n_cases']==10 and result['n_source_blocks']==5
    assert len(result['cases'])==10
    assert {r['case_id'] for r in result['cases']}=={c['case_id'] for c in cases}
    answers={(r['case_id'],r['view']):json.loads(r['response']['text'])['approved'] for r in raw}
    assert len(answers)==30
    blocks=sorted({c['seed'] for c in cases});assert len(blocks)==5
    flags={}
    for c in cases:
        for view in ['A','T','AT']:
            ans=answers[c['case_id'],view]
            flags[c['case_id'],view]=dict(error=int(ans is not None and ans!=c['truth']),
                                         abstain=int(ans is None),correct=int(ans is not None and ans==c['truth']))
    def aggregate(view,fields):
        return [Fraction(sum(sum(flags[c['case_id'],view][f] for f in fields) for c in cases if c['seed']==seed),2) for seed in blocks]
    checked=0
    def verify(values,reported):
        nonlocal checked
        floating=list(map(float,values));mean=sum(values)/5
        boot=np.mean(np.array(list(itertools.product(floating,repeat=5))),axis=1)
        ci=np.quantile(boot,[.025,.975]);half=t.ppf(.975,4)*statistics.stdev(floating)/(5**.5)
        p=sum(sum(a*b for a,b in zip(values,sign))>=sum(values) for sign in itertools.product([-1,1],repeat=5))/32
        assert Fraction(reported['mean_exact'])==mean and reported['mean']==float(mean)
        np.testing.assert_allclose(list(map(float,map(Fraction,reported['ci95_exact']))),ci,atol=1e-14,rtol=0)
        np.testing.assert_allclose(reported['ci95'],ci,atol=1e-14,rtol=0)
        np.testing.assert_allclose(reported['t95'],[float(mean)-half,float(mean)+half],atol=1e-14,rtol=0)
        assert reported['upper_signflip_p']==p and reported['block_values']==floating
        checked+=1
    for view in ['A','T','AT']:
        for field in ['error','abstain','correct']:
            verify(aggregate(view,[field]),result['metrics'][view][field])
            assert result['metrics'][view]['counts'][field]==sum(flags[c['case_id'],view][field] for c in cases)
        verify(aggregate(view,['error','abstain']),result['metrics'][view]['error_or_abstain'])
    for name,view,fields in [('AT_minus_A_error','AT',['error']),('T_minus_A_error','T',['error']),('AT_minus_A_error_or_abstain','AT',['error','abstain'])]:
        verify([a-b for a,b in zip(aggregate(view,fields),aggregate('A',fields))],result['contrasts'][name])
    s=result['contrasts']['AT_minus_A_error'];mean=s['mean'];lo,hi=s['ci95']
    classification='HIT' if mean>=.2 and lo>0 and s['upper_signflip_p']<=.05 else ('DUD' if mean<=.05 or hi<.2 else 'ODD')
    assert result['verdict']==classification
    for record in result['cases']:
        source=next(c for c in cases if c['case_id']==record['case_id'])
        assert record['truth']==source['truth'] and record['source_run']==source['source_run'] and record['seed']==source['seed']
        for view in ['A','T','AT']:
            assert record['views'][view]['approved'] is answers[record['case_id'],view]
            assert {k:int(record['views'][view][k]) for k in ['correct','error','abstain']}==flags[record['case_id'],view]
    return dict(passed=True,raw_answers=30,case_view_cells=30,summary_checks=checked,verdict=classification,
                result_sha256=hashlib.sha256(Path(result_path).read_bytes()).hexdigest())


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s21_audit');p.add_argument('--result',default='results/s21_audit.json');p.add_argument('--out',default='logs/s21_independent.json');a=p.parse_args()
    receipt=check(a.data,a.result);Path(a.out).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
