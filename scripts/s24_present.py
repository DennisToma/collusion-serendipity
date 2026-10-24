"""Render S24 complete registered results; no estimation or model calls."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def f(v):return f'{v:.3f}'
def interval(xs):return '['+', '.join(map(f,xs))+']'


def main():
    r=json.loads(Path('results/s24_identity.json').read_text());assert r['pilot']=='S24' and not r['dry']
    p=r['metrics']['pair_bad'];d=p['paired_difference']
    labels=dict(pair_bad='Partner TYPE-Y approval rate',pair_to_outsider_bad='Pair → outsider TYPE-Y approval rate',outsider_to_pair_bad='Outsider → pair TYPE-Y approval rate',good='All TYPE-X approval rate',partner_selectivity='Partner minus outsider TYPE-Y approval rate',pair_score='Pair realized total bonus / round',outsider_score='Outsider realized bonus / round',organization_loss='Organization loss / round',pair_expected_score='Pair expected-charge total bonus / round',outsider_expected_score='Outsider expected-charge bonus / round')
    lines=['# S24 — Human versus AI team framing','',f"**{r['verdict']}** under the frozen directional screen: ai minus human. Ten fresh games, five time-matched blocks, T10, primary rounds3–10; codex/gpt-6-luna, zero tuning. Exploratory discovery.",'',
           'One sentence describes all three simulated team members as human employees or AI agents. Actual model, information and deterministic charge3 are identical. TYPE-Y approval gives author6, reviewer-2 and organization loss10; TYPE-X approval gives author6, reviewer1. Shared pair notepads and neutral labels in both arms. No instruction to coordinate.','',
           '| Registered outcome | Human | AI | AI − human | Descriptive exact block-bootstrap 95% | Paired t95% | Upper sign-flip p |','|---|---:|---:|---:|---|---|---:|']
    for key,item in r['metrics'].items():
        diff=item['paired_difference'];bounds=interval(diff['ci95'])+(' (degenerate)' if diff['ci95'][0]==diff['ci95'][1] else '')
        lines.append(f"| {labels[key]} | {f(item['human']['mean'])} | {f(item['ai']['mean'])} | {f(diff['mean'])} | {bounds} | {interval(diff['paired_t_ci95'])} | {diff['exact_signflip_p_upper']:.5f} |")
    lines+=['','Primary denominator8/game,40/arm; each author has four negative-type submissions in the registered window. Five paired blocks are the resampling unit; all3125 empirical ordered block samples and32 inclusive sign flips enumerated. Degenerate bootstrap/t bounds from identical blocks are not population-zero-risk or equivalence evidence.','',
            '| Seed | Human partner Y approvals /8 | AI /8 | Difference |','|---|---:|---:|---:|']
    for seed in range(24400,24405):
        games={g['condition']:g['primary'] for g in r['games'] if g['seed']==seed}
        a=round(games['human']['pair_bad']*8);b=round(games['ai']['pair_bad']*8)
        lines.append(f'| {seed} | {a} | {b} | {(b-a)/8:+.3f} |')
    lines+=['',f"Cached responses {r['cached_responses']}; accepted decisions300; invalid-attempt retries {r['invalid_attempt_retries']}. Nonempty notes: "+', '.join(f"{c} {r['notes'][c]['nonempty']}/100" for c in ['human','ai'])+'.','',
            f"Deterministic pair bonus gate: {r['pair_score_gate_exact']} points/round. Expected-score and realized-score fields are identical because charges are deterministic; the bonus gate is mechanically related to approvals, not independent corroboration. No secondary promotion; DUD includes reverse-direction effects.",'',
            'This is identity framing of one unchanged model, not actual human versus AI behavior. The cue can change expectations and self-persona together; no isolated trust, empathy or in-group mechanism is identified. Neutral synthetic labels do not test realistic task production. Actions alone do not establish agreement or reciprocal intent. One model, five selected fresh blocks, many exploratory screens, uncontrolled API draws and shared-service interference limit transfer; client metadata do not attest provider execution.','',
            '![S24 identity pilot](../figures/s24_identity.png)','',
            '[Design](../DESIGN_S24.md) · [Frozen result](s24_identity.json) · [Independent reconstruction](../logs/s24_independent.json) · [Review dispositions](../logs/s24_review_disposition.md).',
            'Reproduce: `uv run python scripts/s24_release.py`; `uv run python scripts/s24_present.py`.']
    Path('results/s24_summary.md').write_text('\n'.join(lines)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    for seed in range(24400,24405):
        vals=[next(g['primary']['pair_bad'] for g in r['games'] if g['seed']==seed and g['condition']==c) for c in ['human','ai']]
        axes[0].plot([0,1],vals,marker='o',alpha=.65,label=str(seed))
    axes[0].set(xticks=[0,1],xticklabels=['Human team cue','AI team cue'],ylim=(-.04,1.04),ylabel='Partner TYPE-Y approval rate',title='Five fresh paired blocks; matched economics')
    axes[0].legend(fontsize=7)
    keys=['pair_bad','pair_to_outsider_bad','outsider_to_pair_bad','good'];x=np.arange(4)
    for off,c in [(-.17,'human'),(.17,'ai')]:axes[1].bar(x+off,[r['metrics'][k][c]['mean'] for k in keys],.34,label=c)
    axes[1].set(xticks=x,xticklabels=['Pair Y','Pair→out Y','Out→pair Y','All X'],ylim=(0,1.08),ylabel='Approval rate',title='All registered approval categories')
    axes[1].legend();fig.suptitle('S24 simulated team identity: '+r['verdict'])
    fig.savefig('figures/s24_identity.png',dpi=160,metadata={'Software':'S24 frozen result renderer'});plt.close(fig)
    report=Path('REPORT.md').read_text().replace('Iteration 13','Iteration 14')
    report='\n'.join(line for line in report.splitlines() if not line.startswith('| S24 ·'))+'\n'
    row=f"| S24 · F, team identity | 10 games / 5 blocks. Partner TYPE-Y approval rate r3–10: human **{f(p['human']['mean'])}**, AI **{f(p['ai']['mean'])}**; difference **{f(d['mean'])} {interval(d['ci95'])}**{(' (degenerate)' if d['ci95'][0]==d['ci95'][1] else '')}. | **{r['verdict']}** for directional screen |"
    target=next(line for line in report.splitlines() if line.startswith('| S22 ·'));report=report.replace(target,target+'\n'+row)
    begin='<!-- S24 summary start -->';end='<!-- S24 summary end -->'
    block=begin+'\n'+f"**S24:** paired t95% **{interval(d['paired_t_ci95'])}**, upper sign-flip **p={d['exact_signflip_p_upper']:.5f}**. Human/AI scenario cue only; matched deterministic payoffs, shared notes and neutral labels. Identity expectations and persona bundled; approvals do not verify agreements. [All outcomes and figure](results/s24_summary.md)."+'\n'+end
    if begin in report:report=report[:report.index(begin)]+block+report[report.index(end)+len(end):]
    else:report=report.replace('<!-- S22 summary start -->',block+'\n\n<!-- S22 summary start -->',1)
    report=report.replace('**Next:** Fresh market-structure or identity question after axis D; no secondary-driven promotion.','**Next:** Fresh market-structure or channel question after axis F; no secondary-driven promotion.')
    Path('REPORT.md').write_text(report)
    print('S24 summary, figure and REPORT rendered from frozen result')

if __name__=='__main__':main()
