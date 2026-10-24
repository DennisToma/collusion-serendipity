"""Render S09 tables and a figure directly from verified results and games."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

r=json.loads(Path('results/s09_replay.json').read_text());q=r['metrics']['quantity'];diff=q['paired_difference']
def interval(s):return f"{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]"
lines=['# S09 — erase versus retain prior private-message memory','',
       f"**{r['verdict']} for the registered quantity-increase screen.** Ten six-round continuations of all five previously observed S07 neutral prefixes; five matched blocks, no tuning.",
       '', 'Primary: pair quantity per firm over rounds7–12, erase minus retain. '
       f"**{interval(diff)}** descriptive block-bootstrap95%; paired t95% [{diff['paired_t_ci95'][0]:+.3f}, {diff['paired_t_ci95'][1]:+.3f}]; upper exact sign-flip p={diff['exact_signflip_p_upper']:.5f}.",
       '', '| Outcome r7–12 | Retain mean | Erase mean | Difference [bootstrap95%] | Paired t95% |',
       '|---|---:|---:|---:|---:|']
for key,s in r['metrics'].items():
    z=s['paired_difference'];lo,hi=z['paired_t_ci95']
    lines.append(f"| {key} | {s['retain']['mean']:.3f} | {s['erase']['mean']:.3f} | {interval(z)} | [{lo:+.3f}, {hi:+.3f}] |")
lines+=['','| Prefix seed | Retain quantity | Erase quantity | Difference | Round7 difference |','|---|---:|---:|---:|---:|']
by={(g['seed'],g['condition']):g for g in r['games']}
for idx,seed in enumerate(range(24080,24085)):
    a,b=[by[seed,c]['primary']['quantity'] for c in ['retain','erase']]
    lines.append(f"| {seed} | {a:.3f} | {b:.3f} | {b-a:+.3f} | {r['fork_seed_differences'][idx]:+.3f} |")
lines+=['', f"Round7-only pair output: {interval(r['fork_quantity_difference'])}; seed differences {r['fork_seed_differences']}. Mean absolute round7 arm difference {r['fork_mean_absolute_difference']:.3f}.",
        f"Outsider round7 output difference mean {r['fork_outsider_mean_difference']:+.3f}; seed differences {r['fork_outsider_seed_differences']} (descriptive negative control).",
        f"Source nonempty message slots: {sum(r['prefix_nonempty_message_slots'].values())}/60, over source rounds1–6; per-prefix counts {r['prefix_nonempty_message_slots']}. Exposure is not an agreement label.",
        f"Cached responses: {r['cached_responses']}; retries by arm: {r['retries_by_arm']}. No failed games.",
        '', '![S09 fork and continuation paths](../figures/s09_replay.png)', '',
        'The initial public history is identical within each block. Only received rounds1–6 private messages are removed; both arms retain their boxes and receive new messages from round8. Public actions can preserve prior agreements; future messages can repair missing information. This estimates the total continuation effect of erasing message memory at this fork, including later behavioral feedback, rather than the original channel effect. It cannot separate empty-inbox cues from message semantics.',
        '', 'Prefixes were previously observed; no independent-seed replication. With n=5, bootstrap and t intervals are fragile; the sign-flip calculation assumes slot exchangeability/symmetric differences. A DUD screen is not evidence of equivalence or absence of a communication effect. No verified agreement/execution labels or collusion inference. Pair-profit changes are descriptive and are not a HIT gate. Model/backend labels and sampling/isolation limitations are inherited from S07.',
        '', 'Mandatory cache-only full replay, every key consumed once, prefix/source/registration and exports/payoffs checks pass. Independent full metric/statistic check: [audit](../logs/s09_independent.json).',
        '', 'Reproduce: `TMPDIR=/var/tmp uv run python -m sim.replay`; `uv run python scripts/s09_analyze.py`; `uv run python scripts/s09_independent.py`; `uv run python scripts/s09_present.py`.',
        '', '[Registered design](../DESIGN_S09.md) · [Machine-readable results](s09_replay.json)']
Path('results/s09_summary.md').write_text('\n'.join(lines)+'\n')
fig,axes=plt.subplots(1,2,figsize=(10,3.5),layout='constrained')
for seed in range(24080,24085):
    axes[0].plot([0,1],[by[seed,c]['primary']['quantity'] for c in ['retain','erase']],marker='o',label=str(seed))
for cond,color in [('retain','#275dad'),('erase','#c45121')]:
    paths=[]
    for seed in range(24080,24085):
        g=json.loads(Path(f'data/s09_replay/game_{seed}_{cond}.json').read_text());pair=g['ground_truth']['assigned_pair']
        paths.append([np.mean([a['quantity'] for a in row['agents'] if a['id'] in pair]) for row in g['rows'][6:]])
    axes[1].plot(range(7,13),np.mean(paths,axis=0),marker='o',label=cond,color=color)
axes[0].set(xticks=[0,1],xticklabels=['Retain','Erase'],ylabel='Pair quantity per firm',title='All five matched prefixes')
axes[0].legend(fontsize=7,ncol=2)
axes[1].set(xlabel='Round',ylabel='Pair quantity per firm',title='Mean continuation paths')
axes[1].legend()
for ax in axes:ax.axhline(6,color='gray',ls=':',lw=1);ax.grid(alpha=.2)
fig.suptitle(f"S09: erase − retain {diff['mean']:+.3f}; {r['verdict']} (exploratory n=5)")
fig.savefig('figures/s09_replay.png',dpi=150)
