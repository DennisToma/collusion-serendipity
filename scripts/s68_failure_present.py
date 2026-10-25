"""Guarded presentation of the registered S68 interruption; no effect estimate."""
import json,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s68_failure_audit import verify
DOCS=['REPORT.md','REPORT_DETAILS.md','README.md','HITS.md']

def outputs(r):
    commit=r['registration_commit']
    old={name:subprocess.check_output(['git','show',f'{commit}:{name}'],text=True) for name in DOCS}
    brief=(f"S68 interrupted: **{r['returned_responses']}/{r['planned_decisions']}** responses returned and accepted from "
           f"**{r['admitted_requests']}** admitted requests;process exit143,one unanswered request,no completion event. "
           '**No behavioral effect estimate or scientific verdict.** Registered whole-pilot interruption rule retained;no restart or replacement call.')
    row=f"| S68 · own, boolean output polarity | Interrupted: {r['returned_responses']}/{r['planned_decisions']} responses accepted,{r['admitted_requests']} requests admitted;exit143,no completion event. No effect estimated. | **FAILED / unclassified** |"
    report=re.sub(r'Iteration \d+','Iteration 51',old['REPORT.md'],count=1)
    report=re.sub(r'<!-- S69 summary start -->.*?<!-- S69 summary end -->','<!-- S69 summary start --><!-- S69 summary end -->',report,flags=re.S)
    at=report.index('| Pilot |');report=report[:at]+'<!-- S68 summary start -->\n**Latest — S68:** '+brief+'\n[Failure evidence and limits](results/s68_summary.md).\n<!-- S68 summary end -->\n\n'+report[at:]
    lines=report.splitlines();at=max(i for i,line in enumerate(lines) if line.startswith('| S'));lines.insert(at+1,row);report='\n'.join(lines)+'\n'
    report=re.sub(r'\*\*Next:\*\*[^\n]*','**Next:** different-axis A/C/F or E;inspect process interruption before any separately registered future pilot. S68 cannot resume. Pilots stop14:30UTC. No sibling headline change.',report)
    assert [l for l in report.splitlines() if l.startswith('| S')][:-1]==[l for l in old['REPORT.md'].splitlines() if l.startswith('| S')]
    section='\n\n## S68 — Interrupted boolean-output polarity pilot\n\n'+brief+'\n\n[Design](DESIGN_S68.md) · [Failure counts and prefix verification](results/s68_failure.json) · [Full limits](results/s68_summary.md). No HIT or sibling headline change.\n'
    readme=section+'\nOffline reproduction: `uv run python scripts/s68_failure_release.py`; clean origin reproduction: `uv run python scripts/s68_failure_release.py --clean-clone`; focused registered protocol checks: `uv run python -m unittest scripts.test_s68`. The archive stays incomplete;these commands verify failure evidence without adding model calls. Existing frozen venv reused.\n'
    docs=dict(zip(DOCS,[report,old['REPORT_DETAILS.md']+section,old['README.md']+readme,old['HITS.md']+section]))
    summary='\n'.join([
      '# S68 — Boolean output polarity: interrupted pilot','',brief,'',
      '| Registered/observed item | Value |','|---|---|',
      '| Source contexts / reused blocks | 10 / 5 |','| New games / tuning attempts | 0 / 0 |',
      f"| Planned choices / admitted requests | {r['planned_decisions']} / {r['admitted_requests']} |",
      f"| Returned / accepted responses | {r['returned_responses']} / {r['accepted_responses']} |",
      f"| Complete three-choice contexts | {r['complete_cases']} / 10 |",
      f"| Logical retries | {r['logical_retries']} |",
      f"| First admission UTC | {r['first_admission_utc']} |",
      f"| Last archived return UTC | {r['last_archived_return_utc']} |",
      f"| Local exit observation UTC | {r['local_exit_observation_utc']} |",
      f"| Registration commit | {r['registration_commit']} |",
      f"| Registered source hashes / verified admission bindings | {r['source_hashes_verified']} / {r['admission_bindings_verified']} |",
      f"| Verified returned-response and accepted-row bindings | {r['returned_response_bindings_verified']} |",
      f"| Prior scientific paths unchanged | {r['prior_scientific_paths_unchanged']} |",'',
      'Anchor/repeat use the original request plus an identical historical-encoding clarification. Inverted changes only the equal-length output true/false instruction;decoded economic actions would be compared above identical-repeat variability. Full histories,incentives,statuses and notes are fixed. The registered excess-disagreement screen has no scientific outcome because the pilot did not complete.',
      'The tool reported process exit143. This is consistent with termination by SIGTERM under common shell conventions;the process/provider root cause and exact process exit time are unknown. One admitted request has no archived reply. A missing archived reply does not establish whether the provider served,completed or billed the invocation. The lone execution journal event is start;no completion or harness failure event was written. Exit receipt is a post-interruption local observation,not provider or OS attestation. No original raw journal was repaired,completed or rewritten.',
      'Failure audit independently binds every returned request/response/accepted JSON row,all30admissions,the schedule/source/registration/runtime hashes,case selection and prospective split append. It checks that validate/analyze/resume reject the incomplete archive with model calls forbidden and bytes preserved. It computes no decoded approval totals,disagreements,effects,confidence intervals,p-values,subgroups or completed-case estimate. No partial-arm analysis,redraw,restart,model substitution or extra scientific call is allowed.',
      'Read-only local diagnostics inspected the manager runner,iteration log,launch receipt,empty pilot stdout and still-active manager. The enclosing iteration had a4500second timeout and remained active;the scientific shell command had no explicit timeout wrapper. These observations do not rule out a tool/session/service/supervisor termination or identify the cause. The local exit observation is not the process exit time and cannot support an elapsed-to-termination claim. The895-test suite produced a complete zero-failure PASS receipt,although its enclosing tool session later also reported143;this additional symptom does not identify a cause. [Local diagnostics](../logs/s68_local_diagnostics.json).',
      'A subsequent supervised repository rerun completed895tests with zero failures/errors and terminal process exit0. This validates the test run but does not identify the scientific-pilot termination cause. [Supervised test receipt](../logs/s68_repository_supervised.json) · [Terminal exit receipt](../logs/s68_repository_supervised_exit.json).',
      'llm.chat retries=1 denotes one attempted router pass,not one extra retry;the pinned Codex model/fallback names coincide. Logical retries0 means no duplicate scientific request/view admission. Provider-side execution/retry behavior for the unanswered request is unknown.',
      'The18registered scientific sources remain unchanged. Additive post-interruption audit/presentation/release code is explicitly post-run. Pre-call design critics and24focused protocol tests passed;these validate design/implementation,not a completed behavioral experiment. Existing historical synthetic fixtures are limited to repository tests;actual prefix/source/deadline audits use the real recorded values. Exploratory history,provider identity/settings,caching and instruction-following limitations in the original design remain. No invariance,absence,equivalence,mechanism,agreement or collusion inference.', '',
      '[Registered design](../DESIGN_S68.md) · [Failure JSON and all journal hashes](s68_failure.json) · [Unchanged raw prefix](../data/s68_polarity/responses.jsonl) · [Process observation](../logs/s68_process_exit.json) · [Original source freeze](../logs/s68_source_freeze.json)'])+'\n'
    return docs,old,summary,row

def render():
    r=verify();docs,old,summary,row=outputs(r)
    for name in DOCS:
        if Path(name).read_text() not in [old[name],docs[name]]:raise RuntimeError('Intervening document change: '+name)
    Path('results/s68_failure.json').write_text(json.dumps(r,indent=2)+'\n')
    Path('results/s68_summary.md').write_text(summary)
    for name,text in docs.items():Path(name).write_text(text)
    return r
if __name__=='__main__':
    r=render();print(json.dumps({k:r[k] for k in ['status','admitted_requests','returned_responses','accepted_responses','scientific_verdict','behavioral_estimates_computed']}))
