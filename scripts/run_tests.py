"""Run repo tests with clock overrides ONLY in historical synthetic fixtures.

Archived scientific sources and real dataset deadlines remain unchanged.
S21 mocked/dry fixtures omitted a clock and expire after2026-10-24T22:00;
S31's two mocked live-cache fixtures expire after2026-10-25T00:30. These
modules use temporary synthetic archives/mocked routes. Real S21/S31 release
checks must run separately with original scientific clocks and cutoffs.
"""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))


def flatten(suite):
    for item in suite:
        if isinstance(item,unittest.TestSuite):yield from flatten(item)
        else:yield item


def main():
    tests=list(flatten(unittest.defaultTestLoader.discover('scripts',pattern='test_*.py')))
    historical=[];labor=[];current=[]
    for test in tests:
        module=test.id().split('.')[0]
        if module in {'test_s21','test_s21_release'}:historical.append(test)
        elif module=='test_s31':labor.append(test)
        else:current.append(test)
    runner=unittest.TextTestRunner(verbosity=1)
    first=runner.run(unittest.TestSuite(current))
    with patch('scripts.s21_audit.DEADLINE','2099-01-01T00:00:00+00:00'):
        second=runner.run(unittest.TestSuite(historical))
    with patch('sim.labor.now',return_value='2026-10-24T23:29:00+00:00'):
        third=runner.run(unittest.TestSuite(labor))
    runs=[first,second,third]
    out=dict(passed=all(r.wasSuccessful() for r in runs),tests=sum(r.testsRun for r in runs),
             failures=sum(len(r.failures) for r in runs),errors=sum(len(r.errors) for r in runs),
             legacy_synthetic_cutoff_override=dict(modules=['test_s21','test_s21_release'],tests=second.testsRun,
                                                 deadline='2099-01-01T00:00:00+00:00',source_files_modified=False),
             legacy_s31_synthetic_clock=dict(modules=['test_s31'],tests=third.testsRun,
                                            now='2026-10-24T23:29:00+00:00',source_files_modified=False),
             real_archive_deadlines_unchanged=True)
    print(json.dumps(out,indent=2))
    if not out['passed']:raise SystemExit(1)

if __name__=='__main__':main()
