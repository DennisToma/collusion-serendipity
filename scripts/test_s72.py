"""Nontrivial aggregation, algebra, statistics and fail-closed release checks."""
import contextlib
import hashlib
import io
from fractions import Fraction
import itertools
from pathlib import Path
import tempfile
import tarfile
import subprocess
import sys
import unittest
from unittest.mock import patch
from scripts import s72_temporal as s
from scripts.s72_independent import reconstruct, exact_bounds


class Tests(unittest.TestCase):
    def test_all_stage_and_two_stage_profiles(self):
        profiles = list(itertools.product([False, True], repeat=4))
        for bits in profiles:
            types, acts = dict(zip('AB', bits[:2])), dict(zip('AB', bits[2:]))
            self.assertEqual(s.stage(types, acts), reconstruct([types], [acts]))
        for one, two in itertools.product(profiles, repeat=2):
            types = [dict(zip('AB', p[:2])) for p in [one, two]]
            acts = [dict(zip('AB', p[2:])) for p in [one, two]]
            actual = s.aggregate([s.stage(t, a) for t, a in zip(types, acts)])
            self.assertEqual(actual, reconstruct(types, acts))

    def test_delayed_benefit_without_any_same_round_benefit(self):
        a = s.stage(dict(A=True, B=False), dict(A=True, B=True))
        b = s.stage(dict(A=False, B=True), dict(A=True, B=True))
        self.assertEqual([a['both_gain'], b['both_gain']], [0, 0])
        full = s.aggregate([a, b])
        self.assertEqual(full['excess'], dict(A=4, B=4))
        self.assertEqual(full['both_gain'], 1)

    def test_positive_pair_total_can_harm_one_employee(self):
        d = s.stage(dict(A=True, B=False), dict(A=True, B=True))
        self.assertEqual(d['pair_excess'], 4)
        self.assertEqual(d['excess'], dict(A=-2, B=6))
        self.assertEqual(d['both_gain'], 0)

    def test_asymmetric_reviewer_and_author_identity_convention(self):
        d = s.stage(dict(A=True, B=False), dict(A=True, B=False))
        self.assertEqual(d['edges']['A']['y_out'], 1)
        self.assertEqual(d['edges']['A']['y_in'], 0)
        self.assertEqual(d['edges']['B']['y_in'], 1)
        self.assertEqual(d['excess'], dict(A=-8, B=5))

    def test_zero_is_not_strict_gain_and_order_does_not_change_sum(self):
        d = s.stage(dict(A=False, B=False), dict(A=True, B=False))
        reverse = s.stage(dict(A=False, B=False), dict(A=False, B=True))
        zero_min = s.aggregate([d, d, d, reverse])
        self.assertEqual(zero_min['min_excess'], 0)
        self.assertEqual(zero_min['both_gain'], 0)
        self.assertEqual(s.aggregate([d, reverse]), s.aggregate([reverse, d]))

    def test_missed_x_can_erase_both_sided_y_gains(self):
        good = s.stage(dict(A=False, B=False), dict(A=True, B=True))
        missed = s.stage(dict(A=True, B=True), dict(A=False, B=False))
        self.assertEqual(s.aggregate([good, missed])['excess'], dict(A=-3, B=-3))

    def test_full_window_can_gain_when_fixed_pairs_do_not(self):
        a = s.stage(dict(A=True, B=False), dict(A=True, B=True))
        b = s.stage(dict(A=False, B=True), dict(A=True, B=True))
        self.assertEqual(s.aggregate([a, a])['both_gain'], 0)
        self.assertEqual(s.aggregate([b, b])['both_gain'], 0)
        self.assertEqual(s.aggregate([a, a, b, b])['both_gain'], 1)

    def test_exhaustive_unique_stage_best_reply(self):
        for types in itertools.product([False, True], repeat=2):
            passed = dict(zip('AB', types))
            equilibria = []
            for decisions in itertools.product([False, True], repeat=2):
                actions = dict(zip('AB', decisions))
                current = s.stage(passed, actions)['actual']
                stable = True
                for a in 'AB':
                    alt = s.stage(passed, actions | {a: not actions[a]})['actual'][a]
                    stable &= alt <= current[a]
                if stable:
                    equilibria.append(actions)
            self.assertEqual(equilibria, [dict(A=passed['B'], B=passed['A'])])

    def test_fractional_statistics_and_independent_quantiles(self):
        v = [Fraction(x, 8) for x in [-4, -1, 0, 3, 7]]
        r = s.summary(v)
        self.assertEqual(list(map(Fraction, r['ci95_exact'])), exact_bounds(v))
        self.assertEqual(Fraction(r['mean_exact']), Fraction(1, 8))
        self.assertEqual(s.summary([Fraction(1, 4)]*5)['ci95_exact'], ['1/4', '1/4'])
        with self.assertRaises(ValueError):
            s.summary(v[:4])
        with self.assertRaisesRegex(ValueError, 'Exact'):
            s.summary([.1]*5)

    def test_invalid_statuses_empty_or_mismatched_windows_reject(self):
        with self.assertRaises(ValueError):
            s.stage(dict(A=1, B=False), dict(A=True, B=False))
        with self.assertRaises(ValueError):
            s.aggregate([])
        a = s.stage(dict(A=True, B=False), dict(A=True, B=True))
        b = s.stage(dict(A=True, C=False), dict(A=True, C=True))
        with self.assertRaises(ValueError):
            s.aggregate([a, b])

    def test_incomplete_release_rejects_before_analysis(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as tmp, contextlib.chdir(tmp):
            Path('one').write_text('keep')
            with patch.object(s, 'ARTIFACTS', ['one', 'two']), patch.object(s, 'analyze') as analysis:
                with self.assertRaisesRegex(ValueError, 'Incomplete'):
                    s.release()
                analysis.assert_not_called()
                self.assertEqual(Path('one').read_text(), 'keep')

    def test_release_guards_actual_llm_entry_point(self):
        import llm
        with tempfile.TemporaryDirectory(dir='/var/tmp') as tmp, contextlib.chdir(tmp):
            with patch.object(s, 'ARTIFACTS', ['one']), patch.object(s, 'analyze', side_effect=lambda: llm.chat('forbidden')):
                with self.assertRaisesRegex(AssertionError, 'forbids scientific'):
                    s.release()

    def test_freeze_rejects_changed_older_science_and_report_rows(self):
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode='w') as tree:
            for path, data in [('old.py', b'original'), ('REPORT.md', b'| S01 | kept |\n')]:
                info = tarfile.TarInfo(path)
                info.size = len(data)
                tree.addfile(info, io.BytesIO(data))
        with patch.object(s.subprocess, 'check_output', return_value=stream.getvalue()):
            with self.assertRaisesRegex(ValueError, 'science changed'):
                s.committed_science_matches({'old.py': hashlib.sha256(b'changed').hexdigest()}, ['| S01 | kept |'])
            with self.assertRaisesRegex(ValueError, 'report rows changed'):
                s.committed_science_matches({'old.py': hashlib.sha256(b'original').hexdigest()}, ['| S01 | altered |'])

    def test_separate_checker_cannot_read_archive_without_registration(self):
        from scripts import s72_independent as independent
        fixture = dict(id='S72', posthoc=True, verdict='ODD/context-only', new_games=0,
            scientific_model_calls=0, tuning_attempts=0, n_blocks=5, primary_rounds='3..10',
            metrics=dict.fromkeys(independent.KEYS))
        seen = []
        def read(path, *args, **kwargs):
            seen.append(str(path))
            raise FileNotFoundError('synthetic missing registration')
        with patch.object(Path, 'read_text', new=read):
            with self.assertRaises(FileNotFoundError):
                independent.verify(fixture)
        self.assertEqual(seen, ['data/s72_registration.json'])

    def test_optimized_python_rejected(self):
        p = subprocess.run([sys.executable, '-O', '-c', 'import scripts.s72_temporal'], capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('without optimization', p.stderr)

    def test_separate_registration_rejects_empty_source_manifest(self):
        import json
        from scripts.s72_independent import verify_registration
        m = dict(id='S72', posthoc=True, scientific_model_calls=0,
            registered_utc='2026-01-01', input_and_source_sha256={}, older_science_sha256={})
        with patch.object(Path, 'read_text', return_value=json.dumps(m)):
            with self.assertRaises(AssertionError):
                verify_registration(dict(registration=m, registration_receipt=m))

    def test_protection_includes_older_top_level_designs_and_protocol(self):
        paths = ['DESIGN_S68.md', 'sim/notepad.py', 'results/s29_notepad.json',
            'CLAUDE.md', 'PLAN.md', 'SCHEMA.md', 'uv.lock', 'data/SPLITS.md', 'REPORT.md']
        self.assertEqual(s.science_paths(paths), set(paths)-{'data/SPLITS.md', 'REPORT.md'})


if __name__ == '__main__':
    unittest.main()
