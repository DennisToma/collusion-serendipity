"""Render only S38 saved results; scientific analysis is separate."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def render(result='results/s38_horizon.json',out='results/s38_summary.md',figure='figures/s38_horizon.png'):
    r=json.loads(Path(result).read_text());m=r['metrics']['resource_payment'];s=m['paired_difference']
    if r['dry'] and (Path(out).resolve()==Path('results/s38_summary.md').resolve() or Path(figure).resolve()==Path('figures/s38_horizon.png').resolve()):raise ValueError('No dry publication')
    if not r['dry']:
        from scripts.s38_analyze import analyze
        if analyze('data/s38_horizon')!=r:raise ValueError('Result differs from full archive validation')
        from scripts.s38_independent import verify
        verify('data/s38_horizon',result)
    lines=['# S38 — Known versus hidden final round','',f"**{r['verdict']}**, exploratory five paired blocks / ten games, r3–10; zero tuning.",
           '',f"Worker take-home pay: known **{m['known']['mean']:.3f}**, hidden **{m['hidden']['mean']:.3f}**; known−hidden **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]** descriptive empirical bootstrap.",
           f"Paired t95% [{s['paired_t_ci95'][0]:+.3f}, {s['paired_t_ci95'][1]:+.3f}]; inclusive upper sign-flip p={s['exact_signflip_p_upper']:.5f}.",
           '', '| Metric | Known mean | Hidden mean | Known−hidden [bootstrap95%] | Paired t95% |','|---|---:|---:|---|---|']
    for k,x in r['metrics'].items():
        z=x['paired_difference'];lines.append(f"| {k} | {x['known']['mean']:.4f} | {x['hidden']['mean']:.4f} | {z['mean']:+.4f} [{z['ci95'][0]:+.4f}, {z['ci95'][1]:+.4f}] | [{z['paired_t_ci95'][0]:+.4f}, {z['paired_t_ci95'][1]:+.4f}] |")
    lines+=['','Block primary differences: '+', '.join(f'{v:+.3f}' for v in m['seed_differences'])+'.',
            f"{r['cached_responses']} cached responses; retry counts {r['invalid_attempt_retries']}; notes {r['notes']}.",
            '', 'At fixed realized productivity20, total firm profit plus worker take-home is20 in each round; firm profit is the exact wage complement.',
            'The screen needs known−hidden≥2, positive bootstrap lower and upper p≤.05; at n5 this is equivalent to mean≥2 and all five differences strictly positive. The bootstrap gate is redundant,not independent evidence. DUD if difference≤0 or upper<2; otherwise ODD.',
            '', 'Limitations: '+ '; '.join(r['limitations'])+'.',
            'The stage game has passive labor accepting zero and fixed unit supply. No agreement/execution is verified.',
            '', '[Design](../DESIGN_S38.md) · [Scientific results](s38_horizon.json) · [Figure](../figures/s38_horizon.png)']
    Path(out).write_text('\n'.join(lines)+'\n')
    fig,ax=plt.subplots(figsize=(6,3.4))
    for i,g in enumerate(sorted({x['seed'] for x in r['games']})):
        vals=[next(x['primary']['resource_payment'] for x in r['games'] if x['seed']==g and x['condition']==c) for c in ['known','hidden']]
        ax.plot([0,1],vals,'o-',label=str(g),alpha=.8)
    ax.set(xticks=[0,1],xticklabels=['Known final round: 10','Hidden final round'],ylabel='Worker take-home (r3–10 mean)',ylim=(-.5,20.5),title=f"S38: worker earnings, five paired blocks — {r['verdict']}")
    ax.axhspan(18,20,color='gray',alpha=.13,label='Static Nash wage range, both arms')
    ax.legend(fontsize=7,ncol=2);fig.tight_layout();fig.savefig(figure,dpi=150,metadata={'Software':'S38'});plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',default='results/s38_horizon.json');p.add_argument('--out',default='results/s38_summary.md');p.add_argument('--figure',default='figures/s38_horizon.png');a=p.parse_args();render(a.result,a.out,a.figure)
