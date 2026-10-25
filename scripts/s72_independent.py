"""Separate same-author raw/algebra/exact-statistics reconstruction for S72."""
from fractions import Fraction
import hashlib
import io
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tarfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy.stats import t

if not __debug__:
    raise RuntimeError('S72 verifier requires Python without optimization')

KEYS = ['stage_both_gain', 'two_round_both_gain', 'full_window_both_gain',
        'min_excess_per_round', 'pair_excess_per_round', 'y_approval_rate', 'missed_x_rate']


def exact_bounds(values):
    sample = sorted(sum(values[i] for i in ix)/5 for ix in itertools.product(range(5), repeat=5))
    bounds = []
    for rank in [Fraction(3124, 40), Fraction(39*3124, 40)]:
        i, rest = divmod(rank.numerator, rank.denominator)
        bounds.append((sample[i]*(rank.denominator-rest)+sample[i+1]*rest)/rank.denominator)
    return bounds


def reconstruct(statuses, decisions):
    """Sum directed reward transfers, independently of the main closed form."""
    ids = sorted(statuses[0])
    real = dict.fromkeys(ids, 0)
    base = dict.fromkeys(ids, 0)
    edges = {a: dict(y_in=0, y_out=0, missed_x_in=0, missed_x_out=0) for a in ids}
    for types, acts in zip(statuses, decisions):
        assert set(types) == set(acts) == set(ids)
        for reviewer in ids:
            author = next(a for a in ids if a != reviewer)
            if acts[reviewer]:
                real[reviewer] += 1
                real[author] += 6
                if not types[author]:
                    real[reviewer] -= 3
                    edges[reviewer]['y_out'] += 1
                    edges[author]['y_in'] += 1
            elif types[author]:
                edges[reviewer]['missed_x_out'] += 1
                edges[author]['missed_x_in'] += 1
            if types[author]:
                base[reviewer] += 1
                base[author] += 6
    delta = {a: real[a]-base[a] for a in ids}
    return dict(actual=real, benchmark=base, excess=delta, edges=edges,
        both_gain=int(min(delta.values()) > 0), min_excess=min(delta.values()),
        pair_excess=sum(delta.values()), y_approvals=sum(v['y_in'] for v in edges.values()),
        missed_x=sum(v['missed_x_in'] for v in edges.values()))


