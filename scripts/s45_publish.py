"""Iteration31 presentation/ledger integration only; no scientific calls or source edits."""
from datetime import datetime,timezone
import sys
from fractions import Fraction
import hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

def replace_section(text,start,end,content):
    block=start+"\n"+content.strip()+"\n"+end
    if start in text:
        assert text.count(start)==text.count(end)==1
        return text[:text.index(start)]+block+text[text.index(end)+len(end):]
    return text.rstrip()+"\n\n"+block+"\n"

from scripts.s45_analyze import analyze
from scripts.s45_independent import verify
r=analyze('data/s45_reviewring');canonical=json.dumps(r,indent=2)+'\n';assert canonical==Path('results/s45_reviewring.json').read_text();verify('data/s45_reviewring','results/s45_reviewring.json')
assert '\tS45-result\t' not in Path('EXPERIMENTS.tsv').read_text(),'Result already integrated;use frozen present/release for regeneration'
p=r['metrics']['pair_bad'];d=p['paired_difference'];ci=d['ci95'];tci=d['paired_t_ci95'];now=datetime.now(timezone.utc).isoformat()
fmt=lambda x:f'{x:.3f}'
bounds=lambda x:'['+', '.join(fmt(v) for v in x)+']'
counts={c:sum(round(g['primary']['pair_bad']*8) for g in r['games'] if g['condition']==c) for c in ['self','shared']}
supported={c:sum(round(g['primary']['pair_good']*8) for g in r['games'] if g['condition']==c) for c in ['self','shared']}
claim=f"Unsupported recommendation rate r3–10: self **{fmt(p['self']['mean'])}** ({counts['self']}/40),shared **{fmt(p['shared']['mean'])}** ({counts['shared']}/40);shared−self **{fmt(d['mean'])} {bounds(ci)}**;paired t95% {bounds(tci)},inclusive upper sign-flip **p={d['exact_signflip_p_upper']:.5f}**. Frozen **{r['verdict']}** for the .25 directional screen."
scope='Ten fresh games/five paired blocks,T10,200 decisions,codex/gpt-6-luna;zero tuning or pooling. This is a synthetic marketplace adaptation of the workplace reciprocal-review structure,with changed payoffs and factual labels;cross-world differences are uncontrolled. Delivery,readability expectations,memory volume and downstream histories are bundled. Unsupported recommendations do not establish agreement or reciprocal intent. Small-n bounds are descriptive;degenerate bounds do not establish population zero risk or equivalence. Consumer loss and seller profit are mechanical functions of the two recommendation rates. Local wrapper overlap does not attest provider execution;served model/settings and tool non-use remain unverified.'
if r['verdict']=='HIT':
 pth=Path('REPORT.md');pth.write_text(pth.read_text().replace('**No hits promoted.**','**S45 exploratory HIT awaiting confirmation.**',1))
pth=Path('HITS.md');s=pth.read_text().replace('after iteration 30','after iteration 31');
if r['verdict']=='HIT':s=s.replace('**No promoted hits after iteration 31.**','**S45 is an exploratory HIT awaiting confirmation.**',1)
s=replace_section(s,'<!-- S45 handoff start -->','<!-- S45 handoff end -->','**S45: '+('HIT awaiting fresh confirmation' if r['verdict']=='HIT' else 'unpromoted '+r['verdict'])+', marketplace recommendations (A5).**\n\n'+claim+'\n\n'+scope+'\n\nFive paired differences: '+str(p['seed_differences'])+'.\n\nFor both siblings: communication effects need to be checked against matched economic and semantic baselines;this pilot supplies no verified collusion label. Suggested confirmation,if prioritized: repeat the frozen comparison with more independent blocks and another seller family;not run here.\n\n[Design](DESIGN_S45.md),[all outcomes/figure](results/s45_summary.md). Reproduce: `uv run python scripts/s45_release.py`.\n');pth.write_text(s)
pth=Path('REPORT_DETAILS.md');pth.write_text(replace_section(pth.read_text(),'<!-- S45 details start -->','<!-- S45 details end -->','## S45 — Marketplace recommendation ring\n\n'+claim+'\n\n'+scope+'\n\nSupported recommendations: self '+str(supported['self'])+'/40,shared '+str(supported['shared'])+'/40. Each primary recommendation rate has8opportunities/game;the five block differences are the resampling unit. Complete outcomes and all secondary bounds are in [the S45 summary](results/s45_summary.md);[preregistered methods](DESIGN_S45.md),[independent reconstruction](logs/s45_independent.json),[method-review dispositions](logs/s45_review_disposition.md). Scientific sources remain frozen.\n'))
pth=Path('README.md');pth.write_text(replace_section(pth.read_text(),'<!-- S45 reproduction start -->','<!-- S45 reproduction end -->','S45 marketplace recommendation pilot completed. '+claim+'\n\n'+scope+'\n\n```sh\nuv run python scripts/s45_analyze.py\nuv run python scripts/s45_independent.py\nuv run python scripts/s45_present.py\nuv run python scripts/s45_release.py\nuv run python -m unittest scripts.test_s45\n```\n\n`uv run python scripts/s45_release.py --clean-clone` uses a fresh full-history origin clone and the installed frozen venv,not a fresh dependency installation. Source changes require returning to the registered/result checkout. No interrupted resume or new scientific calls are allowed during reproduction. This presentation/ledger integrator was added after registration and is outside the frozen scientific manifest.\n'))
pth=Path('IDEAS.tsv');lines=pth.read_text().splitlines();out=[]
for line in lines:
 fields=line.split('\t')
 if len(fields)>1 and fields[1]=='S45':
  fields[5]='complete';fields[6]=f"10games/5blocks;unsupported self{counts['self']}/40,shared{counts['shared']}/40;difference{d['mean']:+.3f}{ci};t{tci};upperp{d['exact_signflip_p_upper']};{r['cached_responses']}responses;zero tuning";fields[7]=r['verdict']+' (registered .25directional screen)';line='\t'.join(fields)
 out.append(line)
