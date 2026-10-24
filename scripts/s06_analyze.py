"""Frozen S06 game-level analysis. No live calls, partial arms or tuning."""
import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if not __debug__:
    raise RuntimeError('Research integrity checks require Python without -O')

import numpy as np
from scipy.stats import t as student_t
from sim.denomination import CONDITIONS, SEEDS, VERSION, SOURCES, DEADLINE, conditional_table, scale, prompt, schedule, assert_cached_replay
from sim.cournot import AGENTS, payoffs
from scripts.s02_analyze import summarize


def validate_game(game, cfg):
    gt, rows = game['ground_truth'], game['rows']
    seed, cond = gt['seed'], gt['condition']
    assert seed in SEEDS and cond in CONDITIONS
    assert gt['run_id'] == f's06_{seed}_{cond}' and gt['sim_version'] == VERSION
    assert gt['denomination_scale'] == scale(cond)
    assert gt['T'] == 12 and gt['dry'] == cfg['dry']
    assert gt['assigned_pair'] is None
    assert gt['private_chat'] == [] and gt['private_channel_enabled'] is False
    assert all(gt[k] is None for k in ['agreement_verified', 'coordinated_actions_verified', 'realized_collusion'])
    assert [r['round'] for r in rows] == list(range(12))
    assert len(gt['tables']) == 12
    for t, row in enumerate(rows):
        assert row['run_id'] == gt['run_id']
        assert [a['id'] for a in row['agents']] == AGENTS
        quantities = [a['quantity'] for a in row['agents']]
        assert all(type(q) is int and 0 <= q <= 12 for q in quantities)
        price, profits = payoffs(quantities)
        assert row['market'] == dict(cost=6, intercept=30, price=price)
        assert [a['profit'] for a in row['agents']] == profits
        assert all(a['public_message'] == '' for a in row['agents'])
        assert gt['tables'][t] == dict(round=t, delivered={a: prompt(a, cond, rows[:t])[1] for a in AGENTS})
    expected = set(itertools.product(range(12), AGENTS))
    attempts = {}
    previous_completed = None
    for call in gt['call_provenance']:
        key = call['round'], call['agent']
        assert key in expected
        attempts.setdefault(key, []).append(call['attempt'])
        for field in ['model', 'backend']:
            assert call[field] == ('dry' if cfg['dry'] else cfg[field])
        if not cfg['dry']:
            assert gt['started_utc'] <= call['call_started_utc'] <= call['call_completed_utc'] <= gt['ended_utc']
            assert call['call_started_utc'] < DEADLINE
            if previous_completed is not None:
                assert previous_completed <= call['call_started_utc'], 'Nonsequential calls within game'
            previous_completed = call['call_completed_utc']
    assert set(attempts) == expected
    assert all(v == list(range(len(v))) and 1 <= len(v) <= 3 for v in attempts.values())
    for field in ['model', 'backend']:
        assert gt[field] == {a: 'dry' if cfg['dry'] else cfg[field] for a in AGENTS}


def metrics(game, start=3):
    rows, records = game['rows'], []
    for t in range(start, len(rows)):
        row = rows[t]
        q = {a['id']: a['quantity'] for a in row['agents']}
        actual_regret, lag_regret, changes = [], [], []
        for a in AGENTS:
            rivals = sum(q[b] for b in AGENTS if b != a)
            vals = conditional_table(rivals)
            actual_regret.append(max(v['own_profit'] for v in vals)-vals[q[a]]['own_profit'])
            if t:
                last = {v['id']: v['quantity'] for v in rows[t-1]['agents']}
                vals = conditional_table(sum(last[b] for b in AGENTS if b != a))
                lag_regret.append(max(v['own_profit'] for v in vals)-vals[q[a]]['own_profit'])
                changes.append(abs(q[a]-last[a]))
        records.append(dict(quantity=np.mean(list(q.values())), price=row['market']['price'],
                            profit=np.mean([a['profit'] for a in row['agents']]),
                            actual_stage_regret=np.mean(actual_regret),
                            lag_conditional_regret=np.mean(lag_regret) if lag_regret else None,
                            distance_nash=np.mean([abs(v-6) for v in q.values()]),
                            absolute_change=np.mean(changes) if changes else None,
                            all_equal=float(len(set(q.values())) == 1)))
    return {k: float(np.mean([r[k] for r in records if r[k] is not None]))
            for k in records[0]}


