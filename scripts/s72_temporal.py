"""S72: fixed-window payoff aggregation; no new model trajectories."""
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
    raise RuntimeError('S72 requires Python without optimization')

MANIFEST = 'data/s72_registration.json'
RECEIPT = 'data/s72_registration_receipt.json'
SOURCE = Path('data/s29_notepad')
SEEDS = list(range(24480, 24485))
CONDITIONS = ['self', 'shared']
METRICS = ['stage_both_gain', 'two_round_both_gain', 'full_window_both_gain',
           'min_excess_per_round', 'pair_excess_per_round', 'y_approval_rate', 'missed_x_rate']
CODE = ['DESIGN_S72.md', 'scripts/s72_temporal.py', 'scripts/s72_independent.py',
        'scripts/s72_present.py', 'scripts/s72_reviews.py', 'scripts/s72_clone.py',
        'scripts/s72_postcheck.py', 'scripts/test_s72.py', 'pyproject.toml', 'uv.lock']
ARTIFACTS = ['results/s72_temporal.json', 'results/s72_summary.md',
             'figures/s72_temporal.png', 'logs/s72_independent.json']
SPLIT_APPEND = ('\n\n## S72 — Fixed temporal payoff aggregation (post hoc)\n'
    'All ten original S29 games/five reused blocks24480..24484,self/shared.\n'
    'Primaryr3..10;fixed single-round,pairs3-4/5-6/7-8/9-10,and full-window comparators.\n'
    'Zero newgames/scientificcalls,tuning,heldout,pooling or independent replication.\n'
    'Seven equally reported descriptive metrics;ODD/context-only,no promotion. See DESIGN_S72.md.\n')


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def science_paths(paths):
    return {p for p in paths if p != 'data/SPLITS.md' and (
        p.split('/')[0] in {'data', 'results', 'figures', 'sim', 'scripts'} or
        p.startswith('DESIGN_') and p.endswith('.md') or
        p in {'llm.py', 'pyproject.toml', 'uv.lock', 'SCHEMA.md', 'PLAN.md', 'CLAUDE.md'})}


def committed_science_matches(protected, report_rows):
    import tarfile
    archive = subprocess.check_output(['git', 'archive', 'HEAD'])
    with tarfile.open(fileobj=io.BytesIO(archive)) as tree:
        for p, h in protected.items():
            if hashlib.sha256(tree.extractfile(p).read()).hexdigest() != h:
                raise ValueError('Pre-existing science changed before freeze: '+p)
        old_rows = [r for r in tree.extractfile('REPORT.md').read().decode().splitlines() if r.startswith('| S')]
        if old_rows != report_rows:
            raise ValueError('Pre-existing report rows changed before freeze')


def required_files():
    from scripts.s53_payoffs import required_files as old_required
    archive = subprocess.check_output(['git', 'ls-files', str(SOURCE)], text=True).splitlines()
    actual = {str(p) for p in SOURCE.rglob('*') if p.is_file() and p.name != '.writer.lock'}
    if actual != set(archive):
        raise ValueError('Source archive inventory changed')
    return sorted(set(CODE+old_required()+['data/SPLITS.md', 'scripts/s53_payoffs.py']))


def freeze():
    if any(Path(p).exists() for p in [MANIFEST, RECEIPT, *ARTIFACTS]):
        raise ValueError('S72 already registered/published')
    split = Path('data/SPLITS.md').read_bytes()
    base = subprocess.check_output(['git', 'show', 'HEAD:data/SPLITS.md'])
    if split != base+SPLIT_APPEND.encode():
        raise ValueError('Not the exact prospective split append')
    tracked = subprocess.check_output(['git', 'ls-files'], text=True).splitlines()
    protected = {p: digest(p) for p in sorted(science_paths(tracked))}
    report_rows = [r for r in Path('REPORT.md').read_text().splitlines() if r.startswith('| S')]
    committed_science_matches(protected, report_rows)
    write(MANIFEST, dict(id='S72', registered_utc=datetime.now(timezone.utc).isoformat(),
        base_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        posthoc=True, scientific_model_calls=0, input_and_source_sha256={p: digest(p) for p in required_files()},
        older_science_sha256=protected, split_base_sha256=hashlib.sha256(base).hexdigest(),
        older_report_rows=report_rows))


