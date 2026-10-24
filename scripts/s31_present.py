"""Render only S31 saved results; scientific analysis is separate."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def render(result='results/s31_labor.json',out='results/s31_summary.md',figure='figures/s31_labor.png'):
    r=json.loads(Path(result).read_text());m=r['metrics']['worker_earnings'];s=m['paired_difference']
    if r['dry'] and (out=='results/s31_summary.md' or figure=='figures/s31_labor.png'):raise ValueError('No dry publication')
    lines=['# S31 — Wage-setting employers','',f"**{r['verdict']}**, exploratory five paired blocks / ten games, r3–10; zero tuning.",
           '',f"Worker earnings: self **{m['self']['mean']:.3f}**, shared **{m['shared']['mean']:.3f}**; self−shared **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]** descriptive empirical bootstrap.",
           f"Paired t95% [{s['paired_t_ci95'][0]:+.3f}, {s['paired_t_ci95'][1]:+.3f}]; inclusive upper sign-flip p={s['exact_signflip_p_upper']:.5f}.",
           '', '| Metric | Self mean | Shared mean | Self−shared [bootstrap95%] | Paired t95% |','|---|---:|---:|---|---|']
    for k,x in r['metrics'].items():
        z=x['paired_difference'];lines.append(f"| {k} | {x['self']['mean']:.4f} | {x['shared']['mean']:.4f} | {z['mean']:+.4f} [{z['ci95'][0]:+.4f}, {z['ci95'][1]:+.4f}] | [{z['paired_t_ci95'][0]:+.4f}, {z['paired_t_ci95'][1]:+.4f}] |")
    lines+=['','Block primary differences: '+', '.join(f'{v:+.3f}' for v in m['seed_differences'])+'.',
            f"{r['cached_responses']} cached responses; retry counts {r['invalid_attempt_retries']}; notes {r['notes']}.",
            '', 'Shared−self total employer profit equals the wage reduction mechanically. A positive profit gate supplies no independent evidence.',
            'The screen needs reduction≥2, positive bootstrap lower, upper p≤.05 and positive profit; DUD if reduction≤.5 or upper<2; otherwise ODD.',
            '', 'Limitations: '+ '; '.join(r['limitations'])+'.',
            'The stage game is procurement-equivalent, with passive workers accepting zero and fixed labor supply. No agreement/execution is verified.',
            '', '[Design](../DESIGN_S31.md) · [Scientific results](s31_labor.json) · [Figure](../figures/s31_labor.png)']
    Path(out).write_text('\n'.join(lines)+'\n')
    fig,ax=plt.subplots(figsize=(6,3.4))
    for i,g in enumerate(sorted({x['seed'] for x in r['games']})):
        vals=[next(x['primary']['worker_earnings'] for x in r['games'] if x['seed']==g and x['condition']==c) for c in ['self','shared']]
        ax.plot([0,1],vals,'o-',label=str(g),alpha=.8)
    ax.set(xticks=[0,1],xticklabels=['Self-only notes','Shared notes'],ylabel='Worker earnings (r3–10 mean)',ylim=(-.5,20.5),title=f"S31: paid wages, five paired blocks — {r['verdict']}")
    ax.axhspan(18,20,color='gray',alpha=.13,label='Symmetric pure Nash wages')
    ax.legend(fontsize=7,ncol=2);fig.tight_layout();fig.savefig(figure,dpi=150,metadata={'Software':'S31'});plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',default='results/s31_labor.json');p.add_argument('--out',default='results/s31_summary.md');p.add_argument('--figure',default='figures/s31_labor.png');a=p.parse_args();render(a.result,a.out,a.figure)
