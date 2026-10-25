"""Separate analytic/raw reconstruction; no imports from the S67 estimator/simulator."""
from fractions import Fraction
import itertools
import json
from pathlib import Path
import numpy as np
from scipy.stats import t

if not __debug__:
    raise RuntimeError('S67 checker requires Python without optimization')

KEYS = ['y_approvals', 'missed_x', 'costly_y_approvals', 'profitable_y_rejections',
        'stage_regret', 'pair_shortfall', 'strict_pareto_rounds', 'organization_loss']


def exact_bounds(values):
    # Independent rank/interpolation calculation; verify exact exported fractions.
    sample = sorted(sum(draw)/5 for draw in itertools.product(values, repeat=5))
    answer = []
    for rank in [Fraction(len(sample)-1, 40), Fraction(39*(len(sample)-1), 40)]:
        i, numerator = divmod(rank.numerator, rank.denominator)
        answer.append((sample[i]*(rank.denominator-numerator) +
                       sample[min(i+1, len(sample)-1)]*numerator)/rank.denominator)
    return answer


def formulas(types, acts, cond):
    ids = sorted(types)
    allocated, actual, base, regrets = {}, {}, {}, {}
    for a in ids:
        b = next(x for x in ids if x != a)
        allocated[a] = 6*acts[b] + (1 if types[b] else -2)*acts[a]
    for a in ids:
        b = next(x for x in ids if x != a)
        if cond == 'individual':
            actual[a] = allocated[a]
            base[a] = 6*types[a] + types[b]
            regrets[a] = (1-acts[a]) if types[b] else 2*acts[a]
        else:
            actual[a] = sum(allocated.values())/2
            base[a] = sum(7 if types[x] else 4 for x in ids)/2
            regrets[a] = (3.5 if types[b] else 2)*(not acts[a])
    y = sum(acts[a] and not types[next(x for x in ids if x != a)] for a in ids)
    missed_x = sum(not acts[a] and types[next(x for x in ids if x != a)] for a in ids)
    rejected_y = sum(not acts[a] and not types[next(x for x in ids if x != a)] for a in ids)
    metrics = dict(y_approvals=y, missed_x=missed_x,
        costly_y_approvals=y if cond == 'individual' else 0,
        profitable_y_rejections=rejected_y if cond == 'pooled' else 0,
        stage_regret=sum(regrets.values()), pair_shortfall=4*rejected_y+7*missed_x,
        strict_pareto_rounds=int(all(actual[a] > base[a] for a in ids)), organization_loss=10*y)
    extra = dict(allocated=allocated, final=actual, nash=base, regret_by_agent=regrets,
        nash_actions={a: (types[next(x for x in ids if x != a)] if cond == 'individual' else True) for a in ids},
        pair_max_bonus=sum(7 if types[a] else 4 for a in ids),
        y_opportunities=sum(not types[a] for a in ids), x_opportunities=sum(types.values()),
        both_y=int(not any(types.values())))
    return metrics | extra


