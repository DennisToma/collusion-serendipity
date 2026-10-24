"""Regression: an incomplete metric table must never receive publication PASS."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts.s22_checked_independent import checked_verify

class Tests(unittest.TestCase):
    def test_incomplete_contract_rejected_before_arithmetic(self):
        result=json.loads(Path('results/s22_enforcement.json').read_text())
        mutations=[]
        r=copy.deepcopy(result);del r['metrics']['organization_loss'];mutations.append(r)
        r=copy.deepcopy(result);r['metrics']['pair_bad']['exact_denominator']=40;mutations.append(r)
        r=copy.deepcopy(result);del r['metrics']['pair_bad']['paired_difference']['exact_signflip_p_upper'];mutations.append(r)
        r=copy.deepcopy(result);r['games'][1]=r['games'][0];mutations.append(r)
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            path=Path(d)/'result.json'
            for r in mutations:
                path.write_text(json.dumps(r))
                with patch('scripts.s22_checked_independent.verify',side_effect=AssertionError('arithmetic must not run')) as arithmetic:
                    with self.assertRaises(AssertionError):checked_verify('data/s22_enforcement',path)
                    arithmetic.assert_not_called()

    def test_complete_archive_passes(self):
        report=checked_verify('data/s22_enforcement','results/s22_enforcement.json')
        self.assertTrue(report['complete_registered_contract']);self.assertEqual(report['sign_tests'],30)

if __name__=='__main__':unittest.main()
