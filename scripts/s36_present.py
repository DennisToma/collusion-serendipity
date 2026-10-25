"""Render only S36 saved results; scientific analysis is separate."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def render(result='results/s36_grossnet.json',out='results/s36_summary.md',figure='figures/s36_grossnet.png'):
    r=json.loads(Path(result).read_text());m=r['metrics']['resource_payment'];s=m['paired_difference']
    if r['dry'] and (Path(out).resolve()==Path('results/s36_summary.md').resolve() or Path(figure).resolve()==Path('figures/s36_grossnet.png').resolve()):raise ValueError('No dry publication')
    lines=['# S36 — Gross versus net wage quotation','',f"**{r['verdict']}**, exploratory five paired blocks / ten games, r3–10; zero tuning.",
           '',f"Worker take-home pay: net **{m['net']['mean']:.3f}**, gross **{m['gross']['mean']:.3f}**; net−gross **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]** descriptive empirical bootstrap.",
           f"Paired t95% [{s['paired_t_ci95'][0]:+.3f}, {s['paired_t_ci95'][1]:+.3f}]; inclusive upper sign-flip p={s['exact_signflip_p_upper']:.5f}.",
           '', '| Metric | Net mean | Gross mean | Net−gross [bootstrap95%] | Paired t95% |','|---|---:|---:|---|---|']
    for k,x in r['metrics'].items():
        z=x['paired_difference'];lines.append(f"| {k} | {x['net']['mean']:.4f} | {x['gross']['mean']:.4f} | {z['mean']:+.4f} [{z['ci95'][0]:+.4f}, {z['ci95'][1]:+.4f}] | [{z['paired_t_ci95'][0]:+.4f}, {z['paired_t_ci95'][1]:+.4f}] |")
    lines+=['','Block primary differences: '+', '.join(f'{v:+.3f}' for v in m['seed_differences'])+'.',
            f"{r['cached_responses']} cached responses; retry counts {r['invalid_attempt_retries']}; notes {r['notes']}.",
            '', 'At fixed realized productivity20, total firm profit plus worker take-home is20 in each round; firm profit is the exact wage complement.',
            'The screen needs net−gross≥2, positive bootstrap lower and upper p≤.05; at n5 this is equivalent to mean≥2 and all five differences strictly positive. The bootstrap gate is redundant,not independent evidence. DUD if difference≤0 or upper<2; otherwise ODD.',
            '', 'Limitations: '+ '; '.join(r['limitations'])+'.',
            'The stage game is procurement-equivalent, with passive resource accepting zero and fixed unit supply. No agreement/execution is verified.',
            '', '[Design](../DESIGN_S36.md) · [Scientific results](s36_grossnet.json) · [Figure](../figures/s36_grossnet.png)']
    Path(out).write_text('\n'.join(lines)+'\n')
    fig,ax=plt.subplots(figsize=(6,3.4))
    for i,g in enumerate(sorted({x['seed'] for x in r['games']})):
        vals=[next(x['primary']['resource_payment'] for x in r['games'] if x['seed']==g and x['condition']==c) for c in ['net','gross']]
        ax.plot([0,1],vals,'o-',label=str(g),alpha=.8)
    ax.set(xticks=[0,1],xticklabels=['NET quote 0–20','GROSS quote 10–30'],ylabel='Worker take-home (r3–10 mean)',ylim=(-.5,20.5),title=f"S36: worker earnings, five paired blocks — {r['verdict']}")
    ax.axhspan(18,20,color='gray',alpha=.13,label='Nash take-home range, both arms')
    ax.legend(fontsize=7,ncol=2);fig.tight_layout();fig.savefig(figure,dpi=150,metadata={'Software':'S36'});plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',default='results/s36_grossnet.json');p.add_argument('--out',default='results/s36_summary.md');p.add_argument('--figure',default='figures/s36_grossnet.png');a=p.parse_args();render(a.result,a.out,a.figure)
