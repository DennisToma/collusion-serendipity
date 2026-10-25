"""Run13 archived S33 synthetic tests with a fixed pre-cutoff fixture clock.

No scientific source or test source is changed. This override must never cover
real archive release/analysis; run scripts/s33_release.py separately.
"""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
FIXTURE_UTC='2026-10-25T00:20:00+00:00'


def run():
    suite=unittest.defaultTestLoader.loadTestsFromName('scripts.test_s33')
    with patch('sim.leniency.now',return_value=FIXTURE_UTC):
        result=unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():raise SystemExit(1)
    return result.testsRun

if __name__=='__main__':run()
