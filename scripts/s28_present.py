"""Render frozen S28 statistics and an idempotent report entry, no estimation."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def f(x):return f'{x:.3f}'
def interval(x):return '['+', '.join(map(f,x))+']'

def main():
    r=json.loads(Path('results/s28_payoff.json').read_text());assert r['pilot']=='S28' and not r['dry']
    p=r['metrics']['pair_bad'];d=p['paired_difference']
    lines=['# S28 — Role-attached payoff table','',
           f"**{r['verdict']}** under the frozen reduction screen. Ten fresh two-person games/five blocks,T10,r3–10,codex/gpt-6-luna,zero tuning. All contrasts are prose minus table (positive primary means fewer adverse approvals with the table).",'',
           'Both arms retain the same bonus prose and shared notes. The table arm adds a six-row decomposition identifying reviewer, author, type, decision and both directed payoffs. Incentives, task schedules, roster and initial user prompt match. Added detail, repetition, format, role salience and prompt length are bundled; arithmetic-error correction is not isolated. No instruction to coordinate.','',
           '| Outcome | Prose | Added table | Prose − table | Descriptive block-bootstrap 95% | Paired t95% | Upper sign p |',
           '|---|---:|---:|---:|---|---|---:|']
    for k,m in r['metrics'].items():
        x=m['paired_difference'];lines.append(f"| {k} | {f(m['prose']['mean'])} | {f(m['table']['mean'])} | {f(x['mean'])} | {interval(x['ci95'])} | {interval(x['paired_t_ci95'])} | {x['exact_signflip_p_upper']:.5f} |")
    lines+=['','Primary denominator8/game,40/arm; X denominator8/game too. All3125 ordered empirical bootstrap samples and32 inclusive sign flips per metric. Five blocks are the resampling unit. Bounds are descriptive and can degenerate; no population-zero-risk or equivalence inference. Per-arm JSON t fields retain an inherited name but are one-sample bounds; contrast t fields are paired bounds.','',
            '| Seed | Prose Y approvals /8 | Table /8 | Prose − table |','|---|---:|---:|---:|']
    for seed in range(24520,24525):
        vals={g['condition']:round(g['primary']['pair_bad']*8) for g in r['games'] if g['seed']==seed}
        lines.append(f"| {seed} | {vals['prose']} | {vals['table']} | {(vals['prose']-vals['table'])/8:+.3f} |")
    lines+=['',f"Cached responses: {r['cached_responses']};200 accepted decisions; invalid-attempt retries {r['invalid_attempt_retries']}. Nonempty notes: "+', '.join(f"{c} {r['notes'][c]['nonempty']}/100" for c in ['prose','table'])+'.','',
            'No profit gate: reducing Y approvals reduces pair bonus holding X fixed. Internal and total pair bonus duplicate; bonus and organization loss mechanically follow approval counts. No secondary or reverse-tail promotion. Fresh sparse prose baseline can limit the screen; comparisons with S29 are not a paired replication.','',
            'One model, five exploratory blocks, multiple pilots without adjustment, uncontrolled provider draws/shared-service interference and synthetic types limit transfer. Shared-note content and downstream histories may diverge. Adverse approvals do not verify agreements or intent; no isolated arithmetic-error mechanism. Actual backend tool non-use and provider execution are unverified.','',
            '![S28 payoff table](../figures/s28_payoff.png)','',
            '[Design](../DESIGN_S28.md) · [Frozen result](s28_payoff.json) · [Independent reconstruction](../logs/s28_independent.json) · [Critic dispositions](../logs/s28_review_disposition.md).',
            'Reproduce: `uv run python scripts/s28_release.py`; `uv run python scripts/s28_present.py`.']
    Path('results/s28_summary.md').write_text('\n'.join(lines)+'\n')
    fig,ax=plt.subplots(figsize=(7,4),layout='constrained')
    for seed in range(24520,24525):
        vals=[next(g['primary']['pair_bad'] for g in r['games'] if g['seed']==seed and g['condition']==c) for c in ['prose','table']]
        ax.plot([0,1],vals,'o-',alpha=.7,label=str(seed))
    ax.set(xticks=[0,1],xticklabels=['Prose payoffs','Prose + role table'],ylim=(-.04,1.04),ylabel='Partner TYPE-Y approval rate',title='S28 role-attached payoff table: '+r['verdict'])
    ax.legend(fontsize=8);fig.savefig('figures/s28_payoff.png',dpi=160,metadata={'Software':'S28 frozen result renderer'});plt.close(fig)
    report=Path('REPORT.md').read_text().replace('Iteration 18 (S28 registered; live results pending)','Iteration 18')
    report='\n'.join(x for x in report.splitlines() if not x.startswith('| S28 ·'))+'\n'
    row=f"| S28 · own, role payoff table | 10 games /5 blocks. Partner Y approval rate r3–10: prose **{f(p['prose']['mean'])}**, table **{f(p['table']['mean'])}**; prose−table **{f(d['mean'])} {interval(d['ci95'])}**. | **{r['verdict']}** for reduction screen |"
    target=next(x for x in report.splitlines() if x.startswith('| S29 ·'));report=report.replace(target,target+'\n'+row)
    begin='<!-- S28 summary start -->';end='<!-- S28 summary end -->'
    block=begin+'\n'+f"**S28:** paired t95% **{interval(d['paired_t_ci95'])}**, upper sign-flip **p={d['exact_signflip_p_upper']:.5f}**. Extra role-attached table with shared notes in both arms; repetition/format/detail bundled. No isolated arithmetic mechanism or agreement claim. [All outcomes and figure](results/s28_summary.md)."+'\n'+end
    if begin in report:report=report[:report.index(begin)]+block+report[report.index(end)+len(end):]
    else:report=report.replace('<!-- S29 summary start -->',block+'\n\n<!-- S29 summary start -->',1)
    Path('REPORT.md').write_text(report)
    print('S28 complete summary, figure and REPORT rendered')

if __name__=='__main__':main()
