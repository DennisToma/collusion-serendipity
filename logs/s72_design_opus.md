# S72 review (based only on the supplied design text)

**Verdict:** the payoff algebra, the benchmark and the bootstrap are correct. One real definition bug (item 1) needs fixing before registration. Everything else is a hardening fix or a limitation the design already admits.

## Checks that pass
- **Benchmark:** `base[a] = 6*passed[a] + passed[b]` matches the stated policy. Under the stage payoff, approving X (+1 vs 0) and rejecting Y (0 vs −2) are strictly dominant, and a's own action never changes what a receives from b. So "unique one-shot Nash" is correct; it is in fact a dominant-strategy equilibrium.
- **Individual identity:** excess = 6(act_b − passed_a) + [passed_b ? act_a − 1 : −2·act_a], which works out to 6·Yin − 2·Yout − 6·Xin − Xout. Correct.
- **Pair identity:** summing both employees gives 4·Y − 7·missedX. Correct.
- **Window aggregation:** the output of `stage` has the same keys as a raw record, so feeding stage results into `aggregate` sums correctly. Window profits are summed before the strict `> 0` test, as specified.
- **Bootstrap:** 5^5 = 3125 ordered draws is correct. Rank q·(n−1) with linear interpolation matches the numpy "linear" quantile. The `min()` guard is harmless.
- **t interval:** df = 4 with ddof = 1 is correct. The degenerate case (all values equal) is already acknowledged.

## Correctness bugs
1. **Measures 6 and 7 have the wrong denominator.** `y_approvals` and `missed_x` add up both employees' outgoing reviews, so a game has 16 review decisions, not 8. Dividing by 8 lets the "rate" reach 2. A Y-approval rate should also be divided by the number of Y opportunities (rounds where the partner's item failed), which depends on the exogenous statuses. Missed X works the same way with X opportunities. Pick one denominator, either 16 decisions or the status-conditional count, and register it before analysis.
2. **The identity checks use `assert`.** Running with `python -O` removes them silently. Replace them with explicit `raise`, since those checks are part of the stated verification.
3. **`summary()` takes any numeric input.** If a ratio arrives as a non-dyadic float (e.g. 1/3), `Fraction(float)` turns the "exact rational" bounds into binary-float artefacts. Require `int`/`Fraction` inputs and reject `float`.

## Structural limits the design should state
- **Rounds where both items passed can never show a gain.** Neither employee's excess can be positive there (maximum 0, no Yin possible). Individual excess is positive only through Yin, so "both better off" in a window means, roughly, mutual Y approvals that outweigh costs. Measures 1–3 therefore depend heavily on how often items fail. Say this explicitly.
- **Pairing needs identical statuses.** The shared-minus-self differences are only meaningful if both arms of a seed see the same exogenous statuses. Add that as a guard, or report status counts per arm.
- **Window sizes are mechanically linked.** Measure 3 is not independent of measures 1–2: a gain in any single round can carry the full window, and the reverse is not guaranteed. "Not independent findings" is already stated; that is enough.

## Claim scope
The design is properly limited: post hoc, labelled ODD/context-only, no p-values, no HIT, five seed blocks as the resampling unit, and it says the benchmark is not a repeated-game counterfactual. The line "the benchmark's paths need not be intervention paths" is the key caveat; keep it in the report text. No overclaim found.

## Provenance and release guards
These are procedurally adequate as written. Patching `llm.chat` to raise blocks only that Python entry point, and the design already says so. I can't verify the hashes, origin state or archive inventory from the text alone.

**Required before registration:** fix item 1. Items 2–3 are cheap hardening.
