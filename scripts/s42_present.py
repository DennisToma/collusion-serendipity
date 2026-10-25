"""Render only S42 saved results; scientific analysis is separate."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def render(result='results/s42_entry.json',out='results/s42_summary.md',figure='figures/s42_entry.png'):
    r=json.loads(Path(result).read_text());m=r['metrics']['resource_payment'];s=m['paired_difference']
    if r['dry'] and (Path(out).resolve()==Path('results/s42_summary.md').resolve() or Path(figure).resolve()==Path('figures/s42_entry.png').resolve()):raise ValueError('No dry publication')
    if not r['dry']:
        from scripts.s42_analyze import analyze
        if analyze('data/s42_entry')!=r:raise ValueError('Result differs from full archive validation')
        from scripts.s42_independent import verify
        verify('data/s42_entry',result)
    lines=['# S42 — Surprise employer entry','',f"**{r['verdict']}**, exploratory five paired blocks / ten games, r7–10; zero tuning.",
           '',f"Worker take-home pay: entry **{m['entry']['mean']:.3f}**, control **{m['control']['mean']:.3f}**; entry−control **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]** descriptive empirical bootstrap.",
           f"Paired t95% [{s['paired_t_ci95'][0]:+.3f}, {s['paired_t_ci95'][1]:+.3f}]; inclusive upper sign-flip p={s['exact_signflip_p_upper']:.5f}.",
           '', '| Metric | Entry mean | Control mean | Entry−control [bootstrap95%] | Paired t95% |','|---|---:|---:|---|---|']
    for k,x in r['metrics'].items():
        z=x['paired_difference'];lines.append(f"| {k} | {x['entry']['mean']:.4f} | {x['control']['mean']:.4f} | {z['mean']:+.4f} [{z['ci95'][0]:+.4f}, {z['ci95'][1]:+.4f}] | [{z['paired_t_ci95'][0]:+.4f}, {z['paired_t_ci95'][1]:+.4f}] |")
    lines+=['','Block primary differences: '+', '.join(f'{v:+.3f}' for v in m['seed_differences'])+'.',
            f"{r['cached_responses']} cached responses; retry counts {r['invalid_attempt_retries']}; notes {r['notes']}.",
            '', 'At fixed realized productivity20, total firm profit plus worker take-home is20 in each round; firm profit is the exact wage complement.',
            'The screen needs entry−control≥4, positive bootstrap lower and upper p≤.05; at n5 this is equivalent to mean≥4 and all five differences strictly positive. The bootstrap gate is redundant,not independent evidence. DUD if difference≤1 or upper<4; otherwise ODD.',
            '', 'Limitations: '+ '; '.join(r['limitations'])+'.',
            'The stage game has passive labor accepting zero and fixed unit supply. No agreement/execution is verified. Total firm profit complements wage and is not separate evidence; per-firm offered-wage/regret means average different populations after entry.',
            '', '[Design](../DESIGN_S42.md) · [Scientific results](s42_entry.json) · [Figure](../figures/s42_entry.png)']
    lines+=['', 'preentry_payment is the r1–5 wage baseline; wage_change is postr7–10 minus prer1–5. The paired wage_change contrast is descriptive difference-in-differences; it does not change the frozen primary screen.', '', '| Block | Entry wage | Control wage | Difference |','|---|---:|---:|---:|']
    for seed in sorted({g['seed'] for g in r['games']}):
        vals={g['condition']:g['primary']['resource_payment'] for g in r['games'] if g['seed']==seed}
        lines.append(f"| {seed} | {vals['entry']:.3f} | {vals['control']:.3f} | {vals['entry']-vals['control']:+.3f} |")
    Path(out).write_text('\n'.join(lines)+'\n')
    fig,ax=plt.subplots(figsize=(6,3.4))
    for i,g in enumerate(sorted({x['seed'] for x in r['games']})):
        vals=[next(x['primary']['resource_payment'] for x in r['games'] if x['seed']==g and x['condition']==c) for c in ['entry','control']]
        ax.plot([0,1],vals,'o-',label=str(g),alpha=.8)
    ax.set(xticks=[0,1],xticklabels=['Third employer from round6','Duopoly throughout'],ylabel='Worker take-home (r7–10 mean)',ylim=(-.5,20.5),title=f"S42: worker earnings, five paired blocks — {r['verdict']}")
    ax.axhspan(18,20,color='gray',alpha=.13,label='Duopoly static Nash wages18–20')
    ax.plot([-.1,.1],[19,19],color='black',linewidth=2,label='Tripoly minimum static Nash wage19')
    ax.legend(fontsize=7,ncol=2);fig.tight_layout();fig.savefig(figure,dpi=150,metadata={'Software':'S42'});plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',default='results/s42_entry.json');p.add_argument('--out',default='results/s42_summary.md');p.add_argument('--figure',default='figures/s42_entry.png');a=p.parse_args();render(a.result,a.out,a.figure)
