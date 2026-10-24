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

Final reviews: pending.
