"""Regression checks for post-outcome request-contract supplement."""
import json
from pathlib import Path
import unittest
from scripts.s19_request_contract import check,check_system

class Tests(unittest.TestCase):
    def fixture(self):
        requests=[json.loads(line) for line in Path('data/s19_labels/raw/requests.jsonl').read_text().splitlines()]
        req=next(r for r in requests if r['payload'][5].endswith('_neutral'))
        gt=json.loads(Path('data/s19_labels/game_24320_neutral.json').read_text())['ground_truth']
        return req['payload'][0],req['payload'][7],gt['assigned_pair']

    def test_all_saved_requests_pass(self):
        self.assertEqual(check()['requests'],300)

    def test_neutral_quality_leak_rejected(self):
        system,agent,pair=self.fixture()
        with self.assertRaises(AssertionError):check_system(system+' FAIL defective quality.','neutral',agent,pair)

    def test_payoff_mutation_rejected(self):
        system,agent,pair=self.fixture()
        with self.assertRaises(AssertionError):check_system(system.replace('author 6 bonus','author 7 bonus'),'neutral',agent,pair)

if __name__=='__main__':unittest.main()
