"""Separate raw-review arithmetic/contrast reconstruction; not independent authorship."""
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


def verify(directory='data/s59_history',result='results/s59_history.json'):
    p=Path(directory);r=json.loads(Path(result).read_text())
    manifest=json.loads((p/'cases.json').read_text());cs=manifest['cases']
    root=Path(__file__).resolve().parents[1]
    assert all(hashlib.sha256((root/name).read_bytes()).hexdigest()==h for name,h in manifest['source_sha256'].items())
    assert not (p/'failure.json').exists() and not (p/'transport_failures.jsonl').exists()
    cfg=json.loads((p/'config.json').read_text());assert r['dry']==cfg['dry']
    source_requests={q['key']:q for q in map(json.loads,(root/'data/s29_notepad/raw/requests.jsonl').read_text().splitlines())}
    for case in cs:
        q=source_requests[case['source_request_key']]['payload']
        assert q[0:2]==[case['original_system'],case['original_prompt']]
        statuses=json.loads(q[1].split('Current authoritative statuses: ',1)[1].split('\n',1)[0])
        assert case['own_status']==statuses[case['agent']]
        g=json.loads((root/f"data/s29_notepad/game_{case['seed']}_shared.json").read_text())
        partner=next(a for a in g['ground_truth']['assigned_pair'] if a!=case['agent'])
        assert partner==case['partner']
        import random
        schedule_rng=random.Random(f"s29-tasks-{case['seed']}-{partner}")
        warm=[False,True];primary=[False]*4+[True]*4
        schedule_rng.shuffle(warm);schedule_rng.shuffle(primary)
        assert [row['market']['passed'][partner] for row in g['rows']]==warm+primary
        last=max(i for i in range(2,10) if not g['rows'][i]['market']['passed'][partner])
        assert case['turn']==last and q[5:8]==[case['source_run'],last,case['agent']]
        archived=next(a for a in g['rows'][last]['agents'] if a['id']==case['agent'])['reviews'][partner]
        assert archived==case['archived_approval']
    rows=[json.loads(x) for x in (p/'responses.jsonl').read_text().splitlines()]
    assert len(rows)==20 and len(cs)==10 and len(r['cases'])==10
    assert [c['case_id'] for c in r['cases']]==[c['case_id'] for c in cs]
    assert r['n_cases']==10 and r['n_source_blocks']==5 and r['n_new_games']==0 and r['n_fresh_decisions']==20
    assert r['tuning_attempts']==0 and r['pilot']=='S59'
    assert r['primary']=='original_minus_compact_adverse_approval'
    assert r['model']=='gpt-6-luna' and r['backend']=='codex'
    quotes={}
    for row in rows:
        case=next(c for c in cs if c['case_id']==row['case_id'])
        # Rebuild only the public-history line independently of the constructor.
        original=case['original_prompt'];lines=original.splitlines(keepends=True)
        index=next(i for i,line in enumerate(lines) if 'Completed public rounds: ' in line)
        prefix,history=lines[index].split('Completed public rounds: ',1)
        history=json.loads(history)
        assert prefix==f"Round {case['turn']+1}. "
        assert len(history)==case['turn']
        assert row['view'] in ['original','compact']
        if row['view']=='compact':
            agents=sorted(history[0]['statuses']);a,b=agents
            cols=['round',f'statuses.{a}',f'statuses.{b}',f'reviews.{a}.{b}',f'reviews.{b}.{a}',f'scores.{a}',f'scores.{b}',f'charges.{a}.{b}',f'charges.{b}.{a}']
            cells=[[h['round'],h['statuses'][a],h['statuses'][b],h['reviews'][a][b],h['reviews'][b][a],h['scores'][a],h['scores'][b],h['charges'][a][b],h['charges'][b][a]] for h in history]
            packed={'column_paths':cols,'rows':cells}
            reconstructed=[]
            for values in packed['rows']:
                n,sa,sb,rab,rba,pa,pb,cab,cba=values
                reconstructed.append(dict(round=n,statuses={a:sa,b:sb},reviews={a:{b:rab},b:{a:rba}},scores={a:pa,b:pb},charges={a:{b:cab},b:{a:cba}}))
            assert reconstructed==history
            assert json.dumps(reconstructed)==json.dumps(history)
            lines[index]=prefix+'Completed public rounds: '+json.dumps(packed,separators=(',',':'))+'\n' 
        expected_prompt=''.join(lines)
        assert row['request']==dict(system=case['original_system'],prompt=expected_prompt,backend='codex',model='gpt-6-luna',tier='cheap',temperature=1.0,max_tokens=512,retries=1)
        assert row['response']['backend']==('dry' if cfg['dry'] else 'codex')
        assert row['response']['model']==('dry' if cfg['dry'] else 'gpt-6-luna')
        obj=strict_json(row['response']['text']);q=obj['reviews'][case['partner']]
        assert set(obj)=={'reviews','reasoning','note'} and type(obj['reasoning']) is str and type(obj['note']) is str
        assert set(obj['reviews'])=={case['partner']} and type(q) is bool
        key=(row['case_id'],row['view']);assert key not in quotes
        quotes[key]=q
    seeds=sorted({c['seed'] for c in cs});assert seeds==list(range(24480,24485))
    assert all(sum(c['seed']==seed for c in cs)==2 for seed in seeds)
    values={v:np.array([sum(quotes[c['case_id'],v] for c in cs if c['seed']==seed)/2 for seed in seeds]) for v in ['original','compact']}
    values['contrast']=values['original']-values['compact']
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
        assert case['archived_approval']==source['archived_approval']
        assert case['seed']==source['seed'] and case['condition']==source['condition']
        assert case['turn']==source['turn'] and case['own_status']==source['own_status']
        for v in ['original','compact']:
            assert case['approvals'][v]==quotes[case['case_id'],v]
            response=next(row for row in rows if row['case_id']==case['case_id'] and row['view']==v)
            assert case['history_bytes'][v]==len(response['request']['prompt'].split('Completed public rounds: ',1)[1].split('\n',1)[0].encode())
    assert r['approval_counts']=={v:sum(quotes[c['case_id'],v] for c in cs) for v in ['original','compact']}
    assert r['archived_match_counts']=={v:sum(quotes[c['case_id'],v]==c['archived_approval'] for c in cs) for v in ['original','compact']}
    mean=values['contrast'].mean();lo,hi=r['contrast']['ci95'];pval=r['contrast']['upper_signflip_p']
    verdict='HIT' if mean>=.25 and lo>0 and pval<=.05 else 'DUD' if mean<=.05 or hi<.25 else 'ODD'
    assert r['verdict']==verdict
    return dict(passed=True,raw_approvals=20,case_prompt_bindings=20,block_cells=15,
                bootstrap_draws_per_summary=3125,summaries=summaries,sign_flips_per_summary=32,
                result_sha256=hashlib.sha256(Path(result).read_bytes()).hexdigest())


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s59_history');p.add_argument('--result',default='results/s59_history.json');p.add_argument('--out',default='logs/s59_independent.json');a=p.parse_args()
    obj=verify(a.data,a.result);Path(a.out).write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(obj,indent=2))
