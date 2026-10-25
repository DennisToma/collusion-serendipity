"""Post-outcome exact-number contract catches perturbations hidden by float tolerance."""
import copy
from fractions import Fraction as F
import json
from pathlib import Path
import unittest
from scripts.s32_exact_check import exact_numbers

class ExactCompanion(unittest.TestCase):
    def test_archive_exact_rational_contract(self):
        r=json.loads(Path('results/s32_resource.json').read_text())
        self.assertEqual(exact_numbers(r),15)
    def test_sub_tolerance_bound_and_mean_mutations(self):
        r=json.loads(Path('results/s32_resource.json').read_text())
        for field in ['ci95_exact','mean_exact']:
            corrupted=copy.deepcopy(r);d=corrupted['metrics']['resource_payment']['paired_difference']
            if field=='ci95_exact':d[field][0]=str(F(d[field][0])+F(1,10**13))
            else:d[field]=str(F(d[field])+F(1,10**13))
            with self.assertRaisesRegex(AssertionError,'Exact'):exact_numbers(corrupted)

if __name__=='__main__':unittest.main()
