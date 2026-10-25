"""Separate raw-rate arithmetic/contrast reconstruction; not independent authorship."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
from scipy.stats import t


def strict_json(text):
    def unique(pairs):
        out={}
        for key,value in pairs:
            assert key not in out,'Duplicate key'
            out[key]=value
        return out
    return json.loads(text,object_pairs_hook=unique,parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def verify(directory='data/s40_memory',result='results/s40_memory.json'):
    p=Path(directory);r=json.loads(Path(result).read_text())
    cs=json.loads((p/'cases.json').read_text())['cases']
    rows=[json.loads(x) for x in (p/'responses.jsonl').read_text().splitlines()]
    assert len(rows)==20 and len(cs)==10
    assert len(r['cases'])==10
    assert [c['case_id'] for c in r['cases']]==[c['case_id'] for c in cs]
    assert r['n_cases']==10 and r['n_source_blocks']==5 and r['n_new_games']==0 and r['n_fresh_decisions']==20
    assert r['tuning_attempts']==0 and r['pilot']=='S40'
    assert r['primary']=='erase_minus_retain_normalized_offer'
    assert r['model']=='gpt-6-luna' and r['backend']=='codex'
    quotes={}
    for row in rows:
        case=next(c for c in cs if c['case_id']==row['case_id'])
        req=row['request'];assert req['system']==case['original_system']
        original=case['original_prompt']
        left,notes=original.split('\nNotes file snapshot: ')
        snapshot,right=notes.split('\nReturn strict JSON only')
        expected=original if row['view']=='retain' else left+'\nNotes file snapshot: []\nReturn strict JSON only'+right
        assert req['prompt']==expected
        assert req==dict(system=case['original_system'],prompt=expected,backend='codex',model='gpt-6-luna',tier='cheap',temperature=1.0,max_tokens=512,retries=1)
        obj=strict_json(row['response']['text']);q=obj['rate']
        assert set(obj)=={'rate','reasoning','note'} and type(obj['reasoning']) is str and type(obj['note']) is str
        assert type(q) is int and 10<=q<=30
        key=(row['case_id'],row['view']);assert key not in quotes
        quotes[key]=q
    seeds=sorted({c['seed'] for c in cs});assert len(seeds)==5
    values={v:np.array([sum(quotes[c['case_id'],v]-10 for c in cs if c['seed']==seed)/2 for seed in seeds]) for v in ['retain','erase']}
    values['contrast']=values['erase']-values['retain']
    indices=np.array(list(itertools.product(range(5),repeat=5)))
    summaries=0
    for name,arr in values.items():
        s=r['contrast'] if name=='contrast' else r['metrics'][name]
        np.testing.assert_array_equal(arr,s['block_values'])
        np.testing.assert_allclose(arr.mean(),s['mean'],rtol=0,atol=1e-12)
        bounds=np.quantile(arr[indices].mean(axis=1),[.025,.975],method='linear')
        np.testing.assert_allclose(bounds,s['ci95'],rtol=0,atol=1e-12)
        limits=arr.mean()+np.array([-1,1])*t.ppf(.975,4)*arr.std(ddof=1)/np.sqrt(5)
        np.testing.assert_allclose(limits,s['t95'],rtol=0,atol=1e-12)
        # Half-unit integer scale avoids float ties in the sign test.
        doubled=np.rint(arr*2).astype(int)
        null=[sum(x*y for x,y in zip(doubled,signs)) for signs in itertools.product([-1,1],repeat=5)]
        assert sum(z>=sum(doubled) for z in null)/32==s['upper_signflip_p']
        summaries+=1
    for case in r['cases']:
        source=next(c for c in cs if c['case_id']==case['case_id'])
        assert case['archived_quote']==source['archived_quote']
        assert case['seed']==source['seed'] and case['condition']==source['condition']
        for v in ['retain','erase']:assert case['quotes'][v]==quotes[case['case_id'],v]
    assert r['floor_counts']=={v:sum(quotes[c['case_id'],v]==10 for c in cs) for v in ['retain','erase']}
    assert r['archived_match_counts']=={v:sum(quotes[c['case_id'],v]==c['archived_quote'] for c in cs) for v in ['retain','erase']}
    mean=values['contrast'].mean();lo,hi=r['contrast']['ci95'];pval=r['contrast']['upper_signflip_p']
    verdict='HIT' if mean>=2 and lo>0 and pval<=.05 else 'DUD' if mean<=0 or hi<2 else 'ODD'
    assert r['verdict']==verdict
    return dict(passed=True,raw_quotes=20,case_prompt_bindings=20,block_cells=15,
                bootstrap_draws_per_summary=3125,summaries=summaries,sign_flips_per_summary=32,
                result_sha256=hashlib.sha256(Path(result).read_bytes()).hexdigest())


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s40_memory');p.add_argument('--result',default='results/s40_memory.json');p.add_argument('--out',default='logs/s40_independent.json');a=p.parse_args()
    obj=verify(a.data,a.result);Path(a.out).write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(obj,indent=2))
