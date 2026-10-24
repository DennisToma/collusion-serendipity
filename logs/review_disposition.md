# Iteration 1 review disposition

## Methodology

Independent Opus and Codex reviews are saved alongside this file. Opus returned
before S01 outputs; its exact-price identifiability caveat barred promotion from
the linear diagnostic. Codex returned after S01 diagnostics and before live S02;
S01 primary estimates were unchanged, its score-bootstrap intervals explicitly
became descriptive, and S02 execution slots were randomized within seed blocks.
No prediction setting was tuned. Both S01 absolute improvement and relative
contrast are reported; neither gives a resolved channel-pair gain.

The originally declared S01 channel-versus-control difference was missing from
the initial JSON. Added it as a secondary descriptive contrast after the code
review, using the same held-out predictions and fixed seed; no primary estimate
changed. This is not a new tuning attempt or independent validation.

## Implementation

`implementation_codex.md` found five issues, all using offline mocks:

1. Generator now rejects wrong model/backend routing labels before accepting an
   action. Limitation retained: llm.py labels the requested route; it does not
   attest server identity. The completed fallback uses explicit Codex model
   routing. Do not describe it as independent verification of the served model.
2. Analyzer now requires complete round/firm call coverage, contiguous attempts,
   bounded retries and model/backend summaries, before computing estimates.
3. New raw cache responses retain original call start/completion UTC; replay uses
   those persisted values. Game start/end timestamps describe the invocation.
   The one older response in the aborted gateway attempt lacks these times and
   is not included in any scientific estimate.
4. Cache loader quarantines only a torn final record and preserves all complete
   records. It rejects interior corruption; a test checks both cases. It also
   terminates a valid non-newline final record before subsequent appends.
5. S01 secondary contrast added as described above.

Seven focused validity tests pass, including planted nonlinear signal recovery,
Nash/joint-payoff enumeration, strict parsing, channel timing/privacy, grouped
fold integrity, wrong/missing provenance rejection, and torn-cache recovery.
Fresh dry replay is byte-identical and refuses configuration drift or accidental
publication of synthetic data. An earlier dry fixture changed export ordering
after the pre-live schedule amendment; it was discarded as a verification
fixture, with no live outcome or economic calculation changed.

## Runtime

The original Aqueduct attempt stalled with four started game slots and one cached
decision, no completed game. Its partial output is retained under
`data/s02_cournot/INCOMPLETE.json`; it is not a null scientific result. The fallback
was registered before completed-game outcomes and uses the remaining six game
slots, a pinned gpt-6-luna/Codex route, and a new directory. The same economics,
prompts and outcome definitions remain frozen. Three seed blocks cannot produce
a HIT under the retained exact-p rule. Temperature is not exposed by Codex exec.

## Final claims

Both final reviews completed (`final_claims_codex.md`, `final_claims_opus.md`)
and matched the reported numbers. Applied: show actual S01 primary n32/n15 beside
total scanned n104, no-channel control gain, all prespecified S02 secondary
outcomes, essentially unchanged profits, final-round quantities, the seed driving
the reduction, and n3 bootstrap-range limitation. Mark the changed model/sample
as a runtime deviation overriding the initial no-fallback plan; tag analysis
temperature as requested-only. Model/temperature labels are not attestation.

Opus suggested the pair-as-one-actor benchmark q4/4/8, P14, profit32 per pair
firm. Enumeration verifies that example but finds THREE discrete grid equilibria
(total pair output 7/8/9 against outsider 9/8/7). Their pair-total profits
56/64/72 do not exceed the unmerged pair's 72; do not claim a unique discrete
equilibrium or that every such equilibrium strictly reduces total pair profit.
The benchmark is interpretation added after outcomes, not a new experiment or
detector setting. Original S02 contrasts and verdict are unchanged.

The full rendered write-up is REPORT_DETAILS.md; REPORT.md is a compact one-page
log preserving primary and secondary outcomes and the central limitations.
