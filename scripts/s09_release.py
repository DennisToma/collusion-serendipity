"""Read-only release checks plus byte-preserving cached resume; no live generation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s09_analyze import analyze
from scripts.s09_independent import verify

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    d=Path('data/s09_replay');cfg=json.loads((d/'config.json').read_text())
    result_path=Path('results/s09_replay.json');result=json.loads(result_path.read_text())
    assert cfg['dry'] is False and result['dry'] is False
    assert result==analyze(d), 'Result differs from canonical replay/analysis'
    paths=sorted(d.glob('game_*.json'))+[d/'config.json',d/'schedule.json',d/'trajectories.jsonl',d/'ground_truth.jsonl',d/'raw/requests.jsonl',d/'raw/responses.jsonl',result_path]
    before={str(p):digest(p) for p in paths}
    # Mandatory analysis already proves all reconstructed calls are cached.
    # Block llm.chat even if the resume runner unexpectedly tries an uncached call.
    import contextlib,io
    from unittest.mock import patch
    from sim.replay import main as resume
    import tempfile
    with patch('sys.argv',['sim.replay','--out',str(d)]),patch('sim.common.llm.chat',side_effect=AssertionError('Live calls forbidden in release')),patch.object(tempfile,'tempdir','/var/tmp'),contextlib.redirect_stdout(io.StringIO()):
        resume()
    assert before=={str(p):digest(p) for p in paths}, 'Cached resume changed data/result bytes'
    independent=verify()
    push=json.loads(Path('logs/s09_registration_push.json').read_text())
    assert push['registration_commit']==cfg['registration_commit']
    calls=[json.loads(x)['response'] for x in (d/'raw/responses.jsonl').read_text().splitlines()]
    assert all(push['push_completed_before_utc']<r['call_started_utc'] for r in calls)
    assert all(r['call_completed_utc']<cfg['deadline_utc'] for r in calls), 'Actual final completion exceeded cutoff'
    frozen={}
    for path,expected in cfg['sources'].items():
        assert digest(Path(path))==expected
        assert hashlib.sha256(subprocess.check_output(['git','show',f"{cfg['registration_commit']}:{path}"])).hexdigest()==expected
        frozen[path]=expected
    audit=dict(canonical_result_identical=True,mandatory_cache_only_replay=True,
               cached_resume_bytes_unchanged=True,live_calls_forbidden_during_resume=True,
               registration_pushed_before_all_calls=True,all_calls_finished_before_cutoff=True,
               earliest_call=min(c['call_started_utc'] for c in calls),latest_completion=max(c['call_completed_utc'] for c in calls),
               independent=independent,sha256=before,frozen_sources=frozen)
    Path('logs/s09_release.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps({k:v for k,v in audit.items() if k not in ['sha256','frozen_sources']},indent=2))

if __name__=='__main__':main()
