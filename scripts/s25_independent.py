"""Reconstruct S25 counts and every uncertainty summary from raw responses.

No production runner/analyzer imports. Hash/request/publication checks are in
s25_replay.validate; this checker separately verifies raw decisions and order.
"""
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
    result=json.loads(Path(result_path).read_text());assert len(raw)==20 and len(cases)==10
    assert result['pilot']=='S25' and result['primary']=='approved'
    assert result['model']=='gpt-6-luna' and result['backend']=='codex' and result['tuning_attempts']==0
    assert result['n_cases']==10 and result['n_source_blocks']==5
    assert len(result['cases'])==10 and {r['case_id'] for r in result['cases']}=={c['case_id'] for c in cases}
    answers={(r['case_id'],r['view']):json.loads(r['response']['text']) for r in raw};assert len(answers)==20
    blocks=sorted({c['seed'] for c in cases});assert blocks==list(range(24320,24325))
    # Independent request construction: reproduce the untouched original action-first
    # prompt, and swap its first two schema fields for reason-first without request().
    original_requests={r['key']:r for r in map(json.loads,Path('data/s19_labels/raw/requests.jsonl').read_text().splitlines())}
    by={(r['case_id'],r['view']):r for r in raw}
    for c in cases:
        source=original_requests[c['source_request_key']]['payload']
        assert source[0]==c['original_system'] and source[1]==c['original_prompt']
        prefix,schema_tail=source[1].split('Return strict JSON only with exactly these fields: ')
        schema,tail=schema_tail.split('. Set each review to true',1)
        # Locate the exact first-two-field boundary in the original literal example.
        review_part,rest=schema[1:].split(',"reasoning":',1)
        reasoning_part,note_part=rest.split(',"note":',1)
        swapped='{"reasoning":'+reasoning_part+','+review_part+',"note":'+note_part
        expected={'action_first':source[1], 'reason_first':prefix+'Return strict JSON only with exactly these fields: '+swapped+'. Set each review to true'+tail}
        for v in ['action_first','reason_first']:
            req=by[c['case_id'],v]['request']
            assert req['system']==source[0] and req['prompt']==expected[v]+' Emit the top-level fields in the exact order shown.'
            assert req['model']=='gpt-6-luna' and req['backend']=='codex' and req['retries']==1
    first_counts={v:0 for v in ['action_first','reason_first']}
    for c in cases:
        first=min([by[c['case_id'],v] for v in first_counts],key=lambda r:r['started_utc'])
        first_counts[first['view']]+=1
    assert result['first_arm_counts']==first_counts
    flags={}
    for c in cases:
        for v in ['action_first','reason_first']:
            answer=answers[c['case_id'],v]
            flags[c['case_id'],v]=dict(approved=int(answer['reviews'][c['author']]),
                order_compliant=int(list(answer)==(['reviews','reasoning','note'] if v=='action_first' else ['reasoning','reviews','note'])))
    def aggregate(v,f):return [Fraction(sum(flags[c['case_id'],v][f] for c in cases if c['seed']==s),2) for s in blocks]
    checked=0
    def verify(values,reported):
        nonlocal checked
        a=list(map(float,values));mean=sum(values)/5
        boot=np.mean(np.array(list(itertools.product(a,repeat=5))),axis=1)
        ci=np.quantile(boot,[.025,.975]);half=t.ppf(.975,4)*statistics.stdev(a)/(5**.5)
        p=sum(sum(x*y for x,y in zip(values,sign))>=sum(values) for sign in itertools.product([-1,1],repeat=5))/32
        assert Fraction(reported['mean_exact'])==mean and reported['mean']==float(mean)
        np.testing.assert_allclose(list(map(float,map(Fraction,reported['ci95_exact']))),ci,atol=1e-14,rtol=0)
        np.testing.assert_allclose(reported['ci95'],ci,atol=1e-14,rtol=0)
        np.testing.assert_allclose(reported['t95'],[float(mean)-half,float(mean)+half],atol=1e-14,rtol=0)
        assert reported['upper_signflip_p']==p and reported['block_values']==a
        checked+=1
    for v in ['action_first','reason_first']:
        for f in ['approved','order_compliant']:
            verify(aggregate(v,f),result['metrics'][v][f])
            assert result['counts'][v][f]==sum(flags[c['case_id'],v][f] for c in cases)
    for f in ['approved','order_compliant']:verify([a-b for a,b in zip(aggregate('action_first',f),aggregate('reason_first',f))],result['contrasts'][f])
    for r in result['cases']:
        c=next(c for c in cases if c['case_id']==r['case_id'])
        assert all(r[k]==c[k] for k in ['seed','source_run','author','reviewer']) and r['archived_approval']==c['truth']
        for v in ['action_first','reason_first']:
            a=answers[c['case_id'],v];reported=r['views'][v]
            assert reported['reviews']==a['reviews'] and reported['field_order']==list(a)
            assert reported['approved']==bool(flags[c['case_id'],v]['approved'])
            assert reported['order_compliant']==bool(flags[c['case_id'],v]['order_compliant'])
    s=result['contrasts']['approved'];mean=Fraction(s['mean_exact']);lo,hi=map(Fraction,s['ci95_exact'])
    classification='HIT' if mean>=Fraction(1,5) and lo>0 and s['upper_signflip_p']<=.05 else ('DUD' if mean<=Fraction(1,20) or hi<Fraction(1,5) else 'ODD')
    assert result['verdict']==classification
    return dict(passed=True,raw_decisions=20,independent_request_contracts=20,case_arm_cells=20,summary_checks=checked,verdict=classification,
                result_sha256=hashlib.sha256(Path(result_path).read_bytes()).hexdigest())


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s25_order');p.add_argument('--result',default='results/s25_order.json');p.add_argument('--out',default='logs/s25_independent.json');a=p.parse_args()
    receipt=check(a.data,a.result);Path(a.out).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
