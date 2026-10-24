"""Read-only S07 release audit plus guarded cached-resume byte check."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.legality import main as resume
from scripts.s07_analyze import analyze
from scripts.s07_publish import validate_registration


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    root=Path('data/s07_legality');guard=validate_registration(root);cfg=json.loads((root/'config.json').read_text())
    frozen=json.loads(Path('logs/s07_analysis_freeze.json').read_text())
    assert frozen['sources']==cfg['sources']
    for name,sha in cfg['sources'].items():
        assert digest(name)==sha
        assert hashlib.sha256(subprocess.check_output(['git','show',cfg['registration_commit']+':'+name])).hexdigest()==sha
    paths=[p for p in root.rglob('*') if p.is_file() and p.name!='.writer.lock']
    before={str(p):digest(p) for p in paths}
    with patch('sim.common.llm.chat',side_effect=AssertionError('Live calls forbidden in release audit')):
        with patch('sys.argv',['sim.legality']):
            with contextlib.redirect_stdout(io.StringIO()):resume()
        canonical=analyze(root)
    assert before=={str(p):digest(p) for p in paths}
    published=Path('results/s07_legality.json').read_bytes()
    assert published==(json.dumps(canonical,indent=2)+'\n').encode()
    sha=hashlib.sha256(published).hexdigest()
    for name in ['s07_verification','s07_independent']:
        record=json.loads(Path(f'logs/{name}.json').read_text());assert record['result_sha256']==sha
    record=json.loads(Path('logs/s07_verification.json').read_text())
    assert all(digest(p)==v for p,v in record['sha256'].items())
    original=json.loads(Path('logs/s07_independent_freeze.json').read_text())
    correction=json.loads(Path('logs/s07_independent_correction.json').read_text())
    assert original['script_sha256']==correction['original_sha256']==digest(correction['original_script'])
    assert correction['corrected_sha256']==digest('scripts/s07_independent.py')
    responses=[json.loads(x)['response'] for x in (root/'raw/responses.jsonl').read_text().splitlines()]
    assert max(x['call_completed_utc'] for x in responses)<cfg['deadline_utc']
    freeze_completed=sum(x['call_completed_utc']<=original['time_utc'] for x in responses)
    assert all(json.loads(p.read_text())['ground_truth']['ended_utc']>original['time_utc'] for p in root.glob('game_*.json'))
    output=dict(supplementary_freeze_completed_responses=freeze_completed,supplementary_freeze_before_any_complete_game=True,
        publication_guard=guard,registration_commit=cfg['registration_commit'],all_source_registration_hashes_match=True,
        all_input_audit_hashes_match=True,guarded_cached_resume_no_model_calls=True,
        all_dataset_bytes_unchanged=True,complete_canonical_result_byte_identical=True,
        supplementary_checker_history_verified=True,actual_run_completed_before_cutoff=True,
        first_call_utc=min(x['call_started_utc'] for x in responses),
        last_call_utc=max(x['call_completed_utc'] for x in responses),result_sha256=sha)
    Path('logs/s07_release_audit.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))

if __name__=='__main__':main()
