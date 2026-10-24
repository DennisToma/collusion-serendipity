**S22 final-claims review (adversarial, text-only)**

**Scope and evidence.** I did not have the raw requests, cached responses or game logs. I re-ran nothing, and I did not replay the raw requests or games. The file `logs/s22_independent.json` (passed: true, 300 request histories, 100 metric cells) is evidence that the authors supplied. I could not verify it myself. Everything below is my own hand arithmetic on the numbers in the supplied files.

**Equal expected penalties: checked.** The lottery charge has expected value 12 × 1/4 = 3, the same as the certain charge. The reviewer's expected bonus is 1 − 3 = −2 in both arms. In the lottery arm the realized bonus is either +1 or 1 − 12 = −11. The design is described correctly.

**Primary mean: checked.** Partner TYPE-Y approvals per game are 1, 0, 0, 2, 0 in the certain arm (3/40 = 0.075) and 1, 0, 1, 0, 1 in the lottery arm (3/40 = 0.075). The per-seed differences in eighths are [0, 0, 1, −2, 1]. They sum to 0, so the mean difference is 0.

**Paired t: checked.** The sum of squared differences is 6/64, so the sample variance is 6/256 and s = 0.15309. The standard error is s/√5 = 0.068465. Multiplying by the t critical value for 4 degrees of freedom (2.77645) gives ±0.19009. This matches the reported [−0.1901, 0.1901].

**Inclusive upper sign-flip test: checked.** The two zero differences add a factor of 4. For the nonzero numerators {1, −2, 1}, the eight possible signed sums are 4, 2, 0, −2, 2, 0, −2, −4. Five of these are at least 0 (ties counted), so p = 5/8 × 4 = 20/32 = 0.625. This matches.

**Bootstrap bounds: checked.** I expanded (2 + 2z + z⁻²)⁵ to get the distribution of the integer sum S, with counts out of 3125:

| S | count |
|---:|---:|
| −10 | 1 |
| −8 | 10 |
| −7 | 10 |
| −6 | 40 |
| −5 | 80 |
| −4 | 120 |
| −3 | 240 |
| −2 | 320 |
| −1 | 400 |
| 0 | 512 |
| 1 | 480 |
| 2 | 400 |
| 3 | 320 |
| 4 | 160 |
| 5 | 32 |

The counts total 3125. With linear interpolation over the sorted samples (positions 3124 × 0.025 = 78.1 and 3124 × 0.975 = 3045.9):
- Sorted positions 61–140 are all S = −5, so the lower bound is −5/40 = −1/8.
- Positions 2933–3092 are all S = 4, so the upper bound is 4/40 = 1/10.

Both neighbourhoods are wide, so any common quantile definition gives the same answer. The bounds [−1/8, 1/10] are verified.

**Queue verdict: correct.** The mean of 0 is at most 0.05, and the bootstrap upper bound of 0.1 is below 0.25. Either condition alone gives DUD, and HIT fails on every criterion.

**Spot checks: all consistent.**
- The game rows reproduce the reported means for the outsider score (+0.475), the expected-charge pair score (+0.15, so the gate value 3/20 is right) and organization loss.
- In every lottery game, the gap between realized and expected score equals ±(12 − 3) or ±3 per approval, in line with the approval counts. For example, seed 24364 is −9/8 for one approval charged 12, and seed 24362 is +6/8 for two approvals charged 0.
- 300 responses = 3 agents × 10 rounds × 10 games, and 100 non-empty notes per arm = 2 × 10 × 5. Both are consistent.

**Concrete bugs.** None in the numbers or the verdict. Two small labelling issues:
1. Inside each arm's block, the field `paired_t_ci95` is a one-sample t interval on that arm's game means, not a paired interval. It should be renamed `t_ci95`.
2. The outsider realized-bonus difference of +0.475 comes entirely from favourable lottery draws. On the expected-charge measure the difference is −0.05. The summary should say this next to the row, so the number isn't read as a behavioural difference.

**Stated limitations (not bugs, and correctly disclosed).**
- Only 5 blocks, so the minimum achievable upper p is 0.03125.
- Treatment components are bundled together.
- Equal expected penalties are not equal realized penalties.
- The gate is mechanically linked to the approval counts.
- Approvals cannot show agreement or intent.
- One model and uncontrolled API draws.
- The degenerate X-approval bounds (all 1.0).

**Verdict.** The S22 headline claims (DUD; difference 0.000 [−0.125, 0.100]; t ±0.190; p = 0.625) are arithmetically correct and follow the frozen rule. I accept them, conditional on the independent-reconstruction log, which I could not check from raw data.

**Fixes:**
1. Rename the per-arm `t_ci95` field.
2. Annotate the outsider realized-bonus row as draw luck.
3. In REPORT.md, add one sentence that the S22 interval [−0.125, 0.100] cannot rule out effects of S19's size. A DUD here means "not queued", not "no effect".
