# S21 independent review dispositions

Prelaunch: Codex and Opus both exit0; original critiques retained verbatim.
No live S21 output existed while applying these changes.

- Codex P1 accepted: shared llm._codex has a hidden cheap-model fallback. Added
  invocation-scoped CODEX_CHEAP=requested-model with restoration after all workers;
  the helper deduplicates that list. Regression mocks a failed subprocess and
  confirms exactly one attempt, strong model only. No shared llm.py file changed.
- Codex P2 accepted: requests journaled before dispatch; failed transports retain
  full case/view/payload/start/failure times, successes retain raw responses even
  when invalid. Any failure blocks analysis and restart; tests cover malformed
  output and wrong-model response in the mocked non-dry branch.
- Codex P2 accepted: independent reconstruction now rejects missing/duplicate
  cases, wrong result metadata and changed floating means; exact interval strings
  also checked against independent NumPy quantiles. Mutation regressions pass.
- Opus opportunity concern accepted as a limitation, not a design rewrite: the
  three explicit contradictions occupy only two source blocks, so the expected
  contradiction-only pattern cannot pass the all-five-positive sign-flip gate.
  The HIT screen is mathematically attainable with errors in other blocks; the
  critique's claim that positive bootstrap lower bounds require all five positive
  blocks is false (four positives and one zero can suffice). No selected subgroup
  promotion, threshold change or new prompt. Analyst prior exposure disclosed;
  selection code itself does not consult explanations.
- Opus strict-output concern retained prospectively: fenced JSON aborts; leading
  whitespace already accepted by json.loads. No output-based parser relaxation.
- Opus retries concern clarified: retries=1 is one outer attempt; retries=0 makes
  no calls in llm.chat. Internal fallback disabled as above. No hidden disk cache
  in llm.chat; complete S21 datasets validate without new calls.
- Opus one-shot concern accepted: exclusive launch receipt outside dataset path,
  bound back during live validation, blocks accidental directory-deletion restart.
  Intentional removal of all evidence remains outside this operational safeguard.
- Opus test concern accepted: selection now has a direct explanation-mutation
  test; mocked live wrong-route/malformed-output tests retain evidence and fail.
- Opus metadata/scope wording accepted: explicit condition IDs omitted, but status
  vocabulary reveals the source condition; text-only performance can reflect
  self-report fidelity. Concurrent worker may finish further calls after a peer
  fails; all remain archived and no partial estimate allowed. Full git history
  through registration and repo-root CLI execution documented.

Final reviews: Codex and Opus both exit0. Original reviews retained verbatim.

- Codex independently reconstructed all30 raw predictions,all15 summaries,the
  frozen DUD and selected source actions/explanations,all four adverse events,
  manifests and registration content. No result-changing bug found.
- Opus had no shell/file access (tools disabled); its supplied-file review
  recomputed all case-level counts and summaries but did NOT inspect raw files.
  This limitation is explicit and is not counted as a second independent raw
  replay. Codex's raw reconstruction and local independent source audit cover it.
- Accepted Opus truth/completeness concern via a separate post-outcome source
  audit without editing the nine frozen scientific sources: independently rebuild
  truths from original S19 game reviews and accepted raw actions; enumerate every
  registered-window source adverse action and assert exact retained-event equality;
  independently check all30 view contracts/routes and strict JSON outputs, then
  bind case predictions/result counts. Three truth/duplicate/completeness
  regressions pass. This supplements the frozen arithmetic checker, which uses
  source-bound cases and is not standalone protocol/provenance validation.
- Codex payout wording accepted in review notes: no separate payout/history fields
  are supplied; full explanations retain their original payoff amounts and
  reciprocity claims. The scientific design/source bytes remain unchanged.
- Opus descriptive conflict suggestion accepted only as prose: the both-view
  predictions include the previously listed contradictions. No selected subgroup
  estimate/test,label,threshold change or secondary promotion added.
- Confident error is the registered operational term for a wrong non-null answer;
  no confidence probability was elicited. Abstentions stay in the denominator
  and are displayed separately, not dropped from analysis.
- Result commit/push and full-history clean clone are final release steps, not
  claims already completed at the time critics read the draft.
