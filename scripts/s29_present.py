"""Render complete frozen S29 statistics without estimation or model calls."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def f(x):return f'{x:.3f}'
def interval(x):return '['+', '.join(map(f,x))+']'
def main():
    r=json.loads(Path('results/s29_notepad.json').read_text());assert r['pilot']=='S29' and not r['dry']
    p=r['metrics']['pair_bad'];d=p['paired_difference']
    lines=['# S29 — Partner notepad delivery','',f"**{r['verdict']}** under the frozen directional screen. Ten fresh games/five blocks,T10,r3–10,codex/gpt-6-luna,zero tuning. Shared minus self-only notepads in two-person teams. Roster, stage payoffs, task schedules and own-note persistence fixed.",'',
           'Both arms retain own notes. Shared additionally delivers partner notes with a truthful readability sentence. Delivery, expectations, memory volume and downstream histories are bundled; public actions remain visible in both arms. TYPE-Y approval pays author6/reviewer-2 and costs organization10; TYPE-X approval pays author6/reviewer1. No instruction to coordinate.','',
           '| Outcome | Self-only | Shared | Shared − self | Descriptive block-bootstrap 95% | Paired t95% | Upper sign p |','|---|---:|---:|---:|---|---|---:|']
    for k,m in r['metrics'].items():
        x=m['paired_difference'];lines.append(f"| {k} | {f(m['self']['mean'])} | {f(m['shared']['mean'])} | {f(x['mean'])} | {interval(x['ci95'])} | {interval(x['paired_t_ci95'])} | {x['exact_signflip_p_upper']:.5f} |")
    lines+=['','Primary denominator8/game,40/arm; X pair-directed approval denominator8/game too. All3125 ordered empirical bootstrap samples and32 inclusive sign flips per metric. Intervals are descriptive; degenerate bounds are not population-zero-risk or equivalence evidence.','',
            '| Seed | Self-only partner Y approvals /8 | Shared /8 | Difference |','|---|---:|---:|---:|']
    for seed in range(24480,24485):
        vals={g['condition']:round(g['primary']['pair_bad']*8) for g in r['games'] if g['seed']==seed}
        lines.append(f"| {seed} | {vals['self']} | {vals['shared']} | {(vals['shared']-vals['self'])/8:+.3f} |")
    lines+=['',f"Cached responses: {r['cached_responses']};200 accepted decisions; invalid-attempt retries {r['invalid_attempt_retries']}. Nonempty notes: "+', '.join(f"{c} {r['notes'][c]['nonempty']}/100" for c in ['self','shared'])+'.','',
            f"Pair-internal bonus gate: {r['pair_score_gate_exact']} points/round. This gate is mechanically related to approvals, not independent corroboration. Pair total bonus equals internal bonus in both arms. These redundant archive fields and the bonus gate are not independent evidence of agreement.",'',
            'Five exploratory blocks, many pilots without multiplicity adjustment, one model, uncontrolled provider draws/shared-service interference and synthetic neutral work types limit transfer. Adverse approvals do not verify agreements or reciprocal intent. Backend tools instruction-restricted but not disabled; actual tool non-use unverified. Client metadata do not attest provider execution.','',
            '![S29 notepad](../figures/s29_notepad.png)','',
            '[Design](../DESIGN_S29.md) · [Frozen result](s29_notepad.json) · [Independent reconstruction](../logs/s29_independent.json) · [Critic dispositions](../logs/s29_review_disposition.md).','Reproduce: `uv run python scripts/s29_release.py`; `uv run python scripts/s29_present.py`.']
    Path('results/s29_summary.md').write_text('\n'.join(lines)+'\n')
    fig,ax=plt.subplots(figsize=(7,4),layout='constrained')
    for seed in range(24480,24485):
        vals=[next(g['primary']['pair_bad'] for g in r['games'] if g['seed']==seed and g['condition']==c) for c in ['self','shared']]
        ax.plot([0,1],vals,'o-',alpha=.7,label=str(seed))
    ax.set(xticks=[0,1],xticklabels=['Self-only notes','Shared notes'],ylim=(-.04,1.04),ylabel='Partner TYPE-Y approval rate',title='S29 partner notepad: '+r['verdict'])
    ax.legend(fontsize=8);fig.savefig('figures/s29_notepad.png',dpi=160,metadata={'Software':'S29 frozen result renderer'});plt.close(fig)
    report=Path('REPORT.md').read_text().replace('Iteration 17 (S29 registered; live results pending)','Iteration 17').replace('Iteration 16','Iteration 17')
    report='\n'.join(x for x in report.splitlines() if not x.startswith('| S29 ·'))+'\n'
    row=f"| S29 · C, partner notepad | 10 games /5 blocks. Partner Y approval rate r3–10: self **{f(p['self']['mean'])}**, shared **{f(p['shared']['mean'])}**; difference **{f(d['mean'])} {interval(d['ci95'])}**. | **{r['verdict']}** for directional screen |"
    target=next(x for x in report.splitlines() if x.startswith('| S27 ·'));report=report.replace(target,target+'\n'+row)
    begin='<!-- S29 summary start -->';end='<!-- S29 summary end -->'
    block=begin+'\n'+f"**S29:** paired t95% **{interval(d['paired_t_ci95'])}**, upper sign-flip **p={d['exact_signflip_p_upper']:.5f}**. Shared versus self-only notepads in fixed two-person teams. Delivery and stated readability bundled; public actions visible in both arms; approvals do not verify agreement. [All outcomes and figure](results/s29_summary.md)."+'\n'+end
    if begin in report:report=report[:report.index(begin)]+block+report[report.index(end)+len(end):]
    else:report=report.replace('<!-- S27 summary start -->',block+'\n\n<!-- S27 summary start -->',1)
    report=report.replace('**Next:** Fresh channel or other-world question after B; no secondary-driven promotion.','**Next:** Fresh other-world or own question after C; no secondary-driven promotion.')
    Path('REPORT.md').write_text(report)
    print('S29 complete summary, figure and REPORT rendered')
if __name__=='__main__':main()
