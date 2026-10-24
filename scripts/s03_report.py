"""Render S03 summaries and standalone figure from frozen results only."""
import json
from pathlib import Path


def fmt(summary, signed=True):
    sign='+' if signed else ''
    return f'{summary["mean"]:{sign}.3f} [{summary["ci95"][0]:{sign}.3f}, {summary["ci95"][1]:{sign}.3f}]'


def render():
    path=Path('results/s03_calculator.json')
    if not path.exists():
        return ('| S03 · own, conditional calculator | Registered: 10 games, 5 fresh blocks, T12, no messages. Exact own-profit table vs none. | **PENDING** |',
                '**S03:** Registered before live outcomes; primary is mean quantity per firm r4–12, calculator minus none. [Design](DESIGN_S03.md).',
                '\n# S03 — exact conditional own-profit calculator\n\nRegistered; live outcome not yet analyzed. See [design](DESIGN_S03.md).\n')
    obj=json.loads(path.read_text())
    assert not obj['dry']
    m=obj['metrics'];q=m['quantity'];d=q['paired_difference'];tc=d['paired_t_ci95']
    row=(f'| S03 · own, conditional calculator | 10 games, 5 blocks. Mean output/firm r4–12: none **{q["none"]["mean"]:.3f}**, calculator **{q["calculator"]["mean"]:.3f}**; difference **{fmt(d)}**. | **{obj["verdict"]}** |')
    text=(f'**S03:** t interval [{tc[0]:+.3f}, {tc[1]:+.3f}], exact higher-output p={d["exact_signflip_p_upper"]:.5f}. '
          f'Average profit difference {fmt(m["profit"]["paired_difference"])}. '
          'The table bundles exact arithmetic with salience and myopic framing; this is not an isolated arithmetic-error effect or a collusion test. '
          '[All S03 outcomes](REPORT_DETAILS.md#s03--exact-conditional-own-profit-calculator).')
    rows=[]
    for key,label in [('quantity','Quantity per firm'),('price','Market price'),('profit','Profit per firm'),
                      ('actual_stage_regret','Stage regret against actual rivals'),
                      ('lag_conditional_regret','Conditional regret against lagged rivals'),
                      ('distance_nash','Absolute distance from symmetric Nash q=6'),('absolute_change','Absolute quantity change'),
                      ('all_equal','All-three quantity equality rate')]:
        x=m[key];t=x['paired_difference']['paired_t_ci95']
        rows.append(f'| {label} | {x["none"]["mean"]:.3f} | {x["calculator"]["mean"]:.3f} | {fmt(x["paired_difference"])} | [{t[0]:+.3f}, {t[1]:+.3f}] |')
    seeds=[]
    for seed in range(24060,24065):
        a,b=[next(g for g in obj['games'] if g['seed']==seed and g['condition']==c) for c in ['none','calculator']]
        seeds.append(f'| {seed} | {a["primary"]["quantity"]:.6f} | {b["primary"]["quantity"]:.6f} | {b["primary"]["quantity"]-a["primary"]["quantity"]:+.6f} |')
    windows=[]
    for label,field in [('All rounds','all_rounds'),('Final round','final')]:
        for c in ['none','calculator']:
            games=[g for g in obj['games'] if g['condition']==c]
            averages={k:sum(g[field][k] for g in games)/5 for k in games[0][field]}
            windows.append(f'| {label} | {c} | '+' | '.join(f'{averages[k]:.3f}' for k in averages)+' |')
    detail=f'''
# S03 — exact conditional own-profit calculator

**Frozen verdict: {obj['verdict']}.** Five fresh seed blocks, ten complete games,
T12, {obj['cached_responses']} cached responses, codex gpt-6-luna, zero tuning attempts.
Every firm gets the same arm's interface; no firm pair, messages or advisor.
From round 2, a calculator lists exact profits for all 13 own quantities conditional
on rivals repeating their last completed quantities. Both arms see those lagged
quantities and all public history; round-one prompts match. This table is not a
forecast. The own-total-profit objective and undisclosed horizon are unchanged.

One primary: output per firm r4–12, calculator minus none **{fmt(d)}**;
paired t 95% interval [{tc[0]:+.3f}, {tc[1]:+.3f}], conditional exact one-sided
higher-output sign enumeration p={d['exact_signflip_p_upper']:.5f}
(lower-tail descriptive p={d['exact_signflip_p_lower']:.5f}). Decisions use exact
integer totals over 27 firm-rounds per game, not rounded numbers. All five seed
contrasts and all prespecified secondaries follow. Bootstrap bounds resample five
seed blocks (10,000 draws, RNG 2406); they are descriptive and may under-cover.
The t interval is fragile at n5. Sign enumeration assumes exchangeable execution
slots/symmetric block differences and can fail under backend/time interference.
The HIT rule requires >=1 unit increase, positive bootstrap lower and p<=.05.
The n5 HIT sign rule requires all five contrasts strictly positive.
DUD is the frozen prioritization label, not proof of no effect or equivalence;
negative effects require the separately registered ODD-reverse rule.

| Seed block | None mean quantity | Calculator mean quantity | Difference |
|---|---|---|---|
{chr(10).join(seeds)}

**Primary-window outcomes:** all differences are calculator minus none. Only
quantity is the primary; no secondary qualifies as a HIT or tunes a choice.
Regret means one-stage forgone profit; it is not dynamic regret or evidence that
an action was irrational in a repeated game. The lagged benchmark matches the
table; actual-rivals regret uses contemporaneous quantities only after decisions.

| Outcome | None | Calculator | Difference [descriptive bootstrap 95%] | Paired t 95% |
|---|---|---|---|---|
{chr(10).join(rows)}

**Other prespecified windows:** lag-conditioned regret/change exclude round one.

| Window | Arm | Quantity | Price | Profit | Actual regret | Lag regret | Distance Nash | Abs change | All equal |
|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(windows)}

![Calculator pilot trajectories and seed contrasts](figures/s03_calculator.png)
*Mean market quantity paths; bands show the range of five games, not confidence
intervals. Right panel shows one primary contrast per seed block.*

**Limits:** the intervention bundles correct arithmetic, longer context, salience
and a possible myopic-policy cue. Changes cannot be attributed to arithmetic
error correction alone. Histories diverge endogenously. No message channel does
not establish tacit collusion; agreement/execution labels remain null. This is a
tiny exploratory test of one table and one model, with no equivalence claim.
Best responses to lagged rivals can cycle (symmetric q4 to q8 and back),
changing behavior while leaving mean output at q6. Read the change and regret
diagnostics beside the primary. Distance |q-6| refers only to symmetric Nash;
the six permutations of (5,6,7) are also grid Nash equilibria.
All seeds provide server-sampled replicates with randomized arm execution slots;
no API seed/temperature control or independent model attestation. Cache-key
separation prevents accidental response reuse; it cannot guarantee independence
of model draws. No sibling headline change follows from this screen alone.

[Design](DESIGN_S03.md) · [Frozen JSON](results/s03_calculator.json) ·
[Verification](logs/s03_verification.json) ·
[Review dispositions](logs/s03_review_disposition.md).
Reproduce: `uv run python scripts/s03_analyze.py`;
`uv run python scripts/s03_verify.py`; `uv run python scripts/render_report.py`;
`uv run python scripts/s03_report.py` (figure only).
'''
    return row,text,detail


