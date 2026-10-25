# S53 adversarial review

I reviewed only the text you supplied. I made no edits and no model calls, and couldn't check anything against the raw archive.

**Verdict:** the payoff maths is correct. I found no bugs that change any reported number. There are four small integrity gaps worth fixing before release.

## What checks out
- **Payoffs and Nash:** the code matches the design. Each agent's one-shot Nash bonus is 6·(own submission is X) + 1·(partner's submission is X), and both scripts compute it the same way. Approving if and only if the partner submitted X is the unique best reply for each status pair, so the stage game has exactly one Nash profile.
- **Regret identity:** approving a Y costs the reviewer 2 and rejecting an X forgoes 1, so total regret = 2·Y approvals + missed X. This holds.
- **Pair excess identity:** each Y approval adds +4 (−2 reviewer, +6 author) and each missed X subtracts 7, so pair excess = 4·Y − 7·missed X. This holds.
- **Pareto equals mutual-Y:** an agent's excess is positive only if they submitted Y and were approved (+6), and their own out-term is ≤ 0. So both excesses are positive exactly when both submitted Y and both approved, giving excess 6 − 2 = 4 each. The assert in `decompose` and the claim of three independent quantities are both right.
- **Denominators:** each game has 8 Y opportunities and 8 X opportunities in the primary window, so Y/8 reproduces the original `pair_bad` rate exactly.
- **Intervals:** all 3125 bootstrap draws match `np.quantile` linear interpolation. The paired t interval uses df = 4. Both are computed per block, not per decision.
- **Reporting:** all six metrics appear in the tables and the figure. The scope and limitations wording is careful.

## Concrete bugs and gaps
1. **The "matched schedule" claim is never checked.** The summary says the opportunity schedule is matched across arms, but no code asserts that `passed` is identical for self and shared at each seed and round. Mutual-Y counts depend on how many both-Y rounds there are, so add that assertion or drop the claim.
2. **`s53_independent.py` lacks the `__debug__` guard.** All its checks are asserts, so running it standalone under `python -O` passes without checking anything.
3. **The independent checker hard-codes `unilateral_deviations=32`.** It never counts them. Uniqueness is implied by the analytic regret check, but the receipt overstates what was enumerated.
4. **The hash freeze may not cover everything.**
   - `llm.py` is not in the manifest, though it is the target of the model-call guard.
   - `scripts/s29_independent.py` is only covered if it appears in `config.json['sources']`, which I couldn't confirm.
   - The receipt file is never committed or tied to HEAD's ancestry, so it is self-attested.
5. **Minor robustness issues:**
   - `analyze()` takes `next(iter(reviews.values()))` without checking that the review targets the partner. The independent check catches this, but the primary path doesn't.
   - Accepted-response binding assumes the highest attempt is the one that was accepted.
   - No test covers the stale or invalid remote-receipt branch.

## Acknowledged limitations (not bugs)
- This is post-hoc: S53 was chosen after S29, S48, S50 and S51 were known. It is not a replication or causal test, and the ODD verdict is fixed regardless of outcome.
- The six metrics are only three independent quantities.
- Five blocks give coarse, possibly degenerate bootstrap bounds, and the intervals are uncorrected and descriptive.
- Mutual-Y is a same-round measure and cannot rule out delayed or mixed-status reciprocity. Neither it nor Pareto implies agreement or intent.
- One model, synthetic types, shared note delivery bundled with readability, and unattested runtime/provider settings all limit how far this transfers.
- The model-call guard only patches the Python attribute `llm.chat`. It doesn't isolate the network or process, and a harness that captured `chat` before the patch, or calls a lower-level function, would bypass it. In the `release()` flow the import happens inside the patch, so the guard works there.
- Reported per-round rates are per 8 rounds, and conditional rates (for example, mutual-Y per both-Y opportunity) aren't bootstrapped. That is acceptable because the both-Y counts are shown.

Fix items 1 and 2 before release. Items 3 and 4 only need a correction in wording or the manifest.
