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

## Final claims reviews

Both final critic processes completed exit0;the parent runner also exited0.
Codex independently reread raw games/cache and reproduced8/40vs7/40,+.025,
bootstrap[-.100,.150],t[-.177366,.227366],all32 sign tails(.5/.75/1),
all50metric cells/15bootstrap+t summaries/15sign tails/200bindings,full replay,
20source registration/runtime/chronology checks and nine read-only checks.
No result-invalidating issue found. It did not inspect the figure,full write-
requiring suite or remote clone;manager separately checked figure/304tests.

Opus was supplied-text-only with CLI tools disabled. Its statement about Bash
calls returning no output is unverified;it did not independently reread raw data.
It hand-reconstructed supplied counts,primary/bootstrap/t arithmetic,screen and
stage payoffs. Its phrase three positive blocks is an error:there are TWO strictly
positive,TWO negative,ONE tie (three nonnegative);the numericalp=.5 is correct.
Its proposed implication that an unrequested check makes the field behaviorally
inert is not adopted:agents still emit the added field;no primary report=true
requests occurred,but wording/output attention/downstream choices still differ.

Accepted Opus primary-request disclosure:REPORT now explicitly says all80 primary
flag decisions report=false,not just the table's0.000 count. No warmup claim.
Baseline cap wording already fixed. No schema-only,attention,deterrence,agreement,
equivalence or S33-explanation inference. All means/intervals/verdict unchanged.

Opus low retry concern was answered by the pre-live llm.py audit:range(retries),
explicit route and deduplicated identical cheap model give one outer transport
invocation;provider-internal behavior remains unattested. Hardcoded written100
is justified by five games each with20 bound actual notes;all200raw note/reason
bindings and actual nonempty100/100each pass. Redundant guards remain frozen.

Both critics' release concerns are accepted:results must be committed/pushed and
origin cloned before completion. The disposition link is tracked in7427939 and
all104 current local links passed the manager release. Origin remote clone of830a62d now passes complete cache-only release,15 S34
protocol tests,independent reconstruction and six byte-identical published
artifacts;clone git status clean. logs/s34_clean_clone.json records the receipt.
Existing frozen dependency environment reused;not a new dependency install.
No additional scientific calls,frozen source changes,tuning or pooling.
