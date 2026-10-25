# S44 — Identical payoff rows in opposite order

**DUD** for the registered one-unit descending-minus-ascending offer increase screen. Ten observed contexts/five source blocks;20 fresh decisions,zero new games,zero tuning.

Focal offer: ascending **10.300**, descending **10.200**; difference **-0.100 [-0.300, +0.000]** descriptive bootstrap95%.
Paired t95% [-0.378, +0.178]; inclusive sign-flip upper p=1.00000, lower p=0.50000, two-sided p=1.00000.

| Source block | Ascending mean | Descending mean | Descending−ascending |
|---|---:|---:|---:|
| 24920 | 10.000 | 10.000 | +0.000 |
| 24921 | 10.500 | 10.000 | -0.500 |
| 24922 | 10.000 | 10.000 | +0.000 |
| 24923 | 10.500 | 10.500 | +0.000 |
| 24924 | 10.500 | 10.500 | +0.000 |

| Case / focal firm | Archived offer (context) | Fresh ascending | Fresh descending |
|---|---:|---:|---:|
| s42_24920_control_A | 10 | 10 | 10 |
| s42_24920_entry_A | 10 | 10 | 10 |
| s42_24921_control_A | 10 | 10 | 10 |
| s42_24921_entry_A | 10 | 11 | 10 |
| s42_24922_control_A | 10 | 10 | 10 |
| s42_24922_entry_A | 10 | 10 | 10 |
| s42_24923_control_B | 10 | 11 | 10 |
| s42_24923_entry_B | 10 | 10 | 11 |
| s42_24924_control_B | 10 | 11 | 10 |
| s42_24924_entry_B | 10 | 10 | 11 |

Offers at0 /10: ascending 0, descending 0. Exact archived-offer matches /10: ascending 7, descending 8.

Both fresh arms receive the same source system, public history, private owner notes, hypothetical fixed-rival scenario and table header. Only the sequence of all21 exact payoff rows reverses. No archived current response or recommended action is supplied. Source histories are the same ten observed S42 contexts used in S43; new outputs come from fresh invocations with uncontrolled provider draws.
Outcome is a focal offer in0–20, not realized worker pay; rivals are not rerun. Five source blocks average two contexts each. All3125 ordered empirical bootstrap draws and32 inclusive sign flips are enumerated. Sign calibration assumes symmetry/exchangeability; enumeration alone does not establish it. With n5, empirical intervals may degenerate and do not establish equivalence. The directional DUD screen does not rule out an opposite effect.
Selection is post hoc and not held out. No pooling, reverse/subgroup/secondary promotion or multiplicity correction. Results cannot identify anchoring, arithmetic errors, coordination, intent or a population prevalence. Row order includes position and recency together; shared-service interference, uncontrolled model draws and small n limit transfer.
Known source CLI codex-cli 0.163.0; replay CLI codex-cli 0.163.0; known local fingerprints equal: False. Complete effective settings/provider identity/tool non-use remain unattested. Codex requests low reasoning; temperature/token arguments are not transmitted as CLI settings.
HIT requires mean≥1,positive bootstrap lower and upperp≤.05;DUD if mean≤0 or upper<1,otherwise ODD. Any HIT requires fresh registered confirmation.

[Design](../DESIGN_S44.md) · [Scientific results](s44_payoff.json) · [Figure](../figures/s44_payoff.png)
