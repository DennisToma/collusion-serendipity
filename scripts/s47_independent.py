"""Separate raw-rate arithmetic/contrast reconstruction; not independent authorship."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
from scipy.stats import t


if not __debug__:raise RuntimeError('Run without -O; assertions verify scientific claims')

def strict_json(text):
    def unique(pairs):
        out={}
        for key,value in pairs:
            assert key not in out,'Duplicate key'
            out[key]=value
        return out
    return json.loads(text,object_pairs_hook=unique,parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def verify(directory='data/s47_example',result='results/s47_example.json'):
    p=Path(directory);r=json.loads(Path(result).read_text())
    manifest=json.loads((p/'cases.json').read_text());cs=manifest['cases']
    root=Path(__file__).resolve().parents[1]
    assert all(hashlib.sha256((root/name).read_bytes()).hexdigest()==h for name,h in manifest['source_sha256'].items())
    assert not (p/'failure.json').exists() and not (p/'transport_failures.jsonl').exists()
    cfg=json.loads((p/'config.json').read_text());assert r['dry']==cfg['dry']
    source_requests={q['key']:q for q in map(json.loads,(root/'data/s42_entry/raw/requests.jsonl').read_text().splitlines())}
    for case in cs:
        q=source_requests[case['source_request_key']]['payload']
        assert q[0:2]==[case['original_system'],case['original_prompt']]
        g=json.loads((root/f"data/s42_entry/game_{case['seed']}_{case['condition']}.json").read_text())
        assert case['agent']==sorted(g['ground_truth']['assigned_pair'])[0]
        assert case['rival_rates']==[a['price'] for a in g['rows'][8]['agents'] if a['id']!=case['agent']]
        assert q[5:9]==[case['source_run'],9,case['agent'],0]
    rows=[json.loads(x) for x in (p/'responses.jsonl').read_text().splitlines()]
    assert len(rows)==20 and len(cs)==10
    assert len(r['cases'])==10
    assert [c['case_id'] for c in r['cases']]==[c['case_id'] for c in cs]
    assert r['n_cases']==10 and r['n_source_blocks']==5 and r['n_new_games']==0 and r['n_fresh_decisions']==20
    assert r['tuning_attempts']==0 and r['pilot']=='S47'
    assert r['primary']=='high_example_minus_low_example_offer'
    assert r['model']=='gpt-6-luna' and r['backend']=='codex'
    quotes={}
    for row in rows:
        case=next(c for c in cs if c['case_id']==row['case_id'])
        req=row['request'];assert req['system']==case['original_system']
        original=case['original_prompt']
        prefix,marker,tail=original.partition('\nReturn strict JSON only')
        rivals=case['rival_rates'];table=[]
        from fractions import Fraction
        for wage in range(21):
            share=Fraction(1,1+sum(x==wage for x in rivals)) if all(wage>=x for x in rivals) else Fraction(0)
            table.append(dict(wage=wage,labor_share=str(share),own_profit=str((20-wage)*share)))
        example=dict(rate=20 if row['view']=='high_example' else 0,reasoning='',note='')
        supplement=('\nCounterfactual one-round payoff table, holding every rival at its last completed public wage offer '
                    +json.dumps(rivals)+'. These are hypothetical fixed rival offers, not their current choices or a forecast. '
                    'All 21 allowed own wages are listed. Fractions are exact; own_profit is your profit for this one round. '
                    +json.dumps(table)
                    +'\nOutput syntax example only; the example rate is not a recommendation. Choose your own rate independently using the stated objective and information. '
                    +json.dumps(example))
        expected=prefix+supplement+marker+tail
        assert req['prompt']==expected
        assert req==dict(system=case['original_system'],prompt=expected,backend='codex',model='gpt-6-luna',tier='cheap',temperature=1.0,max_tokens=512,retries=1)
        assert row['response']['backend']==('dry' if cfg['dry'] else 'codex')
        assert row['response']['model']==('dry' if cfg['dry'] else 'gpt-6-luna')
        obj=strict_json(row['response']['text']);q=obj['rate']
        assert set(obj)=={'rate','reasoning','note'} and type(obj['reasoning']) is str and type(obj['note']) is str
        assert type(q) is int and 0<=q<=20
        key=(row['case_id'],row['view']);assert key not in quotes
        quotes[key]=q
    seeds=sorted({c['seed'] for c in cs});assert len(seeds)==5
    values={v:np.array([sum(quotes[c['case_id'],v] for c in cs if c['seed']==seed)/2 for seed in seeds]) for v in ['low_example','high_example']}
    values['contrast']=values['high_example']-values['low_example']
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
        # Exact rational fields are checked separately from NumPy float quantiles.
        from fractions import Fraction as F
        doubled=np.rint(arr*2).astype(int)
        assert s['mean_exact']==str(F(int(sum(doubled)),10))
        ordered=sorted(sum(x) for x in itertools.product(map(int,doubled),repeat=5))
        exact_bounds=[]
        for numerator in [1,39]:
            pos=F((len(ordered)-1)*numerator,40);index=int(pos);weight=pos-index
            exact_bounds.append(str((ordered[index]*(1-weight)+ordered[index+1]*weight)/10))
        assert s['ci95_exact']==exact_bounds
        # Half-unit integer scale also avoids float ties in the sign test.
        null=[sum(x*y for x,y in zip(doubled,signs)) for signs in itertools.product([-1,1],repeat=5)]
        assert sum(z>=sum(doubled) for z in null)/32==s['upper_signflip_p']
        assert sum(z<=sum(doubled) for z in null)/32==s['lower_signflip_p']
        assert sum(abs(z)>=abs(sum(doubled)) for z in null)/32==s['two_sided_signflip_p']
        summaries+=1
    for case in r['cases']:
        source=next(c for c in cs if c['case_id']==case['case_id'])
        assert case['archived_quote']==source['archived_quote']
        assert case['seed']==source['seed'] and case['condition']==source['condition']
        for v in ['low_example','high_example']:assert case['quotes'][v]==quotes[case['case_id'],v]
    assert r['floor_counts']=={v:sum(quotes[c['case_id'],v]==0 for c in cs) for v in ['low_example','high_example']}
    assert r['archived_match_counts']=={v:sum(quotes[c['case_id'],v]==c['archived_quote'] for c in cs) for v in ['low_example','high_example']}
    mean=values['contrast'].mean();lo,hi=r['contrast']['ci95'];pval=r['contrast']['upper_signflip_p']
    verdict='HIT' if mean>=2 and lo>0 and pval<=.05 else 'DUD' if mean<=0 or hi<2 else 'ODD'
    assert r['verdict']==verdict
    return dict(passed=True,raw_quotes=20,case_prompt_bindings=20,block_cells=15,
                bootstrap_draws_per_summary=3125,summaries=summaries,sign_flips_per_summary=32,
                result_sha256=hashlib.sha256(Path(result).read_bytes()).hexdigest())


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s47_example');p.add_argument('--result',default='results/s47_example.json');p.add_argument('--out',default='logs/s47_independent.json');a=p.parse_args()
    obj=verify(a.data,a.result);Path(a.out).write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(obj,indent=2))
