"""Cache-only S62 failed-prefix audit; never estimates any scientific effect."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import threading
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.notepad_qwen import run_game,schedule,parse_action,SOURCES
from sim.common_qwen import TEMPERATURE


def audit(directory='data/s62_notepad_qwen'):
    root=Path(directory);cfg=json.loads((root/'config.json').read_text())
    journal=root/'raw/execution.jsonl'
    events=[json.loads(s) for s in journal.read_text().splitlines()] if journal.exists() else []
    completed_journal=[e['event'] for e in events]==['start','complete']
    assert list(root.glob('failure_*.json')) or not completed_journal,'Only for failed/interrupted invocations'
    for name,digest in cfg['sources'].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
    assert set(cfg['sources'])==set(SOURCES)
    raw=[json.loads(s) for s in ((root/'raw/responses.jsonl').read_text().splitlines() if (root/'raw/responses.jsonl').exists() else [])]
    requests=[json.loads(s) for s in ((root/'raw/requests.jsonl').read_text().splitlines() if (root/'raw/requests.jsonl').exists() else [])]
    by={r['key']:r['response'] for r in raw};req={r['key']:r for r in requests}
    assert len(raw)==len(by)==len(requests)==len(req) and set(by)==set(req)
    used=set()
    class PrefixCache:
        dry=False
        def __init__(self):self.abort=threading.Event()
        def call(self,system,user,tier,backend,rid,t,agent,attempt,model=None):
            payload=[system,user,tier,backend,TEMPERATURE,rid,t,agent,attempt,model]
            key=hashlib.sha256(json.dumps([False,payload]).encode()).hexdigest()
            if key not in by:raise LookupError('Archived prefix ends; no transport permitted')
            assert key not in used;used.add(key)
            assert req[key]['payload']==payload and req[key]['dry'] is False
            assert req[key]['response_sha256']==hashlib.sha256(json.dumps(by[key],sort_keys=True).encode()).hexdigest()
            return by[key]
    completed=[];prefixes=[]
    for seed,condition in schedule():
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                game=run_game(seed,condition,PrefixCache(),cfg['model'],cfg['backend'])
        except (LookupError,RuntimeError) as exc:
            prefixes.append(dict(seed=seed,condition=condition,end=type(exc).__name__,message=str(exc)))
        else:
            saved=json.loads((root/f'game_{seed}_{condition}.json').read_text())
            assert game['rows']==saved['rows']
            for field in ['reasoning_notes','notes_file','call_provenance']:assert game['ground_truth'][field]==saved['ground_truth'][field]
            completed.append((seed,condition))
    assert used==set(by),'Unused/orphan cached response'
    invalid=sum(parse_action(r['response']['text']) is None for r in raw)
    return dict(pilot='S62',status='FAILED' if list(root.glob('failure_*.json')) else 'INTERRUPTED',effect_estimated=False,cached_responses=len(raw),
                complete_games=len(completed),schema_invalid_texts=invalid,
                all_cached_prefixes_replayed=True,prefixes=prefixes,
                failures=[json.loads(p.read_text()) for p in sorted(root.glob('failure_*.json'))],
                requested_model=cfg['model'],requested_backend=cfg['backend'])


def main():
    result=audit();Path('results/s62_failure.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# S62 — Failed output-contract portability pilot','',
           f"**FAILED / unclassified.** {result['cached_responses']} cached responses, {result['schema_invalid_texts']} outside the registered schema, {result['complete_games']}/10 complete games. No scientific effect estimated.",'',
           'Fresh Qwen/Aqueduct generalization of the S29 shared-versus-self notepad design. The frozen three-attempt/abort policy prevents partial-arm estimation,parser relaxation,replacement games or another model. All returned prefixes replayed from raw requests/responses without calls. This failure does not show that Qwen lacks or exhibits adverse approvals or a channel effect.','',
           '[Design](../DESIGN_S62.md) · [Full failure audit](s62_failure.json).']
    Path('results/s62_summary.md').write_text('\n'.join(lines)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
