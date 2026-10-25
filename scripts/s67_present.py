"""Deterministic presentation of all eight registered S67 accounting metrics."""
from pathlib import Path

LABELS = {
    'y_approvals': 'Y approvals / round',
    'missed_x': 'Missed X approvals / round',
    'costly_y_approvals': 'Costly Y approvals / round',
    'profitable_y_rejections': 'Y rejections forgoing +2 / round',
    'stage_regret': 'Sum of personal stage regret / round',
    'pair_shortfall': 'Pair bonus shortfall / round',
    'strict_pareto_rounds': 'Strict Nash-relative Pareto rounds / round',
    'organization_loss': 'Organization loss / round',
}


def present(result, out='results/s67_summary.md', figure='figures/s67_incentives.png'):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    c, m = result['counts'], result['metrics']
    lines = ['# S67 — Settlement changes what the same approval means', '',
        '**POST-HOC / ODD, context only.** All ten original S65 games, five paired blocks, rounds3–10. '
        'Forty rounds, eighty reviews, forty X and forty Y opportunities per arm. Zero new games or scientific model calls. '
        'Original S65 remains UNRESOLVED/ODD.', '',
        '| Primary-window total | Individual | Pooled |', '|---|---:|---:|']
    for k in LABELS:
        lines.append(f"| {LABELS[k].replace(' / round', '')} | {c['individual'][k]:g} | {c['pooled'][k]:g} |")
    lines += ['', '| Per-primary-round metric | Individual | Pooled | Pooled−individual [bootstrap95%] | Paired t95% |',
              '|---|---:|---:|---|---|']
    for k, label in LABELS.items():
        d = m[k]['difference']
        lines.append(f"| {label} | {m[k]['individual']['mean']:.3f} | {m[k]['pooled']['mean']:.3f} | "
            f"{d['mean']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}] | [{d['t95'][0]:+.3f}, {d['t95'][1]:+.3f}] |")
    lines += ['', 'Costly Y approvals are structurally zero under pooling; Y rejections forgoing +2 are structurally zero under individual settlement; strict Pareto is structurally zero under pooling. '
        'Their contrasts therefore reproduce the nonzero arm with a sign change where applicable. '
        'Pareto counts rounds (at most1 per round); approval counts count directed reviews (up to2 per round). '
        'Regret/shortfall use final bonus points; organization loss uses organization units. '
        'Y approvals/round equals the original Y approval rate only because every game has eight Y opportunities and eight primary rounds.']
    lines += ['', 'All block entries in the following table are totals over eight primary rounds.', '',
              '| Block | Settlement | Y approvals | Missed X | Costly Y | Y rejections forgoing +2 | Stage regret | Pair shortfall | Strict Pareto | Org loss |',
              '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for g in result['games']:
        vals = ' | '.join(f"{g['totals'][k]:g}" for k in LABELS)
        lines.append(f"| {g['seed']} | {g['condition']} | {vals} |")
    lines += ['',
        f"Individual settlement has {c['individual']['costly_y_approvals']:g} immediately costly Y approvals. "
        f"Pooled settlement has {c['pooled']['profitable_y_rejections']:g} rejected Y approvals that would each add2 to the focal agent's final stage bonus, holding the partner action fixed. "
        f"All {c['pooled']['y_approvals']:g} observed pooled Y approvals are individually profitable at that stage; they still impose organization loss. "
        'A rejected review can affect future actions, so stage regret is not a repeated-game irrationality label.', '',
        'Allocation gives the author6 and reviewer1 minus3 for Y. Pooling divides the pair total after charges equally. '
        'Review increments (X,Y) are (+1,−2) individual and (+3.5,+2) pooled. Unique stage Nash is approve-X/reject-Y versus approve-all. '
        'Full approval maximizes pair bonus in both arms. Organization loss is external to settlement. '
        'Pair bonus excludes organizational welfare. Nash-relative Pareto gains change both actions; focal regret changes only one. '
        'Strict Pareto equals simultaneous mutual-Y approval in individual settlement and is impossible in pooled settlement; neither count verifies agreement.', '',
        'Identities: individual regret=2×Y approvals+missed X; pooled regret=2×Y rejections+3.5×missed X. '
        'Pair shortfall=4×Y rejections+7×missed X in both arms; organization loss=10×Y approvals. '
        'The eight metrics are derived bookkeeping quantities, not eight independent findings. '
        'Different settlement regret schedules prevent interpreting their contrast as a controlled measure of optimization quality.', '',
        'Five blocks are resampled; all3125 ordered empirical bootstrap draws, exact rational linear quantiles, paired t95%. '
        'Bounds are descriptive, uncorrected, and may disagree or degenerate. No new p-values, threshold, HIT, equivalence, independent replication, '
        'tuning, heldout set, causal mechanism or collusion label. The decomposition was specified after original S65 outcomes were known. '
        'Settlement and wording are bundled; both arms share memory and notes, with endogenously diverging histories. '
        'One synthetic environment/model and unattested provider/settings/tool non-use limit transfer.', '',
        '[Design](../DESIGN_S67.md) · [All80 rounds,10 games,32 stage profiles](s67_incentives.json) · [Figure](../figures/s67_incentives.png)', '',
        'Reproduce: `uv run --frozen python scripts/s67_audit.py release` and `uv run --frozen python scripts/s67_independent.py`.']
    Path(out).write_text('\n'.join(lines)+'\n')
    fig, axes = plt.subplots(2, 4, figsize=(16, 7))
    for ax, (k, label) in zip(axes.flat, LABELS.items()):
        for i in range(5):
            ax.plot([0, 1], [m[k]['individual']['block_values'][i], m[k]['pooled']['block_values'][i]],
                    'o-', alpha=.75, label=str(25340+i))
        ax.set(xticks=[0, 1], xticklabels=['Individual', 'Pooled'], title=label.replace(' / round', '\nper primary round'))
        ax.axhline(0, color='gray', lw=.6)
    axes.flat[0].legend(title='Original block', fontsize=7)
    fig.suptitle('S67: post-hoc S65 accounting audit — related metrics, five original paired blocks')
    fig.tight_layout()
    fig.savefig(figure, dpi=150, metadata={'Software': 'S67'})
    plt.close(fig)
