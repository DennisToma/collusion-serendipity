"""Economic, numerical and publication-integrity checks, no archived aggregates."""
import contextlib
from fractions import Fraction
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import s67_audit as s


class Tests(unittest.TestCase):
    def test_pooling_after_charge_not_before(self):
        alloc, final = s.payoff(dict(A=False, B=False), dict(A=True, B=False), 'pooled')
        self.assertEqual(alloc, dict(A=-2, B=6))
        self.assertEqual(final, dict(A=2, B=2))

    def test_half_point_supported_review(self):
        d = s.decompose(dict(A=True, B=True), dict(A=False, B=True), 'pooled')
        self.assertEqual(d['final'], dict(A=3.5, B=3.5))
        self.assertEqual(d['stage_regret'], 3.5)
        self.assertEqual(d['pair_shortfall'], 7)

    def test_individual_mutual_y_pareto_but_not_nash(self):
        d = s.decompose(dict(A=False, B=False), dict(A=True, B=True), 'individual')
        self.assertEqual(d['strict_pareto_rounds'], 1)
        self.assertEqual(d['stage_regret'], 4)
        self.assertEqual(d['final'], dict(A=4, B=4))

    def test_pooled_mutual_y_is_nash_and_not_strict_pareto(self):
        d = s.decompose(dict(A=False, B=False), dict(A=True, B=True), 'pooled')
        self.assertEqual(d['strict_pareto_rounds'], 0)
        self.assertEqual(d['stage_regret'], 0)
        self.assertEqual(d['costly_y_approvals'], 0)
        self.assertEqual(d['organization_loss'], 20)

    def test_pooled_rejections_are_profitable_forgone_actions(self):
        d = s.decompose(dict(A=False, B=False), dict(A=False, B=False), 'pooled')
        self.assertEqual(d['profitable_y_rejections'], 2)
        self.assertEqual(d['stage_regret'], 4)
        self.assertEqual(d['pair_shortfall'], 8)

    def test_mixed_individual_approval_not_strict_pareto(self):
        d = s.decompose(dict(A=True, B=False), dict(A=True, B=True), 'individual')
        self.assertEqual(d['strict_pareto_rounds'], 0)
        self.assertEqual(d['stage_regret'], 2)

    def test_exhaustive_independent_analytic_formulas(self):
        from scripts.s67_independent import formulas
        rows = s.stage_table()
        self.assertEqual(len(rows), 32)
        for r in rows:
            self.assertEqual(r, dict(condition=r['condition'], passed=r['passed'], actions=r['actions'],
                                     **formulas(r['passed'], r['actions'], r['condition'])))

    def test_every_unilateral_incentive_sign_and_conservation(self):
        for r in s.stage_table():
            self.assertEqual(sum(r['allocated'].values()), sum(r['final'].values()))
            for a in 'AB':
                b = next(x for x in 'AB' if x != a)
                yes = s.payoff(r['passed'], r['actions'] | {a: True}, r['condition'])[1][a]
                no = s.payoff(r['passed'], r['actions'] | {a: False}, r['condition'])[1][a]
                expected = (1 if r['passed'][b] else -2) if r['condition'] == 'individual' else (3.5 if r['passed'][b] else 2)
                self.assertEqual(yes-no, expected)

    def test_strict_input_validation(self):
        for cond, passed, acts in [('bad', dict(A=True, B=False), dict(A=True, B=False)),
            ('pooled', dict(A=1, B=False), dict(A=True, B=False)),
            ('individual', dict(A=True, B=False), dict(A=True)),
            ('pooled', dict(A=True), dict(A=True))]:
            with self.assertRaises(ValueError):
                s.payoff(passed, acts, cond)

    def test_fractional_summary_and_degenerate_bounds(self):
        self.assertEqual(s.summary([Fraction(1, 16)]*5)['ci95_exact'], ['1/16', '1/16'])
        values = [Fraction(x, 16) for x in [-2, -1, 0, 1, 2]]
        d = s.summary(values)
        self.assertEqual(d['mean_exact'], '0')
        self.assertEqual(Fraction(d['ci95_exact'][0]), -Fraction(d['ci95_exact'][1]))
        self.assertLess(d['t95'][0], d['ci95'][0])

    def test_independent_exact_fraction_boundaries(self):
        from scripts.s67_independent import exact_bounds
        v = [Fraction(x, 16) for x in [-2, -1, 0, 1, 2]]
        self.assertEqual(list(map(Fraction, s.summary(v)['ci95_exact'])), exact_bounds(v))
        corrupted = Fraction(s.summary(v)['ci95_exact'][0]) + Fraction(1, 10**13)
        self.assertNotEqual(corrupted, exact_bounds(v)[0])

    def test_checker_rejects_missing_metrics(self):
        from scripts.s67_independent import verify
        with self.assertRaises(AssertionError):
            verify(dict(id='S67', posthoc=True, verdict='ODD/context-only', source_calibration='UNRESOLVED',
                        new_games=0, scientific_model_calls=0, tuning_attempts=0, n_blocks=5,
                        primary_rounds='3..10', metrics={}))

    def test_incomplete_publication_fails_before_analysis(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td, contextlib.chdir(td):
            Path('one').write_text('existing')
            with patch.object(s, 'ARTIFACTS', ['one', 'missing']), patch.object(s, 'analyze') as analyze:
                with self.assertRaisesRegex(ValueError, 'Incomplete'):
                    s.release()
                analyze.assert_not_called()
                self.assertEqual(Path('one').read_text(), 'existing')

    def test_release_forbids_actual_llm_entrypoint(self):
        import llm
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td, contextlib.chdir(td):
            with patch.object(s, 'ARTIFACTS', ['one']), patch.object(s, 'analyze', side_effect=lambda: llm.chat('forbidden')):
                with self.assertRaisesRegex(AssertionError, 'forbids scientific'):
                    s.release()

    def test_registration_not_committed_rejected(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            m, r = str(Path(td)/'m'), str(Path(td)/'r')
            s.write(m, dict(registered_utc='2026-01-01', input_and_source_sha256={}, older_science_sha256={}))
            s.write(r, dict(commit='abc', remote_main='abc', observed_utc='2026-01-02'))
            with patch.object(s, 'MANIFEST', m), patch.object(s, 'RECEIPT', r), patch.object(s, 'required_files', return_value=[]), patch.object(s.subprocess, 'run'), patch.object(s.subprocess, 'check_output', return_value=b'{}'):
                with self.assertRaisesRegex(ValueError, 'not committed'):
                    s.checked_manifest()

    def test_remote_receipt_mismatch_rejected(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            m, r = str(Path(td)/'m'), str(Path(td)/'r')
            s.write(m, dict(registered_utc='2026-01-01', input_and_source_sha256={}, older_science_sha256={}))
            s.write(r, dict(commit='abc', remote_main='other', observed_utc='2026-01-02'))
            with patch.object(s, 'MANIFEST', m), patch.object(s, 'RECEIPT', r):
                with self.assertRaisesRegex(ValueError, 'Invalid remote'):
                    s.checked_manifest()


if __name__ == '__main__':
    unittest.main()
