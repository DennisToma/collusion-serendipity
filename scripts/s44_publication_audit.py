"""Post-registration publication checks; supplements, never changes frozen science."""
from pathlib import Path
import hashlib
import json
import sys
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if not __debug__:raise RuntimeError('Run without -O')
from scripts import s44_replay as s
from scripts.s44_independent import verify


def check():
    directory=Path('data/s44_payoff')
    original={str(p):s.digest(p) for p in directory.rglob('*') if p.is_file() and p.name!='.writer.lock'}
    with patch.object(s,'chat',side_effect=AssertionError('Publication forbids model calls')):
        cfg,cases,rows=s.validate(directory)
        result=s.analyze(directory)
    canonical=Path('results/s44_payoff.json');assert canonical.read_text()==json.dumps(result,indent=2)+'\n'
    assert json.loads(Path('logs/s44_final_preflight.json').read_text())['sources']==cfg['sources']
    assert json.loads(Path('logs/s44_ready_canonical_pretests.json').read_text())['passed']
    assert len(rows)==20 and all(s.when(r['started_utc'])<s.when(r['ended_utc']) for r in rows)
    verification=verify();assert verification==json.loads(Path('logs/s44_independent.json').read_text())
    assert original=={str(p):s.digest(p) for p in directory.rglob('*') if p.is_file() and p.name!='.writer.lock'}
    spans=[(s.when(r['ended_utc'])-s.when(r['started_utc'])).total_seconds() for r in rows]
    return dict(passed=True,scope='Supplemental publication audit added after registration;no frozen source/estimator changes',
                model_calls_forbidden=True,strictly_positive_local_invocation_intervals=20,
                invocation_seconds_range=[min(spans),max(spans)],last_local_response_utc=max(r['ended_utc'] for r in rows),
                scientific_sha256=s.digest(canonical),registered_sources=cfg['sources'],raw_archive_sha256=original,
                independent=verification)


if __name__=='__main__':
    out=check();Path('logs/s44_publication_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
