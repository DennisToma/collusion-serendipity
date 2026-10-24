"""Offline publication gate: exact S25 requests, raw order, sources and reproduction."""
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s25_replay import run,validate,write
from scripts.s25_analyze import analyze
from scripts.s25_independent import check


def release(directory='data/s25_order',result_path='results/s25_order.json'):
    directory=Path(directory);result_path=Path(result_path)
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(directory.glob('*.json*'))}
    cfg,cases,rows=validate(directory)
    with patch('scripts.s25_replay.chat',side_effect=AssertionError('Forbidden live call during release')):
        run(directory);rebuilt=analyze(directory)
    assert result_path.read_text()==json.dumps(rebuilt,indent=2,ensure_ascii=False)+'\n','Canonical result differs'
    independent=check(directory,result_path)
    after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(directory.glob('*.json*'))}
    assert before==after,'Archive modified during offline replay'
    assert not (directory/'transport_failures.jsonl').exists()
    return dict(passed=True,pilot='S25',registration_commit=cfg['registration']['commit'],
                scientific_source_count=len(cfg['sources']),cached_requests=len(rows),invalid_output_retries=0,
                transport_failures=0,archive_unchanged=True,zero_live_calls=True,
                canonical_result_sha256=hashlib.sha256(result_path.read_bytes()).hexdigest(),
                archive_sha256=before,independent=independent)


if __name__=='__main__':
    receipt=release();write('logs/s25_release.json',receipt);print(json.dumps(receipt,indent=2))
