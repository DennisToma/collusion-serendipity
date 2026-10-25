"""Corruption probes against receipt checks and real disposable S29 replays."""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import portfolio_replay as replay


def main():
    replay.require(__debug__, 'Do not use Python -O')
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', default=replay.OUT)
    parser.add_argument('--out', default='logs/iteration58_verification.json')
    args = parser.parse_args()
    output = replay.output_path(args.out)
    record = json.loads(Path(args.receipt).read_text())
    checked = replay.check(record)
    cases = {
        'missing_pilot': lambda r: r['records'].pop(),
        'duplicate_pilot': lambda r: r['records'].__setitem__(1, deepcopy(r['records'][0])),
        'failed_run': lambda r: r.update(passed=False),
        'wrong_baseline': lambda r: r.update(baseline_commit='0'*40),
        'wrong_runner': lambda r: r.update(runner_sha256='0'*64),
        'changed_checkout': lambda r: r.update(source_checkout_preserved=False),
        'wrong_historical_revision': lambda r: r['special_revisions'].__setitem__('S67', replay.BASELINE),
        'attempted_llm_call': lambda r: r['records'][0].update(llm_chat_attempts=1),
        'dirty_clone': lambda r: r['records'][0].update(clone_clean=False),
        'changed_result': lambda r: r['records'][0].update(result_sha256='0'*64),
        'missing_imported_analyzer': lambda r: r['records'][0]['imported_repo_sources'].pop('scripts/s01_digits.py'),
        'changed_imported_source': lambda r: r['records'][0]['imported_repo_sources'].__setitem__('llm.py', '0'*64),
        'missing_checker': lambda r: r['records'][2].update(independent_checker=None),
        'failed_checker': lambda r: r['records'][2].update(independent_checker={'passed': False}),
        'substituted_checker_receipt': lambda r: r['records'][2].update(independent_checker={'passed': True}),
        'wrong_evidence_manifest': lambda r: r['records'][0].update(evidence_manifest_sha256='0'*64),
        'wrong_evidence_file_count': lambda r: r['records'][0].update(evidence_files_unchanged=0),
        'wrong_preservation_coverage': lambda r: r.update(protected_baseline_files=0),
    }
    probes = {}
    for name, change in cases.items():
        changed = deepcopy(record)
        change(changed)
        try:
            replay.check(changed)
        except (ValueError, KeyError):
            probes[name] = 'rejected'
        else:
            raise AssertionError('Corruption accepted: ' + name)
    # Test the exact comparison at semantic boundaries, not approximate values.
    for a, b in [({'x': False}, {'x': 0}), ({'x': 1}, {'x': True}), ({'x': 1}, {'x': 1.0})]:
        assert replay.canonical(a) != replay.canonical(b)
    assert replay.canonical({'a': 1, 'b': [2]}) == replay.canonical({'b': (2,), 'a': 1})
    probes['bool_integer_float_distinctions'] = 'rejected; key order/tuple normalization accepted'
    spec = next(s for s in replay.specs(replay.ROOT) if s['pilot'] == 'S29')
    before = replay.evidence_snapshot(replay.ROOT)
    with tempfile.TemporaryDirectory(dir='/var/tmp', prefix='portfolio_probes_') as tmp:
        runner = Path(tmp)/'worker.py'
        runner.write_bytes(Path(replay.__file__).read_bytes())
        clone = Path(tmp)/'repo'
        subprocess.run(['git', 'clone', '-q', '--shared', '--no-checkout', str(replay.ROOT), str(clone)], check=True)
        subprocess.run(['git', 'checkout', '-q', '--detach', spec['revision']], cwd=clone, check=True)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(clone),
                   OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                   PYTHONHASHSEED='0', PORTFOLIO_SOURCE_ROOT=str(replay.ROOT))
        env.pop('PYTHONOPTIMIZE', None)
        command = [sys.executable, str(runner), 'worker', '--root', str(clone), '--spec', json.dumps(spec)]
        def invoke():
            return subprocess.run(command, cwd=clone, env=env, text=True, capture_output=True, timeout=90)
        normal = invoke()
        assert normal.returncode == 0, normal.stderr
        probes['uncorrupted_S29_control'] = 'passed'
        changes = {
            'result_integer_to_float': (spec['result'], lambda b: b.replace(b'"n_games": 10,', b'"n_games": 10.0,', 1), 'Archived result differs'),
            'raw_response_corruption': ('data/s29_notepad/raw/responses.jsonl', lambda b: b.replace(b'"text":', b'"broken_text":', 1), "KeyError: 'text'"),
            'model_call_during_import': ('scripts/s29_analyze.py', lambda b: b'import llm\nllm.chat()\n'+b, 'forbids scientific model calls'),
        }
        for name, (path, mutate, error) in changes.items():
            target = clone/path
            original = target.read_bytes()
            changed = mutate(original)
            assert changed != original, 'Mutation did not change bytes: ' + name
            target.write_bytes(changed)
            proc = invoke()
            target.write_bytes(original)
            assert proc.returncode != 0, 'Corruption accepted: ' + name
            if error:
                assert error in proc.stderr, proc.stderr
            probes[name] = dict(rejected=True, stderr=proc.stderr)
        assert replay.git(clone, 'status', '--porcelain') == b''
        for name, command, error in [
            ('optimized_python_rejected', [sys.executable, '-O', str(Path(__file__).resolve()), '--out', str(Path(tmp)/'optimized.json')], 'Do not use Python -O'),
            ('protected_output_rejected', [sys.executable, str(Path(__file__).resolve()), '--out', str(replay.ROOT/'results/s29_notepad.json')], 'Repository output must be'),
        ]:
            rejected = subprocess.run(command, cwd=replay.ROOT, env=env, text=True, capture_output=True, timeout=30)
            assert rejected.returncode != 0 and error in rejected.stderr, rejected.stderr
            probes[name] = 'rejected before verification/output write'
    assert before == replay.evidence_snapshot(replay.ROOT), 'Probe changed source checkout'
    result = dict(passed=True, receipt_check=checked, probes=probes,
                  checker_success_counts={basis:sum(r['checker_success_basis'].startswith(basis) for r in record['records'])
                      for basis in ['explicit', 'completed', 'not available']},
                  receipt_sha256=hashlib.sha256(Path(args.receipt).read_bytes()).hexdigest(),
                  runner_sha256=hashlib.sha256(Path(replay.__file__).read_bytes()).hexdigest(),
                  source_evidence_preserved=True,
                  scope='In-memory receipt corruptions, type boundaries and three real disposable-clone S29 corruptions; no frozen source/archive changed')
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'passed': True, 'probes': len(probes), 'receipt_check': checked}, indent=2))


if __name__ == '__main__':
    main()