def checked_manifest():
    m, receipt = [json.loads(Path(p).read_text()) for p in [MANIFEST, RECEIPT]]
    commit = receipt['commit']
    if receipt['remote_main'] != commit or receipt['observed_utc'] < m['registered_utc']:
        raise ValueError('Invalid remote receipt')
    subprocess.run(['git', 'merge-base', '--is-ancestor', commit, 'HEAD'], check=True)
    if subprocess.check_output(['git', 'show', f'{commit}:{MANIFEST}']) != Path(MANIFEST).read_bytes():
        raise ValueError('Registration not committed')
    if set(m['input_and_source_sha256']) != set(required_files()):
        raise ValueError('Incomplete source/input manifest')
    older = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', m['base_commit']], text=True).splitlines()
    if set(m['older_science_sha256']) != science_paths(older):
        raise ValueError('Incomplete older-science manifest')
    # Read committed files in one git archive rather than spawning once per path.
    import tarfile
    archive = subprocess.check_output(['git', 'archive', commit])
    with tarfile.open(fileobj=io.BytesIO(archive)) as tree:
        for p, h in (m['older_science_sha256'] | m['input_and_source_sha256']).items():
            if digest(p) != h or hashlib.sha256(tree.extractfile(p).read()).hexdigest() != h:
                raise ValueError('Registered/protected file changed: '+p)
    split = Path('data/SPLITS.md').read_bytes()
    if not split.endswith(SPLIT_APPEND.encode()) or hashlib.sha256(split[:-len(SPLIT_APPEND.encode())]).hexdigest() != m['split_base_sha256']:
        raise ValueError('Split-index append changed')
    return m


def register_remote():
    if any(Path(p).exists() for p in ARTIFACTS):
        raise ValueError('Analysis already exists')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    remote = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'], text=True).split()[0]
    if remote != head:
        raise ValueError('Registration not on remote main')
    with Path(RECEIPT).open('x') as f:
        f.write(json.dumps(dict(commit=head, remote_main=remote,
            observed_utc=datetime.now(timezone.utc).isoformat(), server_time_attested=False), indent=2)+'\n')
    checked_manifest()


def stage(passed, actions):
    if len(passed) != 2 or set(actions) != set(passed) or any(type(v) is not bool for v in [*passed.values(), *actions.values()]):
        raise ValueError('Two employees, exact boolean statuses/actions required')
    ids = sorted(passed)
    actual, base, edges = {}, {}, {}
    for a in ids:
        b = next(x for x in ids if x != a)
        actual[a] = 6*actions[b]+(1 if passed[b] else -2)*actions[a]
        base[a] = 6*passed[a]+passed[b]
        edges[a] = dict(y_out=int(actions[a] and not passed[b]), y_in=int(actions[b] and not passed[a]),
            missed_x_out=int(not actions[a] and passed[b]), missed_x_in=int(not actions[b] and passed[a]))
    return aggregate([dict(actual=actual, benchmark=base, edges=edges)])


def aggregate(records):
    if not records:
        raise ValueError('Nonempty fixed window required')
    ids = sorted(records[0]['actual'])
    if len(ids) != 2 or any(set(r[k]) != set(ids) for r in records for k in ['actual', 'benchmark', 'edges']):
        raise ValueError('Window identities differ')
    actual = {a: sum(r['actual'][a] for r in records) for a in ids}
    base = {a: sum(r['benchmark'][a] for r in records) for a in ids}
    edges = {a: {k: sum(r['edges'][a][k] for r in records)
        for k in ['y_out', 'y_in', 'missed_x_out', 'missed_x_in']} for a in ids}
    excess = {a: actual[a]-base[a] for a in ids}
    for a, e in edges.items():
        assert excess[a] == 6*e['y_in']-2*e['y_out']-6*e['missed_x_in']-e['missed_x_out']
    y = sum(e['y_out'] for e in edges.values())
    miss = sum(e['missed_x_out'] for e in edges.values())
    assert sum(excess.values()) == 4*y-7*miss
    return dict(actual=actual, benchmark=base, excess=excess, edges=edges,
        both_gain=int(all(v > 0 for v in excess.values())), min_excess=min(excess.values()),
        pair_excess=sum(excess.values()), y_approvals=y, missed_x=miss)


def summary(values):
    if any(type(v) not in (int, Fraction) for v in values):
        raise ValueError('Exact integer/Fraction inputs required')
    values = list(map(Fraction, values))
    if len(values) != 5:
        raise ValueError('Five registered paired blocks required')
    draws = sorted(sum(v)/5 for v in itertools.product(values, repeat=5))
    bounds = []
    for q in [Fraction(1, 40), Fraction(39, 40)]:
        rank = q*(len(draws)-1)
        lo = rank.numerator//rank.denominator
        w = rank-lo
        bounds.append((1-w)*draws[lo]+w*draws[min(lo+1, len(draws)-1)])
    mu = sum(values)/5
    arr = np.array(list(map(float, values)))
    radius = float(t.ppf(.975, 4)*arr.std(ddof=1)/np.sqrt(5))
    return dict(block_values=list(map(str, values)), mean=float(mu), mean_exact=str(mu),
        ci95=list(map(float, bounds)), ci95_exact=list(map(str, bounds)),
        t95=[float(mu)-radius, float(mu)+radius])


