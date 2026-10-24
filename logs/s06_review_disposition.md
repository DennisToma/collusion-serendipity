# S06 independent review dispositions

Design critics: both Codex/gpt-6.1-sol and Opus/claude-opus-5-5 exited0 before
live launch. Codex executed read-only synthetic checks; Opus reviewed supplied
file contents without tools. Original reviews retained in this directory.

- Both: partial resume resets game start, rejecting reused paid calls. FIXED
  prospectively: game start is earliest cached call or current start; regression
  covers resumed timestamps and strict subsequent validation.
- Codex: within-game sequential timestamps and inter-block barriers not audited.
  FIXED: both checked before publication; synthetic overlap regression included.
- Codex: independent checker accepts missing metric. FIXED: exact registered
  ordered aggregate metric set and full seed/arm set required; mutation regression.
- Opus: interrupt can leave workers spending. FIXED: iterator BaseException sets
  shared abort before executor cleanup; worker-level exception also sets abort.
  SIGKILL cannot cancel already dispatched transport; cached partial resume remains.
- Opus: gate and transport timestamps differ near cutoff. ACKNOWLEDGED fail-closed
  boundary risk in design; actual-start validation stays strict, no exclusions or
  deadline relaxation. Run has substantial cutoff headroom.
- Opus: edits to frozen docs/tests after outcomes break source freeze. RETAINED
  deliberately; append findings to this file/summary, never change frozen sources.
- Opus: push-before-calls not independently attested. Record source commit,
  observed remote SHA and local UTC before launch; no server-time attestation claim.
- Opus: retry selection may differ by arm. Planned post-run full attempt audit and
  per-arm counts/rejection reasons; no retry-based outcome exclusion.
- Opus: monetary units and conversion grammar ambiguous. FIXED consistently in
  both arms: accounting units per product unit, numeric conversion-rate sentence.
- Removed unused visibility/old-system imports; source manifest includes shared
  dependencies but shared frozen sources have no edits.
- Scope retained: calculator-assisted only, one model/scale/T12; magnitude,
  formatting and numeric conversion cue bundled, real stakes unchanged. DUD is
  not equivalence; UNIT differs from previous pilots. Block IDs do not seed draws;
  submission order randomization is not independent transport-slot assignment.
- Abort guard has no atomic transport cancellation: calls already past guard may
  finish; a second flag check covers the synthetic check/clock race. No claim of
  guaranteed physical cancellation. No live calls/outcomes preceded these fixes.

Final reviews: both exit0; complete dispositions below.

Publication preparation (after outcomes): original frozen scientific manifest
and result SHA f9253e97 unchanged. The non-frozen renderer shadowed its CENT arm
mean with a string loop variable; the first attempt wrote the correct detail
and figure but failed before updating REPORT (ValueError at f(c)). Fixed renderer
variable names and repeat-run paragraph handling; canonical analysis never changed.
Final Opus context was assembled before this presentation fix and may mention the
old Pending report; Codex can read current files. Actual final claims are the same
verified primary/secondary result values. Renderer also explicitly explains the
bootstrap/t/sign disagreement and reports prespecified all-round/cycling metrics;
none promotes a secondary or changes the registered ODD classification.

Final Codex/gpt-6.1-sol review exit0. It independently recomputes every240 raw
metric/window cell, all24 bootstrap/eight t intervals, exact block numerators/
sign tails and unchanged ODD verdict; verifies timing, sources, cache replay and
retry counts. One low-severity issue: the frozen independent checker certifies
arithmetic while accepting reversed contrast/window metadata, denominator999 or
extra duplicate result-game records. FIXED via separate
`scripts/s06_checked_independent.py` contract wrapper, used by README and release;
original frozen source/result preserved. New mutation regression rejects every
shown case, plus missing/duplicated records and changed primary/count/tuning
metadata. Canonical reanalysis already binds the entire result; both protections
now run. Wrapped independent output remains byte-identical to original.

Final Opus/claude-opus-5-5 review exit0. Without shell/raw access, it hand-checks
primary arm means/numerators/t/sign arithmetic, secondary means and all-round/
final tables from supplied per-game metric records. It cannot independently
rebuild raw cells or the10000-draw bootstrap; no such claim is attributed to it.
- Stale Pending report was from the context snapshot before the renderer fix;
  corrected report and repeat-run regeneration now PASS.
- Per-arm rejection reasons/timestamps: actual source is s06_retry_audit.py,
  committed in registration1bb6619 (outside13-file frozen manifest), unchanged.
  Added separate s06_attempt_check.py parsing all362 raw responses without the
  production parser; counts/reasons/first-last times match, and original auditor
  resolves byte-for-byte against registration. Integrated in release audit.
- Phase interpretation accepted with scope: explicit odd-window warning,
  prespecified all-round means, all paired primary/secondary t intervals shown.
  Frozen ODD unchanged; no phase-balanced replacement primary or exclusions.
- Deterministic best-response policy and denomination changing initial choices
  are hypotheses, not established mechanisms: LLM choices can deviate from the
  supplied conditional argmax; contemporaneous regret is not the objective table.
- Secondary metrics were prespecified; selecting a cycling narrative is a
  post-outcome interpretation. No secondary promoted. A boundary/floor alone
  does not invalidate a symmetric between-arm comparison; tiny n, uncertainty,
  uncontrolled sampling and phase dependence remain the stated inference limits.
- Rejected recommendation to inspect a new round1 outcome or design a follow-up
  in this iteration; a new registered pilot must use a different axis first.
