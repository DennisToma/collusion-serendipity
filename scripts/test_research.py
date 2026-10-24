"""Small validity checks for simultaneous decisions, economics and held-out data."""
import contextlib
import io
import json
from pathlib import Path
import unittest

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from sim.cournot import parse, payoffs, run_game


class RecordingCache:
    dry = True

    def __init__(self):
        self.prompts = []

    def call(self, system, prompt, tier, backend, run_id, t, agent, attempt, model):
        self.prompts.append((t, agent, system, prompt))
        return dict(text=json.dumps(dict(quantity=6, private_message=f'message_t{t}_{agent}', reasoning='')),
                    model='dry', backend='dry')


class ResearchValidity(unittest.TestCase):
    def test_economics(self):
        self.assertEqual(payoffs([6, 6, 6]), (12, [36, 36, 36]))
        self.assertEqual(payoffs([4, 4, 4]), (18, [48, 48, 48]))
        self.assertEqual(max(payoffs([q, 6, 6])[1][0] for q in range(13)), 36)
        self.assertEqual(max(sum(payoffs([a, b, c])[1]) for a in range(13)
                             for b in range(13) for c in range(13)), 144)
        self.assertEqual(payoffs([12, 12, 12]), (0, [-72, -72, -72]))

    def test_strict_actions(self):
        for q in [True, False, -1, 13, 5.5, '6', None]:
            self.assertIsNone(parse(json.dumps(dict(quantity=q, private_message=''))))
        self.assertEqual(parse('{"quantity":6,"private_message":""}')['quantity'], 6)

    def test_message_timing_and_privacy(self):
        cache = RecordingCache()
        with contextlib.redirect_stdout(io.StringIO()):
            rows, gt = run_game(24020, 'private', cache, 'dry', 'dry', 3)
        for t, agent, system, prompt in cache.prompts:
            self.assertNotIn(f'message_t{t}_', prompt)
            if agent in gt['assigned_pair']:
                self.assertIn('private message box', system)
                if t:
                    self.assertIn(f'message_t{t-1}_', prompt)
            else:
                self.assertNotIn('message_t', prompt)
        self.assertFalse(any('private_message' in a for r in rows for a in r['agents']))
        self.assertEqual(len(gt['private_chat']), 6)
        other = RecordingCache()
        with contextlib.redirect_stdout(io.StringIO()):
            _, control = run_game(24020, 'none', other, 'dry', 'dry', 3)
        self.assertEqual(control['assigned_pair'], gt['assigned_pair'])
        self.assertEqual(control['private_chat'], [])
        self.assertTrue(all('message_t' not in p for _, _, _, p in other.prompts))

    def test_group_folds_and_identifiability(self):
        data = json.loads(Path('results/s01_digits.json').read_text())
        for ds in data.values():
            all_test = []
            for fold in ds['folds']:
                self.assertFalse(set(fold['train']) & set(fold['test']))
                all_test.extend(fold['test'])
            self.assertEqual(len(all_test), len(set(all_test)))
            self.assertEqual(len(all_test), ds['runs'])
            self.assertEqual(ds['exact_price_digit_residual_max'], 0)

    def test_predictive_positive_control(self):
        # Known nonlinear digit mechanism: a flexible digit term must recover it
        # on independent synthetic observations, whereas raw price cannot.
        rng = np.random.default_rng(94)
        source = rng.integers(6, 25, 2000)
        target = 3 * (source % 2) + rng.normal(0, .1, len(source))
        raw = source[:, None]
        aug = np.column_stack([raw, np.eye(10)[source % 10]])
        errs = []
        for x in [raw, aug]:
            fit = make_pipeline(StandardScaler(), Ridge(alpha=10)).fit(x[:1500], target[:1500])
            errs.append(np.mean((target[1500:] - fit.predict(x[1500:]))**2))
        self.assertGreater(errs[0] - errs[1], 1)
        self.assertLess(errs[1], .03)


if __name__ == '__main__':
    unittest.main()
