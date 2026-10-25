"""Render the frozen S33 results and exploratory report row."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def f(x):return f'{x:.3f}'
def interval(x):return '['+', '.join(map(f,x))+']'
def main():
    r=json.loads(Path('results/s33_leniency.json').read_text());assert r['pilot']=='S33' and not r['dry']
    p=r['metrics']['pair_bad'];d=p['paired_difference']
    lines=['# S33 — Private reporting with contingent amnesty','',f"**{r['verdict']}** under the frozen directional reduction screen. Ten fresh games/five blocks,T10,r3–10,codex/gpt-6-luna,zero tuning.",'',
        'Both arms have shared partner notepads and the same private report flag. Baseline reports have no payoff effect. Amnesty activates contingent extra6 charges on a partner adverse review and waives the reporter ordinary3 charge only when the reported partner actually approves TYPE-Y. Both reports can qualify; extra charges cannot be waived. Reviews and requests are simultaneous; raw flags remain private. This intervention bundles reporting, sanctions, immunity and wording. It does not isolate leniency or verify collusion.','',
        '| Outcome | Baseline | Amnesty | Baseline − amnesty | Descriptive bootstrap 95% | Paired t95% | Upper sign p |','|---|---:|---:|---:|---|---|---:|']
    for k,m in r['metrics'].items():
        x=m['paired_difference'];lines.append(f"| {k} | {f(m['baseline']['mean'])} | {f(m['amnesty']['mean'])} | {f(x['mean'])} | {interval(x['ci95'])} | {interval(x['paired_t_ci95'])} | {x['exact_signflip_p_upper']:.5f} |")
    lines+=['','Y/X approval denominators8/game,40/arm. Other metrics are per round; report count per round ranges0..2. All3125 ordered block-bootstrap samples and32 inclusive sign flips. Degenerate empirical bounds do not prove zero population risk or equivalence. Positive contrast always denotes baseline minus amnesty, including secondaries. No secondary/reverse-tail promotion.','',
        '| Seed | Baseline Y approvals /8 | Amnesty /8 | Reduction |','|---|---:|---:|---:|']
    for seed in range(24640,24645):
        vals={g['condition']:round(g['primary']['pair_bad']*8) for g in r['games'] if g['seed']==seed}
        lines.append(f"| {seed} | {vals['baseline']} | {vals['amnesty']} | {(vals['baseline']-vals['amnesty'])/8:+.3f} |")
    lines+=['',f"Cached responses: {r['cached_responses']};200 accepted decisions; invalid-attempt retries {r['invalid_attempt_retries']}. Nonempty notes: "+', '.join(f"{c} {r['notes'][c]['nonempty']}/100" for c in ['baseline','amnesty'])+'.','',
        'Five exploratory blocks, many pilots without multiplicity adjustment, one model, uncontrolled draws/shared-service interference, synthetic types and possible fresh-control floor effects limit transfer. Approvals and notes alone do not verify intent or agreement. Known local CLI inputs are guarded against an immutable closure baseline; effective configuration/provider execution and tool non-use remain unattested.','',
        '![S33 reporting](../figures/s33_leniency.png)','',
        '[Design](../DESIGN_S33.md) · [Frozen result](s33_leniency.json) · [Independent reconstruction](../logs/s33_independent.json) · [Critic dispositions](../logs/s33_review_disposition.md).','Reproduce: `uv run python scripts/s33_release.py`; `uv run python scripts/s33_present.py`.']
    Path('results/s33_summary.md').write_text('\n'.join(lines)+'\n')
    fig,ax=plt.subplots(figsize=(7,4),layout='constrained')
    for seed in range(24640,24645):
        vals=[next(g['primary']['pair_bad'] for g in r['games'] if g['seed']==seed and g['condition']==c) for c in ['baseline','amnesty']]
        ax.plot([0,1],vals,'o-',alpha=.7,label=str(seed))
    ax.set(xticks=[0,1],xticklabels=['Inert report flag','Active reporting/amnesty'],ylim=(-.04,1.04),ylabel='Partner TYPE-Y approval rate',title='S33 reporting package: '+r['verdict']);ax.legend(fontsize=8)
    fig.savefig('figures/s33_leniency.png',dpi=160,metadata={'Software':'S33 frozen result renderer'});plt.close(fig)
    report=Path('REPORT.md').read_text();report='\n'.join(x for x in report.splitlines() if not x.startswith('| S33 ·'))+'\n'
    row=f"| S33 · D, reporting/amnesty | 10 games /5 blocks. Partner Y approval rate r3–10: baseline **{f(p['baseline']['mean'])}**, amnesty **{f(p['amnesty']['mean'])}**; reduction **{f(d['mean'])} {interval(d['ci95'])}**. | **{r['verdict']}** for reduction screen |"
    target=next(x for x in report.splitlines() if x.startswith('| S32 ·'));report=report.replace(target,target+'\n'+row)
    begin='<!-- S33 summary start -->';end='<!-- S33 summary end -->';block=begin+'\n'+f"**S33:** paired t95% **{interval(d['paired_t_ci95'])}**, upper sign-flip **p={d['exact_signflip_p_upper']:.5f}**. Private report flag in both arms; active rule bundles contingent sanctions and immunity. Shared partner notes both arms. No isolated leniency or collusion claim. [All outcomes and figure](results/s33_summary.md)."+'\n'+end
    if begin in report:report=report[:report.index(begin)]+block+report[report.index(end)+len(end):]
    else:report=report.replace('<!-- S32 summary start -->',block+'\n\n<!-- S32 summary start -->',1)
    report=report.replace('2026-10-24 · Iteration 20','2026-10-25 · Iteration 21')
    Path('REPORT.md').write_text(report)
    print('S33 result, figure and REPORT rendered')
if __name__=='__main__':main()
