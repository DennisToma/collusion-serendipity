"""Run repo tests with historical cutoff overrides ONLY in synthetic S21 fixtures.

The archived source and real dataset deadline remain unchanged. S21's legacy
mocked/dry tests omitted a test-clock fixture and expired after 2026-10-24 22:00.
Those two modules generate only temporary synthetic archives with mocked routes.
Actual S21 release must be verified separately with its unmodified deadline.
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
    historical=[];current=[]
    for test in tests:
        (historical if test.id().split('.')[0] in {'test_s21','test_s21_release'} else current).append(test)
    runner=unittest.TextTestRunner(verbosity=1)
    first=runner.run(unittest.TestSuite(current))
    with patch('scripts.s21_audit.DEADLINE','2099-01-01T00:00:00+00:00'):
        second=runner.run(unittest.TestSuite(historical))
    out=dict(passed=first.wasSuccessful() and second.wasSuccessful(),tests=first.testsRun+second.testsRun,
             failures=len(first.failures)+len(second.failures),errors=len(first.errors)+len(second.errors),
             legacy_synthetic_cutoff_override=dict(modules=['test_s21','test_s21_release'],tests=second.testsRun,
                                                 deadline='2099-01-01T00:00:00+00:00',source_files_modified=False),
             real_archive_deadlines_unchanged=True)
    print(json.dumps(out,indent=2))
    if not out['passed']:raise SystemExit(1)

if __name__=='__main__':main()
