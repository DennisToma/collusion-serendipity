# S53 — What the S29 workplace approvals pay

**Post-hoc diagnostic; ODD/context-only.** All ten original S29 games/five blocks;80 primary rounds,160 reviews. Zero new games or scientific model calls. No new HIT or independent replication.

| Primary-window count (40 rounds/80 reviews per arm) | Self | Shared |
|---|---:|---:|
| y_approvals | 2 | 15 |
| missed_x | 0 | 0 |
| mutual_y_rounds | 0 | 0 |
| strict_pareto_rounds | 0 | 0 |
| stage_regret | 4 | 30 |
| pair_excess | 8 | 60 |
| both_y | 9 | 9 |
| mutual_y_edges | 0 | 0 |
| other_y_edges | 2 | 15 |
| organization_loss | 20 | 150 |

| Per-round metric | Self mean | Shared mean | Shared−self [bootstrap95%] | Paired t95% |
|---|---:|---:|---|---|
| y_approvals | 0.050 | 0.375 | +0.325 [+0.100, +0.575] | [-0.049, +0.699] |
| missed_x | 0.000 | 0.000 | +0.000 [+0.000, +0.000] | [+0.000, +0.000] |
| mutual_y_rounds | 0.000 | 0.000 | +0.000 [+0.000, +0.000] | [+0.000, +0.000] |
| strict_pareto_rounds | 0.000 | 0.000 | +0.000 [+0.000, +0.000] | [+0.000, +0.000] |
| stage_regret | 0.100 | 0.750 | +0.650 [+0.200, +1.150] | [-0.098, +1.398] |
| pair_excess | 0.200 | 1.500 | +1.300 [+0.400, +2.300] | [-0.195, +2.795] |

| Block | Arm | Y approvals | Missed X | Both-Y opportunities | Mutual-Y | Stage regret | Pair excess |
|---|---|---:|---:|---:|---:|---:|---:|
| 24480 | self | 0 | 0 | 2 | 0 | 0 | 0 |
| 24480 | shared | 2 | 0 | 2 | 0 | 4 | 8 |
| 24481 | self | 0 | 0 | 2 | 0 | 0 | 0 |
| 24481 | shared | 4 | 0 | 2 | 0 | 8 | 16 |
| 24482 | self | 0 | 0 | 1 | 0 | 0 | 0 |
| 24482 | shared | 6 | 0 | 1 | 0 | 12 | 24 |
| 24483 | self | 1 | 0 | 2 | 0 | 2 | 4 |
| 24483 | shared | 2 | 0 | 2 | 0 | 4 | 8 |
| 24484 | self | 1 | 0 | 2 | 0 | 2 | 4 |
| 24484 | shared | 1 | 0 | 2 | 0 | 2 | 4 |

Strict Pareto improvement and mutual-Y rounds are IDENTICAL for all16 profiles under these payoffs. Regret and pair excess are linear combinations of Y approvals and missed X approvals. Thus the six displayed metrics contain only three independent quantities; none is independent supporting evidence.


Y approvals/round numerically equal the original S29 Y approval rate because each game has eight Y review opportunities and eight primary rounds. The original S29 analysis and ODD verdict are unchanged. Other metrics use rounds as their denominator; counts are not independent sample sizes.

Every adverse approval gives its author6 and costs its reviewer2, holding the incoming review fixed. Rejecting X forgoes1 reviewer point. The unique one-shot Nash approves X and rejects Y. Pair excess over that comparator is exactly4 per Y approval minus7 per missed X approval; stage regret is exactly2 per Y approval plus1 per missed X approval. Excess changes both agents’ actions; regret changes only the focal action. All16 status/action profiles and32 unilateral deviations are checked. Full approval maximizes the pair’s one-round total bonus. These are static comparisons, not repeated-game equilibria or a policy recommendation.

A simultaneous mutual-Y round requires both submissions Y and both approvals true. Strict Pareto improvement means each agent’s realized bonus exceeds its own same-status one-shot Nash bonus. Neither definition identifies an agreement or reciprocal intent. Other Y edges include mixed-status rounds and unilateral approvals; they do not exclude delayed reciprocity. Organization loss is outside the agents’ bonus objective.

All six metrics were fixed before this new decomposition was computed, after S29 and replay outcomes were known. Five source blocks are resampled, with all3125 ordered empirical bootstrap draws and paired t95%. These are descriptive, uncorrected intervals, not six hypothesis tests. Small-n bounds may degenerate. No causal mediation, independent replication, long-run profitability, held-out validation, tuning, equivalence or new collusion label. The opportunity schedule is matched across arms; realized histories differ. One model, synthetic types, bundled note delivery/readability and uncontrolled draws/shared services limit transfer. Original runtime/provider settings remain unattested.

[Design](../DESIGN_S53.md) · [All80 round records,ten game records and sixteen stage profiles](s53_payoffs.json) · [Figure](../figures/s53_payoffs.png)

Reproduce: `uv run --frozen python scripts/s53_payoffs.py --release` and `uv run --frozen python scripts/s53_independent.py`.
