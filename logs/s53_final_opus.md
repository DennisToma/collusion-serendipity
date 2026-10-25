# S53 adversarial review (supplied text only; game files not read; no edits; no model calls)

**Verdict:** All the S53 numbers I checked reproduce. I found no arithmetic or game-theory errors. There are two reporting problems and two integrity gaps.

## What I rebuilt from the 80 supplied round records
- **Counts per block (self/shared):**
  - Y approvals: 0/2, 0/4, 0/6, 1/2, 1/1, which totals **2 vs 15**.
  - Missed X approvals: 0 everywhere.
  - Both-Y rounds: 2, 2, 1, 2, 2, so **9/40** in each arm.
  - Mutual-Y rounds: 0. In all 18 both-Y rounds, both agents rejected.
  - Every game has exactly 8 Y-review opportunities.
- **Identities:** regret = 2·Y + missed X, and pair excess = 4·Y − 7·missed X. Both hold for every round and all 16 stage profiles. Regret and payoffs were spot-checked by hand; for example, shared 24480 round 4 gives actual 4/7 against Nash 6/1. Organization loss is 20 vs 150.
- **Stage game:** the one-shot Nash is unique in each of the 4 status pairs. Pareto improvement occurs exactly when a round is mutual-Y. Full approval maximizes the pair's total bonus. All 32 unilateral deviations are consistent.
- **18 intervals:** I counted the exact bootstrap distributions by hand for Y approvals:
  - self: [0, .1]
  - shared: [.2, .6]
  - shared minus self: [.1, .575]
  
  The paired t95% intervals are [−.035, .135], [.0646, .6854] and [−.0488, .6988]. Regret and pair excess are exactly 2× and 4× these, and linear interpolation preserves that scaling, so they match. The other nine summaries are all zero. Everything matches the JSON to the decimals reported.
- **REPORT claims:** 0/15 and 0/2 mutual-Y edges ✓, 9/40 ✓, +1.300 [+0.400, +2.300] ✓, 0/40 vs 0/40 ✓.

## Concrete problems
1. **One metric is singled out in REPORT.** The design says to report all six metrics equally. Instead, the REPORT table row headlines mutual-Y and the prose highlights the pair-excess bootstrap interval. It leaves out that metric's paired t95% of **[−0.195, +2.795]**, which crosses zero. Either show both intervals, or point to the six-metric table without picking one.
2. **The "new" payoff number is S29's result rescaled.** Missed X and mutual-Y are zero in this data, so in practice there is one non-zero quantity, not three. Pair excess is exactly 4× the S29 primary (0.325 → 1.300). REPORT should say this outright so readers don't take it as a separate payoff finding.
3. **The registration receipt is untracked and not hashed.** `git status` shows `?? data/s53_registration_receipt.json`. `checked_manifest()` reads that file, so a fresh-clone `--release` fails until it is committed. Even once committed, it is a local claim that nobody else can check. Only git or remote push history can actually show the timing.
4. **`byte_identical=bool(before)` is misleading on a first run.** On a first release it records `False`, which reads like a failure when the check simply never ran. Use a three-way state: not checked / identical / changed.
5. **Minor:**
   - `game_metric_cells=60` is a hard-coded constant, not a counted value.
   - The independent checker accepts the highest attempt number, not the attempt that was actually accepted. This doesn't matter here (0 rejections), but it is fragile.
   - The REPORT S53 row doesn't carry the "(degenerate)" tag that other rows with zero-width intervals use.

## Findings worth stating more precisely
Every one of the 17 Y approvals happens in a mixed-status round. In each, the approver's own work passed and was approved back in the same round. Each approver takes −2 against Nash, so no Y approval paid off for the person making it in that round. "Other edges" is therefore really "all mixed-status." But because approving X is the dominant choice anyway, an X approval received in return cannot be read as reciprocity.

## Acknowledged limitations (not bugs)
- The analysis is post hoc on already-inspected S29 histories, with 5 blocks.
- The intervals are descriptive and uncorrected; nine of them are degenerate zeros, which does not mean equivalence.
- The analysis is static: it says nothing about repeated-game equilibrium, delayed reciprocity, intent or mechanism.
- Note delivery and stated readability are bundled in one treatment.
- The `llm.chat` patch is not real process isolation. Also, a `from llm import chat` that runs inside the patch keeps pointing at the mock afterwards.
- Runtime settings are not attested.

The scope wording ("context-only," "not agreement," S29 stays ODD) is appropriately careful.

## Not verified
- File hashes, the commit/remote receipt, and the S29 analyzer and independent-check replay. I had only the supplied text, not the raw archive.
- The 200 raw response/request bindings.
- Figure contents.
- Byte-identical re-release.
- Tests actually passing.
