"""Deterministic extraction of every S07 neutral r1-6 prefix; no selection."""
import hashlib
import json
from pathlib import Path

def extract(seed):
    source=Path(f'data/s07_legality/game_{seed}_neutral.json')
    game=json.loads(source.read_text());gt=game['ground_truth']
    assert gt['seed']==seed and gt['condition']=='neutral' and gt['dry'] is False
    assert gt['run_id']==f's07_{seed}_neutral' and gt['T']==12
    assert gt['model']=={a:'gpt-6-luna' for a in ['A','B','C']}
    assert gt['backend']=={a:'codex' for a in ['A','B','C']}
    return dict(seed=seed,assigned_pair=gt['assigned_pair'],rows=game['rows'][:6],
                private_chat=[m for m in gt['private_chat'] if m['round']<=6],
                source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())

if __name__=='__main__':
    for seed in range(24080,24085):
        path=Path(f'data/s09_prefix/prefix_{seed}.json');obj=extract(seed)
        if path.exists():assert json.loads(path.read_text())==obj
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps(obj,indent=2)+'\n')
    print('All five complete S07 neutral prefixes match deterministic extraction')
