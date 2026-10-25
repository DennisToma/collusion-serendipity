# S67 adversarial review (from the supplied text only; nothing was executed)

**Arithmetic is correct.**
- **Settlement:** an approval moves the pair total by 7 for X and 4 for Y. That gives unilateral increments of +1/−2 under individual settlement and +3.5/+2 under pooled settlement.
- **Comparators:** every action is strictly dominant, so each settlement has one unique stage Nash: approve-X/reject-Y for individual, approve-all for pooled.
- **Regret:** individual regret = 2·Y approvals + missed X. Pooled regret = 2·Y rejections + 3.5·missed X.
- **Pair shortfall:** 7·missed X + 4·Y rejections in both arms, because the pair total does not depend on settlement.
- **Strict Pareto:** in individual settlement the comparison bonuses are 7/7, 6/1 and 0/0, so only both-Y rounds with both agents approving qualify (4/4). Under pooled settlement Nash equals the pair maximum, so it can never happen.
- **Bootstrap:** `pos = q·(n−1)` matches NumPy's default linear quantile.

**Medium**
1. **The no-call guard is narrower than the claim.** `patch('llm.chat')` only catches calls that look up `llm.chat` at call time. Any module that ran `from llm import chat` before the patch keeps the real function, for example a cached `sim/` import. Direct `codex exec`, `opencode` or HTTP calls are not blocked at all. The test only covers attribute calls. Either say "llm.chat entry point patched", or also stub `subprocess` and the network.
2. **Three contrasts just repeat one arm.** Costly Y, profitable Y rejections and strict Pareto are structurally zero in one arm, so each "pooled−individual" interval is only ± the other arm's mean. The report should say this next to the table, not only as "bookkeeping".

**Low**
3. **Positional round slice.** `s67_audit.analyze` takes `game['rows'][2:10]` without checking the length or `round` values. `s67_independent.py` does check, but the estimator should too.
4. **Notes vs reasoning indexing.** The checker matches notes on `round == row['round']+1` and reasoning on `row['round']`. If that is the real schema, comment it. If not, the binding check passes for the wrong reason.
5. **Unit mismatch.** Metric 7 counts round-level events (at most 1 per round); metrics 1–6 and 8 count reviews (up to 2 per round, up to 20 for organization loss). Also, metric 1 equals the S65 Y rate only because every game has exactly 8 Y opportunities. That is asserted, but state it.
6. **Fragile replay checks.** `source_calibration == 'UNRESOLVED'` assumes S65 stored a bare string. `json.dumps(indent=2)` assumes S65's exact serializer, with no `sort_keys`. Both fail safe if wrong, but they could block the release.
7. **Misleading label.** "Profitable Y rejections" reads as if rejecting paid off. Rename it to "Y rejections forgoing +2 (pooled)".
8. **First summary table** uses raw metric keys instead of the labels.
9. **PNG byte-identity** holds only within the pinned matplotlib version.

**Acknowledged limits (not defects)**
- The audit is post hoc and was chosen after S65's results were known.
- Settlement and prompt wording are bundled; histories diverge endogenously.
- The analysis is stage-game only; repeated play is not modelled.
- Five blocks: the bootstrap and t intervals may disagree or degenerate.
- The metrics are derived from each other, not independent.
- The client receipt is not a server-side timestamp.
- Provider and settings are unattested.
- The original UNRESOLVED/ODD verdict stays unchanged.

**Claims are scoped correctly.** No issues with promotion, replication or mechanism language, apart from item 1's wording.
