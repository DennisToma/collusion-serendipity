"""Offline S21 publication gate: source-bound replay, independent checks, byte reproducibility."""
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s21_audit import run,validate,write
from scripts.s21_analyze import analyze
from scripts.s21_independent import check


def release(directory='data/s21_audit',result_path='results/s21_audit.json'):
    directory=Path(directory);result_path=Path(result_path)
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(directory.glob('*.json*'))}
    cfg,cases,rows=validate(directory)
    with patch('scripts.s21_audit.chat',side_effect=AssertionError('Forbidden live call during release')):
        run(directory)
        rebuilt=analyze(directory)
    expected=json.dumps(rebuilt,indent=2,ensure_ascii=False)+'\n'
    assert result_path.read_text()==expected,'Canonical result differs from complete deterministic reanalysis'
    independent=check(directory,result_path)
    after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(directory.glob('*.json*'))}
    assert before==after,'Archive modified during offline replay'
    assert not (directory/'transport_failures.jsonl').exists()
    assert all(row['response']['backend']=='codex' and row['response']['model']=='gpt-6.1-sol' for row in rows)
    return dict(passed=True,pilot='S21',registration_commit=cfg['registration']['commit'],
                scientific_source_count=len(cfg['sources']),cached_requests=len(rows),invalid_output_retries=0,
                transport_failures=0,archive_unchanged=True,zero_live_calls=True,
                canonical_result_sha256=hashlib.sha256(result_path.read_bytes()).hexdigest(),
                archive_sha256=before,independent=independent)


if __name__=='__main__':
    receipt=release();write('logs/s21_release.json',receipt);print(json.dumps(receipt,indent=2))
