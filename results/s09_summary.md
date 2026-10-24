# S09 — erase versus retain prior private-message memory

**DUD for the registered quantity-increase screen.** Ten six-round continuations of all five previously observed S07 neutral prefixes; five matched blocks, no tuning.

Primary: pair quantity per firm over rounds7–12, erase minus retain. **+0.100 [+0.000, +0.300]** descriptive block-bootstrap95%; paired t95% [-0.178, +0.378]; upper exact sign-flip p=0.50000.

| Outcome r7–12 | Retain mean | Erase mean | Difference [bootstrap95%] | Paired t95% |
|---|---:|---:|---:|---:|
| quantity | 5.900 | 6.000 | +0.100 [+0.000, +0.300] | [-0.178, +0.378] |
| outsider_quantity | 6.033 | 6.000 | -0.033 [-0.100, +0.000] | [-0.126, +0.059] |
| price | 12.167 | 12.000 | -0.167 [-0.600, +0.100] | [-0.752, +0.419] |
| pair_profit | 36.200 | 36.000 | -0.200 [-1.200, +0.600] | [-1.560, +1.160] |
| outsider_profit | 37.167 | 36.000 | -1.167 [-3.600, +0.100] | [-4.523, +2.189] |
| message_words | 20.550 | 14.383 | -6.167 [-7.267, -4.667] | [-8.237, -4.096] |
| nonempty_messages | 1.000 | 1.000 | +0.000 [+0.000, +0.000] | [+0.000, +0.000] |

| Prefix seed | Retain quantity | Erase quantity | Difference | Round7 difference |
|---|---:|---:|---:|---:|
| 24080 | 6.000 | 6.000 | +0.000 | +0.000 |
| 24081 | 5.500 | 6.000 | +0.500 | +1.000 |
| 24082 | 6.000 | 6.000 | +0.000 | +0.000 |
| 24083 | 6.000 | 6.000 | +0.000 | +0.000 |
| 24084 | 6.000 | 6.000 | +0.000 | +0.000 |

Round7-only pair output: +0.200 [+0.000, +0.600]; seed differences [0.0, 1.0, 0.0, 0.0, 0.0]. Mean absolute round7 arm difference 0.200.
Outsider round7 output difference mean +0.000; seed differences [0.0, 0.0, 0.0, 0.0, 0.0] (descriptive negative control).
Source nonempty message slots: 60/60, over source rounds1–6; per-prefix counts {'24080': 12, '24081': 12, '24082': 12, '24083': 12, '24084': 12}. Exposure is not an agreement label.
Cached responses: 183; retries by arm: {'retain': 3, 'erase': 0}. No failed games.

![S09 fork and continuation paths](../figures/s09_replay.png)

The initial public history is identical within each block. Only received rounds1–6 private messages are removed; both arms retain their boxes and receive new messages from round8. Public actions can preserve prior agreements; future messages can repair missing information. This estimates the total continuation effect of erasing message memory at this fork, including later behavioral feedback, rather than the original channel effect. It cannot separate empty-inbox cues from message semantics.

Intervals that collapse for constant paired differences describe observed resampling support; they do not establish zero population uncertainty. The outsider has identical round7 prompts across arms, but its separately sampled action can still differ without leakage.

Prefixes were previously observed; no independent-seed replication. With n=5, bootstrap and t intervals are fragile; the sign-flip calculation assumes slot exchangeability/symmetric differences. A DUD screen is not evidence of equivalence or absence of a communication effect. No verified agreement/execution labels or collusion inference. Pair-profit changes are descriptive and are not a HIT gate. Model/backend labels and sampling/isolation limitations are inherited from S07.

Mandatory cache-only full replay, every key consumed once, prefix/source/registration and exports/payoffs checks pass. Independent full metric/statistic check: [audit](../logs/s09_independent.json).

Reproduce: `TMPDIR=/var/tmp uv run python -m sim.replay`; `uv run python scripts/s09_analyze.py`; `uv run python scripts/s09_independent.py`; `uv run python scripts/s09_present.py`.

[Registered design](../DESIGN_S09.md) · [Machine-readable results](s09_replay.json)
