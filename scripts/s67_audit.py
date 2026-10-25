"""Post-hoc settlement-aware S65 audit. No new seller/auditor trajectories."""
import argparse
import contextlib
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import io
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy.stats import t

if not __debug__:
    raise RuntimeError('S67 integrity checks require Python without optimization')

MANIFEST = 'data/s67_registration.json'
RECEIPT = 'data/s67_registration_receipt.json'
RESULT = 'results/s67_incentives.json'
SOURCE = Path('data/s65_bonus_pooling')
CONDITIONS = ['individual', 'pooled']
SEEDS = list(range(25340, 25345))
METRICS = ['y_approvals', 'missed_x', 'costly_y_approvals', 'profitable_y_rejections',
           'stage_regret', 'pair_shortfall', 'strict_pareto_rounds', 'organization_loss']
CODE = ['DESIGN_S67.md', 'scripts/s67_audit.py', 'scripts/s67_independent.py',
        'scripts/s67_present.py', 'scripts/s67_reviews.py', 'scripts/s67_clone.py',
        'scripts/s67_documents.py', 'scripts/s67_integrity.py',
        'scripts/test_s67.py', 'pyproject.toml', 'uv.lock']
ARTIFACTS = [RESULT, 'results/s67_summary.md', 'figures/s67_incentives.png',
             'logs/s67_independent.json']


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def required_files():
    cfg = json.loads((SOURCE / 'config.json').read_text())
    archive = subprocess.check_output(['git', 'ls-files', str(SOURCE)], text=True).splitlines()
    actual = {str(p) for p in SOURCE.rglob('*') if p.is_file() and p.name != '.writer.lock'}
    if actual != set(archive):
        raise ValueError('Archive inventory changed')
    return sorted(set(CODE + list(cfg['sources']) + archive + [
        'scripts/s65_independent.py', 'results/s65_bonus_pooling.json',
        'logs/s65_launch_preflight.json', 'data/SPLITS.md']))


def freeze():
    if any(Path(p).exists() for p in [MANIFEST, RECEIPT, *ARTIFACTS]):
        raise ValueError('S67 registration/results already exist')
    tracked = subprocess.check_output(['git', 'ls-files', 'data', 'results', 'figures',
                                       'sim', 'scripts', 'llm.py'], text=True).splitlines()
    protected = {p: digest(p) for p in tracked}
    write(MANIFEST, dict(id='S67', posthoc=True, scientific_model_calls=0,
        registered_utc=datetime.now(timezone.utc).isoformat(),
        input_and_source_sha256={p: digest(p) for p in required_files()},
        older_report_rows=[row for row in Path('REPORT.md').read_text().splitlines() if row.startswith('| S')],
        older_science_sha256=protected))


def checked_manifest():
    m = json.loads(Path(MANIFEST).read_text())
    receipt = json.loads(Path(RECEIPT).read_text())
    commit = receipt['commit']
    if receipt['remote_main'] != commit or receipt['observed_utc'] < m['registered_utc']:
        raise ValueError('Invalid remote registration receipt')
    subprocess.run(['git', 'merge-base', '--is-ancestor', commit, 'HEAD'], check=True)
    if set(m['input_and_source_sha256']) != set(required_files()):
        raise ValueError('Incomplete source/input manifest')
    if subprocess.check_output(['git', 'show', f'{commit}:{MANIFEST}']) != Path(MANIFEST).read_bytes():
        raise ValueError('Registration not committed')
    for p, h in (m['input_and_source_sha256'] | m['older_science_sha256']).items():
        if digest(p) != h:
            raise ValueError('Registered/protected file changed: ' + p)
        if hashlib.sha256(subprocess.check_output(['git', 'show', f'{commit}:{p}'])).hexdigest() != h:
            raise ValueError('Registered/protected file not committed: ' + p)
    return m


