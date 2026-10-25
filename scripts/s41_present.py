"""Render only S41 saved results; scientific analysis is separate."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def report_row(r):
    m=r['metrics']['resource_payment'];s=m['paired_difference']
    return (f"| S41 · own, wage tick size | 10 games /5 blocks. Paid wage r3–10: fine **{m['fine']['mean']:.3f}**, coarse **{m['coarse']['mean']:.3f}**; fine−coarse **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]**. | **{r['verdict']}** for two-unit increase screen |")


def render(result='results/s41_ticksize.json',out='results/s41_summary.md',figure='figures/s41_ticksize.png'):
    r=json.loads(Path(result).read_text());m=r['metrics']['resource_payment'];s=m['paired_difference']
    if r['dry'] and (Path(out).resolve()==Path('results/s41_summary.md').resolve() or Path(figure).resolve()==Path('figures/s41_ticksize.png').resolve()):raise ValueError('No dry publication')
    if not r['dry']:
        from scripts.s41_analyze import analyze
        if analyze('data/s41_ticksize')!=r:raise ValueError('Result differs from full archive validation')
        from scripts.s41_independent import verify
        verify('data/s41_ticksize',result)
    lines=['# S41 — Half-unit versus unit wage grid','',f"**{r['verdict']}**, exploratory five paired blocks / ten games, r3–10; zero tuning.",
           '',f"Worker take-home pay: fine **{m['fine']['mean']:.3f}**, coarse **{m['coarse']['mean']:.3f}**; fine−coarse **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]** descriptive empirical bootstrap.",
           f"Paired t95% [{s['paired_t_ci95'][0]:+.3f}, {s['paired_t_ci95'][1]:+.3f}]; inclusive upper sign-flip p={s['exact_signflip_p_upper']:.5f}.",
           '', '| Metric | Fine mean | Coarse mean | Fine−coarse [bootstrap95%] | Paired t95% |','|---|---:|---:|---|---|']
    for k,x in r['metrics'].items():
        z=x['paired_difference'];lines.append(f"| {k} | {x['fine']['mean']:.4f} | {x['coarse']['mean']:.4f} | {z['mean']:+.4f} [{z['ci95'][0]:+.4f}, {z['ci95'][1]:+.4f}] | [{z['paired_t_ci95'][0]:+.4f}, {z['paired_t_ci95'][1]:+.4f}] |")
    lines+=['','Block primary differences: '+', '.join(f'{v:+.3f}' for v in m['seed_differences'])+'.',
            f"{r['cached_responses']} cached responses; retry counts {r['invalid_attempt_retries']}; notes {r['notes']}.",
            '', 'At fixed realized productivity20, total firm profit plus worker take-home is20 in each round; firm profit is the exact wage complement.',
            'The screen needs fine−coarse≥2, positive bootstrap lower and upper p≤.05; at n5 this is equivalent to mean≥2 and all five differences strictly positive. The bootstrap gate is redundant,not independent evidence. DUD if difference≤0 or upper<2; otherwise ODD.',
            '', r['interval_field_convention']+'.', '', 'Limitations: '+ '; '.join(r['limitations'])+'.',
            'The stage game has passive labor accepting zero and fixed unit supply. No agreement/execution is verified.',
            '', '[Design](../DESIGN_S41.md) · [Scientific results](s41_ticksize.json) · [Figure](../figures/s41_ticksize.png)']
    Path(out).write_text('\n'.join(lines)+'\n')
    fig,ax=plt.subplots(figsize=(6,3.4))
    for i,g in enumerate(sorted({x['seed'] for x in r['games']})):
        vals=[next(x['primary']['resource_payment'] for x in r['games'] if x['seed']==g and x['condition']==c) for c in ['fine','coarse']]
        ax.plot([0,1],vals,'o-',label=str(g),alpha=.8)
    ax.set(xticks=[0,1],xticklabels=['Half-unit wage grid','Unit wage grid'],ylabel='Worker take-home (r3–10 mean)',ylim=(-.5,20.5),title=f"S41: worker earnings, five paired blocks — {r['verdict']}")
    ax.axhspan(18,20,color='gray',alpha=.13,label='Coarse static Nash wage range')
    ax.axhline(19,color='black',linestyle=':',linewidth=1,label='Fine minimum static Nash wage: 19')
    ax.legend(fontsize=7,ncol=2);fig.tight_layout();fig.savefig(figure,dpi=150,metadata={'Software':'S41'});plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',default='results/s41_ticksize.json');p.add_argument('--out',default='results/s41_summary.md');p.add_argument('--figure',default='figures/s41_ticksize.png');a=p.parse_args();render(a.result,a.out,a.figure)
