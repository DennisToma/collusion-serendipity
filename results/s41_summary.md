# S41 — Half-unit versus unit wage grid

**ODD**, exploratory five paired blocks / ten games, r3–10; zero tuning.

Worker take-home pay: fine **10.188**, coarse **9.225**; fine−coarse **+0.963 [+0.000, +2.688]** descriptive empirical bootstrap.
Paired t95% [-1.378, +3.303]; inclusive upper sign-flip p=0.25000.

| Metric | Fine mean | Coarse mean | Fine−coarse [bootstrap95%] | Paired t95% |
|---|---:|---:|---|---|
| resource_payment | 10.1875 | 9.2250 | +0.9625 [+0.0000, +2.6875] | [-1.3783, +3.3033] |
| offered_rate | 10.1562 | 9.0250 | +1.1313 [+0.0437, +3.0938] | [-1.5450, +3.8075] |
| firm_profit | 9.8125 | 10.7750 | -0.9625 [-2.6875, +0.0000] | [-3.3033, +1.3783] |
| tie_rate | 0.8750 | 0.8000 | +0.0750 [+0.0000, +0.1750] | [-0.0638, +0.2138] |
| stage_regret | 4.4375 | 4.5875 | -0.1500 [-1.2500, +0.4562] | [-1.6564, +1.3564] |
| terminal_payment | 10.2000 | 8.8000 | +1.4000 [+0.0000, +4.0000] | [-2.1502, +4.9502] |

Block primary differences: +0.000, +4.312, +0.000, +0.500, +0.000.
200 cached responses; retry counts {'coarse': 0, 'fine': 0}; notes {'coarse': {'nonempty': 100, 'written': 100}, 'fine': {'nonempty': 100, 'written': 100}}.

At fixed realized productivity20, total firm profit plus worker take-home is20 in each round; firm profit is the exact wage complement.
The screen needs fine−coarse≥2, positive bootstrap lower and upper p≤.05; at n5 this is equivalent to mean≥2 and all five differences strictly positive. The bootstrap gate is redundant,not independent evidence. DUD if difference≤0 or upper<2; otherwise ODD.

paired_t_ci95 is paired t on differences; one-sample t on per-arm values.

Limitations: Five exploratory fresh blocks; zero tuning; no held-out or multiplicity correction; Grid size, action set, numerical salience and equilibrium set change together; no isolated arithmetic, competition or anchoring mechanism; Identical payoff formula and allocation, supplied memory and self-only notepads; feasible deviations differ and workers are passive; Sign-flip calibration requires exchangeability or symmetric paired differences, not enumeration alone; Coarse symmetric pure-Nash wages18,19,20; fine symmetric pure-Nash wages19,19.5,20; multiple equilibria and changed deviations preclude attributing effects solely to representation; No agreement or coordination verified; self-only notepads in both arms; Selected local CLI/environment and referenced-file fingerprints; complete effective configuration and provider execution remain unattested; Backend tools instruction-restricted only; actual tool non-use unverified.
The stage game has passive labor accepting zero and fixed unit supply. No agreement/execution is verified.

[Design](../DESIGN_S41.md) · [Scientific results](s41_ticksize.json) · [Figure](../figures/s41_ticksize.png)