pth.write_text('\n'.join(out)+'\n')
metric=f"Self{p['self']['mean']:.3f}/shared{p['shared']['mean']:.3f};shared-minus-self{d['mean']:+.3f}{ci};pairedt{tci};upperp{d['exact_signflip_p_upper']}"
pth=Path('EXPERIMENTS.tsv');s=pth.read_text()+f"{now}\tS45-result\tShared notes raise unsupported recommendations\tFrozen marketplace self/shared notepad comparison;full replay and independent raw/exact reconstruction\t10games/5fresh blocks24960..24964;T10;r3-10;zero tuning\t{metric}\t"+('keep (HIT;fresh confirmation required)' if r['verdict']=='HIT' else 'discard (DUD for directional screen)' if r['verdict']=='DUD' else 'inconclusive (ODD)')+'\tpending-result-commit\n';pth.write_text(s)
rawroot=Path('data/s45_reviewring');cfg=json.loads((rawroot/'config.json').read_text());snapshot=dict(checked_utc=now,sources=cfg['sources'],archive={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(rawroot.rglob('*')) if p.is_file() and p.name!='.writer.lock'},scientific_result_sha256=hashlib.sha256(canonical.encode()).hexdigest());Path('logs/s45_archive_snapshot.json').write_text(json.dumps(snapshot,indent=2)+'\n')
pth=Path('STATUS.md');s=pth.read_text();a=s.index('## Log');state=f'''# STATUS

## Current state ({now}; Phase2, iteration31 RESULTS)
- A5/S45:10fresh marketplace games/5paired blocks,T10,200valid decisions.
- Unsupported reviews self{counts['self']}/40,shared{counts['shared']}/40;difference{d['mean']:+.3f}{bounds(ci)}.
- Pairedt{bounds(tci)},upperp{d['exact_signflip_p_upper']:.5f};frozen{r['verdict']},no secondary promotion.
- Five block differences:{p['seed_differences']}.
- Full archive/source/registration/environment/timing/prompt/export replay PASS.
- Separate50rawcells/15bootstrap+t summaries/all15sign sets/200bindings PASS.
- Scientific sources unchanged;pre-live509canonical/21scoped tests PASS.
- Reports/HITS/README current;final critics/post-live tests/release next.
- Risks:n5,bundled delivery,synthetic consumers,dependent outcomes,provider unverified.
- Next:final review,call-forbidden regeneration,results push and origin-clone release.

'''
pth.write_text(state+s[a:]+f'\n- {now}: S45 sole runner completed all10games/{r["cached_responses"]}cached responses;invalid-attempt retries{r["invalid_attempt_retries"]}. Full archive eligibility/replay and independent50rawcells/15bootstrap+t summaries/all15sign sets/200action-note-reason bindings PASS. Frozen{r["verdict"]}: {metric};block differences{p["seed_differences"]}. No source/threshold edits,tuning,pooling,exclusions,reverse/secondary promotion,sibling writes or agreement/coordination labels. Reports/HITS/README updated from validated canonical result;final critics/post-live tests/release next.\n')
print(claim)
