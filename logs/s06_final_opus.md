# S06 review: denomination invariance

**Verdict:** I found no remaining bug in the code you gave me for treatment timing, provenance, inference or decision rules. Every guard that earlier reviews asked for is present. What's left is one out-of-date document, one gap in what the independent check covers, and one problem with how the result is read. That last one matters more than the code.

**What I could check:** shell access was turned off in this session, so I couldn't open the raw games or run any scripts. I redid every number in `results/s06_summary.md` by hand, from the per-game metrics in `results/s06_denomination.json` and the code you pasted. So the per-game values themselves are taken on trust from the analysis and the independent checker, not rebuilt from raw games.

## Numbers I recalculated (all match)
- **Primary outcome** (mean quantity per firm, rounds 4–12):
  - UNIT block totals are 162/161/162/158/162, which gives 805/135 = 5.963.
  - CENT block totals are 154/142/159/162/152, which gives 769/135 = 5.696.
  - The block differences are [−8, −19, −3, +4, −10]/27, so CENT minus UNIT = −36/135 = **−0.2667**.
- **Paired t interval:** the differences have standard deviation 8.526/27. With t(4) = 2.776 the interval is [−0.659, +0.125]. ✓
- **Exact sign-flip test:** the absolute differences add up to 44. Only 3 of the 32 sign subsets give a total of 4 or less, and 3 more give 40 or more. That makes the two-sided p = 6/32 = **0.1875** and the lower one-sided p = 0.09375. ✓
- **Verdict:** |−0.267| is above the 0.25 cutoff for DUD and below the 1.0 needed for HIT, so the label is **ODD**. ✓
- **Arm means for price, profit, both regrets, distance from Nash, change and all-equal:** all match the per-game values, as do the block differences. That includes 86.926 for block 24161 and −5.111 for block 24163.
- **All-round and final-round tables:** all 16 cells match.
- **Counts:** 240 metric cells = 10 games × 3 windows × 8 metrics; 24 bootstrap intervals = 8 × 3; 362 cached responses = 360 valid + 2 rejected.
- **Price clipping:** CENT price is 13.2, not 30 − 3 × 5.696 = 12.91. The gap comes entirely from block 24161, where total output went above 30 and price was clipped at 0. That fits its 0↔12 pattern and its negative profit.
- **Not checkable by hand:** the 10,000-draw bootstrap bounds. They agree with the separate enumeration of all 3,125 resamples, which gives [−70/135, −3/135].

## Remaining problems
1. **`REPORT.md` is out of date.** The S06 row still says "Registered… No live results yet / Pending", the header still says "S06 registered", and the "Next:" line still suggests running S06. This is the only definite fix needed before release.
2. **Some summary claims come from code that isn't frozen.** These claims are:
   - extra requests by arm, `{'cent': 2}`;
   - rejection reasons, `reasoning_over_40_words: 2`;
   - the last-response timestamp.

   As far as I can tell they come from `scripts/s06_release.py`, which is not in the frozen source list and shows as modified in git status. `s06_independent.py` doesn't recompute them. The total 362 = 360 + 2 does match, but the per-arm split and the reasons have no second check. Freeze or commit the script before release, or add these counts to the independent check.
3. **Small:** `logs/s06_review_disposition.md` still says "Final reviews: pending" while the final review logs already exist. It needs a closing entry.

## Interpretation problem: the primary result is mostly cycle phase
The pinned code works like this: once a firm has the calculator, it picks the best response to its rivals' previous outputs. If all three firms start at the same quantity q, they then swing between q and 12 − q forever. Over any even number of rounds that averages exactly 6. The primary window is 9 rounds, which is odd. A cycling game therefore misses 6 by ±|q − 6|/9, and which way depends only on the phase at round 4.

The data fit this:
- Block 24162 CENT is a clean 5↔7 swing: every round all-equal, distance 1, change 2, stage regret 4, regret against the calculator 0, mean 159/27. Its −3 difference is pure phase.
- The other CENT blocks look like 4↔8 (24160, 24164) and 0↔12 (24161) swings.
- Over all 12 rounds, an even window, the arms barely differ: UNIT 6.011, CENT 5.956.
- The result sits 2/135 away from being a DUD. That is about three firm-units of output in the whole run.

So the ODD label is fragile, and it should not be read as CENT lowering output. The design does say "phase-sensitive", but the summary understates how much that drives this result.

The pattern that is actually informative is in the secondary outcomes, and it is post hoc. UNIT games locked onto Nash: all-equal 0.93, regret against the calculator exactly 0. CENT games kept cycling: change 3.94 vs 0.49, all-equal 0.64. In both arms firms still followed the calculator closely (that regret is ≤ 1.4).

My guess at the mechanism is that the treatment bites in the first round or two, before the calculator appears, when firms must solve the scaled formula themselves. For example, UNIT blocks 24160 and 24164 sit at 6 in every round from round 1. The calculator then keeps whatever start they chose. Looking at the round-1 raw actions would test this.

The secondary results can't be promoted, for three reasons:
- UNIT sits at zero for distance, change and regret, so any noise in CENT shows up as a "difference". These are not fair two-sided tests.
- Block 24161 dominates, for example −51.9 of the −68.9 total profit difference.
- Every paired t interval includes 0.

Block 24163 runs the other way (UNIT cycled, CENT locked onto Nash), which suggests the lock-in is random in both arms. Any follow-up needs a new registration with a phase-free outcome, such as "locked onto Nash by round 4" or round-1 distance from 6.

## Known limitations (already disclosed, not bugs)
- Only n = 5 blocks. The two-sided p cannot go below 0.0625, and the 0.10 cutoff is a screen, not a significance test.
- The bootstrap and sign-flip conditions are not independent. The sign-flip test assumes the arms are exchangeable.
- The 100× scale changes size, formatting and the conversion cue all at once; real stakes are unchanged.
- One model, one scale, 12 rounds, and calculator-assisted play only.
- The calculator is not a forecast.
- There is no server-side check of time or model, and model labels are client metadata.
- Transport retries already in flight could finish after the cutoff. There is no atomic cancel, and SIGKILL can't stop requests already sent.
- Block IDs don't seed the model's draws.
- DUD would not mean equivalence.
- There are no agreement or collusion labels.

The scope language is otherwise sound. The summary doesn't claim a hit, uses the two-sided p rather than the one-sided 0.094, and keeps the secondaries from changing the verdict.
