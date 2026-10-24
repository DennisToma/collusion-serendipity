"""Post-review independent raw-request timing check; no production prompt helpers."""
import hashlib
import json
from pathlib import Path
import re


def main():
    d=Path('data/s11_delay');games={g['ground_truth']['run_id']:g for g in [json.loads(p.read_text()) for p in d.glob('game_*.json')]}
    path=d/'raw/requests.jsonl';requests=[json.loads(line) for line in path.read_text().splitlines()]
    by_arm={'immediate':0,'delayed':0};tables=0
    for request in requests:
        system,user,_,_,_,rid,t,agent,_=request['payload'][:9]
        condition=rid.rsplit('_',1)[1];lag=1 if condition=='immediate' else 2
        visible=max(0,t+1-lag);game=games[rid]
        assert f'with a {lag}-round lag.' in system
        assert 'Quantities and profits are revealed after each round.' not in system
        assert user.startswith(f'Round {t+1}. Available completed public rounds: ')
        line=user.splitlines()[0].split('Available completed public rounds: ',1)[1]
        history=json.loads(line)
        expected=[]
        for i,row in enumerate(game['rows'][:visible]):
            expected.append(dict(round=i+1,price=row['market']['price'],
                                 quantities={a['id']:a['quantity'] for a in row['agents']},
                                 profits={a['id']:a['profit'] for a in row['agents']}))
        assert history==expected
        assert [row['round'] for row in history]==list(range(1,visible+1))
        match=re.search(r'forecast of their next choices\. (\[.*\])\n',user)
        summary=re.search(r'combined (\d+) units in the latest available round \((\d+)\)',user)
        if visible:
            rival_total=sum(a['quantity'] for a in game['rows'][visible-1]['agents'] if a['id']!=agent)
            assert summary and tuple(map(int,summary.groups()))==(rival_total,visible)
            assert match
            assert json.loads(match.group(1))==[dict(quantity=q,own_profit=(max(0,30-rival_total-q)-6)*q) for q in range(13)]
            tables+=1
        else:assert match is None and summary is None
        by_arm[condition]+=1
    assert sum(by_arm.values())==366
    out=dict(kind='post-review independent raw-request protocol audit; no new estimator or outcome',
             requests_checked=len(requests),by_arm=by_arm,conditional_tables_checked=tables,
             all_history_rounds_exact=True,no_recent_row_in_structured_history=True,
             actual_request_tables_and_rival_summaries_match_visible_history=True,
             system_lag_cue_correct=True,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    Path('logs/s11_request_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
