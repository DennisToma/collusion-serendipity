# S11 independent review dispositions

## Methodology, before live outcomes

Both critics requested before any live S11 calls. Codex reads current source;
Opus receives a fixed stdin snapshot. Later guards are recorded below.

Codex design review exit0: found one medium provenance-resume bug. The cache
could backfill a missing request entry after a pre-existing response. Fixed
before live calls: constructor rejects any pre-existing key-set mismatch and
verifies every request hash, response hash and dry flag. Two new regressions
cover missing and corrupted provenance; no repair occurs. Accepted all listed
scope limitations: full feedback/own recall/warmup/lag wording bundle; n5,
backend interference and uncontrolled sampling; consecutive smoothness is not
convergence, long-run variance reduction or collusion removal. The critic
found no remaining timing/arithmetic/screen error. Its snapshot predated the
new constructor guards; the final review will inspect frozen sources.

Opus design review: pending; no live calls yet.

Opus design review exit0: no blocking implementation defect in pasted snapshot.
- Retained the common directional screening rule used by preceding pilots, including
  five-negative ODD-reverse screen. Every DUD reports the actual mean and intervals;
  DUD never means "nothing here" or equivalence. A strong mixed reverse would be
  shown explicitly. No outcome has been inspected.
- Accepted explicit caveats: naive delayed best response predicts smoother
  consecutive changes, so this alone is not surprising evidence of learning,
  stabilization or collusion removal. Any HITS handoff must say so itself.
- Explained n5 HIT equivalence (five positive differences, mean>=1); bootstrap
  and p conditions are not independent evidential checks.
- Clarified shared RNG2411 draw order in DESIGN before outcomes. No numerical
  estimator change; independent exact3125 bootstrap remains supplementary.
- Source registration/remote ancestry and first-call chronology will be checked
  operationally after push and before generation. No server-time attestation is
  claimed. Historical transport observations S03/S07 are 15-18 minutes for~370
  calls; the critic's two-hour estimate is not supported by those observations.
- Several cited test gaps/tautological test were fixed while the fixed Opus
  snapshot ran. Current tests include no same-round leakage, full dry export/
  source/version/game/failure/cache tampering and missing/corrupt provenance.
- Switched config temperature constant to TEMPERATURE. Fixed own locking resource
  cleanup below; no live scientific request or outcome yet.
