"""Present S62 frozen outputs; no estimation or model access. Preserve prior rows."""
from pathlib import Path
import json
import re


def f(value):return f'{value:+.3f}'
def interval(values):return '['+', '.join(map(f,values))+']'


def main():
    report=Path('REPORT.md').read_text()
    prior=json.loads(Path('logs/s62_prior_report_rows.json').read_text())
    assert all(line in report.splitlines() for line in prior)
    if Path('results/s62_failure.json').exists():
        r=json.loads(Path('results/s62_failure.json').read_text())
        assert r['effect_estimated'] is False
        summary=f"**Latest — S62:** fresh Qwen/Aqueduct notepad pilot **{r['status']} / unclassified**;{r['complete_games']}/10 games complete,{r['cached_responses']} cached responses. No scientific effect estimated. [Failure and limits](results/s62_summary.md)."
        row=f"| S62 · C, Qwen notepad generalization | {r['complete_games']}/10 games complete;{r['cached_responses']} responses;frozen abort policy,no effect estimated. | **FAILED / unclassified** |"
        verdict='FAILED'
    else:
        r=json.loads(Path('results/s62_notepad_qwen.json').read_text())
        assert r['pilot']=='S62' and not r['dry'] and r['n_games']==10
        m=r['metrics']['pair_bad'];d=m['paired_difference'];verdict=r['verdict']
        counts={c:round(m[c]['mean']*40) for c in ['self','shared']}
        summary=(f"**Latest — S62:** ten fresh Qwen/Aqueduct workplace games/five paired blocks. TYPE-Y approvals self-only **{counts['self']}/40**,shared **{counts['shared']}/40**;shared−self **{f(d['mean'])} {interval(d['ci95'])}**,paired t95% {interval(d['paired_t_ci95'])},upper sign-flip p={d['exact_signflip_p_upper']:.5f}. **{verdict} for the frozen .25 screen.**\n"
                 'The bootstrap upper equals.25;DUD requires strictly below.25. TYPE-X approvals also rose,so no selective-Y mechanism is established. '
                 'Fresh generalization attempt of S29 with different seeds and serving stack;one neutral readiness response informed a symmetric exact-JSON-fence allowance before registration. No game-outcome tuning,pooling or controlled model-family comparison. Adverse approvals do not verify agreement or intent;small-sample zeroes cannot establish absence. '
                 '[All outcomes and figure](results/s62_summary.md) · [Independent reconstruction](logs/s62_independent.json) · [All adverse returned text](results/s62_action_text.md).')
        row=(f"| S62 · C, Qwen notepad generalization | 10fresh games/5blocks;self **{counts['self']}/40**,shared **{counts['shared']}/40** Yapprovals;shared−self **{f(d['mean'])} {interval(d['ci95'])}**. | **{verdict}** for .25directional screen |")
    report=re.sub(r'<!-- S60 summary start -->.*?<!-- S60 summary end -->','<!-- S60 summary start --><!-- S60 summary end -->',report,flags=re.S)
    report=re.sub(r'\*\*In progress — S62:\*\*.*?(?=\n\n|\Z)','**Next:** fresh different-axis A/B/F or own pilot;S61,S57,S52,S49 stay queued. No sibling headline change.',report,flags=re.S)
    begin='<!-- S62 summary start -->';end='<!-- S62 summary end -->'
    block=begin+'\n'+summary+'\n'+end
    if begin in report:report=re.sub(re.escape(begin)+'.*?'+re.escape(end),lambda _:block,report,flags=re.S)
    else:report=report.replace('<!-- S60 summary start -->',block+'\n\n<!-- S60 summary start -->',1)
    report='\n'.join(s for s in report.splitlines() if not s.startswith('| S62 '))+'\n'
    last=prior[-1];report=report.replace(last,last+'\n'+row,1)
    if verdict=='HIT':report=report.replace('**No hits promoted.**','**S62 promoted as an exploratory HIT.**')
    assert all(line in report.splitlines() for line in prior)
    Path('REPORT.md').write_text(report)
    details=Path('REPORT_DETAILS.md').read_text()
    start='<!-- S62 details start -->';finish='<!-- S62 details end -->'
    text=start+'\n'+summary+'\n\n[Design](DESIGN_S62.md) · [All metrics and caveats](results/s62_summary.md).\n'+finish
    if start in details:details=re.sub(re.escape(start)+'.*?'+re.escape(finish),lambda _:text,details,flags=re.S)
    else:details+='\n\n'+text+'\n'
    Path('REPORT_DETAILS.md').write_text(details)
    hits=Path('HITS.md').read_text().replace('No promoted hits after iteration 43.','No promoted hits after iteration 44.')
    if verdict=='HIT':
        hits=hits.replace('**No promoted hits after iteration 44.**','**S62: exploratory HIT under its frozen screen.**')
        handoff=('\n\n## S62 — Qwen workplace partner notes\n\n'+summary+'\n\n'
                 'Both siblings:the adverse-action channel contrast generalizes outside price games in this requested serving configuration;no detector claim or verified collusion label follows. Confirm on fresh seeds with a frozen prompt/output contract,larger sample and independent agreement labels before changing any main headline. No controlled cross-model contrast.\n\n'
                 'Reproduce:`uv run --frozen python scripts/s62_release.py`.\n')
        if '## S62 —' not in hits:hits+=handoff
    Path('HITS.md').write_text(hits)
    Path('logs/s62_document_check.json').write_text(json.dumps(dict(passed=True,prior_pilot_rows_preserved=len(prior),new_verdict=verdict),indent=2)+'\n')
    print('S62 documents updated;all older rows preserved')

if __name__=='__main__':main()
