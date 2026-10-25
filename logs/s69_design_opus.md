# S69 design review (supplied text only)

**Verdict: no high-severity correctness issues found.** Payoff arithmetic, prompt substitution and the decision rule are internally consistent. There are two medium issues (interpretation of the classification label, and abort risk near the deadline) and a few low ones.

## Verified within scope

- **Payoffs.** Approving X allocates (1, 6), totals 7, and splits to 3.5 each. Approving Y in LOW allocates (−2, 6), totals 4, giving 2 each. Approving Y in HIGH allocates (−12, 6), totals −6, giving −3 each. Rejecting gives (0, 0). These match both system strings.
- **Stage optimum.** Your own review changes your payoff by +3.5 for X and +2 / −3 for Y, independent of the partner's same-round action. So "approve all" in LOW and "approve X, reject Y" in HIGH are each the unique stage optimum. The disclaimer against claiming repeated-game dominance is correctly conservative.
- **Prompt diff.** The two strings differ only in 3→13, −2→−12 and (2, 2)→(−3, −3). Nothing non-numeric differs.
- **Opportunity count.** Each employee has 4 primary Y tasks, and the partner reviews each one, so there are 4 + 4 = 8 Y opportunities per game. `classify`'s `Fraction(sum, 8*n)` is consistent with this.
- **Sign-flip claim is correct.** For upper p ≤ .05 with n = 5:
  - If all differences are strictly positive, p = 1/32 ≈ .031.
  - Any zero difference doubles the count of patterns reaching the observed sum, so p ≥ 2/32.
  - Any negative difference flipped gives a larger sum, so again p ≥ 2/32.
  - The integer counting is exact and the `>=` comparison is inclusive.
- **Bootstrap.** The 3125 ordered tuples form the exact empirical bootstrap with multiplicities. The quantile uses type-7 interpolation: pos = 0.025 × 3124 = 78.1, so it interpolates between sorted means 78 and 79 with weight 0.1. That is correct.

## Medium

1. **UNRESOLVED → ODD mixes up low power with surprise.** A single tied block makes the result UNRESOLVED. Ties are plausible here: a pair that rejects every Y in both arms (for example out of org-loss salience), or approves every Y in both, contributes a difference of 0. That outcome is a floor or ceiling effect, not an odd finding. Recommendation: when the result is ODD, report descriptively *which* criterion failed (a zero or negative block, or mean < 1/4). Do not let the ODD label imply anomalous behavior. This needs no change to the rule, only to how it is reported.
2. **Abort and deadline exposure.** Several rules combine into a risk of losing the whole pilot:
   - Any first terminal transport or quota failure aborts everything, with no restart or partial estimation.
   - Retries are capped at 1.
   - The codex 5h rolling limit is a live risk.
   - There are about 200 calls at a maximum concurrency of 2.

   At roughly 30–90 s per call, that is about 50–150 min of wall time. The design should state the expected latency, and the planned launch time should fit before 13:30 admission and the 14:30 pilot end, with margin. Otherwise an UNRESOLVED or aborted outcome is likely on operational grounds alone. This is a known design choice, but it is flagged here as a practical risk.

## Low

- **Gate redundancy.** If all block differences are strictly positive, the bootstrap lower bound is automatically > 0. The effective rule is therefore "every block difference ≥ 1 and their sum ≥ 10". Stating that would be clearer.
- **Org-loss metric is not independent.** Org loss per primary round equals exactly 10 × the Y-approval fraction, so its contrast is a rescaling of the primary contrast. The screen effectively has 4 metrics, not 5.
- **Final-pair bonus differs by construction.** Its contrast differs across arms even under identical behavior, because the per-Y-approval weights differ (+4 vs −6). This is already acknowledged and is fine as long as it is never read as behavioral evidence.
- **Missing key in the supplied code.** `classify` reads `summary['exact_signflip_p_upper']`, but `exact_summary` does not return that key. It must be merged in elsewhere. Check that the merged sign-flip result belongs to the same metric (partner-Y), so one metric's p is not paired with another metric's CI.
- **Degenerate t interval.** If all 5 differences are equal, `std(ddof=1)` is 0 and the t interval has zero width. Report that case as degenerate rather than as a precise estimate.
- **Wording ambiguity.** The prompt says "1 review point" while elsewhere it says "bonus points", which could read as a separate currency. The "allocated reviewer bonus −2 (1 review point minus …)" line and the final table resolve it, and the wording is identical in both arms, so there is no differential effect.

## Known limits (acknowledged in the design, not defects)

- Instructions and actual incentives change together, so no mechanism, salience or understanding claim is possible.
- The magnitudes are asymmetric (+2 vs −3).
- Temperature is not forwarded, and the CLI flattens roles.
- Provider identity is unverified.
- Equal pooling makes the game pure common-interest, so this is not a collusion test.
- Five blocks give a coarse percentile bootstrap.
- There is no held-out data, and no pooling with older pilots.

**Scope:** supplied text only. No filesystem audit, no bootstrap enumeration and no cache inspection were performed. I made no edits and no LLM calls.
