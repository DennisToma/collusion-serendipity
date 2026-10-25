# S42 — Surprise employer entry

**DUD**, exploratory five paired blocks / ten games, r7–10; zero tuning.

Worker take-home pay: entry **10.000**, control **10.000**; entry−control **+0.000 [+0.000, +0.000]** descriptive empirical bootstrap.
Paired t95% [+0.000, +0.000]; inclusive upper sign-flip p=1.00000.

| Metric | Entry mean | Control mean | Entry−control [bootstrap95%] | Paired t95% |
|---|---:|---:|---|---|
| resource_payment | 10.0000 | 10.0000 | +0.0000 [+0.0000, +0.0000] | [+0.0000, +0.0000] |
| offered_rate | 9.8667 | 10.0000 | -0.1333 [-0.2000, -0.0833] | [-0.2259, -0.0408] |
| firm_profit | 10.0000 | 10.0000 | +0.0000 [+0.0000, +0.0000] | [+0.0000, +0.0000] |
| tie_rate | 1.0000 | 1.0000 | +0.0000 [+0.0000, +0.0000] | [+0.0000, +0.0000] |
| stage_regret | 5.6667 | 4.0000 | +1.6667 [+1.6667, +1.6667] | [+1.6667, +1.6667] |
| terminal_payment | 10.0000 | 10.0000 | +0.0000 [+0.0000, +0.0000] | [+0.0000, +0.0000] |
| preentry_payment | 10.0000 | 10.0000 | +0.0000 [+0.0000, +0.0000] | [+0.0000, +0.0000] |
| wage_change | 0.0000 | 0.0000 | +0.0000 [+0.0000, +0.0000] | [+0.0000, +0.0000] |

Block primary differences: +0.000, +0.000, +0.000, +0.000, +0.000.
225 cached responses; retry counts {'control': 0, 'entry': 0}; notes {'control': {'nonempty': 100, 'written': 100}, 'entry': {'nonempty': 125, 'written': 125}}.

At fixed realized productivity20, total firm profit plus worker take-home is20 in each round; firm profit is the exact wage complement.
The screen needs entry−control≥4, positive bootstrap lower and upper p≤.05; at n5 this is equivalent to mean≥4 and all five differences strictly positive. The bootstrap gate is redundant,not independent evidence. DUD if difference≤1 or upper<4; otherwise ODD.

Limitations: Five exploratory fresh blocks; zero tuning; no held-out validation or multiplicity correction; Entry changes market size, visible identities, prompt length and endogenous histories; not an isolated competition mechanism; Entry is unannounced until round6; the entrant receives all public history and an empty private notepad; Seeds fix identities and task ordering, not model draws; pre-entry paths can differ between arms; Sign-flip calibration requires exchangeability or symmetric paired differences, not enumeration alone; Stage Nash sets change with market size; low wages do not verify agreement or coordination; Passive labor accepts zero, fixed supply, identical revenue20 and self-only notepads; no strategic workers; Known local CLI fingerprints only; effective configuration, provider execution and actual tool non-use unattested.
The stage game has passive labor accepting zero and fixed unit supply. No agreement/execution is verified. Total firm profit complements wage and is not separate evidence; per-firm offered-wage/regret means average different populations after entry.

[Design](../DESIGN_S42.md) · [Scientific results](s42_entry.json) · [Figure](../figures/s42_entry.png)

preentry_payment is the r1–5 wage baseline; wage_change is postr7–10 minus prer1–5. The paired wage_change contrast is descriptive difference-in-differences; it does not change the frozen primary screen.

| Block | Entry wage | Control wage | Difference |
|---|---:|---:|---:|
| 24920 | 10.000 | 10.000 | +0.000 |
| 24921 | 10.000 | 10.000 | +0.000 |
| 24922 | 10.000 | 10.000 | +0.000 |
| 24923 | 10.000 | 10.000 | +0.000 |
| 24924 | 10.000 | 10.000 | +0.000 |
