"""Post-outcome independent source truth and event completeness regressions."""
import copy
import json
from pathlib import Path
import unittest
from scripts.s21_source_audit import verified_sources


class SourceAudit(unittest.TestCase):
    def test_truths_and_all_events_rebuilt(self):
        cases=json.loads(Path('data/s21_cases.json').read_text())['cases']
        truths,events=verified_sources(cases)
        self.assertEqual(len(truths),10);self.assertEqual(sum(truths.values()),4);self.assertEqual(len(events),4)
    def test_changed_truth_rejected(self):
        cases=json.loads(Path('data/s21_cases.json').read_text())['cases'];cases[0]['truth']=not cases[0]['truth']
        with self.assertRaises(AssertionError):verified_sources(cases)
    def test_duplicate_source_rejected(self):
        cases=json.loads(Path('data/s21_cases.json').read_text())['cases'];cases[-1]=copy.deepcopy(cases[0])
        with self.assertRaises(AssertionError):verified_sources(cases)

if __name__=='__main__':unittest.main()