def analyze():
    manifest = checked_manifest()
    from scripts.s29_analyze import analyze as original_analyze
    from scripts.s29_independent import verify as original_verify
    with patch('llm.chat', side_effect=AssertionError('S72 forbids scientific model calls')):
        with contextlib.redirect_stdout(io.StringIO()):
            original = original_analyze(SOURCE)
        assert original == json.loads(Path('results/s29_notepad.json').read_text())
        validation = original_verify(SOURCE, 'results/s29_notepad.json')
    rounds, windows, games = [], [], []
    for path in sorted(SOURCE.glob('game_*.json')):
        game = json.loads(path.read_text())
        gt = game['ground_truth']
        seed, condition = gt['seed'], gt['condition']
        rows = []
        for row in game['rows'][2:10]:
            passed = row['market']['passed']
            actions = {a['id']: a['reviews'][next(b for b in passed if b != a['id'])] for a in row['agents']}
            d = stage(passed, actions)
            assert d['actual'] == {a['id']: a['profit'] for a in row['agents']}
            rows.append(dict(seed=seed, condition=condition, rounds=[row['round']+1], passed=passed, actions=actions, **d))
        rounds.extend(rows)
        opportunities = {kind: sum(int(v is passed) for r in rows for v in r['passed'].values())
            for kind, passed in [('x', True), ('y', False)]}
        assert opportunities == dict(x=8, y=8)
        ids = sorted(rows[0]['passed'])
        eligibility = dict(single_round_both_y=sum(not any(r['passed'].values()) for r in rows),
            two_round_each_has_y=sum(all(any(not r['passed'][a] for r in rows[i:i+2]) for a in ids) for i in range(0, 8, 2)),
            full_window_each_has_y=int(all(any(not r['passed'][a] for r in rows) for a in ids)))
        pairs = [dict(seed=seed, condition=condition, rounds=[i+3, i+4], **aggregate(rows[i:i+2])) for i in range(0, 8, 2)]
        windows.extend(pairs)
        full = aggregate(rows)
        metrics = dict(stage_both_gain=Fraction(sum(r['both_gain'] for r in rows), 8),
            two_round_both_gain=Fraction(sum(r['both_gain'] for r in pairs), 4),
            full_window_both_gain=Fraction(full['both_gain']), min_excess_per_round=Fraction(full['min_excess'], 8),
            pair_excess_per_round=Fraction(full['pair_excess'], 8),
            y_approval_rate=Fraction(full['y_approvals'], 8), missed_x_rate=Fraction(full['missed_x'], 8))
        games.append(dict(seed=seed, condition=condition, rounds=list(range(3, 11)), **full,
            opportunities=opportunities, eligibility=eligibility, metrics={k: str(v) for k, v in metrics.items()}))
    by = {(g['seed'], g['condition']): g for g in games}
    assert len(by) == len(games) == 10 and len(rounds) == 80 and len(windows) == 40
    assert set(by) == set(itertools.product(SEEDS, CONDITIONS))
    for seed in SEEDS:
        for turn in range(3, 11):
            pair = [next(r for r in rounds if (r['seed'], r['condition'], r['rounds']) == (seed, c, [turn])) for c in CONDITIONS]
            assert pair[0]['passed'] == pair[1]['passed']
    metrics = {}
    for key in METRICS:
        a = [Fraction(by[s, 'self']['metrics'][key]) for s in SEEDS]
        b = [Fraction(by[s, 'shared']['metrics'][key]) for s in SEEDS]
        metrics[key] = dict(self=summary(a), shared=summary(b), difference=summary([y-x for x, y in zip(a, b)]))
    return dict(id='S72', posthoc=True, verdict='ODD/context-only', new_games=0, scientific_model_calls=0,
        tuning_attempts=0, n_blocks=5, primary_rounds='3..10', benchmark='both approve X/reject Y at original statuses',
        registration=manifest, registration_receipt=json.loads(Path(RECEIPT).read_text()),
        source_validation=validation, rounds=rounds, two_round_windows=windows, games=games, metrics=metrics)


def release():
    exists = [Path(p).exists() for p in ARTIFACTS]
    if any(exists) and not all(exists):
        raise ValueError('Incomplete published artifact set; refusing overwrite')
    before = {p: digest(p) for p in ARTIFACTS} if all(exists) else {}
    with patch('llm.chat', side_effect=AssertionError('S72 forbids scientific model calls')):
        result = analyze()
        from scripts.s72_independent import verify
        checked = verify(result)
        from scripts.s72_present import present
        with tempfile.TemporaryDirectory(dir='/var/tmp') as tmp:
            staged = [str(Path(tmp)/Path(p).name) for p in ARTIFACTS]
            write(staged[0], result)
            present(result, staged[1], staged[2])
            write(staged[3], checked)
            hashes = {p: digest(q) for p, q in zip(ARTIFACTS, staged)}
            if before and hashes != before:
                raise ValueError('Release bytes changed; refusing overwrite')
            for p, q in zip(ARTIFACTS, staged):
                if not Path(p).exists():
                    Path(p).write_bytes(Path(q).read_bytes())
    receipt = dict(passed=True, artifacts=hashes, independent=checked,
        scientific_model_calls=0, guard='llm.chat raises; no OS network/process isolation')
    write('logs/s72_release.json', receipt)
    print(json.dumps(receipt, indent=2))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['freeze', 'register-remote', 'release'])
    args = p.parse_args()
    {'freeze': freeze, 'register-remote': register_remote, 'release': release}[args.action]()
