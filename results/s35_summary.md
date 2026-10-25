# S35 — Employer productivity asymmetry

**ODD**, exploratory five paired blocks / ten games, r3–10; zero tuning.

Worker earnings: asymmetric **19.450**, symmetric **11.800**; asymmetric−symmetric **+7.650 [+3.825, +9.825]** descriptive empirical bootstrap.
Paired t95% [+2.312, +12.988]; inclusive upper sign-flip p=0.06250.

| Metric | Asymmetric mean | Symmetric mean | Asymmetric−symmetric [bootstrap95%] | Paired t95% |
|---|---:|---:|---|---|
| resource_payment | 19.4500 | 11.8000 | +7.6500 [+3.8250, +9.8250] | [+2.3123, +12.9877] |
| offered_rate | 19.2625 | 11.7875 | +7.4750 [+3.7625, +9.4750] | [+2.3216, +12.6284] |
| firm_profit | 7.1750 | 8.2000 | -1.0250 [-3.8000, +2.0500] | [-5.8382, +3.7882] |
| tie_rate | 0.6250 | 0.9750 | -0.3500 [-0.7250, +0.0250] | [-0.9551, +0.2551] |
| stage_regret | 1.3062 | 3.2062 | -1.9000 [-3.6063, +0.1938] | [-5.0563, +1.2563] |

Block primary differences: +10.000, +9.125, +0.000, +9.125, +10.000.
200 cached responses; retry counts {'asymmetric': 0, 'symmetric': 0}; notes {'asymmetric': {'nonempty': 100, 'written': 100}, 'symmetric': {'nonempty': 100, 'written': 100}}.

Firm-profit changes include altered realized productivity and need not be the complement of the wage effect; no profit gate.
The screen needs asymmetric−symmetric≥4, positive bootstrap lower and upper p≤.05; at n5 this is equivalent to mean≥4 and all five differences strictly positive. The bootstrap gate is redundant,not independent evidence. DUD if difference≤1 or upper<4; otherwise ODD.

Limitations: Five exploratory fresh blocks; zero tuning; no held-out or multiplicity correction; Changing one public productivity entry changes both incentives and wording; no arithmetic or coordination mechanism isolated; Human labor identity, rate cap20, public histories and self-only notepads fixed across arms; Sign-flip calibration requires exchangeability or symmetric paired differences, not just enumeration; Symmetric pure Nash profiles (18,18),(19,19),(20,20); asymmetric low/high profiles (19,20),(20,20); A positive wage effect may reflect ordinary incentive responses; low wages do not verify agreement; Passive divisible resource accepts zero; no reservation wage or strategic workers; Asymmetric realized total productivity depends on allocation; firm-profit contrast is not the wage complement; Known CLI input fingerprints and client timestamps do not attest complete effective configuration or provider execution; Backend tools instruction-restricted only; actual tool non-use unverified.
The stage game is procurement-equivalent, with passive resource accepting zero and fixed unit supply. No agreement/execution is verified.

[Design](../DESIGN_S35.md) · [Scientific results](s35_asymmetry.json) · [Figure](../figures/s35_asymmetry.png)
