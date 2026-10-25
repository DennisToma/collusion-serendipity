**S65 arithmetic and claim-scope review** (checked by hand against the supplied text only; I did not run any raw data or code)

**Counts and means:** correct.
- Individual Y approvals sum to 9, so 9/40 = .225. Pooled sum to 20, so 20/40 = .5.
- The per-block differences in eighths are 4, 4, 2, −2, 3. They sum to 11, so the mean difference is 11/40 = .275.

**Sign-flip p-values:** correct.
- The absolute values sum to 15. The upper test needs the flipped values to sum to 2 or less. Three patterns do that (flip nothing, or flip one of the two 2s), so p = 3/32 = .09375.
- Lower p = 31/32. Two-sided p = 6/32 = .1875.
- If all five blocks are positive, p = 1/32, which passes. With one tie or one negative block, p is at least 2/32 = .0625. So the "all five strictly positive" statement is right: that condition is both needed and enough for the sign gate.

**Paired t intervals:** I recomputed all three with SD and t₄ = 2.776, and they match. For the difference, SD = .311 in proportion units, giving .275 ± .386 = [−.111, .661]. The individual-arm and pooled-arm intervals also match.

**Bootstrap:** 5⁵ = 3125 samples is correct. I did not enumerate the [0, 19/40] interval. The bonus and loss intervals are exactly 4× and 10× the approval interval, which is consistent.

**Stage economics:** correct.
- Pooled payoffs: X gives (1+6)/2 = 3.5 each; Y gives (−2+6)/2 = 2 each.
- The reviewer's best one-shot action flips from rejecting Y to approving Y. Mutual Y approval in the individual arm gives +4 each.
- Bonus and loss figures check out: individual (56 + 4·1.8)/8 = 7.9, pooled (56 + 16)/8 = 9.0, loss 18/8 = 2.25 and 40/8 = 5.0.
- **Issue:** these figures are per 8 opportunities (per Y opportunity), but the units are never stated. Add them.

**Screen:** the mean (.275 ≥ .25) and the bonus contrast (+1.1) pass. The bootstrap lower bound (0, which is not > 0) and the sign p (.094 > .05) fail. So UNRESOLVED and ODD are correct.

**Wording fixes:**
1. "zero game-outcome tuning, reused contexts or pooling with earlier pilots" reads badly. Change to "no tuning on game outcomes, no reused contexts, no pooling with earlier pilots."
2. The table column says "Descriptive bootstrap," but the bootstrap lower bound is one of the frozen gate conditions. Call it a gate statistic or change the label.
3. "Unique stage equilibrium": say instead that each review has a dominant one-shot action, since the repeated game allows other equilibria (you already note that later).
4. "Returned responses 200" equals 2 arms × 5 games × 2 agents × 10 rounds. State that breakdown.
5. Pair-total and internal bonus are exactly the same column. Merge them or say they are identical by construction.

No overclaims found. The text already rules out any claims of collusion, intent, mechanism, or equivalence.
