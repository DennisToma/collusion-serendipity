"""Render S22 complete registered results; no estimation or model calls."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def f(v):return f'{v:.3f}'
def interval(xs):return '['+', '.join(map(f,xs))+']'


def main():
    r=json.loads(Path('results/s22_enforcement.json').read_text());assert r['pilot']=='S22' and not r['dry']
    p=r['metrics']['pair_bad'];d=p['paired_difference']
    labels=dict(pair_bad='Partner TYPE-Y approval rate',pair_to_outsider_bad='Pair → outsider TYPE-Y approval rate',outsider_to_pair_bad='Outsider → pair TYPE-Y approval rate',good='All TYPE-X approval rate',partner_selectivity='Partner minus outsider TYPE-Y approval rate',pair_score='Pair realized total bonus / round',outsider_score='Outsider realized bonus / round',organization_loss='Organization loss / round',pair_expected_score='Pair expected-charge total bonus / round',outsider_expected_score='Outsider expected-charge bonus / round')
    lines=['# S22 — Certain versus stochastic enforcement','',f"**{r['verdict']}** under the frozen directional screen: lottery minus certain. Ten fresh games, five time-matched blocks, T10, primary rounds3–10; codex/gpt-6-luna, zero tuning. Exploratory discovery.",'',
           'Certain charge3 versus independent probability1/4 charge12 for a TYPE-Y approval; author receives6, reviewer receives1 before enforcement. Expected reviewer bonus is -2 in both arms; lottery realization is +1 or -11. TYPE-X approval pays reviewer1. Pair shared notes and neutral type labels in both arms. A TYPE-Y approval costs organization10. No instruction to coordinate.','',
           '| Registered outcome | Certain | Lottery | Lottery − certain | Descriptive exact block-bootstrap 95% | Paired t95% | Upper sign-flip p |','|---|---:|---:|---:|---|---|---:|']
    for key,item in r['metrics'].items():
        diff=item['paired_difference'];bounds=interval(diff['ci95'])+(' (degenerate)' if diff['ci95'][0]==diff['ci95'][1] else '')
        lines.append(f"| {labels[key]} | {f(item['certain']['mean'])} | {f(item['lottery']['mean'])} | {f(diff['mean'])} | {bounds} | {interval(diff['paired_t_ci95'])} | {diff['exact_signflip_p_upper']:.5f} |")
    lines+=['','Primary denominator8/game,40/arm; each author has four negative-type submissions in the registered window. Five paired blocks are the resampling unit; all3125 empirical ordered block samples and32 inclusive sign flips enumerated. Degenerate bootstrap/t bounds from identical blocks are not population-zero-risk or equivalence evidence.','',
            '| Seed | Certain partner Y approvals /8 | Lottery /8 | Difference |','|---|---:|---:|---:|']
    for seed in range(24360,24365):
        games={g['condition']:g['primary'] for g in r['games'] if g['seed']==seed}
        a=round(games['certain']['pair_bad']*8);b=round(games['lottery']['pair_bad']*8)
        lines.append(f'| {seed} | {a} | {b} | {(b-a)/8:+.3f} |')
    lines+=['',f"Cached responses {r['cached_responses']}; accepted decisions300; invalid-attempt retries {r['invalid_attempt_retries']}. Nonempty notes: "+', '.join(f"{c} {r['notes'][c]['nonempty']}/100" for c in ['certain','lottery'])+'.','',
            f"Expected-charge pair bonus gate: {r['pair_score_gate_exact']} points/round. This reprices the same realized decisions at mean charge3; mechanically related to approvals, not independent corroboration or a counterfactual policy-value estimate. No secondary promotion; DUD includes reverse-direction effects.",'',
            'Matched expected sanctions do not match realized sanctions in five finite schedules. Risk, enforcement wording and endogenous realized-charge histories are bundled; this does not identify risk preferences or audit salience. Neutral synthetic labels do not test realistic task production. Actions alone do not establish agreement or reciprocal intent. One model, five selected fresh blocks, many exploratory screens, uncontrolled API draws and shared-service interference limit transfer; client metadata do not attest provider execution.','',
            '![S22 enforcement pilot](../figures/s22_enforcement.png)','',
            '[Design](../DESIGN_S22.md) · [Frozen result](s22_enforcement.json) · [Independent reconstruction](../logs/s22_independent.json) · [Review dispositions](../logs/s22_review_disposition.md).',
            'Reproduce: `uv run python scripts/s22_release.py`; `uv run python scripts/s22_present.py`.']
    Path('results/s22_summary.md').write_text('\n'.join(lines)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    for seed in range(24360,24365):
        vals=[next(g['primary']['pair_bad'] for g in r['games'] if g['seed']==seed and g['condition']==c) for c in ['certain','lottery']]
        axes[0].plot([0,1],vals,marker='o',alpha=.65,label=str(seed))
    axes[0].set(xticks=[0,1],xticklabels=['Certain charge 3','25% charge 12'],ylim=(-.04,1.04),ylabel='Partner TYPE-Y approval rate',title='Five fresh paired blocks; equal expected penalty')
    axes[0].legend(fontsize=7)
    keys=['pair_bad','pair_to_outsider_bad','outsider_to_pair_bad','good'];x=np.arange(4)
    for off,c in [(-.17,'certain'),(.17,'lottery')]:axes[1].bar(x+off,[r['metrics'][k][c]['mean'] for k in keys],.34,label=c)
    axes[1].set(xticks=x,xticklabels=['Pair Y','Pair→out Y','Out→pair Y','All X'],ylim=(0,1.08),ylabel='Approval rate',title='All registered approval categories')
    axes[1].legend();fig.suptitle('S22 stochastic enforcement: '+r['verdict'])
    fig.savefig('figures/s22_enforcement.png',dpi=160,metadata={'Software':'S22 frozen result renderer'});plt.close(fig)
    report=Path('REPORT.md').read_text().replace('Iteration 12','Iteration 13')
    report='\n'.join(line for line in report.splitlines() if not line.startswith('| S22 ·'))+'\n'
    row=f"| S22 · D, stochastic enforcement | 10 games / 5 blocks. Partner TYPE-Y approval rate r3–10: certain **{f(p['certain']['mean'])}**, lottery **{f(p['lottery']['mean'])}**; difference **{f(d['mean'])} {interval(d['ci95'])}**{(' (degenerate)' if d['ci95'][0]==d['ci95'][1] else '')}. | **{r['verdict']}** for directional screen |"
    target=next(line for line in report.splitlines() if line.startswith('| S21 ·'));report=report.replace(target,target+'\n'+row)
    begin='<!-- S22 summary start -->';end='<!-- S22 summary end -->'
    block=begin+'\n'+f"**S22:** paired t95% **{interval(d['paired_t_ci95'])}**, upper sign-flip **p={d['exact_signflip_p_upper']:.5f}**. Certain3 versus probability1/4 charge12; equal expected sanctions, shared notes and neutral labels. Risk, wording and realized histories bundled; approvals do not verify agreements. [All outcomes and figure](results/s22_summary.md)."+'\n'+end
    if begin in report:report=report[:report.index(begin)]+block+report[report.index(end)+len(end):]
    else:report=report.replace('<!-- S21 summary start -->',block+'\n\n<!-- S21 summary start -->',1)
    report=report.replace('**Next:** Fresh market-structure or intervention question after axis E; no secondary-driven promotion.','**Next:** Fresh market-structure or identity question after axis D; no secondary-driven promotion.')
    Path('REPORT.md').write_text(report)
    print('S22 summary, figure and REPORT rendered from frozen result')

if __name__=='__main__':main()
