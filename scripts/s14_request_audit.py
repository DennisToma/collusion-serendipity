"""Independent saved-prompt protocol audit; no production prompt/sim helpers."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import random

if not __debug__:
    raise RuntimeError('Research integrity checks require Python without -O')


def after_json(text,prefix):
    suffix=text.split(prefix,1)[1]
    return json.JSONDecoder().raw_decode(suffix)[0]


def check(data='data/s14_tender',out='logs/s14_request_audit.json'):
    d=Path(data);cfg=json.loads((d/'config.json').read_text())
    games=[json.loads(p.read_text()) for p in sorted(d.glob('game_*.json'))];assert len(games)==10
    by={g['ground_truth']['run_id']:g for g in games};assert len(by)==10
    requests=[json.loads(l) for l in (d/'raw/requests.jsonl').read_text().splitlines()]
    responses={r['key']:r['response'] for r in [json.loads(l) for l in (d/'raw/responses.jsonl').read_text().splitlines()]}
    assert len(responses)==len(requests)==len({r['key'] for r in requests})
    journal=[json.loads(l) for l in (d/'raw/execution.jsonl').read_text().splitlines()]
    assert [e['event'] for e in journal]==['start','complete']
    checks=0;inbox_prompts=0;available_appearances=0;first={};last={}
    for req in requests:
        assert req['dry']==cfg['dry']
        system,user,tier,backend,temp,rid,t,agent,attempt,model=req['payload']
        assert tier=='cheap' and backend=='codex' and model=='gpt-6-luna' and temp==1
        assert agent in 'ABC' and 0<=t<12 and 0<=attempt<3
        assert hashlib.sha256(json.dumps([req['dry'],req['payload']]).encode()).hexdigest()==req['key']
        response=responses[req['key']]
        assert hashlib.sha256(json.dumps(response,sort_keys=True).encode()).hexdigest()==req['response_sha256']
        game=by[rid];gt=game['ground_truth'];rows=game['rows'];pair=random.Random(gt['seed']).sample(list('ABC'),2)
        assert gt['assigned_pair']==pair
        history=after_json(user,'Completed public rounds: ')
        expected=[dict(round=i+1,payment=r['market']['payment'],bids={a['id']:a['price'] for a in r['agents']},
                       allocations={a['id']:a['quantity'] for a in r['agents']},profits={a['id']:a['profit'] for a in r['agents']}) for i,r in enumerate(rows[:t])]
        assert history==expected
        assert user.startswith(f'Round {t+1}. Completed public rounds: ')
        box=gt['condition']=='private' and agent in pair
        if box:
            partner=next(a for a in pair if a!=agent)
            assert f'private message box with firm {partner}.' in system
            inbox=after_json(user,'Messages in your private box: ')
            assert inbox==[m for m in gt['private_chat'] if m['recipient']==agent and m['round']<=t]
            assert len(inbox)==t
            assert all(m['sender']==partner and m['recipient']==agent and 1<=m['round']<=t for m in inbox)
            assert all(m['round']<=11 for m in inbox)
            available_appearances+=len(inbox);inbox_prompts+=1
        else:
            assert 'Messages in your private box:' not in user and 'private message box with' not in system
            assert 'You have no message box.' in user
        if not cfg['dry']:
            start=datetime.fromisoformat(response['call_started_utc']);end=datetime.fromisoformat(response['call_completed_utc'])
            assert datetime.fromisoformat(journal[0]['utc'])<=start<=end<=datetime.fromisoformat(journal[1]['utc'])
            first[rid]=min(first.get(rid,start),start);last[rid]=max(last.get(rid,end),end)
        checks+=1
    overlap=[]
    if not cfg['dry']:
        for s in range(24200,24205):
            n=f's14_{s}_none';p=f's14_{s}_private'
            gap=abs((first[n]-first[p]).total_seconds());duration=(min(last[n],last[p])-max(first[n],first[p])).total_seconds()
            assert gap<=60 and duration>=0
            overlap.append(dict(seed=s,first_call_gap_seconds=gap,raw_call_overlap_seconds=duration))
    output=dict(saved_requests_checked=checks,completed_public_histories_exact=True,recipient_only_delayed_inboxes_exact=True,
                no_current_round_leak=True,no_own_sent_messages_replayed=True,box_prompt_attempts=inbox_prompts,
                incoming_history_appearances_including_retries=available_appearances,pair_timing=overlap,
                raw_request_sha256=hashlib.sha256((d/'raw/requests.jsonl').read_bytes()).hexdigest())
    Path(out).write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2));return output

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s14_tender');p.add_argument('--out',default='logs/s14_request_audit.json');a=p.parse_args();check(a.data,a.out)
