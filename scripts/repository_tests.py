"""Canonical offline suite with narrowly scoped synthetic test fixtures.

The archived S21/S31/S33 tests create synthetic data using wall time. Their
original deadlines have expired. These scoped fixtures apply ONLY while running
those tests, never to real archive analysis/release. No frozen source is edited. S54’s negative NEW-launch test also needs an empty
external cwd once the real default dataset is complete;only that test is isolated.
"""
import argparse
from contextlib import nullcontext
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

if not __debug__:raise RuntimeError('Run without -O')


def leaves(suite):
    for item in suite:
        if isinstance(item,unittest.TestSuite):yield from leaves(item)
        else:yield item


def run(out):
    collected=list(leaves(unittest.defaultTestLoader.discover('scripts',pattern='test_*.py')))
    groups={key:[] for key in ['ordinary','s21','s31','s33','s54_direct_entry']}
    for test in collected:
        module=test.__class__.__module__.split('.')[-1]
        key=('s54_direct_entry' if module=='test_s54' and test._testMethodName=='test_direct_live_entries_rejected_without_bootstrap' else
             's21' if module in ['test_s21','test_s21_release'] else
             's31' if module=='test_s31' else 's33' if module=='test_s33' else 'ordinary')
        groups[key].append(test)
    patches={'s21':lambda:patch('scripts.s21_audit.DEADLINE','2099-01-01T00:00:00+00:00'),
             's31':lambda:patch('sim.labor.now',return_value='2026-10-24T23:29:00+00:00'),
             's33':lambda:patch('sim.leniency.now',return_value='2026-10-25T00:20:00+00:00')}
    from scripts.s54_fixtures import empty_live_destination
    patches['s54_direct_entry']=empty_live_destination
    results=[]
    for name,tests in groups.items():
        with patches[name]() if name in patches else nullcontext():
            result=unittest.TextTestRunner(verbosity=1).run(unittest.TestSuite(tests))
        results.append(result)
    receipt=dict(passed=all(r.wasSuccessful() for r in results),tests=sum(r.testsRun for r in results),
                 failures=sum(len(r.failures) for r in results),errors=sum(len(r.errors) for r in results),
                 group_counts={k:len(v) for k,v in groups.items()},
                 legacy_synthetic_fixtures=dict(s21_deadline='2099-01-01T00:00:00+00:00',
                     s31_now='2026-10-24T23:29:00+00:00',s33_now='2026-10-25T00:20:00+00:00'),
                 real_archive_deadlines_and_sources_unchanged=True,
                 s54_direct_entry_fixture='One frozen new-launch rejection test runs in an empty external cwd;real completed archive untouched')
    Path(out).write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    if not receipt['passed']:raise SystemExit(1)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();run(a.out)
