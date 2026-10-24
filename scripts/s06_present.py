"""Render S06 frozen outcomes; no estimation or model calls."""
from pathlib import Path
import json
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def f(v):return f'{v:.3f}'
def interval(s,key='ci95'):return '['+', '.join(f(v) for v in s[key])+']'


def main():
    r=json.loads(Path('results/s06_denomination.json').read_text())
    ind=json.loads(Path('logs/s06_independent.json').read_text())
    retries=json.loads(Path('logs/s06_retry_audit.json').read_text())
    m=r['metrics'];p=m['quantity']['paired_difference'];u=m['quantity']['unit']['mean'];c=m['quantity']['cent']['mean']
    games=[json.loads(p.read_text()) for p in sorted(Path('data/s06_denomination').glob('game_*.json'))]
    lines=['# S06 — denomination invariance (own)', '',
        f'**{r["verdict"]}** for the registered two-sided exploratory screen. Ten fresh games / five time-matched blocks; T12, no messages, exact conditional calculator in both arms. Every monetary display is multiplied by100 in CENT, with explicit conversion; actions and real payoffs are unchanged.', '',
        f'Primary mean quantity/firm r4–12: UNIT **{f(u)}**, CENT **{f(c)}**; CENT−UNIT **{f(p["mean"])}**, descriptive bootstrap95% **{interval(p)}**, paired t95% **{interval(p,"paired_t_ci95")}**, two-sided sign-flip **p={p["exact_signflip_p_two_sided"]}**. Zero tuning attempts; no held-out test claim.', '',
        f'Exact block difference numerators /27: {m["quantity"]["exact_seed_difference_numerators"]}. Separate enumeration of all3125 empirical resamples gives {ind["exact_3125_bootstrap_ci95"]}; the registered10000-draw bounds remain the reported estimate.', '',
        '| Outcome r4–12 | UNIT | CENT | CENT−UNIT [bootstrap95%] | Paired t95% |',
        '|---|---:|---:|---|---|']
    for k,v in m.items():lines.append(f'| {k} | {f(v["unit"]["mean"])} | {f(v["cent"]["mean"])} | {f(v["paired_difference"]["mean"])} {interval(v["paired_difference"])} | {interval(v["paired_difference"],"paired_t_ci95")} |')
    lines+=['','All money outcomes above use common currency, so the displayed100x denomination is normalized out. Regrets are individual one-step diagnostics; the conditional table is not a forecast or dynamic optimum. Secondary outcomes cannot promote a hit.', '',
        '| Block | UNIT primary quantity | CENT primary quantity | Difference |','|---|---:|---:|---:|']
    for s in range(24160,24165):
        vals=[next(g for g in r['games'] if g['seed']==s and g['condition']==c)['primary']['quantity'] for c in ['unit','cent']]
        lines.append(f'| {s} | {f(vals[0])} | {f(vals[1])} | {f(vals[1]-vals[0])} |')
    lines+=['','All-round and final-round descriptive means (no further tests):','','| Window | Arm | Quantity | Price | Profit | Change |','|---|---|---:|---:|---:|---:|']
    for window in ['all_rounds','final']:
        for c in ['unit','cent']:
            vals={k:float(np.mean([g[window][k] for g in r['games'] if g['condition']==c])) for k in ['quantity','price','profit','absolute_change']}
            lines.append(f'| {window} | {c} | '+' | '.join(f(v) for v in vals.values())+' |')
    lines+=['',f'{r["cached_responses"]} cached responses /360 valid decisions. Extra requests by arm: {retries["retry_requests"]}; rejected-output reasons: {retries["rejection_reasons"]}. No excluded/replacement game. Last response {retries["last_call_completed_utc"]}; all logical calls started before cutoff. Complete exact-request replay consumes every key once and checks source registration, exports, actions, tables and payoffs. Independent raw recomputation checks {ind["independent_metric_cells"]} metric/window cells, {ind["bootstrap_intervals"]} bootstrap and {ind["paired_t_intervals"]} paired t intervals.', '',
        'The HIT screen requires |mean|≥1, bootstrap exclusion of0 and two-sided sign p≤.10. With n5 the minimum two-sided p is.0625; HIT reduces to five strictly same-sign differences and |mean|≥1. These are dependent screening conditions, not multiple confirmations or a .05 significance claim. DUD is not equivalence evidence.', '',
        'Denomination changes numeric magnitude, formatting and the explicit conversion cue together, with no change in real stakes. This does not isolate arithmetic, attention or risk preferences. Common static symmetric Nash remains q6/P12/profit36; coordinated full-market joint output q4 is a benchmark, not a label. No agreement/execution labels, no collusion finding, no sibling headline change.', '',
        'Tiny sample, short/phase-sensitive games, exploratory pilot selection and shared API interference limit inference. Block IDs time-match games and do not seed action draws. Randomized submission order is not an independent transport-slot assignment; exact sign-flip interpretation assumes exchangeability/symmetric differences. Backend/model labels are client metadata; sampling, tool behavior and OS information isolation are not independently attested. In-flight/internal transport retries are not separately bounded by the logical-call cutoff.', '',
        '![S06 quantity paths and paired output](../figures/s06_denomination.png)', '',
        '[Design](../DESIGN_S06.md) · [Results](s06_denomination.json) · [Independent check](../logs/s06_independent.json) · [Request audit](../logs/s06_request_audit.json) · [Review dispositions](../logs/s06_review_disposition.md)']
    Path('results/s06_summary.md').write_text('\n'.join(lines)+'\n')
    fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for cond,color in [('unit','#2563eb'),('cent','#d97706')]:
        paths=[np.array([np.mean([a['quantity'] for a in row['agents']]) for row in g['rows']]) for g in games if g['ground_truth']['condition']==cond]
        for path in paths:axs[0].plot(range(1,13),path,color=color,alpha=.2,lw=1)
        axs[0].plot(range(1,13),np.mean(paths,axis=0),color=color,lw=2.5,label=cond)
    axs[0].axhline(6,color='gray',ls='--',lw=1,label='symmetric Nash6')
    axs[0].set(xlabel='Round',ylabel='Mean quantity / firm',title='Five paths per arm; thick = arm mean');axs[0].legend(fontsize=8)
    for s in range(24160,24165):
        vals=[next(g for g in r['games'] if g['seed']==s and g['condition']==c)['primary']['quantity'] for c in ['unit','cent']]
        axs[1].plot([0,1],vals,marker='o',label=str(s))
    axs[1].set(xticks=[0,1],xticklabels=['UNIT','CENT'],ylabel='Mean quantity / firm, r4–12',title=f'CENT−UNIT {f(p["mean"])}; {r["verdict"]}');axs[1].legend(fontsize=8)
    fig.savefig('figures/s06_denomination.png',dpi=150);plt.close(fig)
    report=Path('REPORT.md').read_text()
    report=re.sub(r'2026-10-24 .*? · Iteration \d+ ·', '2026-10-24 · Iteration 7 ·', report,count=1)
    row=f'| S06 · own, denomination | 10 games / 5 time-matched pairs. Mean quantity r4–12: UNIT **{f(u)}**, CENT **{f(c)}**; difference **{f(p["mean"])} {interval(p)}**. | **{r["verdict"]}** for invariance screen |'
    if '| S06 ·' in report:report=re.sub(r'^\| S06 ·.*$',lambda _:row,report,flags=re.M)
    else:
        ix=report.index('\n\n**S11:');report=report[:ix]+'\n'+row+report[ix:]
    start=report.index('**S11:');end=report.index('**Earlier caveats:',start)
    paragraph=(f'**S06:** all displayed prices/profits and conditional tables scale100x, with explicit conversion and identical real incentives. CENT−UNIT quantity: paired t95% **{interval(p,"paired_t_ci95")}**, two-sided sign-flip **p={p["exact_signflip_p_two_sided"]}**. The registered .10 queue threshold allows the n5 minimum p=.0625; this is exploratory. Denomination bundles magnitude, formatting and conversion wording. DUD would not establish equivalence. [All outcomes and figure](results/s06_summary.md).\n\n')
    report=report[:start]+paragraph+report[end:]
    if 'S11 compares' not in report:report=report.replace('**Earlier caveats:**','**Earlier caveats:** S11 compares delayed feedback including own recall/warmup; slower consecutive changes do not establish convergence or reduced collusion. [S11 details](results/s11_summary.md).')
    report=report.replace('· [S11](DESIGN_S11.md).','· [S11](DESIGN_S11.md) · [S06](DESIGN_S06.md).')
    report=re.sub(r'\*\*Next:\*\*.*', '**Next:** Portfolio complete; choose a different axis next, or a justified fresh confirmation. Keep checkpoint documents presentable; no secondary-driven promotion.',report)
    report=report.replace('[S11 replay/release verification](logs/s11_release.json) · [Independent checks](logs/s11_independent.json) · [Review dispositions](logs/s11_review_disposition.md).','[S06 replay/release verification](logs/s06_release.json) · [Independent checks](logs/s06_independent.json) · [Review dispositions](logs/s06_review_disposition.md).')
    Path('REPORT.md').write_text(report)

if __name__=='__main__':main()
