# S72 review (supplied text only)

**Verdict:** I found no correctness bugs. Every displayed number I could check agrees with the per-game table. The claim scope (post hoc, ODD/context-only, no tests, no HIT) is stated consistently. I didn't open raw or game files, archives or source, and I didn't enumerate the bootstrap. "Reconstructed" below means recomputed by hand from the summary's per-game table.

## Checks that pass
- **Comparator.** Approving Y costs the reviewer 2, and missing an X costs the reviewer 1. So "approve X, reject Y" is strictly dominant for each reviewer, and the "unique one-shot Nash" claim holds.
- **Algebra.** The two individual excesses sum to 4·Y − 7·missedX, which matches the stated pair formula.
- **Per-game excesses.** All 10 rows follow from the Y-by-reviewer counts with missedX = 0. For example, 24482 shared gives 6·3 − 2·3 = 12 for each employee, and 24480 shared gives B = −4, C = +12.
- **Y approval rate.**
  - Self values 0, 0, 0, .125, .125 give a mean of .050.
  - Shared values .25, .5, .75, .25, .125 give .375.
  - The difference is .325.
- **Pair excess per round.** Per-game differences are 1, 2, 3, .5, 0. Mean is 1.3, SD is 1.204, and t₄ = 2.776, giving [−0.195, 2.795]. ✓
- **Minimum individual excess per round.** Self mean is −.100 and shared mean is .250. Differences are −.5, 1, 1.5, −.25, 0, with mean .35 and t interval [−0.716, 1.416]. ✓
- **Full-window both-gain.** Shared values 0, 1, 1, 0, 0 give a mean of .4 and t interval [−0.28, 1.08]. ✓
  - Bootstrap: the sum is Binomial(5, .4). P(0) = .078, so the lower bound is 0. The 97.5% point falls in k = 4 (P(≤3) = .913, P(≤4) = .990), so the upper bound is .8. The interpolation indices (78.1 and 3045.6) both fall within single plateaus. ✓
- **Two-round both-gain.** 2 of 20 windows and the intervals [0, .2] and [−.07, .27] are exactly a ×0.25 copy of the full-window figures. That implies one window each in 24481 and 24482. The summary text doesn't show this placement, so I can't confirm it.
- **Counts.** 16 reviews/game, 8 X + 8 Y opportunities, 21 = 7×3 summaries, 70 = 10×7 cells. full_window_each_has_y = 5/5 follows automatically, since each employee has four Ys. Opportunity counts are equal across arms, which is consistent with matched statuses.
- **Single-round zero.** 0 of 40 is consistent with S53. Both-gain was possible in 9 rounds per arm.

## Not verifiable from the supplied text
- The arm-specific bootstrap bounds, e.g. shared minimum excess [−.45, 1.0], Y rate [.2, .6], and difference [−.30, 1.05].
- Which windows hold the 2 two-round gains, and the 12 and 9 opportunity counts.
- Hash freezing, the 200-response replay, call-blocking, origin-clone reproduction, and receipts from the critics.
- `logs/s72_independent.json` only records counts and `passed: true`. It has no values or hashes, so it doesn't support "independent reconstruction". It's also by the same author, which is already acknowledged.

## Acknowledged limits (not bugs)
- The window scales were chosen after outcomes were known.
- The seven measures are dependent.
- n = 5 blocks.
- Binary t intervals go outside [0, 1].
- Degenerate bounds.
- The comparator changes both actions and doesn't replay histories.
- Provider and runtime aren't attested.

## Interpretive risks to state more plainly
1. **The "both gain" signal is thin.** Both full-window gains (24481, 24482) are just symmetric mutual Y approvals of 2–3 each. Independent, unconditional over-approval at similar rates produces the same pattern. The no-reciprocity disclaimer covers this, but a reader will likely still read "both gain" as cooperation.
2. **The shared-arm Y increase is often one-sided.** In 24480, 24483 and 24484 one employee loses. Pair excess (+1.3) therefore overstates mutual benefit, and the minimum-excess difference CI includes negatives. Lead with this, not with 2/5.
3. **A nit.** The per-game table shows Python dict reprs (`{'B': -4, 'C': 12}`); split them into columns for judges.
4. **Inconsistent brief.** It asks for raw-file reconstruction but limits me to the supplied text. This review only covers the latter.
