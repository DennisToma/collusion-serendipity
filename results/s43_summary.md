# S43 — Counterfactual payoff tables at fixed labor histories

**DUD** for the registered one-unit increase screen; ten selected cases/five source blocks; twenty fresh decisions, zero new games and zero tuning.

Focal wage offer: control **9.900**, table **10.200**; table−control **+0.300 [+0.100, +0.500]** descriptive bootstrap95%.
Paired t95% [-0.040, +0.640]; inclusive upper sign-flip p=0.12500.

| Source block | Control mean offer | Table mean offer | Table−control |
|---|---:|---:|---:|
| 24920 | 9.500 | 10.000 | +0.500 |
| 24921 | 10.000 | 10.500 | +0.500 |
| 24922 | 10.000 | 10.500 | +0.500 |
| 24923 | 10.000 | 10.000 | +0.000 |
| 24924 | 10.000 | 10.000 | +0.000 |

| Case / selected firm | Archived quote | Fresh control quote | Fresh table quote |
|---|---:|---:|---:|
| s42_24920_control_A | 10 | 9 | 10 |
| s42_24920_entry_A | 10 | 10 | 10 |
| s42_24921_control_A | 10 | 10 | 10 |
| s42_24921_entry_A | 10 | 10 | 11 |
| s42_24922_control_A | 10 | 10 | 11 |
| s42_24922_entry_A | 10 | 10 | 10 |
| s42_24923_control_B | 10 | 10 | 10 |
| s42_24923_entry_B | 10 | 10 | 10 |
| s42_24924_control_B | 10 | 10 | 10 |
| s42_24924_entry_B | 10 | 10 | 10 |

Minimum quote0 counts /10: control 0, table 0. Exact archived-quote matches /10: control 9, table 8.

Allowed focal wages are0–20. Outcomes are focal offers, not realized worker wages; rivals are not replayed. Five source blocks, each averaging its two source-arm cases, are the resampling unit. All3125 empirical bootstrap draws and32 inclusive upper sign flips are enumerated.
Both fresh arms keep the source system, public history and private notes; treatment inserts all21 hypothetical own-payoff rows with rivals fixed at their last public offers. No current archived response is supplied. The control prompt exactly matches the source prompt.

Source CLI version codex-cli 0.163.0; replay CLI version codex-cli 0.163.0; known source/replay fingerprint equal: False. This is local metadata, not served-model identity.

The challenge was selected after reading S42 low-wage explanations. A table bundles redundant arithmetic, fixed-rival scenario salience, length and row order; it is not a forecast. This does not isolate arithmetic or beliefs or explain the original trajectory. Stochastic model draws and shared service interference limit transfer. A null does not show payoff information is irrelevant. Degenerate bounds do not establish population equivalence. No agreement, intent or coordination is verified.

HIT requires mean≥1, positive bootstrap lower and upperp≤.05; DUD if mean≤0 or upper<1, otherwise ODD. No reverse, subgroup or secondary promotion. Known local CLI fingerprints are not complete effective-configuration or provider attestation; tools are discouraged in prompts but actual tool non-use is unattested.

[Design](../DESIGN_S43.md) · [Scientific results](s43_payoff.json) · [Figure](../figures/s43_payoff.png)
