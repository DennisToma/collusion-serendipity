"""Frozen S01 cross-fitted price prediction and exact-price identifiability check."""
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def interval(values, seed=2401):
    x = np.asarray(values, float)
    rng = np.random.default_rng(seed)
    samples = x[rng.integers(len(x), size=(10000, len(x)))].mean(axis=1)
    return dict(mean=float(x.mean()), ci95=np.quantile(samples, [.025, .975]).tolist(), n=len(x))


def analyze(dataset):
    path = Path('data/s01_prices') / dataset
    rows = [json.loads(x) for x in (path / 'trajectories.jsonl').read_text().splitlines()]
    meta = {x['run_id']: x for x in map(json.loads, (path / 'assignments.jsonl').read_text().splitlines())}
    games = {}
    for row in rows:
        games.setdefault(row['run_id'], []).append(row)
    for rid, game in games.items():
        game.sort(key=lambda r: r['round'])
        assert len(game) == meta[rid]['T'] == 20
        assert [r['round'] for r in game] == list(range(20))
    assert set(games) == set(meta), 'Incomplete input snapshot'
    agents = ['A', 'B', 'C', 'D']
    X, Z, y, keys = [], [], [], []
    prices_seen = []
    for rid, game in sorted(games.items()):
        ps = np.array([[next(a['price'] for a in row['agents'] if a['id'] == aid)
                        for aid in agents] for row in game])
        prices_seen.extend(ps.ravel().tolist())
        for t in range(1, len(game) - 1):
            for source, target in itertools.permutations(range(4), 2):
                rest = [i for i in range(4) if i not in (source, target)]
                features = [ps[t, source], ps[t, target], ps[t-1, source], ps[t-1, target],
                            *sorted(ps[t, rest]), *sorted(ps[t-1, rest]),
                            game[t]['market']['cost'], int(game[t]['market']['demand_shock'] == 'high')]
                digit = np.eye(10)[int(ps[t, source]) % 10]
                X.append(features)
                Z.append([*features, *digit])
                y.append(ps[t+1, target] - ps[t, target])
                keys.append((rid, tuple(sorted([agents[source], agents[target]]))))
    X, Z, y = np.array(X), np.array(Z), np.array(y)
    rids = np.array([k[0] for k in keys])
    losses = np.empty((len(y), 2))
    folds = []
    unique = np.array(sorted(games))
    for fold, (itrain, itest) in enumerate(KFold(5, shuffle=True, random_state=2401).split(unique)):
        train = np.isin(rids, unique[itrain])
        test = np.isin(rids, unique[itest])
        assert not set(rids[train]) & set(rids[test])
        folds.append(dict(fold=fold, train=unique[itrain].tolist(), test=unique[itest].tolist()))
        for j, features in enumerate([X, Z]):
            model = make_pipeline(StandardScaler(), Ridge(alpha=10))
            model.fit(features[train], y[train])
            losses[test, j] = (y[test] - model.predict(features[test])) ** 2
    pair_values = {}
    for k, gain in zip(keys, losses[:, 0] - losses[:, 1]):
        pair_values.setdefault(k, []).append(float(gain))
    records = []
    for rid in sorted(games):
        m = meta[rid]
        pair = tuple(sorted(m['assigned_pair'] or (
            sorted(itertools.combinations(agents, 2))[
                int(hashlib.sha256(rid.encode()).hexdigest()[:8], 16) % 6])))
        gains = {''.join(p): float(np.mean(vals)) for (r, p), vals in pair_values.items() if r == rid}
        chosen = gains[''.join(pair)]
        other = np.mean([v for p, v in gains.items() if p != ''.join(pair)])
        records.append(dict(run_id=rid, condition=m['condition'], pair=''.join(pair),
                            gain=chosen, other_gain=float(other), within_contrast=float(chosen-other),
                            baseline_mse=float(losses[rids == rid, 0].mean()),
                            augmented_mse=float(losses[rids == rid, 1].mean())))
    channel = [r for r in records if r['condition'] in ['C', 'D']]
    control = [r for r in records if r['condition'] in ['A', 'B']]
    # Full-price indicator span contains digit indicators for EVERY permitted price.
    grid = np.arange(6, 25)
    exact = np.eye(len(grid))
    digit = np.eye(10)[grid % 10]
    residual = digit - exact @ np.linalg.lstsq(exact, digit, rcond=None)[0]
    residual_max = float(np.abs(residual).max())
    assert residual_max < 1e-12
    result = dict(dataset=dataset, runs=len(games), excluded_runs=0, rounds=len(rows),
                  observations=len(y), noninteger_prices=sum(p != int(p) for p in prices_seen),
                  unique_prices=sorted(set(prices_seen)), alpha=10, tuning_attempts=0,
                  primary_within_channel=interval([r['within_contrast'] for r in channel]),
                  channel_gain=interval([r['gain'] for r in channel]),
                  control_gain=interval([r['gain'] for r in control]),
                  exact_price_digit_residual_max=residual_max, run_results=records, folds=folds,
                  verdict='DUD for an identifiable digit side channel; linear prediction diagnostic only')
    return result


def main():
    out = {name: analyze(name) for name in ['llm_v1', 'llm_ds_p2']}
    Path('results/s01_digits.json').write_text(json.dumps(out, indent=2) + '\n')
    for name, r in out.items():
        print(name, json.dumps({k: v for k, v in r.items() if k not in ['run_results', 'folds']}))


if __name__ == '__main__':
    main()