def register_remote():
    if Path(RESULT).exists():
        raise ValueError('Analysis already exists')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    remote = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'], text=True).split()[0]
    if head != remote:
        raise ValueError('Registration not pushed to remote main')
    receipt = dict(commit=head, remote_main=remote, server_time_attested=False,
                   observed_utc=datetime.now(timezone.utc).isoformat())
    with Path(RECEIPT).open('x') as f:
        f.write(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    checked_manifest()


def payoff(passed, actions, condition):
    if condition not in CONDITIONS or len(passed) != 2 or set(actions) != set(passed):
        raise ValueError('Requires two people and a registered settlement')
    if any(type(v) is not bool for v in [*passed.values(), *actions.values()]):
        raise ValueError('Strict booleans required')
    allocated = {a: 0.0 for a in passed}
    for reviewer in passed:
        author = next(a for a in passed if a != reviewer)
        if actions[reviewer]:
            allocated[reviewer] += 1 if passed[author] else -2
            allocated[author] += 6
    final = allocated.copy() if condition == 'individual' else {a: sum(allocated.values()) / 2 for a in passed}
    return allocated, final


def decompose(passed, actions, condition):
    allocated, final = payoff(passed, actions, condition)
    nash_actions = {a: (passed[next(b for b in passed if b != a)] if condition == 'individual' else True) for a in passed}
    nash = payoff(passed, nash_actions, condition)[1]
    regret = {}
    for a in passed:
        flipped = actions | {a: not actions[a]}
        regret[a] = max(0.0, payoff(passed, flipped, condition)[1][a] - final[a])
    y = sum(actions[a] and not passed[next(b for b in passed if b != a)] for a in passed)
    missed_x = sum(not actions[a] and passed[next(b for b in passed if b != a)] for a in passed)
    rejected_y = sum(not actions[a] and not passed[next(b for b in passed if b != a)] for a in passed)
    best = sum(payoff(passed, {a: True for a in passed}, condition)[1].values())
    strict = int(all(final[a] > nash[a] for a in passed))
    result = dict(allocated=allocated, final=final, nash_actions=nash_actions,
        nash=nash, regret_by_agent=regret, pair_max_bonus=best,
        y_approvals=y, missed_x=missed_x,
        costly_y_approvals=y if condition == 'individual' else 0,
        profitable_y_rejections=rejected_y if condition == 'pooled' else 0,
        stage_regret=sum(regret.values()), pair_shortfall=best - sum(final.values()),
        strict_pareto_rounds=strict, organization_loss=10 * y,
        y_opportunities=sum(not v for v in passed.values()),
        x_opportunities=sum(passed.values()), both_y=int(not any(passed.values())))
    expected_regret = 2*y + missed_x if condition == 'individual' else 2*rejected_y + 3.5*missed_x
    assert result['stage_regret'] == expected_regret
    assert result['pair_shortfall'] == 4*rejected_y + 7*missed_x
    assert sum(allocated.values()) == sum(final.values())
    assert strict == (int(not any(passed.values()) and all(actions.values())) if condition == 'individual' else 0)
    return result


def stage_table():
    rows = []
    for condition in CONDITIONS:
        for types in itertools.product([False, True], repeat=2):
            passed = dict(zip('AB', types))
            profiles = []
            for acts in itertools.product([False, True], repeat=2):
                actions = dict(zip('AB', acts))
                profiles.append(dict(condition=condition, passed=passed, actions=actions,
                                     **decompose(passed, actions, condition)))
            equilibria = [p['actions'] for p in profiles if p['stage_regret'] == 0]
            assert equilibria == [profiles[0]['nash_actions']]
            assert sum(p['pair_shortfall'] == 0 for p in profiles) == 1
            rows.extend(profiles)
    return rows


def summary(values):
    values = list(map(Fraction, values))
    assert len(values) == 5
    draws = sorted(sum(values[i] for i in ix)/5 for ix in itertools.product(range(5), repeat=5))
    bounds = []
    for q in [Fraction(1, 40), Fraction(39, 40)]:
        pos = q * (len(draws)-1)
        lo = pos.numerator // pos.denominator
        weight = pos-lo
        bounds.append(draws[lo]*(1-weight) + draws[min(lo+1, len(draws)-1)]*weight)
    mu = sum(values)/5
    arr = np.array(list(map(float, values)))
    radius = float(t.ppf(.975, 4)*arr.std(ddof=1)/np.sqrt(5))
    return dict(block_values=list(map(float, values)), mean=float(mu), mean_exact=str(mu),
        ci95=list(map(float, bounds)), ci95_exact=list(map(str, bounds)),
        t95=[float(mu)-radius, float(mu)+radius])


def analyze():
    manifest = checked_manifest()
    with patch('llm.chat', side_effect=AssertionError('S67 forbids scientific model calls')):
        from scripts.s65_analyze import analyze as source_analyze
        from scripts.s65_independent import verify as source_verify
        with contextlib.redirect_stdout(io.StringIO()):
            original = source_analyze(SOURCE)
        assert json.dumps(original, indent=2)+'\n' == Path('results/s65_bonus_pooling.json').read_text()
        source_validation = source_verify(SOURCE, 'results/s65_bonus_pooling.json')
    rows, games = [], []
    for p in sorted(SOURCE.glob('game_*.json')):
        game = json.loads(p.read_text())
        assert [r['round'] for r in game['rows']] == list(range(10))
        gt = game['ground_truth']
        seed, condition = gt['seed'], gt['condition']
        totals = {k: 0 for k in METRICS}
        opportunities = dict(y_opportunities=0, x_opportunities=0, both_y=0)
        for row in game['rows'][2:10]:
            passed = row['market']['passed']
            acts = {a['id']: a['reviews'][next(b for b in passed if b != a['id'])] for a in row['agents']}
            decomposition = decompose(passed, acts, condition)
            assert decomposition['final'] == {a['id']: a['profit'] for a in row['agents']}
            assert decomposition['organization_loss'] == row['market']['organization_loss']
            rows.append(dict(seed=seed, condition=condition, round=row['round']+1,
                             passed=passed, actions=acts, **decomposition))
            for k in METRICS:
                totals[k] += decomposition[k]
            for k in opportunities:
                opportunities[k] += decomposition[k]
        assert opportunities['y_opportunities'] == opportunities['x_opportunities'] == 8
        saved = next(g['primary'] for g in original['games'] if (g['seed'], g['condition']) == (seed, condition))
        assert totals['y_approvals']/8 == saved['pair_bad']
        games.append(dict(seed=seed, condition=condition, totals=totals, opportunities=opportunities))
    by = {(g['seed'], g['condition']): g for g in games}
    assert len(by) == len(games) == 10 and len(rows) == 80
    assert set(by) == set(itertools.product(SEEDS, CONDITIONS))
    for seed in SEEDS:
        for turn in range(3, 11):
            matched = [r['passed'] for r in rows if r['seed'] == seed and r['round'] == turn]
            assert len(matched) == 2 and matched[0] == matched[1]
    metrics = {}
    for k in METRICS:
        a = [Fraction(by[s, 'individual']['totals'][k])/8 for s in SEEDS]
        b = [Fraction(by[s, 'pooled']['totals'][k])/8 for s in SEEDS]
        metrics[k] = dict(individual=summary(a), pooled=summary(b),
                          difference=summary([y-x for x, y in zip(a, b)]))
    counts = {c: {k: sum(g['totals'].get(k, g['opportunities'].get(k, 0)) for g in games if g['condition'] == c)
                   for k in [*METRICS, 'y_opportunities', 'x_opportunities', 'both_y']} for c in CONDITIONS}
    return dict(id='S67', posthoc=True, verdict='ODD/context-only', new_games=0,
        scientific_model_calls=0, tuning_attempts=0, n_blocks=5, primary_rounds='3..10',
        registration_sha256=digest(MANIFEST), registration_receipt=json.loads(Path(RECEIPT).read_text()),
        source_validation=source_validation, source_calibration=original['calibration'],
        stage_table=stage_table(), rounds=rows, games=games, metrics=metrics, counts=counts)


def release():
    from scripts.s67_independent import verify
    from scripts.s67_present import present
    before = {p: digest(p) for p in ARTIFACTS if Path(p).exists()}
    if before and len(before) != len(ARTIFACTS):
        raise ValueError('Incomplete existing S67 publication')
    with patch('llm.chat', side_effect=AssertionError('S67 release forbids scientific calls')):
        result = analyze()
        checked = verify(result)
        with tempfile.TemporaryDirectory(prefix='s67_release_', dir='/var/tmp') as td:
            staged = [str(Path(td)/Path(p).name) for p in ARTIFACTS]
            write(staged[0], result)
            present(result, staged[1], staged[2])
            write(staged[3], checked)
            hashes = {p: digest(q) for p, q in zip(ARTIFACTS, staged)}
            if before and hashes != before:
                raise ValueError('S67 release bytes changed')
            for p, q in zip(ARTIFACTS, staged):
                if not Path(p).exists():
                    Path(p).write_bytes(Path(q).read_bytes())
    checked_manifest()
    receipt = dict(passed=True, llm_chat_entrypoint_blocked=True,
                   guard_scope='Actual replay transport uses llm.chat; no OS network/process isolation',
                   artifacts=hashes, independent=checked)
    write('logs/s67_release.json', receipt)
    print(json.dumps(receipt, indent=2))
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['freeze', 'register-remote', 'release'])
    args = parser.parse_args()
    {'freeze': freeze, 'register-remote': register_remote, 'release': release}[args.action]()