def verify_registration(result):
    # No archive outcomes may be read until the pushed source/input freeze binds.
    m = json.loads(Path('data/s72_registration.json').read_text())
    receipt = json.loads(Path('data/s72_registration_receipt.json').read_text())
    assert m['id'] == 'S72' and m['posthoc'] is True and m['scientific_model_calls'] == 0
    needed = {'data/SPLITS.md', 'data/s29_notepad/config.json', 'results/s29_notepad.json',
        'data/s29_notepad/raw/requests.jsonl', 'data/s29_notepad/raw/responses.jsonl',
        'scripts/s29_analyze.py', 'scripts/s29_independent.py', 'sim/notepad.py', 'DESIGN_S72.md',
        'scripts/s72_temporal.py', 'scripts/s72_independent.py', 'scripts/s72_present.py',
        'scripts/s72_reviews.py', 'scripts/s72_clone.py', 'scripts/s72_postcheck.py',
        'scripts/test_s72.py', 'pyproject.toml', 'uv.lock'}
    assert needed <= set(m['input_and_source_sha256'])
    assert result['registration'] == m and result['registration_receipt'] == receipt
    commit = receipt['commit']
    assert commit == receipt['remote_main'] and receipt['observed_utc'] >= m['registered_utc']
    subprocess.run(['git', 'merge-base', '--is-ancestor', commit, 'HEAD'], check=True)
    prior_paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', m['base_commit']], text=True).splitlines()
    expected = set()
    for p in prior_paths:
        if p == 'data/SPLITS.md':
            continue
        if (p.partition('/')[0] in ['data', 'results', 'figures', 'sim', 'scripts'] or
                p.startswith('DESIGN_') and p.endswith('.md') or
                p in ['llm.py', 'pyproject.toml', 'uv.lock', 'SCHEMA.md', 'PLAN.md', 'CLAUDE.md']):
            expected.add(p)
    assert set(m['older_science_sha256']) == expected
    original_config = json.loads(Path('data/s29_notepad/config.json').read_text())
    assert set(original_config['sources']) <= set(m['input_and_source_sha256'])
    tracked = set(subprocess.check_output(['git', 'ls-files', 'data/s29_notepad'], text=True).splitlines())
    actual = {str(p) for p in Path('data/s29_notepad').rglob('*') if p.is_file() and p.name != '.writer.lock'}
    assert actual == tracked and tracked <= set(m['input_and_source_sha256'])
    prior_split = subprocess.check_output(['git', 'show', f"{m['base_commit']}:data/SPLITS.md"])
    assert hashlib.sha256(prior_split).hexdigest() == m['split_base_sha256']
    split = Path('data/SPLITS.md').read_bytes()
    append = ('\n\n## S72 — Fixed temporal payoff aggregation (post hoc)\n'
        'All ten original S29 games/five reused blocks24480..24484,self/shared.\n'
        'Primaryr3..10;fixed single-round,pairs3-4/5-6/7-8/9-10,and full-window comparators.\n'
        'Zero newgames/scientificcalls,tuning,heldout,pooling or independent replication.\n'
        'Seven equally reported descriptive metrics;ODD/context-only,no promotion. See DESIGN_S72.md.\n').encode()
    assert split == prior_split+append
    with tarfile.open(fileobj=io.BytesIO(subprocess.check_output(['git', 'archive', commit]))) as tree:
        assert tree.extractfile('data/s72_registration.json').read() == Path('data/s72_registration.json').read_bytes()
        for p, expected in (m['older_science_sha256'] | m['input_and_source_sha256']).items():
            assert hashlib.sha256(Path(p).read_bytes()).hexdigest() == expected, p
            assert hashlib.sha256(tree.extractfile(p).read()).hexdigest() == expected, p


