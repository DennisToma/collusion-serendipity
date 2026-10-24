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
- Validation: 8 S03 tests within a 21-test suite PASS, including complete dry analysis/replay, strict parser,
  deadline/cache reuse, missing/empty manifests, malformed cache, tampering and
  incomplete/dry publication gates. Final complete dry run uses /var/tmp only.
  Intermediate dry failures came from the inherited dummy's fake message and
  were corrected before all tests passed; no live calls/data were involved.

## Final claim reviews

All ten games completed; 368 cached calls, 8 invalid-output retries, zero failed
games. Mandatory analyzer replay, separate full replay/export/independent primary
and regret checks PASS. Reanalysis byte-identical and all frozen source hashes
match. Figure visually inspected. Final claims reviews requested below.

Post-outcome interpretation uses prespecified quantity-change and regret metrics:
observed output decrease/cycling is visible, but original higher-output hypothesis
and reverse-screen magnitude rules remain DUD. No secondary HIT or new detector
experiment; no promotion. Presentation supplement s03_present.py leaves all
pre-outcome simulation/analysis/report-source hashes unchanged.

## Final critic outcomes and applied dispositions

Both final critics completed exit 0:
[Codex](s03_final_codex.md), [Opus](s03_final_opus.md).
Codex independently recalculated all 240 game/window metric cells, aggregate
means, seed contrasts, bootstrap/t intervals and displayed tables; complete
canonical reanalysis was byte-identical. Opus independently checked means,
integer totals, sign enumeration, t intervals and table arithmetic; it did not
execute bootstrap code. Both confirm the unchanged DUD verdict and find no
numerical defect in this dataset.

- Opus C1–C3: explicitly state above-Nash control baseline, extra low-output phase
  in the nine-round primary window, all-round 4/5 negative contrasts, calculator
  all-round mean 6.006 near Nash 6, phase-sensitive endpoints/price/profit and
  profits below static Nash. No secondary/negative-tail HIT or changed window.
- Opus C4: describe lag-regret as table adherence/manipulation check; current-rival
  regret is a one-stage diagnostic, not dynamic rationality or proof of mechanism.
- Opus B1: inherited Cache can normalize a malformed last line during construction.
  Added read-only s03_audit preflight that requires newline-complete raw evidence
  before reconstruction; current raw hashes unchanged. Frozen code retained.
- Both critics' unused-cache defect: s03_audit now requires every raw key consumed
  exactly once, matching all recorded attempts and request keys. All 368 pass.
  Publication regression test rejects orphan/missing requests.
- Codex incomplete-verifier defect: the new audit binds result SHA256, requires
  byte-identical full canonical results and independently recomputes the rational
  queue classification. New tests reject a changed verdict, changed confidence
  bounds, and even a canonical-equal but wrongly labeled result. All pass.
- Opus timing/retry details: audit parses actual UTC datetimes; every game ended
  before the cutoff, and all logical starts preceded it. Invalid retries are
  calculator 5 / none 3, all reasoning >40 words; all failed attempts retained.
- Codex transport-cutoff defect: llm.chat may retry internally after the wrapper
  deadline check. This limitation of the FROZEN transport harness is retained,
  not claimed fixed by logical timestamp checks. The entire run finished before
  16:08 UTC, well before 16:35, so it cannot explain this run. Future strict
  cutoff enforcement must occur per backend/transport attempt, with separate
  attempt logs, before any new experiment relies on that boundary.
- Test wording corrected: 8 S03 tests within a 21-test pre-run suite. Two further
  publication-audit regression tests pass after concrete final-review findings.
- Opus low-severity notes do not justify changing any scientific outcome, parser,
  threshold or window after results. Nearly deterministic paths, n5, uncontrolled
  API draws/interference and the bundled treatment remain stated limitations.

No new model calls or experiment followed completion. No HIT or sibling headline
change. The next portfolio work is D/E/F, before deepening own/B/A/C axes.
