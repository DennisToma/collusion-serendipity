"""Bounded independent text and read-only critics for the final editorial handoff.

Usage: uv run --frozen python scripts/iteration60_reviews.py closure
No scientific generation. CLI outputs and review scopes are retained separately.
"""
import sys, json, subprocess, hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path.cwd()))
from scripts.s16_reviews import run_bounded
stage=sys.argv[1]
names=['scripts/export_report.py','REPORT.md','README.md','logs/iteration60_exports.json']
if stage=='design': names=['HITS.md']
hashes={n:hashlib.sha256(Path(n).read_bytes()).hexdigest() for n in names if Path(n).exists()}
texts=[]
for n in names:
 if Path(n).exists():
  t=Path(n).read_text()
  if n=='README.md':t='\n'.join(t.splitlines()[:85])+'\n[remainder omitted]' 
  if n=='HITS.md':t=t.split('\n---\n',1)[0]
  texts.append('FILE '+n+'\n'+t)
for n in ['results/s48_summary.md','results/s58_summary.md','results/s59_summary.md','results/s69_summary.md','results/s70_summary.md','results/s72_summary.md','results/iteration54_brief.md']:
 texts.append('SAVED EVIDENCE '+n+'\n'+Path(n).read_text())
prompt=('Adversarial review of iteration60 final handoff prose and suggested future methodology. No edits, subagents, model calls, installations or full replay. Finish within four minutes. No new scientific experiment or estimate is authorized. Review the current shipped report/exporter and current reader future paragraph; earlier HITS drafts are unshipped and HITS is archived unchanged. This is a prospective suggestion with explicit open decisions, not a runnable registration; do not require a finished protocol. Check overclaims, reuse versus independence, future control identifiability, primary contrast, outcome units, failure policy and whether future suggestion is mistakenly represented as registration/confirmation. Report concrete high/medium issues, optional nits separately. Scope your evidence honestly.\n')
if stage=='wording':
 prompt=('Narrow final editorial review, finish within two minutes. No edits, subagents, scientific generation or replay. Review only whether the current report/README/reader future paragraph resolves: primary-versus-secondary contrasts and rationale; primary holding addressing fixed versus self-only changing addressing; prospective model/backend/settings/direction/decision-rule choices; replacement of the archived suggestion; identical shared paragraph and archived-link labels. It is an unfinished unregistered suggestion, not a runnable protocol. Flag remaining concrete high/medium issues in this narrow scope only, with optional nits separately. Supplied-text reviewers cannot attest execution or hashes.\n')
Path('logs/iteration60_review_prompt_'+stage+'.md').write_text(prompt+'\n'+'\n\n'.join(texts))
def review(kind):
 out=Path('logs/iteration60_'+kind+'_'+stage+'.md')
 if kind=='codex':
  cmd=['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(out.resolve()),prompt+'Read logs/iteration60_review_prompt_'+stage+'.md and relevant actual repo sources.']
  code=run_bounded(cmd,'/var/tmp/iteration60_codex_'+stage+'.log')
 else:
  code=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],out,prompt+'Supplied text only; no filesystem or execution verification.\n'+'\n\n'.join(texts))
 return {'critic':kind,'exit':code,'scope':'repository read-only' if kind=='codex' else 'supplied text only'}
with ThreadPoolExecutor(max_workers=2) as p: records=list(p.map(review,['codex','opus']))
Path('logs/iteration60_reviews_'+stage+'.json').write_text(json.dumps({'reviews':records,'source_hashes_at_launch':hashes,'sources_unchanged_during_review':all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==v for n,v in hashes.items())},indent=2)+'\n')
print(json.dumps(records))
