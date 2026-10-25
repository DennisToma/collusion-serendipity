"""Restored mutation checks against the actual S67 release; no frozen source edits."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.s67_audit import ARTIFACTS, checked_manifest, release


def main():
    target = Path(ARTIFACTS[0])
    original = target.read_bytes()
    try:
        target.write_bytes(original+b'\n')
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                release()
        except ValueError as e:
            assert 'release bytes changed' in str(e)
        else:
            raise AssertionError('Corrupt published bytes accepted')
        assert target.read_bytes() == original+b'\n', 'Corrupt artifact silently rewritten'
    finally:
        target.write_bytes(original)
    canary = Path('data/s65_bonus_pooling/raw/s67_inventory_canary')
    assert not canary.exists()
    try:
        canary.write_text('injected archive file')
        try:
            checked_manifest()
        except ValueError as e:
            assert 'Archive inventory changed' in str(e)
        else:
            raise AssertionError('Added archive file accepted')
    finally:
        if canary.exists():
            canary.unlink()
    # Mutate a copy in memory: verify exact rational metadata, not just float tolerances.
    from scripts.s67_independent import verify
    r = json.loads(original)
    from fractions import Fraction
    saved = r['metrics']['stage_regret']['difference']['ci95_exact']
    saved[0] = str(Fraction(saved[0])+Fraction(1, 10**13))
    try:
        verify(r)
    except AssertionError:
        pass
    else:
        raise AssertionError('Incorrect exact endpoint accepted')
    proc = subprocess.run([sys.executable, '-O', '-c', 'import scripts.s67_audit'], capture_output=True, text=True)
    assert proc.returncode and 'without optimization' in proc.stderr
    with contextlib.redirect_stdout(io.StringIO()):
        release()
    assert target.read_bytes() == original
    result = dict(passed=True, corrupt_result_rejected_without_rewrite=True,
        added_archive_file_rejected=True, incorrect_exact_endpoint_rejected=True,
        optimized_python_rejected=True, all_mutations_restored=True)
    Path('logs/s67_integrity.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
