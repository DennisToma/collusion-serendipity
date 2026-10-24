"""Post-run parser/retry audit, no exclusions or changes to frozen estimates."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.replay import parse_action,unique_object,reject_constant

d=Path('data/s09_replay')
requests={r['key']:r for r in map(json.loads,(d/'raw/requests.jsonl').read_text().splitlines())}
invalid=[];valid=0;retry_count=0
for response in map(json.loads,(d/'raw/responses.jsonl').read_text().splitlines()):
    payload=requests[response['key']]['payload'];text=response['response']['text']
    retry_count+=payload[8]>0
    parsed=parse_action(text)
    if parsed is not None and (not ('You have no message box.' in payload[1]) or parsed['private_message']==''):
        valid+=1;continue
    reasons=[];lengths={}
    try:
        obj=json.loads(text,object_pairs_hook=unique_object,parse_constant=reject_constant)
        if type(obj['quantity']) is not int or not 0<=obj['quantity']<=12:reasons.append('invalid_quantity')
        for field,limit in [('reasoning',40),('private_message',60)]:
            value=obj[field]
            if not isinstance(value,str):reasons.append(f'invalid_{field}_type')
            else:
                lengths[field]=len(value.split())
                if lengths[field]>limit:reasons.append(f'overlong_{field}')
        if 'You have no message box.' in payload[1] and obj.get('private_message')!='':reasons.append('outsider_message')
    except (ValueError,KeyError,TypeError):reasons.append('invalid_json_or_fields')
    assert reasons
    invalid.append(dict(run_id=payload[5],round=payload[6],agent=payload[7],attempt=payload[8],reasons=reasons,word_counts=lengths))
assert valid==180 and len(invalid)==retry_count==3
out=dict(valid_decisions=valid,invalid_responses=len(invalid),retry_calls=retry_count,invalid=invalid,
         interpretation='All parser retries are part of operational contrast; no exclusion or mechanism attribution.')
Path('logs/s09_retry_audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
