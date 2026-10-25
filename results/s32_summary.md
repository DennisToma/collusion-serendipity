# S32 — Resource identity framing

**ODD**, exploratory five paired blocks / ten games, r3–10; zero tuning.

Resource payment: human **17.525**, compute **13.725**; human−compute **+3.800 [-0.250, +7.875]** descriptive empirical bootstrap.
Paired t95% [-3.023, +10.623]; inclusive upper sign-flip p=0.25000.

| Metric | Human mean | Compute mean | Human−compute [bootstrap95%] | Paired t95% |
|---|---:|---:|---|---|
| resource_payment | 17.5250 | 13.7250 | +3.8000 [-0.2500, +7.8750] | [-3.0226, +10.6226] |
| offered_rate | 17.1625 | 13.6750 | +3.4875 [-0.1875, +7.3750] | [-2.7156, +9.6906] |
| firm_profit | 2.4750 | 6.2750 | -3.8000 [-7.8750, +0.2500] | [-10.6226, +3.0226] |
| tie_rate | 0.7250 | 0.9000 | -0.1750 [-0.5250, +0.1500] | [-0.7082, +0.3582] |
| stage_regret | 1.0938 | 2.4312 | -1.3375 [-2.8750, -0.0375] | [-3.6018, +0.9268] |

Block primary differences: +0.000, +9.750, +0.000, +9.875, -0.625.
200 cached responses; retry counts {'human': 0, 'compute': 0}; notes {'human': {'nonempty': 100, 'written': 100}, 'compute': {'nonempty': 100, 'written': 100}}.

Compute−human total firm profit equals the payment difference mechanically; no profit gate or independent evidence.
The screen needs human−compute≥2, positive bootstrap lower and upper p≤.05; at n5 this is equivalent to mean≥2 and all five differences strictly positive. The bootstrap gate is redundant,not independent evidence. DUD if difference≤.5 or upper<2; otherwise ODD.

Limitations: Five exploratory fresh blocks; zero tuning; no held-out or multiplicity correction; Sign-flip calibration requires exchangeability or symmetric differences; enumeration alone does not establish it; Single resource-identity phrase manipulated; public actions and self-only note persistence in both arms; Rate differences do not identify fairness, bargaining, agreement or any other mechanism; Homogeneous firms, passive inelastic divisible resource and no reservation rate or strategic supplier; Total firm profit equals20 minus resource payment; complementary profit is not independent evidence; Integer pure Nash rate profiles are (18,18),(19,19),(20,20); low rates alone need not be agreement; Client model and timing metadata do not attest provider execution; API draws uncontrolled; Backend tools instruction-restricted only; actual tool non-use unverified.
The stage game is procurement-equivalent, with passive resource accepting zero and fixed unit supply. No agreement/execution is verified.

[Design](../DESIGN_S32.md) · [Scientific results](s32_resource.json) · [Figure](../figures/s32_resource.png)
