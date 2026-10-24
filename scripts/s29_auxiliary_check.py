"""Post-outcome raw-only verification of every S29 emitted note/explanation.

Companion to the frozen independent metric/history checker. Checks final-round
notes and registered nonempty-note metadata too. No simulator imports, model
calls, classification, outcome change or source-manifest mutation.
"""
import hashlib
import json
from pathlib import Path


def check():
    root=Path('data/s29_notepad');result_path=Path('results/s29_notepad.json')
    before=hashlib.sha256(result_path.read_bytes()).hexdigest()
    result=json.loads(result_path.read_text());assert result['pilot']=='S29' and not result['dry']
    assert result['invalid_attempt_retries']==dict(self=0,shared=0)
    raw={r['key']:r['response'] for r in map(json.loads,(root/'raw/responses.jsonl').read_text().splitlines())}
    requests={};used=set()
    for req in map(json.loads,(root/'raw/requests.jsonl').read_text().splitlines()):
        assert req['dry'] is False
        assert req['key']==hashlib.sha256(json.dumps([False,req['payload']]).encode()).hexdigest()
        assert req['response_sha256']==hashlib.sha256(json.dumps(raw[req['key']],sort_keys=True).encode()).hexdigest()
        system,user,tier,backend,temp,rid,t,agent,attempt,model=req['payload']
        assert attempt==0
        identity=rid,t,agent;assert identity not in requests
        requests[identity]=req
    counts={c:dict(nonempty=0,written=0) for c in ['self','shared']};checked=final=0
    paths=sorted(root.glob('game_*.json'));assert len(paths)==10
    for path in paths:
        game=json.loads(path.read_text());gt=game['ground_truth'];cond=gt['condition']
        notes={(n['round'],n['author']):n['text'] for n in gt['notes_file']}
        reasons={(n['round'],n['agent']):n['reasoning'] for n in gt['reasoning_notes']}
        assert len(notes)==len(gt['notes_file'])==len(reasons)==len(gt['reasoning_notes'])==20
        for t,row in enumerate(game['rows']):
            for rec in row['agents']:
                req=requests[gt['run_id'],t,rec['id']];key=req['key'];assert key not in used;used.add(key)
                response=raw[key];assert response['model']=='gpt-6-luna' and response['backend']=='codex'
                obj=json.loads(response['text']);assert set(obj)=={'reviews','reasoning','note'}
                assert obj['reviews']==rec['reviews']
                assert isinstance(obj['note'],str) and isinstance(obj['reasoning'],str)
                assert obj['note']==notes[t+1,rec['id']]
                assert obj['reasoning']==reasons[t,rec['id']]
                counts[cond]['written']+=1;counts[cond]['nonempty']+=bool(obj['note'].strip())
                checked+=1;final+=t==9
    assert used==set(raw) and len(used)==len(requests)==checked==200 and final==20
    assert counts==result['notes']
    assert hashlib.sha256(result_path.read_bytes()).hexdigest()==before
    receipt=dict(passed=True,raw_auxiliary_outputs_checked=checked,final_round_outputs_checked=final,
                 note_counts=counts,scientific_result_sha256=before,scope='Raw note/explanation and registered note-count verification only;no semantic labels or new outcome')
    Path('logs/s29_raw_auxiliary_check.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2));return receipt

if __name__=='__main__':check()
