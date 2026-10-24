# S04 independent review disposition

## Before live games

Both [Codex](s04_design_codex.md) and [Opus](s04_design_opus.md) reviewed the
methodology independently. All changes below precede live game outcomes and are
recorded in DESIGN_S04.md and registration commit 3f75341.

- Cache separation is already by run/arm, round, role/slot, attempt and model;
  a mocked live-call test verifies separate samples and reuse only of the same key.
- Existing Codex adapter uses a fresh empty cwd, read-only sandbox, no resume,
  no-tools instruction. This is context isolation, not an OS file-read boundary.
- Synthetic instrument precheck added, separate cache; no prompt/model selection.
- Routable second-member variation, rather than full-vector variation, gates
  every verdict. <25% => UNINFORMATIVE; all-round variation remains descriptive.
- DUD no longer discards consistent moderate effects via a bootstrap bound.
  Consistent large reverse effects are ODD-reverse; a single primary retained.
- No fresh seeds, shortened arm, deletion of failed blocks or partial estimates.
  Exact cached resume only; unresolved failure => inconclusive.
- Fixed seed-block barrier limits drift. Sign-flip is a conditional enumeration
  diagnostic, requiring slot exchangeability/symmetry, not guaranteed calibration.
- Added unshown outsider-advice matching, all-round/final-round outcomes and an
  exact roundwise accounting decomposition of pair-profit changes.
- Kept common sampling interpretation narrow: no strategic hub/advisor claim,
  no detector performance or intent claim, no public-message absence proof.
- Planning power note uses unstable n3 S02 variance; no new outcome data. No
  co-primary added, to avoid widening the pilot's result-selection rule.

## Final claims

Pending full-arm completion and independent review. No hit promoted.

## Implementation review, before complete outcomes

[Codex review](s04_implementation_codex.md) found one blocking numerical bug:
an exact -1 quantity contrast could round to -0.9999999999999997 and miss the
registered magnitude threshold. Fixed using integer totals and Fraction means
for quantity/profit verdicts and exact sign enumeration; exposure gate also uses
an exact count/90. Added a regression test including zero profit. No scientific
rule changed, no full-arm estimate inspected; corrected hashes recorded in
s04_analysis_freeze.json. All 13 tests and a complete offline synthetic analysis
pass. No other blocking implementation issue was found.
