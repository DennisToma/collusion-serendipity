"""Render complete frozen S27 statistics without estimation or model calls."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def f(x):return f'{x:.3f}'
def interval(x):return '['+', '.join(map(f,x))+']'
def main():
    r=json.loads(Path('results/s27_concentration.json').read_text());assert r['pilot']=='S27' and not r['dry']
    p=r['metrics']['pair_bad'];d=p['paired_difference']
    lines=['# S27 — Team concentration','',f"**{r['verdict']}** under the frozen directional screen. Ten fresh games/five blocks,T10,r3–10,codex/gpt-6-luna,zero tuning. Two minus three active employees. Pair-directed stage payoffs, task schedules and shared-note access fixed.",'',
           'Removing the outsider also removes their reviews, public history and income opportunities, and reduces the pair\'s action count. This is a team-size intervention; competition, workload, reciprocity and schema effects are not separated. TYPE-Y approval pays author6/reviewer-2 and costs organization10; TYPE-X approval pays author6/reviewer1. No instruction to coordinate.','',
           '| Outcome | Three | Two | Two − three | Descriptive block-bootstrap 95% | Paired t95% | Upper sign p |','|---|---:|---:|---:|---|---|---:|']
    for k,m in r['metrics'].items():
        x=m['paired_difference'];lines.append(f"| {k} | {f(m['three']['mean'])} | {f(m['two']['mean'])} | {f(x['mean'])} | {interval(x['ci95'])} | {interval(x['paired_t_ci95'])} | {x['exact_signflip_p_upper']:.5f} |")
    lines+=['','Primary denominator8/game,40/arm; X pair-directed approval denominator8/game too. All3125 ordered empirical bootstrap samples and32 inclusive sign flips per metric. Intervals are descriptive; degenerate bounds are not population-zero-risk or equivalence evidence.','',
            '| Seed | Three partner Y approvals /8 | Two /8 | Difference |','|---|---:|---:|---:|']
    for seed in range(24440,24445):
        vals={g['condition']:round(g['primary']['pair_bad']*8) for g in r['games'] if g['seed']==seed}
        lines.append(f"| {seed} | {vals['three']} | {vals['two']} | {(vals['two']-vals['three'])/8:+.3f} |")
    lines+=['',f"Cached responses: {r['cached_responses']};250 accepted decisions; invalid-attempt retries {r['invalid_attempt_retries']}. Nonempty notes: "+', '.join(f"{c} {r['notes'][c]['nonempty']}/100" for c in ['three','two'])+'.','',
            f"Pair-internal bonus gate: {r['pair_score_gate_exact']} points/round. This gate is mechanically related to approvals, not independent corroboration. Pair total bonus includes outsider edges only in three; total organization loss has fewer possible edges in two. Neither is a like-for-like directed payoff comparison.",'',
            'Five exploratory blocks, many pilots without multiplicity adjustment, one model, uncontrolled provider draws/shared-service interference and synthetic neutral work types limit transfer. Adverse approvals do not verify agreements or reciprocal intent. Backend tools instruction-restricted but not disabled; actual tool non-use unverified. Client metadata do not attest provider execution.','',
            '![S27 concentration](../figures/s27_concentration.png)','',
            '[Design](../DESIGN_S27.md) · [Frozen result](s27_concentration.json) · [Independent reconstruction](../logs/s27_independent.json) · [Critic dispositions](../logs/s27_review_disposition.md).','Reproduce: `uv run python scripts/s27_release.py`; `uv run python scripts/s27_present.py`.']
    Path('results/s27_summary.md').write_text('\n'.join(lines)+'\n')
    fig,ax=plt.subplots(figsize=(7,4),layout='constrained')
    for seed in range(24440,24445):
        vals=[next(g['primary']['pair_bad'] for g in r['games'] if g['seed']==seed and g['condition']==c) for c in ['three','two']]
        ax.plot([0,1],vals,'o-',alpha=.7,label=str(seed))
    ax.set(xticks=[0,1],xticklabels=['Three employees','Two employees'],ylim=(-.04,1.04),ylabel='Partner TYPE-Y approval rate',title='S27 team concentration: '+r['verdict'])
    ax.legend(fontsize=8);fig.savefig('figures/s27_concentration.png',dpi=160,metadata={'Software':'S27 frozen result renderer'});plt.close(fig)
    report=Path('REPORT.md').read_text().replace('Iteration 15','Iteration 16')
    report='\n'.join(x for x in report.splitlines() if not x.startswith('| S27 ·'))+'\n'
    row=f"| S27 · B, team concentration | 10 games /5 blocks. Partner Y approval rate r3–10: three **{f(p['three']['mean'])}**, two **{f(p['two']['mean'])}**; difference **{f(d['mean'])} {interval(d['ci95'])}**. | **{r['verdict']}** for directional screen |"
    target=next(x for x in report.splitlines() if x.startswith('| S25 ·'));report=report.replace(target,target+'\n'+row)
    begin='<!-- S27 summary start -->';end='<!-- S27 summary end -->'
    block=begin+'\n'+f"**S27:** paired t95% **{interval(d['paired_t_ci95'])}**, upper sign-flip **p={d['exact_signflip_p_upper']:.5f}**. Two versus three active employees; pair payoffs and shared notes fixed. Team size bundles outsider interaction, workload and history dimension; approvals do not verify agreement. [All outcomes and figure](results/s27_summary.md)."+'\n'+end
    if begin in report:report=report[:report.index(begin)]+block+report[report.index(end)+len(end):]
    else:report=report.replace('<!-- S25 summary start -->',block+'\n\n<!-- S25 summary start -->',1)
    report=report.replace('**Next:** Fresh market-structure or channel question after own; no secondary-driven promotion.','**Next:** Fresh channel or other-world question after B; no secondary-driven promotion.')
    Path('REPORT.md').write_text(report)
    print('S27 complete summary, figure and REPORT rendered')
if __name__=='__main__':main()