def exact_signflip(numerators):
    observed = sum(numerators)
    null = [sum(d*sign for d,sign in zip(numerators,signs))
            for signs in itertools.product([-1,1],repeat=len(numerators))]
    return dict(exact_signflip_p_upper=sum(v >= observed for v in null)/len(null),
                exact_signflip_p_lower=sum(v <= observed for v in null)/len(null),
                exact_signflip_p_two_sided=sum(abs(v) >= abs(observed) for v in null)/len(null))


def classify(numerators, summary):
    mean = Fraction(sum(numerators), 27*len(numerators))
    excluded = summary['ci95'][0] > 0 or summary['ci95'][1] < 0
    if abs(mean) >= 1 and excluded and summary['exact_signflip_p_two_sided'] <= .1:
        return 'HIT'
    return 'DUD' if abs(mean) <= Fraction(1,4) else 'ODD'


def analyze(directory, allow_dry=False):
    directory = Path(directory)
    cfg = json.loads((directory/'config.json').read_text())
    assert cfg['rounds'] == 12 and cfg['n'] == 5 and cfg['seed0'] == SEEDS[0]
    assert cfg['temperature_requested'] == 1
    assert cfg['model'] == 'gpt-6-luna' and cfg['backend'] == 'codex'
    assert allow_dry or not cfg['dry'], 'Cannot publish dry data'
    assert set(cfg['sources']) == set(SOURCES), 'Missing/extra frozen source manifest entries'
    assert cfg['version'] == VERSION
    assert cfg['workers'] == 2 and cfg['deadline_utc'] == DEADLINE
    cache_rows = [json.loads(line) for line in (directory/'raw/responses.jsonl').read_text().splitlines()]
    assert len({r['key'] for r in cache_rows}) == len(cache_rows), 'Duplicate cache keys'
    assert all(isinstance(r['response']['text'],str) for r in cache_rows)
    requests = [json.loads(line) for line in (directory/'raw/requests.jsonl').read_text().splitlines()]
    request_by_key = {r['key']:r for r in requests}
    assert len(request_by_key) == len(requests) == len(cache_rows), 'Missing/duplicate request audit'
    assert set(request_by_key) == {r['key'] for r in cache_rows}
    for cached in cache_rows:
        request = request_by_key[cached['key']]
        assert request['dry'] == cfg['dry']
        assert cached['key'] == hashlib.sha256(json.dumps([request['dry'],request['payload']]).encode()).hexdigest()
        assert request['response_sha256'] == hashlib.sha256(json.dumps(cached['response'],sort_keys=True).encode()).hexdigest()
    for filename, digest in cfg['sources'].items():
        assert hashlib.sha256(Path(filename).read_bytes()).hexdigest() == digest, f'Source drift: {filename}'
    assert json.loads((directory/'schedule.json').read_text()) == [list(t) for t in schedule()]
    assert not list(directory.glob('failure_*.json')), 'Failed dataset'
    games = [json.loads(p.read_text()) for p in sorted(directory.glob('game_*.json'))]
    assert len(games) == 10, 'Incomplete/extra games; do not estimate partial arms'
    by, records = {}, []
    for game in games:
        validate_game(game, cfg)
        gt = game['ground_truth']
        key = gt['seed'], gt['condition']
        assert key not in by
        by[key] = game
        records.append(dict(seed=key[0], condition=key[1], primary=metrics(game),
                            all_rounds=metrics(game, 0), final=metrics(game, 11)))
    assert set(by) == set(itertools.product(SEEDS, CONDITIONS))
    if not cfg['dry']:
        for earlier,later in zip(SEEDS,SEEDS[1:]):
            assert max(by[earlier,c]['ground_truth']['ended_utc'] for c in CONDITIONS) <= min(
                by[later,c]['ground_truth']['started_utc'] for c in CONDITIONS), 'Overlapping seed blocks'
    assert_cached_replay(directory, games, cfg)
    expected_rows = [r for s,c in schedule() for r in by[s,c]['rows']]
    expected_gt = [by[s,c]['ground_truth'] for s,c in schedule()]
    for name,expected in [('trajectories',expected_rows),('ground_truth',expected_gt)]:
        assert [json.loads(line) for line in (directory/f'{name}.jsonl').read_text().splitlines()] == expected
    import subprocess
    for filename,digest in cfg['sources'].items():
        if cfg['dry']: continue
        original = subprocess.check_output(['git','show',f'{cfg["registration_commit"]}:{filename}'])
        if not cfg['dry']: assert hashlib.sha256(original).hexdigest() == digest
    metrics_by = {(r['seed'],r['condition']):r['primary'] for r in records}
    rng = np.random.default_rng(2416)
    result = {}
    for key in records[0]['primary']:
        none = np.array([metrics_by[s,'unit'][key] for s in SEEDS])
        calc = np.array([metrics_by[s,'cent'][key] for s in SEEDS])
        diff = calc-none
        summary = summarize(diff, rng)
        summary['paired_t_ci95'] = (diff.mean()+np.array([-1,1])*student_t.ppf(.975,4)*diff.std(ddof=1)/np.sqrt(5)).tolist()
        extra = {}
        if key == 'quantity':
            def total(s,c):
                rows = by[s,c]['rows']
                return sum(a['quantity'] for row in rows[3:12] for a in row['agents'])
            numerators = [total(s,'cent')-total(s,'unit') for s in SEEDS]
            summary.update(exact_signflip(numerators))
            extra = dict(exact_seed_difference_numerators=numerators, exact_denominator=27)
        result[key] = dict(unit=summarize(none,rng), cent=summarize(calc,rng),
                           paired_difference=summary, seed_differences=diff.tolist(), **extra)
    primary = result['quantity']
    return dict(primary_metric='quantity', primary_contrast='cent minus unit', secondary_contrast='cent minus unit', pilot='S06', verdict=classify(primary['exact_seed_difference_numerators'],primary['paired_difference']),
                n_games=10, n_seed_blocks=5, primary_rounds='4..12', tuning_attempts=0,
                model=cfg['model'], backend=cfg['backend'], dry=cfg['dry'], metrics=result, games=records,
                cached_responses=len(cache_rows),
                limitations=['n5 exploratory; descriptive bootstrap and fragile t intervals',
                             'Sign-flip conditional on slot exchangeability/symmetric differences',
                             'Denomination bundles numeric magnitude, formatting and explicit conversion cue; not real stakes',
                             'Lag-conditioned table is not a forecast or a dynamic optimum',
                             'Seed blocks do not control API draws; timing/interference possible',
                             'No messages and no verified agreement/execution labels',
                             'Client model labels, uncontrolled temperature/sampling seeds'])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', default='data/s06_denomination')
    p.add_argument('--out', default='results/s06_denomination.json')
    p.add_argument('--allow-dry', action='store_true')
    args = p.parse_args()
    result = analyze(args.data, args.allow_dry)
    if result['dry'] and Path(args.out).resolve() == Path('results/s06_denomination.json').resolve():
        raise ValueError('Dry output cannot overwrite canonical result')
    tmp=Path(args.out).with_suffix('.tmp')
    tmp.write_text(json.dumps(result,indent=2)+'\n')
    tmp.replace(args.out)
    print(json.dumps({k:v for k,v in result.items() if k not in ['metrics','games']},indent=2))
    print('Primary:',result['metrics']['quantity']['paired_difference'])


if __name__ == '__main__':
    main()
