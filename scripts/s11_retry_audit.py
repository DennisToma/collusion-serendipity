"""Post-run full-cache response/attempt audit, no new scientific outcomes or calls."""
from collections import Counter,defaultdict
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.delay import DEADLINE,parse_action


def main():
    d=Path('data/s11_delay');raw={r['key']:r['response'] for r in map(json.loads,(d/'raw/responses.jsonl').read_text().splitlines())}
    req=[json.loads(line) for line in (d/'raw/requests.jsonl').read_text().splitlines()]
    games=[json.loads(p.read_text()) for p in d.glob('game_*.json')];assert len(games)==10
    attempts=defaultdict(list);rejected=Counter();retry_requests=Counter();valid=Counter();reasons=defaultdict(Counter)
    for row in req:
        payload=row['payload'];rid,t,agent,attempt=payload[5:9];c=rid.rsplit('_',1)[1]
        response=raw[row['key']];obj=parse_action(response['text'])
        assert response['model']=='gpt-6-luna' and response['backend']=='codex'
        assert response['call_started_utc']<DEADLINE
        attempts[rid,t,agent].append((attempt,obj is not None))
        if attempt>0:retry_requests[c]+=1
        if obj is not None:valid[c]+=1
        else:
            rejected[c]+=1
            try:
                fields=json.loads(response['text'])
                if isinstance(fields.get('reasoning'),str) and len(fields['reasoning'].split())>40:reason='reasoning_over_40_words'
                elif fields.get('private_message')!='':reason='nonempty_or_missing_message'
                else:reason='other_strict_schema_rejection'
            except (ValueError,AttributeError):reason='json_or_object_rejection'
            reasons[c][reason]+=1
    assert len(attempts)==360
    for seq in attempts.values():
        seq.sort();assert [i for i,_ in seq]==list(range(len(seq)))
        assert [accepted for _,accepted in seq]==[False]*(len(seq)-1)+[True]
    assert sum(valid.values())==360 and sum(rejected.values())==sum(retry_requests.values())
    out=dict(valid_decisions=dict(valid),rejected_responses=dict(rejected),retry_requests=dict(retry_requests),
             rejection_reasons={k:dict(v) for k,v in reasons.items()},cached_responses=len(raw),
             first_call_started_utc=min(r['call_started_utc'] for r in raw.values()),
             last_call_completed_utc=max(r['call_completed_utc'] for r in raw.values()),
             all_routes_pinned=True,all_360_attempt_sequences_valid=True,all_logical_calls_before_cutoff=True)
    Path('logs/s11_retry_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
