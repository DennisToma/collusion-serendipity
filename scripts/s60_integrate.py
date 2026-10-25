"""Documentation integration only, from the fully frozen and verified S60 result."""
from datetime import datetime,timezone
import contextlib
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import subprocess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s60_analyze import analyze

def bounds(vals):return '['+', '.join(f'{v:+.3f}' for v in vals)+']'

def main(*,document_capture=False):
    current_iteration=re.search(r'· Iteration (\d+) ·',Path('REPORT.md').read_text())
    if not document_capture and current_iteration and int(current_iteration[1])>43:
        raise RuntimeError('S60 document writer is pinned to iteration43;use the read-only publication checker after later pilots')
    with contextlib.redirect_stdout(io.StringIO()):r=analyze('data/s60_author_bonus')
    rp=Path('results/s60_author_bonus.json');assert r==json.loads(rp.read_text()) and not r['dry']
    independent=json.loads(Path('logs/s60_independent.json').read_text());assert independent['passed']
    registration=json.loads(Path('data/s60_author_bonus/config.json').read_text())['registration_commit']
    def baseline(name):return subprocess.check_output(['git','show',f'{registration}:{name}']).decode('utf-8')
    p=r['metrics']['pair_bad'];d=p['paired_difference'];verdict=r['verdict']
    counts={c:sum(round(g['primary']['pair_bad']*8) for g in r['games'] if g['condition']==c) for c in ['low','high']}
    snapshot=json.loads(Path('logs/s60_prior_snapshot.json').read_text())
    assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in snapshot['protected_sha256'].items())
    brief=(f"**Latest — S60:** ten fresh workplace games/five paired blocks. TYPE-Y approvals with author bonus6 **{counts['high']}/40**,bonus1 **{counts['low']}/40**;high−low **{d['mean']:+.3f} {bounds(d['ci95'])}**,paired t95% {bounds(d['paired_t_ci95'])},upper sign-flip p={d['exact_signflip_p_upper']:.5f}. **{verdict} for the .25 reduction screen.**\n"
        'Reviewer net payoff from TYPE-Y approval remains−2;paired task assignments match. At bonus1,each harmful approval lowers pair total by1,and approve-X/reject-Y already maximizes pair total. Author benefit,incoming reward,joint surplus,numeral salience and downstream histories change together. No agreement,intent or reciprocity mechanism is established;this does not replicate S29’s channel comparison. [All outcomes and limits](results/s60_summary.md) · [All adverse returned text](results/s60_action_text.md).')
    report=baseline('REPORT.md')
    assert [line for line in report.splitlines() if line.startswith('| S') and not line.startswith('| S60 ') ]==snapshot['prior_pilot_rows']
    report=re.sub(r'2026-10-25 · Iteration \d+ · .*?\n',
        '2026-10-25 · Iteration 43 · '+('**One exploratory hit;confirmation required.**' if verdict=='HIT' else '**No hits promoted.**')+' Exploratory pilots;zero tuning attempts.\n',report,count=1)
    # Preserve all older anchors and pilot rows;the previous prose is already in details.
    for old in re.findall(r'<!-- (S\d+) summary start -->',report):
        if old=='S60':continue
        report=re.sub(r'<!-- '+old+r' summary start -->.*?<!-- '+old+r' summary end -->',
            '<!-- '+old+' summary start --><!-- '+old+' summary end -->',report,flags=re.S)
    latest='<!-- S60 summary start -->\n'+brief+'\n<!-- S60 summary end -->'
    if '<!-- S60 summary start -->' in report:
        report=re.sub(r'<!-- S60 summary start -->.*?<!-- S60 summary end -->',lambda _:latest,report,flags=re.S)
    else:report=report.replace('\n| Pilot |','\n'+latest+'\n\n| Pilot |',1)
    row=(f"| S60 · D, author approval benefit | 10fresh games/5blocks;author6 **{counts['high']}/40**,author1 **{counts['low']}/40** Yapprovals;high−low **{d['mean']:+.3f} {bounds(d['ci95'])}**. | **{verdict}** for .25 reduction screen |")
    if any(x.startswith('| S60 ') for x in report.splitlines()):report=re.sub(r'^\| S60 .*$',lambda _:row,report,flags=re.M)
    else:
        last=snapshot['prior_pilot_rows'][-1];report=report.replace(last,last+'\n'+row,1)
    report=re.sub(r'\*\*Next:\*\*.*', '**Next:** fresh different-axis B/F/A pilot;own S61,S57,S52,S49 remain queued. '+('HIT requires independently registered confirmation.' if verdict=='HIT' else 'No sibling headline change.'),report,count=1)
    assert [line for line in report.splitlines() if line.startswith('| S') and not line.startswith('| S60 ')]==snapshot['prior_pilot_rows']
    details=(brief+'\n\nFive paired differences: '+str(p['seed_differences'])+f";upper sign p={d['exact_signflip_p_upper']:.5f},lower={d['exact_signflip_p_lower']:.5f},two-sided={d['exact_signflip_p_two_sided']:.5f}.\n\n"
        'Post-outcome interpretation clarification:with author1,pair bonus=2*approvedX−approvedY,so relative to approve-X/reject-Y the gap is−2*rejectedX−approvedY<=0 in every stage,and therefore over any fixed task sequence. Intertemporal cooperation in the frozen design/summary does not imply joint improvement over that benchmark. The higher-author arm changes this surplus geometry. This is an algebraic clarification,not a new observed endpoint or mechanism attribution. [Exhaustive static verification](logs/s60_static_bound.json),[verification code](scripts/s60_static_bound.py). Fresh balanced task schedules,shared notepads,both current types public,undisclosed horizon. Sole200accepted-decision run;no archived-history reuse,pooling or tuning. Approval author benefit6 versus1 for X and Y;reviewer +1 for X and−2 for Y. Unique stage equilibrium approve X/reject Y in both arms. Both-Y mutual approval gives each+4 versus−1;low does not rule out intertemporal cooperation. No bonus gate because bonus changes mechanically with author multiplier. Other four metrics and all bootstrap/t intervals stay in full results. Five blocks,one model,extensive prior exploration,no multiplicity correction,held-out validation or equivalence claim. Sparse baselines limit sensitivity;all reverse/secondary/subgroup patterns remain unpromoted. The simulator system/user fields are flattened into one CLI prompt,not transmitted as native provider roles. Source/runtime/local chronology checks do not attest served identity,settings or tool non-use. [Design](DESIGN_S60.md) · [Separate reconstruction](logs/s60_independent.json) · [Figure](figures/s60_author_bonus.png).')
    for name,marker,title,body in [('REPORT_DETAILS.md','details','',details),('HITS.md','handoff','## S60 — '+('Exploratory HIT:author-benefit intervention' if verdict=='HIT' else 'Unpromoted author-benefit intervention'),details+'\n\nFor both siblings:adverse approvals are an action-level outcome,not evidence verifying agreements or collusion. '+('Suggested confirmation:fresh independently registered larger paired sample,reviewer cost fixed,matching tasks;do not pool these exploratory blocks.' if verdict=='HIT' else 'No confirmation trigger or headline change.'))]:
        path=Path(name);text=baseline(name)
        if name=='HITS.md':
            text=text.replace('**No promoted hits after iteration 42.**','**One exploratory HIT after iteration 43;confirmation required.**' if verdict=='HIT' else '**No promoted hits after iteration 43.**')
        section=f'<!-- S60 {marker} start -->\n'+title+'\n\n'+body+f'\n<!-- S60 {marker} end -->'
        if f'<!-- S60 {marker} start -->' in text:text=re.sub(r'<!-- S60 '+marker+r' start -->.*?<!-- S60 '+marker+r' end -->',lambda _:section,text,flags=re.S)
        else:text+='\n\n'+section+'\n'
        path.write_text(text)
    Path('REPORT.md').write_text(report)
    readme=Path('README.md');text=baseline('README.md')
    if '## S60 — Author approval benefit' not in text:
        text+='\n\n## S60 — Author approval benefit\n\nTen fresh paired workplace games;author1 versus6,reviewer net TYPE-Y approval payoff−2 in both arms. [Design](DESIGN_S60.md),[results](results/s60_summary.md),[all adverse returned text](results/s60_action_text.md).\n\n```bash\nuv run --frozen python scripts/s60_publish_check.py\nuv run --frozen python scripts/s60_independent.py\nuv run --frozen python scripts/s60_present.py\nuv run --frozen python -m unittest scripts.test_s60 scripts.test_s60_presentation\nuv run --frozen python scripts/s60_publish_check.py --clean-clone\n```\n\nRelease forbids scientific calls,requires byte-identical result and full archived replay. Origin-clone proof reuses the installed frozen venv;it is not a fresh dependency installation. Original historical sources/data stay unchanged. Canonical offline suite:`uv run --frozen python scripts/repository_tests.py --out /var/tmp/serendipity_tests.json`.\n'
    text+='\nThe canonical publication entry compares the frozen rendered summary,figure,appendix and independently generated S60 document sections;it rejects false prose even when links are valid. Original document text comes from the registration commit,not the displayed copies. The registered `s60_release.py` remains the underlying archive-only check. Simulator system/user fields are flattened into one CLI prompt. The post-outcome [static-bound check](logs/s60_static_bound.json) clarifies that low-reward Y approvals cannot raise pair total above approve-X/reject-Y.\n'
    readme.write_text(text)
    receipt=dict(passed=True,scientific_result_sha256=hashlib.sha256(rp.read_bytes()).hexdigest(),prior_scientific_artifacts_unchanged=len(snapshot['protected_sha256']),prior_pilot_rows_unchanged=len(snapshot['prior_pilot_rows']),pilot_rows=44,verdict=verdict,generated_from_frozen_result=True)
    Path('logs/s60_document_check.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