def verify(result=None):
    if result is None:
        result = json.loads(Path('results/s72_temporal.json').read_text())
    assert result['id'] == 'S72' and result['posthoc'] is True
    assert result['verdict'] == 'ODD/context-only'
    assert result['new_games'] == result['scientific_model_calls'] == result['tuning_attempts'] == 0
    assert result['n_blocks'] == 5 and result['primary_rounds'] == '3..10'
    assert set(result['metrics']) == set(KEYS)
    verify_registration(result)
    source = Path('data/s29_notepad')
    raw_rows = [json.loads(line) for line in (source/'raw/responses.jsonl').read_text().splitlines()]
    raw = {r['key']: r['response'] for r in raw_rows}
    assert len(raw) == len(raw_rows)
    accepted = {}
    for q in map(json.loads, (source/'raw/requests.jsonl').read_text().splitlines()):
        rid, ti, agent, attempt = q['payload'][5:9]
        obj = json.loads(raw[q['key']]['text'])
        # This specific completed archive contains no invalid retries.
        assert attempt == 0 and (rid, ti, agent) not in accepted
        assert set(obj) == {'reviews', 'reasoning', 'note'}
        accepted[rid, ti, agent] = obj
    assert len(accepted) == len(raw) == 200
    rounds, pairs, games, by = [], [], [], {}
    bindings = 0
    for path in sorted(source.glob('game_*.json')):
        g = json.loads(path.read_text())
        gt = g['ground_truth']
        seed, cond, rid = gt['seed'], gt['condition'], gt['run_id']
        assert [r['round'] for r in g['rows']] == list(range(10))
        types, acts, singles = [], [], []
        for row in g['rows']:
            statuses = row['market']['passed']
            decisions = {}
            for rec in row['agents']:
                a = rec['id']
                b = next(x for x in statuses if x != a)
                obj = accepted[rid, row['round'], a]
                assert obj['reviews'] == rec['reviews'] and set(obj['reviews']) == {b}
                assert type(obj['reviews'][b]) is bool
                assert [n['text'] for n in gt['notes_file'] if n['author'] == a and n['round'] == row['round']+1] == [obj['note']]
                assert [n['reasoning'] for n in gt['reasoning_notes'] if n['agent'] == a and n['round'] == row['round']] == [obj['reasoning']]
                decisions[a] = obj['reviews'][b]
                bindings += 1
            r = reconstruct([statuses], [decisions])
            assert r['actual'] == {a['id']: a['profit'] for a in row['agents']}
            assert row['market']['organization_loss'] == 10*r['y_approvals']
            if row['round'] < 2:
                continue
            types.append(statuses)
            acts.append(decisions)
            singles.append(r)
            rounds.append(dict(seed=seed, condition=cond, rounds=[row['round']+1], passed=statuses, actions=decisions, **r))
        twos = []
        for start in [0, 2, 4, 6]:
            w = reconstruct(types[start:start+2], acts[start:start+2])
            twos.append(w)
            pairs.append(dict(seed=seed, condition=cond, rounds=[start+3, start+4], **w))
        full = reconstruct(types, acts)
        x_count = sum(sum(t.values()) for t in types)
        y_count = 16-x_count
        assert x_count == y_count == 8
        identities = sorted(types[0])
        eligibility = dict(single_round_both_y=sum(sum(t.values()) == 0 for t in types),
            two_round_each_has_y=sum(all(sum(types[j][a] for j in [i, i+1]) < 2 for a in identities) for i in [0, 2, 4, 6]),
            full_window_each_has_y=int(all(sum(t[a] for t in types) < 8 for a in identities)))
        m = dict(stage_both_gain=Fraction(sum(w['both_gain'] for w in singles), 8),
            two_round_both_gain=Fraction(sum(w['both_gain'] for w in twos), 4),
            full_window_both_gain=Fraction(full['both_gain']), min_excess_per_round=Fraction(min(full['excess'].values()), 8),
            pair_excess_per_round=Fraction(sum(full['excess'].values()), 8),
            y_approval_rate=Fraction(sum(w['y_approvals'] for w in singles), 8),
            missed_x_rate=Fraction(sum(w['missed_x'] for w in singles), 8))
        games.append(dict(seed=seed, condition=cond, rounds=list(range(3, 11)), **full,
            opportunities=dict(x=x_count, y=y_count), eligibility=eligibility, metrics={k: str(v) for k, v in m.items()}))
        assert (seed, cond) not in by
        by[seed, cond] = m
    assert result['rounds'] == rounds and len(rounds) == 80
    assert result['two_round_windows'] == pairs and len(pairs) == 40
    assert result['games'] == games and len(games) == 10
    seeds = list(range(24480, 24485))
    assert set(by) == set(itertools.product(seeds, ['self', 'shared']))
    intervals = 0
    for key in KEYS:
        a = [by[s, 'self'][key] for s in seeds]
        b = [by[s, 'shared'][key] for s in seeds]
        assert set(result['metrics'][key]) == {'self', 'shared', 'difference'}
        for label, v in [('self', a), ('shared', b), ('difference', [y-x for x, y in zip(a, b)])]:
            saved = result['metrics'][key][label]
            assert set(saved) == {'block_values', 'mean', 'mean_exact', 'ci95', 'ci95_exact', 't95'}
            assert list(map(Fraction, saved['block_values'])) == v
            assert Fraction(saved['mean_exact']) == sum(v)/5
            assert list(map(Fraction, saved['ci95_exact'])) == exact_bounds(v)
            arr = np.array(list(map(float, v)))
            boots = [sum(arr[i] for i in indices)/5 for indices in itertools.product(range(5), repeat=5)]
            assert abs(saved['mean']-arr.mean()) < 1e-12
            assert np.allclose(saved['ci95'], np.quantile(boots, [.025, .975]), rtol=0, atol=1e-12)
            radius = t.ppf(.975, 4)*arr.std(ddof=1)/np.sqrt(5)
            assert np.allclose(saved['t95'], [arr.mean()-radius, arr.mean()+radius], rtol=0, atol=1e-12)
            intervals += 1
    assert intervals == 21
    return dict(passed=True, raw_action_note_reason_bindings=bindings, primary_rounds=80,
        fixed_two_round_windows=40, full_windows=10, game_metric_cells=70,
        exact_bootstrap_and_t_summaries=21,
        authorship='Separate implementation by same manager; independent critics recorded separately')


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
