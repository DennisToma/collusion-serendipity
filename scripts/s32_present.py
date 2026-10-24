"""Render only S32 saved results; scientific analysis is separate."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def render(result='results/s32_resource.json',out='results/s32_summary.md',figure='figures/s32_resource.png'):
    r=json.loads(Path(result).read_text());m=r['metrics']['resource_payment'];s=m['paired_difference']
    if r['dry'] and (Path(out).resolve()==Path('results/s32_summary.md').resolve() or Path(figure).resolve()==Path('figures/s32_resource.png').resolve()):raise ValueError('No dry publication')
    lines=['# S32 — Resource identity framing','',f"**{r['verdict']}**, exploratory five paired blocks / ten games, r3–10; zero tuning.",
           '',f"Resource payment: human **{m['human']['mean']:.3f}**, compute **{m['compute']['mean']:.3f}**; human−compute **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]** descriptive empirical bootstrap.",
           f"Paired t95% [{s['paired_t_ci95'][0]:+.3f}, {s['paired_t_ci95'][1]:+.3f}]; inclusive upper sign-flip p={s['exact_signflip_p_upper']:.5f}.",
           '', '| Metric | Human mean | Compute mean | Human−compute [bootstrap95%] | Paired t95% |','|---|---:|---:|---|---|']
    for k,x in r['metrics'].items():
        z=x['paired_difference'];lines.append(f"| {k} | {x['human']['mean']:.4f} | {x['compute']['mean']:.4f} | {z['mean']:+.4f} [{z['ci95'][0]:+.4f}, {z['ci95'][1]:+.4f}] | [{z['paired_t_ci95'][0]:+.4f}, {z['paired_t_ci95'][1]:+.4f}] |")
    lines+=['','Block primary differences: '+', '.join(f'{v:+.3f}' for v in m['seed_differences'])+'.',
            f"{r['cached_responses']} cached responses; retry counts {r['invalid_attempt_retries']}; notes {r['notes']}.",
            '', 'Compute−human total firm profit equals the payment difference mechanically; no profit gate or independent evidence.',
            'The screen needs human−compute≥2, positive bootstrap lower and upper p≤.05; at n5 this is equivalent to mean≥2 and all five differences strictly positive. The bootstrap gate is redundant,not independent evidence. DUD if difference≤.5 or upper<2; otherwise ODD.',
            '', 'Limitations: '+ '; '.join(r['limitations'])+'.',
            'The stage game is procurement-equivalent, with passive resource accepting zero and fixed unit supply. No agreement/execution is verified.',
            '', '[Design](../DESIGN_S32.md) · [Scientific results](s32_resource.json) · [Figure](../figures/s32_resource.png)']
    Path(out).write_text('\n'.join(lines)+'\n')
    fig,ax=plt.subplots(figsize=(6,3.4))
    for i,g in enumerate(sorted({x['seed'] for x in r['games']})):
        vals=[next(x['primary']['resource_payment'] for x in r['games'] if x['seed']==g and x['condition']==c) for c in ['human','compute']]
        ax.plot([0,1],vals,'o-',label=str(g),alpha=.8)
    ax.set(xticks=[0,1],xticklabels=['Human labor','Automated compute'],ylabel='Resource payment (r3–10 mean)',ylim=(-.5,20.5),title=f"S32: resource rates, five paired blocks — {r['verdict']}")
    ax.axhspan(18,20,color='gray',alpha=.13,label='Symmetric pure Nash rates')
    ax.legend(fontsize=7,ncol=2);fig.tight_layout();fig.savefig(figure,dpi=150,metadata={'Software':'S32'});plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',default='results/s32_resource.json');p.add_argument('--out',default='results/s32_summary.md');p.add_argument('--figure',default='figures/s32_resource.png');a=p.parse_args();render(a.result,a.out,a.figure)
