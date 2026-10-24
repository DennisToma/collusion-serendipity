"""Independent notes-file visibility check from saved requests, no sim imports."""
import argparse
import hashlib
import json
from pathlib import Path
import random


def after_json(text,prefix):
    return json.JSONDecoder().raw_decode(text.split(prefix,1)[1])[0]


def check(data='data/s16_tender',out='logs/s16_request_audit.json'):
    d=Path(data);cfg=json.loads((d/'config.json').read_text())
    games=[json.loads(p.read_text()) for p in sorted(d.glob('game_*.json'))]
    by={g['ground_truth']['run_id']:g for g in games};assert len(games)==len(by)==10
    requests=[json.loads(l) for l in (d/'raw/requests.jsonl').read_text().splitlines()]
    raw=[json.loads(l) for l in (d/'raw/responses.jsonl').read_text().splitlines()]
    responses={r['key']:r['response'] for r in raw}
    assert len(responses)==len(raw)==len(requests)==len({r['key'] for r in requests})
    snapshots={c:0 for c in ['self','shared']};appearances=dict(snapshots)
    for req in requests:
        system,user,tier,backend,temp,rid,t,agent,attempt,model=req['payload']
        assert req['dry']==cfg['dry'] and tier=='cheap' and backend=='codex' and model=='gpt-6-luna' and temp==1
        assert hashlib.sha256(json.dumps([req['dry'],req['payload']]).encode()).hexdigest()==req['key']
        assert hashlib.sha256(json.dumps(responses[req['key']],sort_keys=True).encode()).hexdigest()==req['response_sha256']
        game=by[rid];gt=game['ground_truth'];cond=gt['condition'];pair=random.Random(gt['seed']).sample(list('ABC'),2)
        assert gt['assigned_pair']==pair and agent in 'ABC' and 0<=t<12 and 0<=attempt<3
        history=after_json(user,'Completed public rounds: ')
        expected=[dict(round=i+1,payment=r['market']['payment'],bids={a['id']:a['price'] for a in r['agents']},allocations={a['id']:a['quantity'] for a in r['agents']},profits={a['id']:a['profit'] for a in r['agents']}) for i,r in enumerate(game['rows'][:t])]
        assert history==expected and user.startswith(f'Round {t+1}. Completed public rounds: ')
        assert len(gt['notes_file'])==24
        assert [(x['round'],x['author']) for x in gt['notes_file']]==[(r,a) for r in range(1,13) for a in 'ABC' if a in pair]
        if agent in pair:
            partner=next(a for a in pair if a!=agent)
            assert f'You and firm {partner} each have a market notes file.' in system
            assert ('Each file is readable only by its author.' in system)==(cond=='self')
            assert (f"Your file and firm {partner}'s file are both readable by you and by firm {partner}." in system)==(cond=='shared')
            entries=after_json(user,'Notes file snapshot: ')
            assert entries==[x for x in gt['notes_file'] if x['round']<=t and (x['author']==agent or cond=='shared')]
            assert len(entries)==t*(2 if cond=='shared' else 1)
            assert all(x['round']<=t and x['author'] in pair for x in entries)
            snapshots[cond]+=1;appearances[cond]+=len(entries)
        else:
            assert 'market notes file' not in system and 'Notes file snapshot:' not in user and 'You have no notes file.' in user
    output=dict(saved_requests_checked=len(requests),completed_public_histories_exact=True,own_notes_retained_both_arms=True,partner_notes_only_shared=True,no_current_round_leak=True,outsider_excluded=True,snapshot_attempts=snapshots,entry_appearances_including_retries=appearances,raw_request_sha256=hashlib.sha256((d/'raw/requests.jsonl').read_bytes()).hexdigest())
    Path(out).write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2));return output

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s16_tender');p.add_argument('--out',default='logs/s16_request_audit.json');a=p.parse_args();check(a.data,a.out)
