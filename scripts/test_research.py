"""Small validity checks for simultaneous decisions, economics and held-out data."""
import contextlib
import io
import json
from pathlib import Path
import unittest
import tempfile

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from sim.cournot import parse, payoffs, run_game, benchmarks
from sim.common import Cache
from scripts.s02_analyze import validate_calls


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
        eq = benchmarks()['pair_as_single_actor_equilibria']
        self.assertIn(dict(pair_total=8, outsider_quantity=8, pair_profit_total=64, price=14), eq)
        self.assertEqual(len(eq), 3)
        self.assertTrue(all(e['pair_profit_total'] <= 72 for e in eq))
        self.assertEqual(payoffs([4, 4, 8]), (14, [32, 32, 64]))

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

    def test_missing_or_wrong_model_provenance(self):
        cache = RecordingCache()
        with contextlib.redirect_stdout(io.StringIO()):
            _, gt = run_game(24020, 'none', cache, 'dry', 'dry', 1)
        cfg = dict(rounds=1, dry=True, model='dry', backend='dry')
        validate_calls(gt, cfg)
        calls = gt['call_provenance']
        gt['call_provenance'] = []
        with self.assertRaises(AssertionError):
            validate_calls(gt, cfg)
        gt['call_provenance'] = calls
        cfg.update(dry=False, model='qwen-3.6-35b', backend='aqueduct')
        with self.assertRaises(AssertionError):
            validate_calls(gt, cfg)
        cache.dry = False
        with self.assertRaisesRegex(RuntimeError, 'model/backend mismatch'):
            run_game(24020, 'none', cache, 'qwen-3.6-35b', 'aqueduct', 1)

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

    def test_torn_cache_recovery(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as folder:
            path = Path(folder) / 'responses.jsonl'
            valid = json.dumps(dict(key='paid', response=dict(text='saved'))).encode() + b'\n'
            path.write_bytes(valid + b'{"key":"torn')
            cache = Cache(path, dry=True)
            self.assertEqual(cache.entries['paid']['text'], 'saved')
            self.assertEqual(path.read_bytes(), valid)
            self.assertEqual(len(list(Path(folder).glob('*.torn.*'))), 1)
            path.write_bytes(b'broken\n' + valid)
            with self.assertRaisesRegex(ValueError, 'Damaged cache'):
                Cache(path, dry=True)


if __name__ == '__main__':
    unittest.main()
