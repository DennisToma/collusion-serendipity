"""Render only S21 registered results and all case predictions."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.s21_audit import write


def present():
    r=json.loads(Path('results/s21_audit.json').read_text());assert not r['dry']
    primary=r['contrasts'][r['primary']]
    lines=['# S21 — Can explanations override recorded actions?','',
           'Exploratory source-aware factual audit, gpt-6.1-sol/codex; zero tuning. Ten selected existing S19 cases, five source seed blocks, thirty independent stateless calls. One case per source game; negative-type approvals preferred, without inspecting explanations. All four observed adverse actions plus six rejections: this enriched challenge does not estimate population prevalence.','',
           '| View | Correct / 10 | Confident errors / 10 | Abstentions / 10 |','|---|---:|---:|---:|']
    for v,title in [('A','Actions'),('T','Explanations'),('AT','Both')]:
        counts=r['metrics'][v]['counts'];lines.append(f"| {title} | {counts['correct']} | {counts['error']} | {counts['abstain']} |")
    lines+=['',f"Primary both−actions confident-error difference: **{primary['mean']:+.3f} [{primary['ci95'][0]:+.3f}, {primary['ci95'][1]:+.3f}]** descriptive exact block-bootstrap95%; paired t95% [{primary['t95'][0]:+.3f}, {primary['t95'][1]:+.3f}], upper sign-flip p={primary['upper_signflip_p']:.5f}. Frozen queue verdict **{r['verdict']}**.",'',
            'Abstentions remain in the ten-case denominator and are reported separately. Source-priority instructions explicitly define reviews as executed actions and reasoning as explanation. An explanation-only auditor cannot observe actual actions; correct guesses do not repair that missing information. These are factual action-reading results, with no intent, agreement or collusion classification.','',
            '| Registered contrast | Mean | Bootstrap95% | Paired t95% | Upper p |','|---|---:|---|---|---:|']
    for name,s in r['contrasts'].items():lines.append(f"| {name} | {s['mean']:+.3f} | [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}] | [{s['t95'][0]:+.3f}, {s['t95'][1]:+.3f}] | {s['upper_signflip_p']:.5f} |")
    lines+=['','All secondaries descriptive; no promotion. Uncertainty resamples five source seed blocks, not thirty auditor calls. Empirical degenerate bounds do not establish population zero error or equivalence. Same-family generation/auditing, selected cases, n5, uncontrolled draws and shared service limit generalization. No prompt tuning, general detector validation or independent-source replication.','',
            '| Case | Source run | Actual approval | Actions prediction | Explanation prediction | Both prediction |','|---|---|---|---|---|---|']
    for c in r['cases']:lines.append('| '+' | '.join([c['case_id'],c['source_run'],str(c['truth'])]+[str(c['views'][v]['approved']) for v in ['A','T','AT']])+' |')
    lines+=['','![S21 predictions](../figures/s21_audit.png)','',
            '[Frozen design](../DESIGN_S21.md) · [Source-bound challenge](../data/s21_cases.json) · [All results](s21_audit.json).',
            'Reproduce: `uv run python scripts/s21_analyze.py && uv run python scripts/s21_independent.py && uv run python scripts/s21_present.py`.']
    Path('results/s21_summary.md').write_text('\n'.join(lines)+'\n')
    fig,ax=plt.subplots(figsize=(6,3.5));x=range(3)
    correct=[r['metrics'][v]['counts']['correct'] for v in ['A','T','AT']]
    errors=[r['metrics'][v]['counts']['error'] for v in ['A','T','AT']]
    abstain=[r['metrics'][v]['counts']['abstain'] for v in ['A','T','AT']]
    ax.bar(x,correct,label='Correct',color='#33836b');ax.bar(x,errors,bottom=correct,label='Confident error',color='#c34e4e')
    ax.bar(x,abstain,bottom=[a+b for a,b in zip(correct,errors)],label='Abstain',color='#a6abb3')
    ax.set_xticks(list(x),['Actions','Explanation','Both']);ax.set_ylim(0,11);ax.set_ylabel('Selected cases (n=10)')
    ax.set_title('Source-aware factual action reading');ax.legend(loc='upper center',bbox_to_anchor=(.5,-.12),ncol=3)
    fig.tight_layout();fig.savefig('figures/s21_audit.png',dpi=150);plt.close(fig)
    report=Path('REPORT.md').read_text().replace('Iteration 11','Iteration 12')
    counts={v:r['metrics'][v]['counts'] for v in ['A','T','AT']}
    row=(f"| S21 · E, action/explanation audit | 10 selected S19 cases / 5 source blocks; 30 gpt-6.1-sol calls. "
         f"Confident errors actions **{counts['A']['error']}/10**, both **{counts['AT']['error']}/10**; "
         f"difference **{primary['mean']:+.3f} [{primary['ci95'][0]:+.3f}, {primary['ci95'][1]:+.3f}]**. | **{r['verdict']}** for factual-audit screen |")
    report='\n'.join(line for line in report.splitlines() if not line.startswith('| S21 ·'))+'\n'
    target=next(line for line in report.splitlines() if line.startswith('| S19 ·'));report=report.replace(target,target+'\n'+row)
    begin='<!-- S21 summary start -->';end='<!-- S21 summary end -->'
    block=(begin+'\n'+f"**S21:** action/both correct **{counts['A']['correct']}/10** / **{counts['AT']['correct']}/10**; "
           f"explanation-only **{counts['T']['correct']}/10** correct, **{counts['T']['error']}/10** confident errors, "
           f"**{counts['T']['abstain']}/10** abstentions. Source-priority instructions and enriched post-outcome case selection limit this to factual action reading; "
           f"no intent/agreement labels or population error bound. Primary upper sign-flip p={primary['upper_signflip_p']:.5f}. "
           '[All views, uncertainty and figure](results/s21_summary.md).\n'+end)
    if begin in report:report=report[:report.index(begin)]+block+report[report.index(end)+len(end):]
    else:report=report.replace('<!-- S19 summary start -->',block+'\n\n<!-- S19 summary start -->',1)
    old=next(line for line in report.splitlines() if line.startswith('**Next:**'))
    report=report.replace(old,'**Next:** Fresh market-structure or intervention question after axis E; no secondary-driven promotion.')
    Path('REPORT.md').write_text(report)


if __name__=='__main__':present()
