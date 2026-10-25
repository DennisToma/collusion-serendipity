# S56 — Can a tender pair and outsider profitably deviate?

**POST-HOC; ODD/context-only.** All ten original S14 games/five source blocks,90 primary rounds. Zero new games, scientific model calls or tuning. S14 remains ODD; no new collusion label or independent replication.

| Per-round metric (45 rounds per arm) | Arm/contrast | Mean | Bootstrap95% | t95% |
|---|---|---:|---|---|
| payment | none | +8.777778 | [+6.000000, +14.333333] | [+1.065430, +16.490125] |
| payment | private | +11.111111 | [+6.444444, +16.133333] | [+3.243005, +18.979218] |
| payment | difference | +2.333333 | [-5.600000, +10.000000] | [-10.573736, +15.240403] |
| pair_profit | none | +1.948148 | [+0.000000, +5.844444] | [-3.460778, +7.357075] |
| pair_profit | private | +2.748148 | [+0.296296, +5.937037] | [-1.732294, +7.228591] |
| pair_profit | difference | +0.800000 | [-4.633333, +5.233333] | [-7.294225, +8.894225] |
| above_nash | none | +0.200000 | [+0.000000, +0.600000] | [-0.355289, +0.755289] |
| above_nash | private | +0.400000 | [+0.000000, +0.800000] | [-0.280087, +1.080087] |
| above_nash | difference | +0.200000 | [-0.400000, +0.800000] | [-0.838851, +1.238851] |
| payment_excess | none | +2.577778 | [+0.000000, +7.733333] | [-4.579281, +9.734836] |
| payment_excess | private | +4.400000 | [+0.000000, +9.200000] | [-3.132307, +11.932307] |
| payment_excess | difference | +1.822222 | [-5.733333, +9.200000] | [-10.493448, +14.137892] |
| pair_joint_regret | none | +0.740741 | [+0.059259, +2.014815] | [-1.009205, +2.490687] |
| pair_joint_regret | private | +1.955556 | [+0.088889, +4.229630] | [-1.316298, +5.227409] |
| pair_joint_regret | difference | +1.214815 | [-1.303704, +4.014815] | [-3.132609, +5.562238] |
| outsider_regret | none | +1.755556 | [+0.000000, +5.251852] | [-3.092981, +6.604092] |
| outsider_regret | private | +2.274074 | [+0.029630, +5.229630] | [-1.843527, +6.391675] |
| outsider_regret | difference | +0.518519 | [-4.455556, +4.544444] | [-6.923850, +7.960887] |
| coalition_stable | none | +0.644444 | [+0.311111, +0.888889] | [+0.172540, +1.116349] |
| coalition_stable | private | +0.422222 | [+0.111111, +0.733333] | [-0.079021, +0.923465] |
| coalition_stable | difference | -0.222222 | [-0.733333, +0.377778] | [-1.110985, +0.666540] |
| strict_pair_improvement | none | +0.311111 | [+0.088889, +0.622222] | [-0.107350, +0.729573] |
| strict_pair_improvement | private | +0.422222 | [+0.133333, +0.711111] | [-0.039489, +0.883934] |
| strict_pair_improvement | difference | +0.111111 | [-0.422222, +0.577778] | [-0.693343, +0.915565] |

| Sum over45 rounds (money sums in currency units) | No box | Private box |
|---|---:|---:|
| payment | 395 | 500 |
| pair_profit | 263/3 | 371/3 |
| above_nash | 9 | 18 |
| payment_excess | 116 | 198 |
| pair_joint_regret | 100/3 | 88 |
| outsider_regret | 79 | 307/3 |
| coalition_stable | 29 | 19 |
| strict_pair_improvement | 14 | 19 |

Exhaustive3375-profile census: 44 static pure Nash profiles with buyer payments [6, 7]; 30 fixed-pair/singleton stable profiles with payments [6, 7]. 2141 profiles permit a strict gain for BOTH pair members without transfers.

Pair joint regret holds the outsider bid fixed and maximizes pair-total profit over all225 ordered pair bids. Outsider regret holds pair bids fixed and maximizes outsider profit over15 bids. Coalition-stable means both exact regrets are zero (a competitive static benchmark, not a collusion label); this fixed partition allows joint pair valuation but is NOT strong equilibrium, coalition-proofness or repeated-game stability. Pair-total gain may sacrifice one member; strict_pair_improvement separately requires both individual profits to increase without transfers. Neither counterfactual assumes an actual side payment or reruns a policy.

above_nash is the fraction of payments strictly above7, the maximum static pure-Nash payment. payment_excess is max(0,payment−7); it does not assign a collusion label. payment and pair_profit reproduce S14 means and add no independent evidence. Stability implies payment≤7, so coalition_stable≤1−above_nash in every round. Other metrics may also be related; none promotes a HIT.

All eight metrics were fixed after S14 outcomes were known but before this new decomposition. All90 rounds and all five paired source blocks retained. Every arm mean and private-minus-none contrast uses all3125 ordered empirical block resamples and exact rational linear quantiles, plus t95%. This differs from S14’s original10000-draw bootstrap; original S14 inference and verdict are untouched. The24 summaries contain48 descriptive, uncorrected intervals; small-n bounds may degenerate. Counts are not independent observations. No significance tests, equivalence, population, causal-mediation, agreement, intent or repeated-game equilibrium claim.

One model, many explored pilots, reused outcomes, divisible tie allocation, identical public costs, compulsory purchase, bounded integer bids, full public histories and bundled role/channel cues restrict transfer. Provider identity/settings and tool non-use remain unattested. Patching llm.chat forbids that scientific entry point, not OS-level network/process use.

[Design](../DESIGN_S56.md) · [All90 records,80game cells,24summaries and full census](s56_coalitions.json) · [Figure](../figures/s56_coalitions.png)

Reproduce: `uv run --frozen python scripts/s56_coalitions.py --release` and `uv run --frozen python scripts/s56_independent.py`.
