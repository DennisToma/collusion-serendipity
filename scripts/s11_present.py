"""S11 presentation, using only verified frozen-analysis output."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    r=json.loads(Path('results/s11_delay.json').read_text())
    assert r['pilot']=='S11' and not r['dry']
    ind=json.loads(Path('logs/s11_independent.json').read_text())
    p=r['metrics']['absolute_change'];q=r['metrics']['quantity'];v=r['verdict']
    f=lambda x:f'{x:.3f}'
    ci=lambda xs:'['+', '.join(f(x) for x in xs)+']'
    games=[json.loads(path.read_text()) for path in sorted(Path('data/s11_delay').glob('game_*.json'))]
    retries={c:sum(call['attempt']>0 for g in games if g['ground_truth']['condition']==c for call in g['ground_truth']['call_provenance']) for c in ['immediate','delayed']}
    lines=['# S11 — delayed market feedback', '',f'**{v}** under the frozen consecutive-change screen. Ten fresh games, five paired blocks, no messages; zero tuning.', '',
           'Primary: mean |q(t)−q(t−1)| per firm, rounds4–12. Positive immediate−delayed means slower consecutive changes, not convergence or less collusion.', '',
           '| Outcome r4–12 | Immediate | Delayed | Contrast | Descriptive bootstrap95% | Paired t95% |',
           '|---|---:|---:|---:|---|---|']
    for k,m in r['metrics'].items():
        d=m['paired_difference'];name=k+(' (immediate−delayed)' if k=='absolute_change' else ' (delayed−immediate)')
        lines.append(f'| {name} | {f(m["immediate"]["mean"])} | {f(m["delayed"]["mean"])} | {f(d["mean"])} | {ci(d["ci95"])} | {ci(d["paired_t_ci95"])} |')
    d=p['paired_difference']
    lines+=['',f'Primary block differences: {p["seed_differences"]}; exact integer numerators {p["exact_seed_difference_numerators"]}/27. Upper sign-flip p={d["exact_signflip_p_upper"]:.5f}; lower p={d["exact_signflip_p_lower"]:.5f}.',
            f'Independent exact enumeration of all3125 empirical bootstrap resamples: {ci(ind["exact_3125_bootstrap_ci95"])}. The frozen10000-draw bootstrap remains the reported estimate.', '',
            '| Block | Immediate change | Delayed change | Immediate quantity | Delayed quantity |',
            '|---|---:|---:|---:|---:|']
    for s in range(24110,24115):
        im=next(g for g in r['games'] if g['seed']==s and g['condition']=='immediate')['primary']
        de=next(g for g in r['games'] if g['seed']==s and g['condition']=='delayed')['primary']
        lines.append(f'| {s} | {f(im["absolute_change"])} | {f(de["absolute_change"])} | {f(im["quantity"])} | {f(de["quantity"])} |')
    lines+=['','All-round and final-round arm means (descriptive, not additional tests):', '',
            '| Window | Immediate change | Delayed change | Immediate quantity | Delayed quantity |','|---|---:|---:|---:|---:|']
    for window in ['all_rounds','final']:
        m=lambda c,k:float(np.mean([g[window][k] for g in r['games'] if g['condition']==c]))
        lines.append(f'| {window} | {f(m("immediate","absolute_change"))} | {f(m("delayed","absolute_change"))} | {f(m("immediate","quantity"))} | {f(m("delayed","quantity"))} |')
    lines+=['',f'All {r["cached_responses"]} requests/responses cached; 360 valid decisions; retries by arm {retries}. Complete mandatory replay consumes every key once and verifies all exports, payoffs and registered source hashes. Independent checker reproduces {ind["independent_metric_cells"]} metric/window cells, {ind["bootstrap_intervals"]} bootstrap intervals and {ind["paired_t_intervals"]} paired t intervals.', '',
            'Both arms receive an exact conditional own-profit calculator. Immediate prompts reveal rounds1..t−1; delayed prompts reveal1..t−2, including own feedback. The delayed warmup also lacks a table at round2. This tests a bundled information-timing intervention in stateless agents. It does not isolate a realistic rival-only information lag.', '',
            'No verified agreement/execution labels. Smoother consecutive output can coexist with persistent cycles; low mean output, high price, common trajectories and individual-profit arithmetic are not collusion labels. Quantity/price/profit and lag1 regret are secondary; lag1 regret is computed even when that feedback is hidden. There is no no-calculator arm and no causal identification of the calculator mechanism. S03 is motivation, not pooled data.', '',
            'At n5 HIT is equivalent to five strictly positive block differences and mean reduction ≥1; these are not three independent evidential checks. DUD means the directional screen failed, not no effect. The predicted best-response timing pattern itself is not a surprising collusion finding. T12 and the nine-transition primary window cannot establish asymptotic stabilization. n5 is exploratory; bootstrap bounds are descriptive, paired t intervals fragile, and sign-flip validity requires exchangeability/symmetric differences despite possible shared-backend interference. Submission order is randomized within block; firm order is fixed. Seeds do not control API draws. No independently attested model identity, temperature, tool behavior or OS information isolation. Fresh empty directories/read-only requests are verified invocation properties only.', '',
            '![S11 quantity paths and primary changes](../figures/s11_delay.png)', '',
            '[Design](../DESIGN_S11.md) · [Frozen results](s11_delay.json) · [Independent checks](../logs/s11_independent.json) · [Review dispositions](../logs/s11_review_disposition.md)']
    Path('results/s11_summary.md').write_text('\n'.join(lines)+'\n')
    fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for c,color in [('immediate','#2563eb'),('delayed','#d97706')]:
        trajectories=[]
        for g in games:
            if g['ground_truth']['condition']!=c:continue
            path=np.array([np.mean([a['quantity'] for a in row['agents']]) for row in g['rows']])
            trajectories.append(path);axs[0].plot(range(1,13),path,color=color,alpha=.22,lw=1)
        axs[0].plot(range(1,13),np.mean(trajectories,axis=0),color=color,label=c,lw=2.5)
    axs[0].axhline(6,color='gray',ls='--',lw=1,label='symmetric Nash6')
    axs[0].set(xlabel='Round',ylabel='Mean quantity / firm',title='Five paths / arm; thick line = arm mean');axs[0].legend(fontsize=8)
    for i,s in enumerate(range(24110,24115)):
        vals=[next(g for g in r['games'] if g['seed']==s and g['condition']==c)['primary']['absolute_change'] for c in ['immediate','delayed']]
        axs[1].plot([0,1],vals,marker='o',label=str(s))
    axs[1].set(xticks=[0,1],xticklabels=['immediate','delayed'],ylabel='Mean |q(t)−q(t−1)|, r4–12',title=f'Primary reduction {f(d["mean"])}; {v}')
    axs[1].legend(fontsize=8);fig.savefig('figures/s11_delay.png',dpi=150);plt.close(fig)

if __name__=='__main__':main()
