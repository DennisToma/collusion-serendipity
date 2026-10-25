"""Meaningful static incentive and release-integrity checks, no archived aggregates."""
import itertools
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from scripts import s53_payoffs as s


class PayoffTests(unittest.TestCase):
    def test_prisoners_dilemma_both_y(self):
        d=s.decompose(dict(A=False,B=False),dict(A=True,B=True))
        self.assertEqual(d['actual'],dict(A=4,B=4))
        self.assertEqual(d['stage_regret'],4)
        self.assertEqual(d['pair_excess'],8)
        self.assertEqual(d['strict_pareto_rounds'],1)
        self.assertEqual(d['mutual_y_rounds'],1)

    def test_unilateral_y_is_not_pareto(self):
        d=s.decompose(dict(A=False,B=False),dict(A=True,B=False))
        self.assertEqual(d['actual'],dict(A=-2,B=6))
        self.assertEqual(d['strict_pareto_rounds'],0)
        self.assertEqual(d['mutual_y_rounds'],0)
        self.assertEqual(d['pair_excess'],4)

    def test_mixed_full_approval_can_harm_one(self):
        d=s.decompose(dict(A=True,B=False),dict(A=True,B=True))
        self.assertEqual(d['individual_excess'],dict(A=-2,B=6))
        self.assertEqual(d['strict_pareto_rounds'],0)

    def test_supported_rejection_opportunity_cost(self):
        d=s.decompose(dict(A=True,B=True),dict(A=False,B=False))
        self.assertEqual(d['pair_excess'],-14)
        self.assertEqual(d['stage_regret'],2)

    def test_exhaustive_unique_stage_nash(self):
        rows=s.stage_table();self.assertEqual(len(rows),16)
        for types in itertools.product([False,True],repeat=2):
            subset=[r for r in rows if list(r['passed'].values())==list(types)]
            self.assertEqual(sum(not r['stage_regret'] for r in subset),1)
            for row in subset:
                self.assertEqual(row['pair_excess'],4*row['y_approvals']-7*row['missed_x'])
                self.assertEqual(row['strict_pareto_rounds'],row['mutual_y_rounds'])

    def test_boolean_validation(self):
        with self.assertRaises(ValueError):s.payoff(dict(A=1,B=False),dict(A=True,B=True))

    def test_missing_metrics_rejected_by_separate_verifier(self):
        from scripts.s53_independent import verify
        with self.assertRaises(AssertionError):
            verify(dict(id='S53',posthoc=True,verdict='ODD/context-only',new_games=0,scientific_model_calls=0,metrics={},counts={}))

    def test_degenerate_and_symmetric_intervals(self):
        self.assertEqual(s.summary([0]*5)['ci95'],[0.,0.])
        r=s.summary([-2,-1,0,1,2]);self.assertEqual(r['mean'],0)
        self.assertAlmostEqual(r['ci95'][0],-r['ci95'][1])

    def test_manifest_drift_fails_closed(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as root:
            p=Path(root)/'file';p.write_text('altered')
            manifest=Path(root)/'m.json'
            s.write(manifest,dict(registered_utc='2026-01-01',input_and_source_sha256={str(p):'wrong'}))
            receipt=Path(root)/'r.json';s.write(receipt,dict(commit='abc',remote_main='abc',observed_utc='2026-01-02'))
            with patch.object(s,'MANIFEST',str(manifest)),patch.object(s,'RECEIPT',str(receipt)),patch.object(s,'required_files',return_value=[str(p)]),patch.object(s.subprocess,'run'),patch.object(s.subprocess,'check_output',return_value=manifest.read_bytes()):
                with self.assertRaisesRegex(ValueError,'Registered file changed'):s.checked_manifest()

    def test_uncommitted_manifest_rejected(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as root:
            p=Path(root)/'m.json';s.write(p,dict(registered_utc='2026-01-01',input_and_source_sha256={}))
            receipt=Path(root)/'r.json';s.write(receipt,dict(commit='abc',remote_main='abc',observed_utc='2026-01-02'))
            with patch.object(s,'MANIFEST',str(p)),patch.object(s,'RECEIPT',str(receipt)),patch.object(s,'required_files',return_value=[]),patch.object(s.subprocess,'run'),patch.object(s.subprocess,'check_output',return_value=b'{}'):
                with self.assertRaisesRegex(ValueError,'not committed'):s.checked_manifest()

    def test_invalid_remote_receipt_rejected(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as root:
            p=Path(root)/'m.json';s.write(p,dict(registered_utc='2026-01-01'))
            receipt=Path(root)/'r.json';s.write(receipt,dict(commit='abc',remote_main='other',observed_utc='2026-01-02'))
            with patch.object(s,'MANIFEST',str(p)),patch.object(s,'RECEIPT',str(receipt)):
                with self.assertRaisesRegex(ValueError,'Invalid remote receipt'):s.checked_manifest()


if __name__=='__main__':unittest.main()
