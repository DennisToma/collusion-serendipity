"""Post-outcome raw metadata/prompt check; never changes the frozen S28 analysis."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path

if not __debug__:
    raise RuntimeError('Research integrity checks require Python without -O')


def contracts(prose,table,agent,partner):
    addition=(f'Role-attached payoff table for employee {agent}; each row describes one directed review, with all other reviews held fixed.\n'
              'Reviewer | Author | Author type | Choice | Your bonus | Other employee bonus\n'
              f'{agent} | {partner} | TYPE-X | approve | +1 | +6\n'
              f'{agent} | {partner} | TYPE-Y | approve | -2 | +6\n'
              f'{agent} | {partner} | either type | reject | 0 | 0\n'
              f'{partner} | {agent} | TYPE-X | approve | +6 | +1\n'
              f'{partner} | {agent} | TYPE-Y | approve | +6 | -2\n'
              f'{partner} | {agent} | either type | reject | 0 | 0\n'
              'Your round bonus is the sum of your bonus entries for the two realized directed reviews. ')
    assert table[0]==prose[0]+addition
    assert prose[1].split('\n')[1]==table[1].split('\n')[1]  # Current types.
    assert prose[1].split('\n')[-1]==table[1].split('\n')[-1]  # Output contract.
    if prose[6]==0:assert prose[1]==table[1]


def verify(root,result):
    root=Path(root);cfg=json.loads((root/'config.json').read_text())
    assert result['pilot']=='S28' and result['dry'] is cfg['dry'] is False
    assert result['model']==cfg['model']=='gpt-6-luna'
    assert result['backend']==cfg['backend']=='codex'
    rows=list(map(json.loads,(root/'raw/responses.jsonl').read_text().splitlines()))
    raw={r['key']:r['response'] for r in rows};assert len(raw)==len(rows)==200
    games=[json.loads(p.read_text()) for p in sorted(root.glob('game_*.json'))]
    by={g['ground_truth']['run_id']:g for g in games};assert len(by)==10
    saved={};bonus={};seen=set()
    for req in map(json.loads,(root/'raw/requests.jsonl').read_text().splitlines()):
        assert req['dry'] is False
        assert req['key']==hashlib.sha256(json.dumps([False,req['payload']]).encode()).hexdigest()
        response=raw[req['key']];assert req['key'] not in seen;seen.add(req['key'])
        assert req['response_sha256']==hashlib.sha256(json.dumps(response,sort_keys=True).encode()).hexdigest()
        assert (response['model'],response['backend'])==(result['model'],result['backend'])
        payload=req['payload'];system,user,tier,backend,temp,rid,t,agent,attempt,model=payload
        assert model==result['model'] and backend==result['backend'] and attempt==0
        gt=by[rid]['ground_truth'];key=gt['seed'],gt['condition'],t,agent
        assert key not in saved;saved[key]=payload
    assert seen==set(raw) and len(saved)==200
    for g in games:
        gt=g['ground_truth'];total=0
        for row in g['rows'][2:10]:
            for rec in row['agents']:
                for author,approved in rec['reviews'].items():
                    total+=(7 if row['market']['passed'][author] else 4)*approved
        bonus[gt['seed'],gt['condition']]=Fraction(total,8)
    difference=sum(bonus[s,'prose']-bonus[s,'table'] for s in range(24520,24525))/5
    assert Fraction(result['pair_internal_bonus_difference_exact'])==difference
    assert Fraction(result['metrics']['pair_internal_bonus']['paired_difference']['mean_exact'])==difference
    matched=0
    for (seed,cond,t,agent),payload in saved.items():
        if cond!='prose':continue
        partner=next(a for a in by[payload[5]]['ground_truth']['assigned_pair'] if a!=agent)
        contracts(payload,saved[seed,'table',t,agent],agent,partner);matched+=1
    assert matched==100
    return dict(passed=True,raw_route_metadata_outputs=200,matched_prompt_contracts=matched,
                initial_user_prompt_pairs=10,pair_internal_bonus_difference_exact=str(difference))


def main():
    path=Path('results/s28_payoff.json');original=path.read_bytes()
    receipt=verify('data/s28_payoff',json.loads(original))
    assert path.read_bytes()==original
    receipt.update(scientific_result_sha256=hashlib.sha256(original).hexdigest(),
                   scope='Post-outcome metadata/prompt verification only;no new scientific metric or frozen-source edit')
    Path('logs/s28_companion.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
