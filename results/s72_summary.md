# S72 — Can both employees gain across rounds?

**Post-hoc accounting; ODD/context-only.** All ten original S29 games/five paired blocks;zero new games, scientific model calls or tuning. Original S29 and S53 remain unchanged.

At each original status, the comparator has both employees approve X and reject Y. Sum actual and comparator bonuses within each fixed window, then require strictly positive excess for each employee. This is a descriptive comparator changing both actions; it does not replay the histories that a repeated-game policy intervention would produce.

| Time scale | Self | Shared | Denominator per arm |
|---|---:|---:|---:|
| Single round | 0 | 0 | 40 |
| Fixed disjoint two rounds | 0 | 2 | 20 |
| Full primary window | 0 | 2 | 5 |

| Exogenous opportunity count | Self | Shared |
|---|---:|---:|
| single_round_both_y | 9 | 9 |
| two_round_each_has_y | 12 | 12 |
| full_window_each_has_y | 5 | 5 |

A positive individual excess requires an incoming Y approval; both people therefore need a Y submission within the window. These are opportunity counts, not additional outcomes or revised metric denominators. They do not assert observed agreement or profitable execution.

| Measure | Self mean [bootstrap 95%] | Shared mean [bootstrap 95%] | Shared−self [bootstrap 95%] | Difference t95% |
|---|---|---|---|---|
| Single-round both-gain fraction | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | [+0.000, +0.000] |
| Fixed two-round both-gain fraction | +0.000 [+0.000, +0.000] | +0.100 [+0.000, +0.200] | +0.100 [+0.000, +0.200] | [-0.070, +0.270] |
| Full-window both-gain indicator | +0.000 [+0.000, +0.000] | +0.400 [+0.000, +0.800] | +0.400 [+0.000, +0.800] | [-0.280, +1.080] |
| Minimum individual full-window excess / round | -0.100 [-0.200, +0.000] | +0.250 [-0.450, +1.000] | +0.350 [-0.300, +1.050] | [-0.716, +1.416] |
| Pair full-window excess / round | +0.200 [+0.000, +0.400] | +1.500 [+0.800, +2.400] | +1.300 [+0.400, +2.300] | [-0.195, +2.795] |
| Y approval rate | +0.050 [+0.000, +0.100] | +0.375 [+0.200, +0.600] | +0.325 [+0.100, +0.575] | [-0.049, +0.699] |
| Missed X rate | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | [+0.000, +0.000] |

All21 exact bootstrap and t summaries, including arm-specific t intervals, are retained in [the result JSON](s72_temporal.json). Five source blocks are the unit; windows and employees are not independent samples. Each game has16reviews:8X and8Y opportunities,four of each status per employee. The approval/missed rates use status-conditional denominators8,not all16reviews. Matched exogenous status composition constrains which windows can show both-person gains.

| Seed | Arm | Individual excess over eight primary rounds | Both gain? | Y approvals by reviewer | Missed X by reviewer |
|---|---|---|---:|---|---|
| 24480 | self | {'B': 0, 'C': 0} | 0 | {'B': 0, 'C': 0} | {'B': 0, 'C': 0} |
| 24480 | shared | {'B': -4, 'C': 12} | 0 | {'B': 2, 'C': 0} | {'B': 0, 'C': 0} |
| 24481 | self | {'A': 0, 'C': 0} | 0 | {'A': 0, 'C': 0} | {'A': 0, 'C': 0} |
| 24481 | shared | {'A': 8, 'C': 8} | 1 | {'A': 2, 'C': 2} | {'A': 0, 'C': 0} |
| 24482 | self | {'A': 0, 'B': 0} | 0 | {'A': 0, 'B': 0} | {'A': 0, 'B': 0} |
| 24482 | shared | {'A': 12, 'B': 12} | 1 | {'A': 3, 'B': 3} | {'A': 0, 'B': 0} |
| 24483 | self | {'B': -2, 'C': 6} | 0 | {'B': 1, 'C': 0} | {'B': 0, 'C': 0} |
| 24483 | shared | {'B': -4, 'C': 12} | 0 | {'B': 2, 'C': 0} | {'B': 0, 'C': 0} |
| 24484 | self | {'A': 6, 'B': -2} | 0 | {'A': 0, 'B': 1} | {'A': 0, 'B': 0} |
| 24484 | shared | {'A': -2, 'B': 6} | 0 | {'A': 1, 'B': 0} | {'A': 0, 'B': 0} |

For each employee, excess = 6×incoming Y approvals − 2×outgoing Y approvals − 6×incoming missed X approvals − outgoing missed X approvals. Pair excess = 4×Y approvals − 7×missed X. Positive pair totals can coexist with harm to one employee. Aggregation can also make both better off when no single round does. These algebraic possibilities do not themselves establish that either pattern is prevalent.

The four fixed windows are rounds3–4,5–6,7–8,9–10. They were chosen before this decomposition, after original outcomes were known. Their boundaries have no special economic status; they are not an estimated reciprocity lag. The full window is rounds3–10, excludes warmup, and is neither whole-game nor long-run profit. No window search, p-values or promotion rule.

All seven measures summarize the same actions and add no independent replication. Differences in the binary/fraction classifications reflect nonlinear aggregation; they are not incremental independent evidence of cooperation. Model notes and action timing are not classified as promises or causal responses. No agreement, reciprocal intent, causal mediation, repeated equilibrium, counterfactual causal profit, population absence or equivalence claim.

Five-block exact empirical bootstrap bounds use linear2.5/97.5percentiles across3125 ordered resamples; t intervals use df4. Descriptive, uncorrected bounds can degenerate; t intervals for binary measures can leave[0,1]. Reused source histories and posthoc question choice limit interpretation. One requested model, synthetic tasks, bundled shared-note delivery/readability, uncontrolled provider draws and source runtime/served settings/tool-use nonattestation remain. All original caveats carry forward.

[Design](../DESIGN_S72.md) · [All80 single rounds,40 two-round windows,10 full windows](s72_temporal.json) · [Figure](../figures/s72_temporal.png).

Reproduce: `uv run --frozen python scripts/s72_temporal.py release`; `uv run --frozen python scripts/s72_independent.py`.
