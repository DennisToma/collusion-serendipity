"""Iteration38 post-outcome documentation and ledger integration; no scientific edits."""
from datetime import datetime,timezone
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s54_analyze import analyze
from scripts.s54_independent import verify


def section(text,key,body):
    start=f'<!-- S54 {key} start -->';end=f'<!-- S54 {key} end -->'
    block=start+'\n'+body.strip()+'\n'+end
    if start in text:
        assert text.count(start)==text.count(end)==1
        return text[:text.index(start)]+block+text[text.index(end)+len(end):]
    return text.rstrip()+'\n\n'+block+'\n'


def main():
    with contextlib.redirect_stdout(io.StringIO()):r=analyze('data/s54_opportunities')
    canonical=json.dumps(r,indent=2)+'\n';assert canonical==Path('results/s54_opportunities.json').read_text()
    verify('data/s54_opportunities','results/s54_opportunities.json')
    assert '\tS54-result\t' not in Path('EXPERIMENTS.tsv').read_text(),'Already integrated;use present/release for regeneration'
    now=datetime.now(timezone.utc).isoformat();p=r['metrics']['pair_bad'];d=p['paired_difference'];ci=d['ci95'];tci=d['paired_t_ci95']
    bounds=lambda vals:'['+', '.join(f'{v:+.3f}' for v in vals)+']'
    counts={c:sum(round(g['primary']['pair_bad']*8) for g in r['games'] if g['condition']==c) for c in ['alternating','synchronized']}
    claim=f"TYPE-Y approvals alternating **{counts['alternating']}/40**, synchronized **{counts['synchronized']}/40**; synchronized−alternating **{d['mean']:+.3f} {bounds(ci)}**; pairedt95% {bounds(tci)}, upper sign-flip **p={d['exact_signflip_p_upper']:.5f}**. Frozen **{r['verdict']}** for the .25 directional screen."
    scope='Ten fresh workplace games/five paired blocks25040..25044,T10,r3–10,200 accepted decisions,codex/gpt-6-luna;zero tuning or pooling. Both arms have shared notepads and four X/four Y tasks per employee in the primary window. Synchronized versus complementary schedules change joint opportunities,public status composition and downstream histories together. First-employee assignments match;second-employee per-round assignments differ. This is no replication of S29’s channel effect or isolated coordination mechanism. Actions do not verify agreement,reciprocal intent or collusion. Small-n intervals are descriptive;degenerate bounds do not prove equivalence. Requested backend/model labels/local fingerprints do not attest served identity,settings,routing or tool non-use.'
    report=Path('REPORT.md').read_text();lines=report.splitlines();lines[2]=f"2026-10-25 · Iteration 38 · **{'S54 exploratory HIT awaiting fresh confirmation.' if r['verdict']=='HIT' else 'No hits promoted.'}** Exploratory pilots; zero tuning attempts."
    report='\n'.join(lines)+'\n';anchor=next(x for x in report.splitlines() if x.startswith('| S53 ·'))
    row=f"| S54 · own, task correlation | 10 fresh games /5 blocks. TYPE-Y approval rate r3–10: alternating **{p['alternating']['mean']:.3f}**, synchronized **{p['synchronized']['mean']:.3f}**; difference **{d['mean']:+.3f} {bounds(ci)}**. | **{r['verdict']}** for .25 directional screen |"
    report=report.replace(anchor,anchor+'\n'+row)
    report=section(report,'summary','**S54:** '+claim+' Five block differences '+str(p['seed_differences'])+'. Shared notes and marginal task counts fixed; joint statuses and downstream histories change together. This does not verify coordination or replicate S29’s channel contrast. [All outcomes, caveats and figure](results/s54_summary.md) · [All adverse returned text](results/s54_action_text.md).')
    report='\n'.join('**Next:** Fresh different-axis pilot after own/S54; prefer a new A/B question over archived-history perturbations. S52/S49/S46/S39 remain proposed, S32 unconfirmed and S30 unrun. Avoid repeated perturbations of the same archived focal histories.' if x.startswith('**Next:**') else x for x in report.splitlines())+'\n'
    Path('REPORT.md').write_text(report)
    for doc,key,title in [('HITS.md','handoff','S54: '+('HIT awaiting fresh confirmation' if r['verdict']=='HIT' else 'unpromoted '+r['verdict'])),('REPORT_DETAILS.md','details','S54 — Correlated task opportunities'),('README.md','reproduction','S54 reproduction')]:
        body='**'+title+'**\n\n'+claim+'\n\n'+scope+'\n\nFive block differences: '+str(p['seed_differences'])+'.\n\n[Design](DESIGN_S54.md) · [All outcomes/figure](results/s54_summary.md) · [All adverse texts](results/s54_action_text.md) · [Independent checks](logs/s54_independent.json).\n'
        if doc=='HITS.md':body+='\nFor both siblings: explore opportunity structure as a boundary condition;this supplies no verified collusion label or change to pricing/detector headlines. Suggested confirmation if prioritized: fresh larger paired sample and another model family at the same frozen task schedules;not run here.\n'
        if doc=='README.md':body+='\n```sh\nuv run python scripts/s54_analyze.py\nuv run python scripts/s54_independent.py\nuv run python scripts/s54_present.py\nuv run python scripts/s54_release.py\nuv run python -m unittest scripts.test_s54\n```\n\n`uv run python scripts/s54_release.py --clean-clone` verifies a fresh full-history origin clone using the installed frozen venv,not a fresh dependency install. Interrupted live continuation and new scientific calls are forbidden. This documentation integrator is outside the frozen scientific manifest.\n'
        path=Path(doc);text=path.read_text()
        if r['verdict']=='HIT' and doc=='HITS.md':
            import re
            text=re.sub(r'\*\*No promoted hits after iteration \d+\.\*\*','**S54 exploratory HIT awaiting fresh confirmation.**',text,count=1)
        if r['verdict']!='HIT' and doc=='HITS.md':
            import re
            text=re.sub(r'\*\*No promoted hits after iteration \d+\.\*\*','**No promoted hits after iteration 38.**',text,count=1)
        path.write_text(section(text,key,body))
    path=Path('IDEAS.tsv');out=[]
    metric=f"alternating{counts['alternating']}/40,synchronized{counts['synchronized']}/40;difference{d['mean']:+.3f}{ci};pairedt{tci};upperp{d['exact_signflip_p_upper']}"
    for line in path.read_text().splitlines():
        fields=line.split('\t')
        if len(fields)>1 and fields[1]=='S54':fields[5]='complete';fields[6]='10games/5freshblocks;'+metric+f";{r['cached_responses']}responses;zero tuning";fields[7]=r['verdict']+' (registered .25directional screen)';line='\t'.join(fields)
        out.append(line)
    path.write_text('\n'.join(out)+'\n')
    decision={'HIT':'keep (HIT;fresh confirmation required)','DUD':'discard (directional screen)','ODD':'inconclusive (ODD)'}[r['verdict']]
    path=Path('EXPERIMENTS.tsv');path.write_text(path.read_text()+f'{now}\tS54-result\tSynchronized task opportunities raise adverse approvals\tFrozen shared-note workplace joint-type comparison;full replay and separate raw/exact reconstruction\t10freshgames/5blocks25040..25044;T10;r3-10;zero tuning\t{metric}\t{decision}\tpending-result-commit\n')
    root=Path('data/s54_opportunities');cfg=json.loads((root/'config.json').read_text())
    snapshot=dict(checked_utc=now,sources=cfg['sources'],archive={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and p.name!='.writer.lock'},scientific_result_sha256=hashlib.sha256(canonical.encode()).hexdigest())
    Path('logs/s54_archive_snapshot.json').write_text(json.dumps(snapshot,indent=2)+'\n')
    path=Path('STATUS.md');s=path.read_text();state=f'''# STATUS

## Current state ({now}; Phase2, iteration38 RESULTS)
- Own/S54:10freshgames/5paired blocks,T10,200accepted decisions;zero tuning.
- Y approvals alternating{counts['alternating']}/40,synchronized{counts['synchronized']}/40;difference{d['mean']:+.3f}{bounds(ci)}.
- Pairedt95%{bounds(tci)},upperp{d['exact_signflip_p_upper']:.5f};frozen{r['verdict']}.
- Five block differences:{p['seed_differences']}.
- Shared notepads/payoffs/marginaltaskcounts fixed;jointstatuses/history change together.
- Full source/registration/runtime/UTC/request/export replay PASS.
- Separate50cells/15bootstrap+t/all15signsets/200rawbindings PASS.
- Reports/ledgers current;finalcritics/post-live tests/release/originclone next.
- No pooling,source edits,secondary promotion or verified coordination labels.
- Risks:n5,synthetic tasks,uncontrolled draws,provider unverified;no S29replication.

'''
    path.write_text(state+s[s.index('## Log'):]+f'\n- {now}: S54 sole run complete;{metric};frozen{r["verdict"]}. Full source/archive/registration/runtime/UTC/schedule/request/response replay and independent50rawcells/15bootstrap+t/all sign tails/200bindings PASS. Allscientificsources frozen,no extra games/tuning/pooling/exclusions/siblingwrites/DIRECTIONdeviation. Reports/ledgers updated;finalcritics/post-live suite/figure/release/originclone next.\n')
    print(claim)

if __name__=='__main__':main()
