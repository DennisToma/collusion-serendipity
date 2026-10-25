# S34 review dispositions

## Before outcomes

Both design critics completed with process exit0. Codex read repo files and ran
in-memory synthetic checks. Opus reviewed supplied source text without tools;
its context preceded the fixture-clock and preflight patches. Neither saw live
S34 outcomes,which did not exist during review.

- Codex medium actual-call pairing: accepted. Publication now checks first actual
  transport starts within60s and overlapping first-start/last-completion lifetimes.
  Wrapper timestamps are insufficient. Synthetic serial-transport canary rejects.
- Codex medium preflight chronology/headroom: accepted. Runtime checks record an
  exact UTC timestamp;publication recomputes remaining seconds from it,orders
  launch/execution/runtime/dispatch/first admission,checks required headroom at
  actual first admission. Cache also enforces this before the first transport.
  Seven isolated serial/touching/start-gap/timestamp/headroom canaries pass.
- Opus medium future fixture expiry: accepted before its review finished. All new
  S34 temporary/mocked fixtures pin only sim.salience.now to00:40UTC;real archive
  analysis/release never imports this test clock. Historical frozen sources unchanged.
- Opus low retry ambiguity: inspected llm.chat's range(retries):retries=1 means one
  outer attempt. Explicit backend gives one route;_codex deduplicates model and
  cheap fallback,which are both gpt-6-luna here. Thus one CLI process per logical
  transport invocation;provider-side internal execution remains unattested.
- Opus low commit coverage: raw caches are not gitignored;remote clean-clone
  reproduction will test all required artifacts after results are pushed.
- Opus slow admission/order caveat retained. No causal interpretation of first-call
  ordering;local binary hashing is guarded identically in both arms.
- Opus floor and wording interpretation: accepted for results. Plain rates must
  accompany DUD;screen branch will be reported. The flag says request a check but
  no check runs;it is recorded only. No deterrence,attention or schema-only claim.

Patch-specific Codex review completed exit0. It confirmed chronology/headroom
fixes and reproduced a touching-endpoint loophole. Accepted:changed overlap to
strictly positive,added its endpoint canary,isolated start-gap and late-runtime
mutations,and persisted its first-admission-before-transport rejection check.
All15 scoped tests pass after these changes. No additional scientific call.
Remaining context:the patch review saw the pre-fix comparison;the final small
boundary/test fix is manager-verified and final critics will see frozen sources. Original code review findings remain in
logs/s34_design_codex.md and logs/s34_design_opus.md. No scientific call has run.
