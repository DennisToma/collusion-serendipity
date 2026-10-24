"""Regression checks for concrete final-review audit failures; no model calls."""
import copy
import json
from pathlib import Path
import unittest

from scripts.s03_audit import check_publication, check_consumed


class S03Publication(unittest.TestCase):
    def test_mutated_verdict_and_intervals_fail(self):
        canonical=json.loads(Path('results/s03_calculator.json').read_text())
        self.assertEqual(check_publication(canonical,canonical),'DUD')
        bad=copy.deepcopy(canonical);bad['verdict']='HIT'
        with self.assertRaisesRegex(ValueError,'canonical reanalysis'):
            check_publication(bad,canonical)
        bad=copy.deepcopy(canonical)
        bad['metrics']['quantity']['paired_difference']['ci95']=[10,20]
        with self.assertRaisesRegex(ValueError,'canonical reanalysis'):
            check_publication(bad,canonical)
        # Even a self-consistent wrong label fails the independent rational screen.
        bad=copy.deepcopy(canonical);bad['verdict']='HIT'
        with self.assertRaisesRegex(ValueError,'independent classification'):
            check_publication(bad,bad)

    def test_orphan_and_missing_requests_fail(self):
        check_consumed({'paid'},{'paid'},{'paid'})
        with self.assertRaisesRegex(ValueError,'Unused or missing'):
            check_consumed({'paid'},{'paid','orphan'},{'paid','orphan'})
        with self.assertRaisesRegex(ValueError,'Unused or missing'):
            check_consumed({'paid'},{'paid'},set())


if __name__=='__main__':
    unittest.main()