def figure():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    obj=json.loads(Path('results/s03_calculator.json').read_text())
    assert not obj['dry']
    fig,axes=plt.subplots(1,2,figsize=(9,3.5))
    for c,color in [('none','#3675a9'),('calculator','#c6742a')]:
        games=[json.loads(p.read_text()) for p in Path('data/s03_calculator').glob(f'game_*_{c}.json')]
        series=np.array([[sum(a['quantity'] for a in r['agents'])/3 for r in g['rows']] for g in games])
        axes[0].plot(range(1,13),series.mean(axis=0),color=color,label=c)
        axes[0].fill_between(range(1,13),series.min(axis=0),series.max(axis=0),alpha=.1,color=color)
    axes[0].axhline(6,ls='--',color='gray',label='static Nash')
    axes[0].set(xlabel='Round (bands: range across 5 games)',ylabel='Mean quantity per firm')
    axes[0].legend(fontsize=8)
    diff=obj['metrics']['quantity']['seed_differences']
    axes[1].bar([str(s) for s in range(24060,24065)],diff,color='#6b7294')
    axes[1].axhline(0,color='gray',lw=1)
    axes[1].axhline(1,color='gray',ls=':',label='HIT magnitude threshold')
    axes[1].set(xlabel='Seed block',ylabel='Calculator minus none quantity (r4–12)')
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig('figures/s03_calculator.png',dpi=170)
    plt.close(fig)


if __name__=='__main__':
    figure()
