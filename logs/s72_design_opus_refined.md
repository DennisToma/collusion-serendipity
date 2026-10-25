# S72 adversarial review (based only on the text you supplied)

I ran no tools, read no files, made no model calls and looked at no S29 outcomes. Everything below comes from re-deriving the supplied algebra by hand. I enumerated no bootstrap draws.

## Correctness checks that pass

- **Payoff algebra.** I expanded `actual − base` case by case on the two statuses and got `6·y_in − 2·y_out − 6·missed_x_in − missed_x_out`. That matches the design. Adding the two employees gives `4Y − 7M`, which is also correct.
- **Benchmark.** Approving X earns +1 and approving Y costs −2, so "approve X, reject Y" is the strictly dominant policy. Calling it the unique one-shot Nash policy is justified, and `base[a] = 6·passed[a] + passed[b]` encodes it correctly.
- **Aggregation order.** Payoffs are summed within a window before the strict `> 0` test, and equality counts as failure. Both match the design.
- **`summary()`.** It draws all 5⁵ = 3125 ordered resamples. The quantile rank is (1/40)·3124 = 78.1, with weight 1/10, which is the standard linear interpolation. The type check correctly rejects bools and floats. t intervals use df = 4.

## Bugs and hazards

1. **The two identity `assert`s check the code against itself, not against the data.** `stage()` builds the excess and the edge counts from the same inputs, so the identity holds automatically. It also disappears under `python -O`. It does not check that the assumed constants (6 / +1 / −2) match S29's logged bonuses. **Fix:** compare `actual[a]` with S29's per-round logged payoff for all 160 person-rounds. Use `raise`, not `assert`.
2. **Key convention is ambiguous (silent-error risk).** `passed` is keyed by author and `actions` by reviewer (`actions[a]` is a's decision on b's submission). With two employees the set-equality check still passes if a caller keys `actions` by author instead, and every edge count flips. **Fix:** add an asymmetric negative control, e.g. a is X, b is Y, only a approves. That should give `y_out[a] = 1` and `excess[a] = −2`. Also make sure the independent reconstruction derives this convention from the raw S29 records.
3. **The caller must pass `Fraction(m, 8)`.** `min_excess/8` with plain `/` produces a float. That fails loudly, which is safe, but measures 1, 2, 4, 5, 6 and 7 all need explicit Fraction construction. Add a test for it.
4. **Unchecked pairing order.** `summary()` does not check that the five block differences line up by seed (24480..24484). Assert seed order before taking differences.

## Limits the design already acknowledges, plus one to make concrete

- **Most rounds cannot show a two-sided gain at all.** An employee's excess can be positive only through `y_in`, which requires that employee's own submission to be Y. A round with one X and one Y caps the X employee at ≤ 0, and an XX round caps both at ≤ 0. So a single-round both-gain can only happen in a YY round, where both employees approve and each gets +4. The design says status composition constrains this, but measure 1 still uses 8 rounds per game as the denominator. **Recommendation:** export the number of eligible (YY) rounds per game and the number of two-round windows where each employee has a Y. Without those counts, a low fraction on measure 1 is mostly a fact about status composition, not behaviour.
- **Measure 3 is very coarse.** With five binary blocks, its bootstrap and t intervals are close to meaningless (t bounds can fall outside [0,1], and both kinds can collapse to a single value). The design acknowledges this.
- **The comparator is not a counterfactual.** It changes both employees' actions at fixed statuses and replays no histories, so it cannot measure reciprocity or causal profit. The claim scope says this correctly.

## Claim scope

The scope holds up: post hoc, ODD/context-only, no p-values, no HIT, and all seven measures are deterministic and reported equally. Two wording fixes:

- Don't describe the seven measures as "consistent findings". They all come from the same actions.
- Say explicitly that a pair-total excess > 0 (measure 5) is compatible with one employee losing. Measure 4 is the person-level check.

## Verdict

I found no algebraic or statistical bug in the supplied code. Items 1 and 2 are real verification gaps and should block registration until you add (a) a check against S29's logged payoffs and (b) the asymmetric key-convention control. Items 3 and 4 are small hardening fixes. The eligibility-count export is the main reporting fix.
