"""Deterministic S72 presentation and guarded updates of four research documents."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import re
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

LABELS = dict(stage_both_gain='Single-round both-gain fraction',
    two_round_both_gain='Fixed two-round both-gain fraction',
    full_window_both_gain='Full-window both-gain indicator',
    min_excess_per_round='Minimum individual full-window excess / round',
    pair_excess_per_round='Pair full-window excess / round',
    y_approval_rate='Y approval rate', missed_x_rate='Missed X rate')


def counts(result):
    return {c: dict(stage=sum(r['both_gain'] for r in result['rounds'] if r['condition'] == c),
        two=sum(r['both_gain'] for r in result['two_round_windows'] if r['condition'] == c),
        full=sum(g['both_gain'] for g in result['games'] if g['condition'] == c)) for c in ['self', 'shared']}


def contrast(d):
    return f"{d['mean']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}]"


def present(r, summary_path, figure_path):
    c = counts(r)
    lines = ['# S72 — Can both employees gain across rounds?', '',
        '**Post-hoc accounting; ODD/context-only.** All ten original S29 games/five paired blocks;'
        'zero new games, scientific model calls or tuning. Original S29 and S53 remain unchanged.', '',
        'At each original status, the comparator has both employees approve X and reject Y. '
        'Sum actual and comparator bonuses within each fixed window, then require strictly positive '
        'excess for each employee. This is a descriptive comparator changing both actions; '
        'it does not replay the histories that a repeated-game policy intervention would produce.', '',
        '| Time scale | Self | Shared | Denominator per arm |', '|---|---:|---:|---:|']
    for label, key, denominator in [('Single round', 'stage', 40), ('Fixed disjoint two rounds', 'two', 20), ('Full primary window', 'full', 5)]:
        lines.append(f"| {label} | {c['self'][key]} | {c['shared'][key]} | {denominator} |")
    lines += ['', '| Exogenous opportunity count | Self | Shared |', '|---|---:|---:|']
    for key in ['single_round_both_y', 'two_round_each_has_y', 'full_window_each_has_y']:
        values = {cond: sum(g['eligibility'][key] for g in r['games'] if g['condition'] == cond) for cond in ['self', 'shared']}
        lines.append(f"| {key} | {values['self']} | {values['shared']} |")
    lines += ['', 'A positive individual excess requires an incoming Y approval; '
        'both people therefore need a Y submission within the window. These are opportunity counts, '
        'not additional outcomes or revised metric denominators. They do not assert observed agreement or profitable execution.']
    lines += ['', '| Measure | Self mean [bootstrap 95%] | Shared mean [bootstrap 95%] | Shared−self [bootstrap 95%] | Difference t95% |',
        '|---|---|---|---|---|']
    for key, label in LABELS.items():
        m = r['metrics'][key]
        d = m['difference']
        lines.append(f"| {label} | {contrast(m['self'])} | {contrast(m['shared'])} | {contrast(d)} | [{d['t95'][0]:+.3f}, {d['t95'][1]:+.3f}] |")
    lines += ['', 'All21 exact bootstrap and t summaries, including arm-specific t intervals, are retained in '
        '[the result JSON](s72_temporal.json). Five source blocks are the unit; windows and employees are not independent samples. '
        'Each game has16reviews:8X and8Y opportunities,four of each status per employee. '
        'The approval/missed rates use status-conditional denominators8,not all16reviews. '
        'Matched exogenous status composition constrains which windows can show both-person gains.', '',
        '| Seed | Arm | Individual excess over eight primary rounds | Both gain? | Y approvals by reviewer | Missed X by reviewer |',
        '|---|---|---|---:|---|---|']
    for g in r['games']:
        lines.append(f"| {g['seed']} | {g['condition']} | {g['excess']} | {g['both_gain']} | "
            f"{ {a: e['y_out'] for a,e in g['edges'].items()} } | { {a: e['missed_x_out'] for a,e in g['edges'].items()} } |")
    lines += ['', 'For each employee, excess = 6×incoming Y approvals − 2×outgoing Y approvals '
        '− 6×incoming missed X approvals − outgoing missed X approvals. Pair excess = 4×Y approvals − 7×missed X. '
        'Positive pair totals can coexist with harm to one employee. Aggregation can also make both better off '
        'when no single round does. These algebraic possibilities do not themselves establish that either pattern is prevalent.', '',
        'The four fixed windows are rounds3–4,5–6,7–8,9–10. They were chosen before this decomposition, '
        'after original outcomes were known. Their boundaries have no special economic status; '
        'they are not an estimated reciprocity lag. The full window is rounds3–10, excludes warmup, '
        'and is neither whole-game nor long-run profit. No window search, p-values or promotion rule.', '',
        'All seven measures summarize the same actions and add no independent replication. '
        'Differences in the binary/fraction classifications reflect nonlinear aggregation; '
        'they are not incremental independent evidence of cooperation. Model notes and action timing '
        'are not classified as promises or causal responses. No agreement, reciprocal intent, '
        'causal mediation, repeated equilibrium, counterfactual causal profit, population absence or equivalence claim.', '',
        'Five-block exact empirical bootstrap bounds use linear2.5/97.5percentiles across3125 ordered resamples; '
        't intervals use df4. Descriptive, uncorrected bounds can degenerate; t intervals for binary measures '
        'can leave[0,1]. Reused source histories and posthoc question choice limit interpretation. '
        'One requested model, synthetic tasks, bundled shared-note delivery/readability, uncontrolled provider draws '
        'and source runtime/served settings/tool-use nonattestation remain. All original caveats carry forward.', '',
        '[Design](../DESIGN_S72.md) · [All80 single rounds,40 two-round windows,10 full windows](s72_temporal.json) '
        '· [Figure](../figures/s72_temporal.png).', '',
        'Reproduce: `uv run --frozen python scripts/s72_temporal.py release`; '
        '`uv run --frozen python scripts/s72_independent.py`.']
    Path(summary_path).write_text('\n'.join(lines)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 4, figsize=(14, 7))
    for ax, (key, label) in zip(axes.flat, LABELS.items()):
        m = r['metrics'][key]
        for i, seed in enumerate(range(24480, 24485)):
            ax.plot([0, 1], [float(Fraction(m['self']['block_values'][i])), float(Fraction(m['shared']['block_values'][i]))],
                'o-', alpha=.7, label=str(seed))
        ax.set(xticks=[0, 1], xticklabels=['Self notes', 'Shared notes'], title=label)
        ax.axhline(0, color='gray', lw=.5)
        ax.title.set_fontsize(9)
    axes.flat[0].legend(fontsize=6)
    axes.flat[-1].axis('off')
    axes.flat[-1].text(.05, .8, 'Post hoc; five original paired blocks\nSame actions at three time scales\nSeven dependent descriptive measures\nNo agreement or causal reciprocity claim', va='top', fontsize=10)
    fig.suptitle('S72: Nash-relative payoff aggregation in original S29 primary rounds3–10')
    fig.tight_layout()
    fig.savefig(figure_path, dpi=150, metadata={'Software': 'S72'})
    plt.close(fig)


def documents(check=False):
    from scripts.s72_temporal import checked_manifest
    m = checked_manifest()
    r = json.loads(Path('results/s72_temporal.json').read_text())
    from scripts.s72_independent import verify
    verify(r)
    commit = r['registration_receipt']['commit']
    c = counts(r)
    d = r['metrics']['full_window_both_gain']['difference']
    row = (f"| S72 · E, temporal payoff audit | All10 original S29 games/5blocks;zero new calls. "
        f"Both gain across r3–10: self **{c['self']['full']}/5**,shared **{c['shared']['full']}/5**; "
        f"difference **{contrast(d)}**. Single-round both-gain **{c['self']['stage']}/40** versus **{c['shared']['stage']}/40**. "
        "[All7 measures](results/s72_summary.md). | **ODD / context-only**, post hoc |")
    latest = (f"**Latest — S72 (post hoc):** Both employees beat the same-status one-shot Nash comparator "
        f"over the fixed primary window in **{c['self']['full']}/5** self-note games and **{c['shared']['full']}/5** shared-note games; "
        f"single-round counts remain **{c['self']['stage']}/40** and **{c['shared']['stage']}/40**. "
        f"Fixed two-round counts: **{c['self']['two']}/20** and **{c['shared']['two']}/20**. "
        "Payoff aggregation can change the classification; this does not establish agreement, reciprocal intent or a causal profit effect. "
        "[All measures, individual excesses and limits](results/s72_summary.md).")
    expected = {}
    paths = ['REPORT.md', 'REPORT_DETAILS.md', 'HITS.md', 'README.md']
    bases = {p: subprocess.check_output(['git', 'show', f'{commit}:{p}']).decode() for p in paths}
    report = re.sub(r'Iteration \d+', 'Iteration 52', bases['REPORT.md'], count=1)
    report = re.sub(r'<!-- S68 summary start -->.*?<!-- S68 summary end -->',
        '<!-- S68 summary start --><!-- S68 summary end -->', report, flags=re.S)
    report = report.replace('| Pilot |', '<!-- S72 summary start -->\n'+latest+'\n<!-- S72 summary end -->\n\n| Pilot |', 1)
    lines = report.splitlines()
    last = max(i for i, x in enumerate(lines) if x.startswith('| S'))
    lines.insert(last+1, row)
    report = '\n'.join(lines)+'\n'
    report = re.sub(r'\*\*Next:\*\*[^\n]*', '**Next:** different-axis fresh pilot only if valuable before14:30UTC; '
        'S68 remains interrupted with no estimate or restart. No promoted HIT or sibling headline change.', report)
    assert all(report.count(old) == 1 for old in m['older_report_rows'])
    assert len([x for x in report.splitlines() if x.startswith('| S')]) == len(m['older_report_rows'])+1
    expected['REPORT.md'] = report
    expected['REPORT_DETAILS.md'] = bases['REPORT_DETAILS.md']+'\n## Iteration52 — S72 temporal payoff aggregation\n\n'+latest+'\n\n'+row+'\n\n'+(
        'All80 single-round,40 fixed two-round and10 full-window records are exported. '
        'Seven dependent descriptive measures,21bootstrap/t summaries;five reused paired blocks. '
        'Posthoc question after original outcomes known;no new HIT,replication,agreement or causal reciprocity claim. '
        'Source S29 and S53 unchanged. [Design](DESIGN_S72.md) · [Full audit](results/s72_summary.md) · [Figure](figures/s72_temporal.png).\n')
    expected['HITS.md'] = bases['HITS.md']+'\n## S72 — Unpromoted temporal payoff accounting\n\n'+latest+'\n\n'+(
        '**ODD/context-only;no promotion rule or confirmation request.** For both siblings: '
        'absence of simultaneous two-sided gains does not by itself exclude gains exchanged across rounds. '
        'This posthoc comparator at fixed statuses is not a repeated-policy intervention,agreement label or reciprocal-intent test. '
        'Reproduce `uv run --frozen python scripts/s72_temporal.py release`.\n')
    expected['README.md'] = bases['README.md']+'\n## S72: temporal payoff accounting of all S29 games\n\n'+(
        '[Design](DESIGN_S72.md) · [All seven measures and caveats](results/s72_summary.md) · [Figure](figures/s72_temporal.png).\n\n'
        'Posthoc,zero new scientific calls/games;all original ten S29 games/five blocks. '
        'Uses fixed single-round,two-round and full-primary-window accounting with the original stage Nash comparator. '
        'No agreement,causal reciprocal response or independent confirmation claim. '
        'Full source/raw replay,source/input hashes,older science bytes and separate exact reconstruction are checked. '
        'llm.chat is patched to raise;this is not OS network/process isolation. Existing pinned venv reused.\n\n'
        '```bash\nuv run --frozen python scripts/s72_temporal.py release\n'
        'uv run --frozen python scripts/s72_independent.py\n'
        'uv run --frozen python scripts/s72_present.py --check-documents\n'
        'uv run --frozen python scripts/s72_postcheck.py\n'
        'uv run --frozen python -m unittest scripts.test_s72\n```\n\n'
        '`scripts/s72_clone.py` reproduces a pushed revision in a fresh full-history origin clone. '
        'Registration freeze/register-remote steps are one-time and must not be repeated.\n')
    # Exclusive writer required: prevalidation is not concurrent-writer atomicity.
    for p, value in expected.items():
        actual = Path(p).read_text()
        if check and actual != value:
            raise ValueError('Published document changed: '+p)
        if not check and actual not in [bases[p], value]:
            raise ValueError('Unexpected document edit; refusing overwrite: '+p)
    if not check:
        for p, value in expected.items():
            Path(p).write_text(value)
    result = dict(passed=True, prior_pilot_rows=len(m['older_report_rows']),
        current_pilot_rows=len(m['older_report_rows'])+1, documents=paths,
        guard='Exclusive-writer prevalidation; no atomic concurrent-writer guarantee')
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--check-documents', action='store_true')
    args = p.parse_args()
    documents(args.check_documents)
