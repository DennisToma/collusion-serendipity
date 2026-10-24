# S03 review disposition — iteration 3

Before live calls: [Codex](s03_design_codex.md) and [Opus](s03_design_opus.md)
both completed (exit 0); neither critic ran live models or edited files.
Initial registration commit: 424c351. All fixes below precede live outcomes.

- Codex high provenance defect: store full request payloads/response hashes in
  requests.jsonl; validate key/digest sets; integrate complete cache-only replay
  into the analyzer before estimates, with live calls forbidden. Separate verifier
  repeats replay, compares exports, independently recomputes primary and regrets.
  A tampered reasoning-note regression test fails as required.
- Both critics' freeze defect: hash s02_analyze helper, uv.lock and pyproject.toml;
  require exact manifest membership/version. Record Python/NumPy/SciPy versions.
- Codex execution controls: pin gpt-6-luna/codex and workers=2 before calls; record
  concurrency and cutoff. At/after 16:35 UTC no new uncached requests; in-flight
  responses retained. Cached replay allowed after cutoff.
- Codex optimized-Python defect: fail immediately under -O in simulation/analysis/
  verification. Required integrity checks therefore cannot silently disappear.
- Codex parser defect: S03 dedicated JSON-only parser accepts only integer q,
  string reasoning <=40 words, empty private_message; extra fields ignored.
  No prose extraction/integral floats/truncation. Dry-only dummy adapter empties
  the shared harness's fake message; original dummy response still audited.
- Opus table-economics check: exhaustively compare all 13^3 action combinations
  against the actual payoff engine. Reviewer remedy's [0] meant profit tuple;
  the correct implementation uses payoffs(...)[1][0], not the market-price value.
- Opus objective wording: original shared system already says own total profit
  over many rounds; additionally put the reminder in BOTH arms, so table/caption
  is the entire interface contrast after completed history.
- Both: exact-sign zero/tie tests; all five positive primary contrasts required
  for n5 HIT. Bootstrap sign clause redundant but retained as registered.
- Interpretive limits retained: arithmetic/salience/myopia bundled; lag best
  responses can cycle without a mean shift; output alone cannot establish
  collusion; |q-6| is distance to symmetric Nash (asymmetric grid Nash also exist).
  Submission slots are randomized, but parallel server draws are uncontrolled;
  pairing provides temporal blocks, not common random numbers.
- Documentation: cached exact requests are now stored, not merely reconstructible;
  temperature is requested in shared harness but uncontrolled in Codex.
- Validation: 21 tests PASS, including complete dry analysis/replay, strict parser,
  deadline/cache reuse, missing/empty manifests, malformed cache, tampering and
  incomplete/dry publication gates. Final complete dry run uses /var/tmp only.
  Intermediate dry failures came from the inherited dummy's fake message and
  were corrected before all tests passed; no live calls/data were involved.

## Final claim reviews

Pending complete games, independent verification, and report rendering. No HIT
promoted and no scientific outcome viewed at the design freeze.