def verify(result=None):
    if result is None:
        result = json.loads(Path('results/s67_incentives.json').read_text())
    assert result['id'] == 'S67' and result['posthoc'] is True
    assert result['verdict'] == 'ODD/context-only' and result['source_calibration'] == 'UNRESOLVED'
    assert result['new_games'] == result['scientific_model_calls'] == result['tuning_attempts'] == 0
    assert result['n_blocks'] == 5 and result['primary_rounds'] == '3..10'
    assert set(result['metrics']) == set(KEYS)
    source = Path('data/s65_bonus_pooling')
    games = [json.loads(p.read_text()) for p in sorted(source.glob('game_*.json'))]
    assert len(games) == 10 and not list(source.glob('failure_*.json'))
    raw = {r['key']: r['response'] for r in map(json.loads, (source/'raw/responses.jsonl').read_text().splitlines())}
    accepted = {}
    for q in map(json.loads, (source/'raw/requests.jsonl').read_text().splitlines()):
        rid, ti, agent, attempt = q['payload'][5:9]
        text = raw[q['key']]['text']
        if text.startswith('```json\n') and text.endswith('\n```'):
            text = text[8:-4]
        obj = json.loads(text)
        assert attempt == 0  # Specific complete S65 archive has no retries.
        assert (rid, ti, agent) not in accepted
        accepted[rid, ti, agent] = obj
    assert len(accepted) == len(raw) == 200
    by, reconstructed = {}, {}
    bindings = 0
    saved_rounds = {(r['seed'], r['condition'], r['round']): r for r in result['rounds']}
    saved_games = {(g['seed'], g['condition']): g for g in result['games']}
    assert len(saved_rounds) == len(result['rounds']) == 80
    assert len(saved_games) == len(result['games']) == 10
    for game in games:
        gt = game['ground_truth']
        seed, cond, rid = gt['seed'], gt['condition'], gt['run_id']
        totals = dict.fromkeys(KEYS, 0)
        opp = dict(y_opportunities=0, x_opportunities=0, both_y=0)
        assert [r['round'] for r in game['rows']] == list(range(10))
        for row in game['rows']:
            records = {a['id']: a for a in row['agents']}
            types = row['market']['passed']
            acts = {}
            for a in records:
                b = next(x for x in records if x != a)
                obj = accepted[rid, row['round'], a]
                assert set(obj) == {'reviews', 'reasoning', 'note'}
                assert set(obj['reviews']) == {b} and type(obj['reviews'][b]) is bool
                assert obj['reviews'] == records[a]['reviews']
                # SCHEMA uses 1-based note rounds and 0-based decision/reasoning rounds.
                assert [n['text'] for n in gt['notes_file'] if n['author'] == a and n['round'] == row['round']+1] == [obj['note']]
                assert [n['reasoning'] for n in gt['reasoning_notes'] if n['agent'] == a and n['round'] == row['round']] == [obj['reasoning']]
                acts[a] = obj['reviews'][b]
                bindings += 1
            f = formulas(types, acts, cond)
            assert f['final'] == {a: records[a]['profit'] for a in records}
            if row['round'] < 2:
                continue
            key = seed, cond, row['round']+1
            expected = dict(seed=seed, condition=cond, round=row['round']+1,
                            passed=types, actions=acts, **f)
            assert saved_rounds[key] == expected
            reconstructed[key] = expected
            assert f['organization_loss'] == row['market']['organization_loss']
            for k in totals:
                totals[k] += f[k]
            for k in opp:
                opp[k] += f[k]
        assert opp['x_opportunities'] == opp['y_opportunities'] == 8
        assert saved_games[seed, cond] == dict(seed=seed, condition=cond, totals=totals, opportunities=opp)
        by[seed, cond] = totals | opp
    conditions, seeds = ['individual', 'pooled'], list(range(25340, 25345))
    assert set(by) == set(itertools.product(seeds, conditions))
    for s in seeds:
        for ti in range(3, 11):
            assert reconstructed[s, 'individual', ti]['passed'] == reconstructed[s, 'pooled', ti]['passed']
    intervals = 0
    for key, metric in result['metrics'].items():
        a = [Fraction(by[s, 'individual'][key])/8 for s in seeds]
        b = [Fraction(by[s, 'pooled'][key])/8 for s in seeds]
        assert set(metric) == {'individual', 'pooled', 'difference'}
        for label, values in [('individual', a), ('pooled', b), ('difference', [y-x for x, y in zip(a, b)])]:
            v = np.array(list(map(float, values)))
            boot = [sum(v[i] for i in ix)/5 for ix in itertools.product(range(5), repeat=5)]
            expected_ci = np.quantile(boot, [.025, .975])
            saved = metric[label]
            assert set(saved) == {'block_values', 'mean', 'mean_exact', 'ci95', 'ci95_exact', 't95'}
            assert Fraction(saved['mean_exact']) == sum(values)/5
            assert np.allclose(saved['block_values'], v, rtol=0, atol=1e-12)
            assert abs(saved['mean']-v.mean()) < 1e-12
            assert np.allclose(saved['ci95'], expected_ci, rtol=0, atol=1e-12)
            assert list(map(Fraction, saved['ci95_exact'])) == exact_bounds(values)
            radius = t.ppf(.975, 4)*v.std(ddof=1)/np.sqrt(5)
            assert np.allclose(saved['t95'], [v.mean()-radius, v.mean()+radius], rtol=0, atol=1e-12)
            intervals += 1
    assert set(result['counts']) == set(conditions)
    for cond in conditions:
        assert result['counts'][cond] == {k: sum(by[s, cond][k] for s in seeds) for k in by[seeds[0], cond]}
    assert len(result['stage_table']) == 32
    profiles = set()
    deviations = 0
    for row in result['stage_table']:
        types, acts, cond = row['passed'], row['actions'], row['condition']
        key = (cond, *(types[a] for a in 'AB'), *(acts[a] for a in 'AB'))
        assert key not in profiles
        profiles.add(key)
        assert row == dict(condition=cond, passed=types, actions=acts, **formulas(types, acts, cond))
        for a in 'AB':
            alt = formulas(types, acts | {a: not acts[a]}, cond)
            assert row['regret_by_agent'][a] == max(0, alt['final'][a]-row['final'][a])
            deviations += 1
    assert profiles == set((c, *vs) for c in conditions for vs in itertools.product([False, True], repeat=4))
    assert intervals == 24 and bindings == 200 and deviations == 64
    return dict(passed=True, raw_action_note_reason_bindings=bindings, primary_rounds=80,
        game_metric_cells=80, bootstrap_and_t_summaries=intervals, stage_profiles=32,
        unilateral_deviations=deviations,
        authorship='Separate implementation by same manager; independent critics recorded separately')


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
