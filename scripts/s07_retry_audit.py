"""Operational parser rejection audit, no treatment-effect analysis or live calls."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.legality import unique_object,reject_constant


def reason(text,user):
    try:obj=json.loads(text,object_pairs_hook=unique_object,parse_constant=reject_constant)
    except (ValueError,TypeError):return 'invalid_json'
    if not isinstance(obj,dict):return 'not_object'
    if type(obj.get('quantity')) is not int or not 0<=obj['quantity']<=12:return 'invalid_quantity'
    if not isinstance(obj.get('reasoning'),str):return 'invalid_reasoning_type'
    if len(obj['reasoning'].split())>40:return 'reasoning_over40_words'
    if not isinstance(obj.get('private_message'),str):return 'invalid_message_type'
    if len(obj['private_message'].split())>60:return 'message_over60_words'
    if 'You have no message box.' in user and obj['private_message']!='':return 'outsider_message'
    return None


def main():
    root=Path('data/s07_legality/raw')
    requests={r['key']:r for r in map(json.loads,(root/'requests.jsonl').read_text().splitlines())}
    responses={r['key']:r['response'] for r in map(json.loads,(root/'responses.jsonl').read_text().splitlines())}
    assert set(requests)==set(responses)
    counts={c:Counter() for c in ['neutral','legality']};keys=[]
    for key,request in requests.items():
        payload=request['payload'];arm=payload[5].rsplit('_',1)[1]
        failure=reason(responses[key]['text'],payload[1])
        if failure:counts[arm][failure]+=1;keys.append(key)
    out=dict(rejected_outputs_by_arm={c:dict(v) for c,v in counts.items()},
             rejected_response_keys=keys,total_raw_responses=len(responses),
             raw_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.jsonl')})
    Path('logs/s07_retry_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['rejected_response_keys','raw_sha256']},indent=2))

if __name__=='__main__':main()
