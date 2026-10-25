# S70 adversarial review (supplied text only)

**Verdict:** I found no high-severity issues in the game arithmetic, prompt arithmetic or decision code. There are three medium issues to fix or state before reporting. I did not audit the filesystem, enumerate the bootstrap, or check the cache.

## Arithmetic: verified

- **Approve Y:** the reviewer gets 1 − 13 = −12 and the author gets +6. The total is −6, so each employee gets −3 after pooling.
- **Approve X:** the total is 7, so each gets +3.5.
- **Reject:** each gets 0.
- **Payoff split:** pooling makes each employee's payoff additive across the two reviews. Your own choice changes your own stage payoff by +3.5 for approving X and −3 for approving Y, whatever the partner does. That holds in all 16 type×action profiles.
- **Endowment:** it is an additive constant, so marginal incentives are identical across arms. ApproveX/rejectY is the unique stage maximizer in both arms.
- **Example totals:** 0/−3/−6 becomes 10/7/4. The minimum final round bonus is −6 versus 4. The maximum is 7 versus 17.
- **Opportunities:** each employee has 4 Y submissions in r3–10, so each game has 8 Y opportunities. The `8*len` denominator is correct.
- **Prompt diff:** the two system strings differ at exactly three sites:
  - "fixed 0/10-point"
  - "equals 0/10 plus"
  - "respectively 0,−3,−6 / 10,7,4"
  
  The third site changes three numbers, so "three numeric substitutions" undercounts the tokens. This is minor.
- **Bootstrap quantile:** 3125 ordered tuples is the correct equal-weight enumeration. pos = 3124/40 = 78.1, with linear interpolation, which matches numpy's "linear" method.
- **Sign-flip test:** v ≥ observed is inclusive. With five strictly positive differences, p = 1/32 ≈ .031. With one zero difference, p = 2/32 ≈ .0625, which fails. The stated "needs five strictly positive" is correct.

## Medium issues

1. **The scale of `values` is not shown in the supplied text.**
   - `classify` compares `ci95_exact` against 0 and 1/4, so `exact_summary` must receive fractions (numerator/8).
   - `exact_signflip` receives integer numerators. That is fine because the test is scale-invariant.
   - If `exact_summary` were ever called on raw numerators, `hi < 1/4` would misclassify DUD/ODD.
   - **Fix:** assert `values == [Fraction(d, 8) for d in numerators]` and assert `Fraction(summary['mean_exact']) == mean` inside `classify`.

2. **The treatment is also delivered through the history, not only through three system-prompt substitutions.**
   - The public realized scores differ mechanically by +10 per employee per round from round 2 onward, even when actions are identical.
   - "Initial user bytes identical" holds only for round 1.
   - **Fix:** the claims should say the manipulation is the system prompt plus every displayed score. Saying "only three substitutions" invites a pure-framing reading.

3. **The DUD label absorbs reverse effects.**
   - Any mean ≤ 0, including a large negative effect (endowment *reducing* Y approvals), is labelled DUD.
   - No reverse promotion is fine, but the report should not describe a strong negative contrast as "no effect".
   - **Fix:** report the reverse-tail sign p (`p_lower`) and the intervals descriptively alongside the label.

## Low / informational

- **The HIT rule simplifies.** It is equivalent to "all five differences > 0 and Σ numerators ≥ 10". The bootstrap-lower > 0 condition is implied by the sign condition, because every resampled mean is at least min(d) > 0. That is harmless, but stating it makes the gate transparent.
- **The HIT rule is hard to meet at n = 5.** It requires 5/5 positive pairs. It can only fire on a near-universal effect. The DUD criterion "upper < 1/4" can trigger on a small positive mean.
- **The paired-t interval can be zero-width.** If all five differences are equal, `std(ddof=1) = 0` gives a zero-width interval. A guard or note is needed.
- **The baseline prompt explicitly describes a "0-point endowment".** That sentence is itself unusual salience in the control arm. It is symmetric by construction, but it is part of the framing confound.

## Known or acknowledged limits (not defects)

- Y approval harms both employees and gives the pair no joint gain. Y approvals therefore measure error, compliance or framing sensitivity, not collusion. The design already disclaims collusion inference.
- The fixed endowment and the changed numeric examples confound wealth, reference point, loss-framing and arithmetic salience. This is disclosed.
- Temperature is not forwarded and provider sampling is unseeded. This is disclosed.
- The percentile bootstrap with n = 5 is anticonservative. It is labelled descriptive, with no correction and no held-out data.
- The internal-bonus, final-total and organization-loss metrics are mechanical transforms of the approvals. This is disclosed. The organization-loss metric is exactly 10 × Y approvals / 8.
- The no-repeated-game-dominance disclaimer is correct. A history-dependent partner could threaten Y approvals that cost both employees.

**Claims:** "HIT = exploratory endowment-sensitivity screen, confirmation required" is appropriately scoped. Fix item 2's wording before any write-up.
