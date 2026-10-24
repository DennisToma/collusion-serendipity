"""Regression for final critic's independently demonstrated metadata mutations."""
import copy
import json
from pathlib import Path
import unittest
from scripts.s06_checked_independent import validate_contract


class Tests(unittest.TestCase):
    def test_rejects_false_metadata_and_duplicate_game(self):
        original=json.loads(Path('results/s06_denomination.json').read_text())
        validate_contract(original)
        for field,value in [('primary_contrast','unit minus cent'),('primary_rounds','1..12'),
                            ('primary_metric','absolute_change'),('n_games',9),('tuning_attempts',1)]:
            changed=copy.deepcopy(original);changed[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):validate_contract(changed)
        changed=copy.deepcopy(original);changed['metrics']['quantity']['exact_denominator']=999
        with self.assertRaises(ValueError):validate_contract(changed)
        changed=copy.deepcopy(original);changed['games'].append(changed['games'][0])
        with self.assertRaises(ValueError):validate_contract(changed)
        changed=copy.deepcopy(original);changed['games'][1]=changed['games'][0]
        with self.assertRaises(ValueError):validate_contract(changed)

if __name__=='__main__':unittest.main()
