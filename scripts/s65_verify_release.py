"""Adversarial editorial release checks on the complete S65 archive.

Reversible report mutation and injected post-snapshot archive file are restored
in finally blocks. Registered sources, raw decisions and estimates never change.
"""
import contextlib,hashlib,io,json,os,subprocess,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s65_release_final import check

if not __debug__:raise RuntimeError('Run without optimization')

def main():
    report=Path('REPORT.md');original=report.read_bytes()
    marker=Path('data/s65_bonus_pooling/raw/release_inventory_canary.txt')
    assert not marker.exists()
    try:
        report.write_bytes(b'S65 proved collusion with fabricated numbers.\n'+original)
        try:
            with contextlib.redirect_stdout(io.StringIO()):check()
        except AssertionError as exc:assert 'Rendered document/asset mismatch: REPORT.md' in str(exc)
        else:raise AssertionError('Contradictory extra headline accepted')
    finally:report.write_bytes(original)
    try:
        def inject():marker.write_text('Injected after archive snapshot\n')
        with patch('sim.bonus_pooling.main',side_effect=inject):
            try:
                with contextlib.redirect_stdout(io.StringIO()):check()
            except AssertionError as exc:assert 'Archive file inventory changed' in str(exc)
            else:raise AssertionError('Added archive file accepted')
    finally:
        if marker.exists():marker.unlink()
    proc=subprocess.run([sys.executable,'-O','-c','import scripts.s65_release_final'],capture_output=True,text=True)
    assert proc.returncode!=0 and 'requires Python without optimization' in proc.stderr
    with contextlib.redirect_stdout(io.StringIO()):receipt=check()
    assert report.read_bytes()==original
    result=dict(passed=True,contradictory_extra_headline_rejected_without_rewrite=True,
                file_added_after_snapshot_rejected=True,optimized_python_rejected=True,
                all_mutations_restored=True,clean_release_passed=receipt['passed'],
                report_sha256=hashlib.sha256(original).hexdigest())
    Path('logs/s65_release_mutations.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
