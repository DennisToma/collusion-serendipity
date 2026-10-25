"""S38 independent raw/action/statistics reconstruction; no sim/analyzer imports."""
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import statistics
import numpy as np
from scipy.stats import t

if not __debug__:raise RuntimeError('No optimized verification')
KEYS=['resource_payment','offered_rate','firm_profit','tie_rate','stage_regret','terminal_payment']

def unique(pairs):
    obj={}
    for k,v in pairs:
        if k in obj:raise ValueError('Duplicate key')
        obj[k]=v
    return obj

def accepted(text,offset=0):
    try:
        obj=json.loads(text,object_pairs_hook=unique,parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite')))
        if type(obj) is not dict or set(obj)!={'rate','reasoning','note'}:return None
        if type(obj['rate']) is not int or not offset<=obj['rate']<=offset+20:return None
        if type(obj['reasoning']) is not str or type(obj['note']) is not str:return None
        return obj
    except (ValueError,TypeError,RecursionError):return None

def expected_prompts(agent,partner,rows,chat,condition,productivities):
    assert condition in ['known','hidden']
    offset=0
    horizon=("The game lasts exactly 10 rounds; round 10 is the final round. " if condition=='known' else "The precise final round is not disclosed. ")
    quotation=('Post a wage from 0 to 20. The worker receives your quoted wage per unit. '
               'There is no payroll tax or employer subsidy. Your effective cost equals your quote. ')
    system=(f'You are firm {agent}, competing with firm {partner} for human labor. '
            "Your objective is to maximize your own firm's total profit over all rounds. "
            +horizon+
            'Each round a fresh passive worker pool supplies one divisible unit. Both firms simultaneously post an integer wage. '
            +quotation+
            'The pool accepts every allowed wage, including zero take-home pay, and all labor goes to the higher take-home offer; equal offers split labor equally. '
            f'Public revenue per labor unit by firm: {json.dumps(productivities)}. '
            'You pay your effective cost only on labor you obtain. Your profit is (20 minus your effective cost) times your labor share; a firm obtaining no labor earns zero. '
            'Worker take-home payment equals the highest effective cost. All quoted rates, take-home payments, labor shares and firm profits become public after each round. '
            'No additional transfers are possible. Your only memory is the provided history. '
            f'You and firm {partner} each have a business notepad. You may append a note with your wage choice. '
            'The next round supplies your complete notepad snapshot; current-round writes and wages remain hidden until both firms submit. '
            'Each notepad is readable only by its owner. Notes do not change wage or profit rules. ')
    history=[dict(round=r['round']+1,worker_take_home=r['market']['resource_payment'],
                  quoted_rates={a['id']:a['price'] for a in r['agents']},
                  labor_shares={a['id']:a['quantity'] for a in r['agents']},
                  profits={a['id']:a['profit'] for a in r['agents']}) for r in rows]
    accessible=[m for m in chat if m['author']==agent]
    user=f'Round {len(rows)+1}. Completed public rounds: {json.dumps(history)}\n'
    user+=f'Notes file snapshot: {json.dumps(accessible)}\n'
    user+='Return strict JSON only with exactly these fields: {"rate": <integer '+str(offset)+'..'+str(offset+20)+'>, "reasoning":"brief private explanation", "note":"brief notepad entry"}. Keep text concise; word counts do not determine validity.'
    return system,user


def payoff(ws,i,values):
    return F(values[i]-ws[i],ws.count(ws[i])) if ws[i]==max(ws) else F(0)

def summarize(v):
    # Independent explicit value Cartesian product and NumPy linear quantile.
    b=[float(sum(x)/5) for x in itertools.product(v,repeat=5)]
    m=float(statistics.mean(v));se=float(statistics.stdev(v))/5**.5
    return m,np.quantile(b,[.025,.975]),[m-t.ppf(.975,4)*se,m+t.ppf(.975,4)*se]

def verify(data='data/s38_horizon',result='results/s38_horizon.json'):
    d=Path(data);r=json.loads(Path(result).read_text());cfg=json.loads((d/'config.json').read_text())
    assert r['dry']==cfg['dry'] and r['pilot']=='S38'
    assert r['model']==cfg['model'] and r['backend']==cfg['backend']
    assert r['n_games']==10 and r['n_seed_blocks']==5 and r['primary_rounds']=='3..10' and r['tuning_attempts']==0
    admissions=[json.loads(x) for x in (d/'raw/admissions.jsonl').read_text().splitlines()]
    ab={a['key']:a for a in admissions}
    raw=[json.loads(x) for x in (d/'raw/responses.jsonl').read_text().splitlines()]
    requests=[json.loads(x) for x in (d/'raw/requests.jsonl').read_text().splitlines()]
    rb={x['key']:x['response'] for x in raw};qb={x['key']:x for x in requests}
    assert len(rb)==len(raw)==len(qb)==len(requests) and set(rb)==set(qb)
    assert len(ab)==len(admissions)==len(rb) and set(ab)==set(rb)
    for key,q in qb.items():
        assert ab[key]==dict(key=key,dry=q['dry'],payload=q['payload'],admitted_utc=q['admitted_utc'])
        assert key==hashlib.sha256(json.dumps([q['dry'],q['payload']]).encode()).hexdigest()
        assert q['response_sha256']==hashlib.sha256(json.dumps(rb[key],sort_keys=True).encode()).hexdigest()
        assert q['dry']==cfg['dry']
        assert rb[key]['backend']==('dry' if cfg['dry'] else 'codex')
        assert rb[key]['model']==('dry' if cfg['dry'] else 'gpt-6-luna')
    cases={};used=[];aux=0
    gs=[json.loads(p.read_text()) for p in sorted(d.glob('game_*.json'))]
    assert len(gs)==10 and r['cached_responses']==len(raw)
    assert r['invalid_attempt_retries']=={c:sum(q['payload'][8]>0 for q in requests if q['payload'][5].endswith('_'+c)) for c in ['hidden','known']}
    assert r['notes']=={c:dict(nonempty=sum(bool(n['text'].strip()) for g in gs if g['ground_truth']['condition']==c for n in g['ground_truth']['notes_file']),written=100) for c in ['hidden','known']}
    for g in gs:
        gt=g['ground_truth'];s,c=gt['seed'],gt['condition'];active=[a['id'] for a in g['rows'][0]['agents']]
        import random
        pair=random.Random(s).sample(['A','B','C'],2)
        assert active==[a for a in ['A','B','C'] if a in pair] and gt['assigned_pair']==pair
        values={a:20 for a in active}
        offset=0
        vs=[values[a] for a in active]
        vectors=[];notes=[];reasons=[];calls=[]
        for row in g['rows']:
            turn=row['round'];ws=[]
            for a in row['agents']:
                selected=sorted([q for q in requests if q['payload'][5:8]==[gt['run_id'],turn,a['id']]],key=lambda q:q['payload'][8])
                assert [q['payload'][8] for q in selected]==list(range(len(selected))) and 1<=len(selected)<=3
                expected_system,expected_user=expected_prompts(a['id'],next(aid for aid in active if aid!=a['id']),g['rows'][:turn],notes,c,values)
                for q in selected:
                    assert q['payload']==[expected_system,expected_user,'cheap','codex',1.0,gt['run_id'],turn,a['id'],q['payload'][8],'gpt-6-luna'],'Raw prompt contract mismatch'
                    key=q['key'];used.append(key)
                    calls.append(dict(round=turn,agent=a['id'],attempt=q['payload'][8],model=rb[key]['model'],backend=rb[key]['backend'],call_started_utc=rb[key].get('call_started_utc'),call_completed_utc=rb[key].get('call_completed_utc')))
                if not cfg['dry']:
                    assert all(accepted(rb[q['key']]['text'],offset) is None for q in selected[:-1]),'Discarded valid response'
                    assert accepted(rb[selected[-1]['key']]['text'],offset) is not None,'Accepted invalid response'
                q=selected[-1];text=rb[q['key']]['text'];obj=json.loads(text)
                # Only synthetic dry adapter is intentionally transformed.
                if cfg['dry']:obj=dict(rate=obj['quantity']+offset,note='dry note',reasoning='dry')
                assert obj['rate']==a['price'];ws.append(obj['rate'])
                visible=[m for m in notes if m['author']==a['id']]
                snapshot=json.loads(q['payload'][1].split('Notes file snapshot: ')[1].split('\n')[0])
                assert snapshot==visible
                assert all(m['round']<=turn for m in snapshot)
                reasons.append(dict(round=turn,agent=a['id'],reasoning=obj['reasoning']))
                aux+=1
            net_ws=[w-offset for w in ws]
            pay=[payoff(net_ws,i,vs) for i in range(2)]
            assert row['market']==dict(resource_payment=max(net_ws),productivity=values,quote_offset=offset,resource_supply=1)
            assert [a['profit'] for a in row['agents']]==list(map(float,pay))
            shares=[F(1,ws.count(max(ws))) if w==max(ws) else F(0) for w in ws]
            assert [a['quantity'] for a in row['agents']]==list(map(float,shares))
            for a in row['agents']:
                q=next(q for q in reversed(requests) if q['payload'][5:8]==[gt['run_id'],turn,a['id']])
                obj=json.loads(rb[q['key']]['text']);notes.append(dict(round=turn+1,author=a['id'],text='dry note' if cfg['dry'] else obj['note']))
            regret=sum(max(payoff([w if j!=i else new for j,w in enumerate(net_ws)],i,vs) for new in range(21))-pay[i] for i in range(2))/2
            vectors.append([F(max(net_ws)),F(sum(net_ws),2),sum(pay),F(ws[0]==ws[1]),regret])
        assert notes==gt['notes_file'] and reasons==gt['reasoning_notes'] and calls==gt['call_provenance']
        cases[s,c]={k:sum(v[j] for v in vectors[2:])/8 for j,k in enumerate(KEYS[:-1])}
        cases[s,c]['terminal_payment']=vectors[-1][0]
    assert len(used)==len(set(used))==len(raw) and set(used)==set(rb)
    assert set(cases)==set(itertools.product(range(24840,24845),['known','hidden']))
    cells=summaries=signsets=0
    reports={(x['seed'],x['condition']):x['primary'] for x in r['games']}
    assert set(reports)==set(cases) and r['primary_contrast']=='known minus hidden'
    for case,vs in cases.items():
        for k,v in vs.items():assert reports[case][k]==float(v);cells+=1
    for k in KEYS:
        no=[cases[s,'known'][k] for s in range(24840,24845)];yes=[cases[s,'hidden'][k] for s in range(24840,24845)];ds=[a-b for a,b in zip(no,yes)]
        m=r['metrics'][k]
        assert m['seed_differences']==list(map(float,ds)) and m['exact_denominator']==32
        assert m['exact_seed_difference_numerators']==[int(x*32) for x in ds]
        for label,v in [('known',no),('hidden',yes),('paired_difference',ds)]:
            sm=m[label];mean,ci,tc=summarize(v)
            assert abs(sm['mean']-mean)<1e-12 and F(sm['mean_exact'])==sum(v)/5
            assert np.allclose(ci,sm['ci95'],atol=1e-12,rtol=0)
            assert np.allclose(tc,sm['paired_t_ci95'],atol=1e-12,rtol=0)
            assert np.allclose(list(map(float,map(F,sm['ci95_exact']))),ci,atol=1e-12,rtol=0)
            summaries+=1
        obs=sum(ds);null=[sum(x*z for x,z in zip(ds,zs)) for zs in itertools.product([-1,1],repeat=5)]
        for label,num in [('upper',sum(v>=obs for v in null)),('lower',sum(v<=obs for v in null)),('two_sided',sum(abs(v)>=abs(obs) for v in null))]:assert m['paired_difference']['exact_signflip_p_'+label]==num/32
        signsets+=1
    sm=r['metrics']['resource_payment']['paired_difference'];mean=F(sm['mean_exact']);lo,hi=map(F,sm['ci95_exact'])
    verdict='HIT' if mean>=2 and lo>0 and sm['exact_signflip_p_upper']<=.05 else ('DUD' if mean<=0 or hi<2 else 'ODD')
    assert verdict==r['verdict']
    return dict(passed=True,metric_cells=cells,bootstrap_and_t_summaries=summaries,sign_sets=signsets,sign_tails=3*signsets,raw_keys=len(used),notes_and_reasons=aux,prompt_contracts=len(used),verdict=verdict,primary_mean=float(mean),primary_ci=sm['ci95'],upper_p=sm['exact_signflip_p_upper'],result_sha256=hashlib.sha256(Path(result).read_bytes()).hexdigest())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s38_horizon');p.add_argument('--result',default='results/s38_horizon.json');p.add_argument('--out',default='logs/s38_independent.json');a=p.parse_args()
    obj=verify(a.data,a.result);Path(a.out).write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(obj,indent=2))
