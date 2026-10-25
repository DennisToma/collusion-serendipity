"""Run frozen S54 tests with NEW-launch rejection in its own empty directory."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s54_fixtures import empty_live_destination
from scripts.repository_tests import leaves


def run(out=None):
    snapshot=json.loads(Path('logs/s54_archive_snapshot.json').read_text())
    frozen={**snapshot['sources'],**snapshot['archive']}
    before={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in frozen}
    assert before==frozen,'Real source/archive changed before tests'
    tests=list(leaves(unittest.defaultTestLoader.loadTestsFromName('scripts.test_s54')))
    target='test_direct_live_entries_rejected_without_bootstrap'
    isolated=[test for test in tests if test._testMethodName==target]
    ordinary=[test for test in tests if test._testMethodName!=target]
    assert len(isolated)==1 and len(ordinary)==22
    results=[unittest.TextTestRunner(verbosity=1).run(unittest.TestSuite(ordinary))]
    with empty_live_destination():results.append(unittest.TextTestRunner(verbosity=1).run(unittest.TestSuite(isolated)))
    after={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in frozen}
    assert after==before,'Real source/archive changed during tests'
    receipt=dict(verified_registered_sources=len(snapshot['sources']),verified_archive_files=len(snapshot['archive']),passed=all(r.wasSuccessful() for r in results),tests=sum(r.testsRun for r in results),
                 failures=sum(len(r.failures) for r in results),errors=sum(len(r.errors) for r in results),
                 isolated_synthetic_test=target,real_archive_and_frozen_sources_unchanged=True)
    if out:Path(out).write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    if not receipt['passed']:raise SystemExit(1)
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out');a=p.parse_args();run(a.out)
