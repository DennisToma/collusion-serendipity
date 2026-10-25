# S70 adversarial review (supplied text only)

**Verdict:** I found no high or medium issues. Everything that can be checked from the supplied text holds, including the bootstrap and sign-flip results. The DUD call is correct, and the claims stay within what the data supports.

**Scope:** I worked only from the pasted design, summary and verification JSON. I did not open the repo, the raw games or the caches, and made no edits or LLM calls. I rebuilt the statistics from the per-seed table, not from raw games, so I can't vouch for cache or provenance.

## Game, reward and prompt arithmetic: all correct
- **Per-approval increments:** approving X gives 6+1=7, pooled to +3.5 each. Approving Y gives 7−13=−6, pooled to −3 each. Rejecting gives 0.
- **Unique best action:** each reviewer's own action changes their bonus by +3.5 (X) or −3 (Y), and the 10-point endowment is a constant. So approve-X / reject-Y is the unique best stage action in both arms. It is also best for the partner and the pair.
- **Bonus range:** with both Y tasks approved, the endowed arm's minimum is 10−6=4 and the baseline's is −6. The prompt examples 0/−3/−6 → 10/7/4 match 0, 1 and 2 Y approvals.
- **Counts:**
  - 4X+4Y primary tasks per employee gives 8 Y opportunities per game and 40 per arm.
  - 10 games × 10 rounds × 2 employees = 200 calls, which matches 200 request histories and 200 note snapshots.
  - 20 system groups and 20 initial prompts = 10 games × 2 employees.
  - 50 metric cells = 5 metrics × 10 games.

## Metrics: all reproduce
- **Approval rates:** Y approvals are 2/40 = 0.050 in each arm; X approvals are 40/40 = 1.000.
- **Internal bonus:** (5×8×7 − 2×6)/40 = 268/40 = 6.700 in both arms. The pair-total bonus is 6.7 + 20 = 26.7.
- **Organization loss:** 2×10/40 = 0.500.
- **Primary result:** block differences are [−1, 0, 0, 0, +1]/8, so the mean is 0. Mean ≤ 0, so the result is DUD.

## Bootstrap (all 3,125 resamples, worked out by hand)
- Each resampled mean is 0.025·S. The counts for S = −5…0 are 1, 15, 95, 330, 685, 873, symmetric about 0, totalling 3,125.
- The linear quantile position is 3124×0.025 = 78.1. Sorted positions 16–110 all have S = −3, so the lower bound is −0.075 and the upper is +0.075. ✓
- The other contrasts are the same distribution rescaled:
  - internal bonus: ±0.75 per block → ±0.45 ✓
  - organization loss: ±1.25 per block → ±0.75 ✓
  - pair total: 20 ± 0.45 ✓
  - X approvals: all differences are 0 → [0, 0] ✓

## Paired t-test (df 4)
- Standard error = 0.125·√0.1 = 0.03953; × 2.7764 = 0.1097, so ±0.110 ✓.
- Rescaled: ×6 = 0.6585 → 0.658 ✓; ×10 = 1.097 ✓.

## Sign-flip tests (32 patterns)
- **Primary:** the three zero differences can't change the sum, so the possible sums are {−.25, 0, 0, +.25}, each 8 times. Upper and lower p = 24/32 = 0.75; two-sided p = 1 ✓.
- **Pair total:** all five differences are positive, so p = 1/32 = 0.03125 ✓.
- **X approvals:** p = 1 ✓.
- **Five-positive rule:** "five strictly positive differences required" is correct. Any zero difference doubles the matching patterns, so p ≥ 2/32 > .05.

## Low issues
1. **Pair-total p = 0.03125 could be misread as a finding.** It comes purely from the built-in 20-point offset. The summary does say this; consider labelling that row "mechanical" in the table itself.
2. **The verification JSON's counts are hard to read.** "15 bootstrap / 15 t / 15 sign" is presumably 5 contrasts × 3, but the 3 isn't named. One way to read it is (baseline, endowed, difference) for the intervals and (upper, lower, two-sided) for the sign tests. The JSON should say which.
3. **The precision can be over-read.** The ±0.075 interval comes from n=5, with only two seeds disagreeing, in opposite directions. It reflects noise, not precision. The summary's no-equivalence statement covers this, but REPORT.md should repeat it if it quotes the interval.

## Known limits, correctly disclosed (not new issues)
- **What the endowment changes:** it alters both the numbers in the prompt and the public score history, so its effect can't be pinned to one mechanism.
- **Run settings:** temperature wasn't forwarded, roles were flattened, and the served model isn't provider-attested.
- **Sample size:** n=5, uncorrected, no held-out split.
- **Ceiling performance:** both arms play almost perfectly (100% X approvals, 95% Y rejections). There was plenty of room for Y approvals to rise, so a null in that direction is informative. A decrease could barely have been detected; the screen is one-directional, as registered.
- **Not a collusion test:** approving Y hurts both employees and the organization, so it's an error, not a profitable collusive act. The "no collusion inference" disclaimer is necessary and present. Any REPORT.md text should frame S70 as a check of sensitivity to income level, not to collusion.

**Bottom line:** the registered DUD for the +.25 increase screen is correct and the numbers reproduce. The remaining open item is checking cache, provenance and per-seed counts against the raw games, which needs the repo.
