"""Independent-review mutation regressions; no scientific calls or archive edits."""
import copy
import json
from pathlib import Path
import unittest
from scripts.s28_companion import verify,contracts

class Companion(unittest.TestCase):
    def test_top_level_mutations_rejected(self):
        result=json.loads(Path('results/s28_payoff.json').read_text())
        self.assertTrue(verify('data/s28_payoff',result)['passed'])
        for field,value in [('model','wrong'),('backend','wrong'),('pair_internal_bonus_difference_exact','999')]:
            changed=copy.deepcopy(result);changed[field]=value
            with self.assertRaises(AssertionError):verify('data/s28_payoff',changed)

    def test_nonempty_history_prompt_prefix_corruption_rejected(self):
        requests=[json.loads(line)['payload'] for line in Path('data/s28_payoff/raw/requests.jsonl').read_text().splitlines()]
        prose=next(p for p in requests if p[5]=='s28_24520_prose' and p[6]==9)
        table=next(p for p in requests if p[5]=='s28_24520_table' and p[6]==9 and p[7]==prose[7])
        gt=json.loads(Path('data/s28_payoff/game_24520_prose.json').read_text())['ground_truth']
        agent=prose[7];partner=next(a for a in gt['assigned_pair'] if a!=agent)
        contracts(prose,table,agent,partner)
        changed=copy.deepcopy(table);changed[0]='Extra instruction. '+changed[0]
        with self.assertRaises(AssertionError):contracts(prose,changed,agent,partner)

if __name__=='__main__':unittest.main()
