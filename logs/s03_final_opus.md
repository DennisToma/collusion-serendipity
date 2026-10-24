Exit code: 0
# S03 adversarial review: exact conditional profit calculator

I reviewed S03 only. I edited nothing and ran no models. This session had no shell or file-read tools, so I worked only from the files you pasted. Every number below I recalculated by hand from `results/s03_calculator.json` and the per-game records.

## Verdict

The code and arithmetic hold up. Every S03 number I checked is correct, and the frozen **DUD** label is applied correctly. Nothing I found changes the verdict.

The weak point is interpretation, not computation. Most of the measured effect comes from two things: the control arm producing above Nash, and an odd-length analysis window cutting through a two-round cycle. The current wording does not make this clear enough (C1–C3 below).

## Independent recalculation (all match)

**Primary measure: output per firm, rounds 4–12** (27 firm-rounds per game)

| Seed | None total | Calculator total | Difference (numerator) |
|---|---|---|---|
| 24060 | 180 | 159 | −21 |
| 24061 | 189 | 156 | −33 |
| 24062 | 187 | 156 | −31 |
| 24063 | 189 | 159 | −30 |
| 24064 | 162 | 158 | −4 |

- **Means:** the differences sum to −119, and −119/135 = **−0.88148**. Arm means are 907/135 = 6.7185 (none) and 788/135 = 5.8370 (calculator).
- **Classification:** the mean is above −1, so the reverse label does not apply. It is at most 1/4, so the result is DUD. This is correct.
- **Sign test:** with every difference negative, the higher-output p is 32/32 = 1.0 and the lower-tail p is 1/32. Both correct.
- **Paired t interval:** standard deviation of the differences 0.44397, standard error 0.19855, t(.975, 4) = 2.7764, giving **[−1.4328, −0.3302]**. Correct.
- **Bootstrap bounds:** I could not reproduce these without running code. They are plausible; for example, −1.170 is just above the smallest seed difference, −1.222.

**Secondary measures:** all match to 3 decimals.
- Price (+2.644, which is exactly 3 × 0.8815) and profit (+6.393, t interval [−0.364, 13.149]).
- Regret against actual rivals (2.630 → 8.259) and against last round's rivals (2.570 → 0.119).
- Distance from Nash (t interval [0.073, 1.246]), absolute change (+2.689) and the all-equal rate (+0.178).
- Every cell of the all-rounds and final-round tables in REPORT_DETAILS.
- The seed-block table, 368 = 360 + 8 cached responses, and the matching REPORT.md statements.

**Per-game spot checks against the payoff formula:**
- 24062 calculator: firms alternate between all-4 and all-8, five low rounds and four high in the window. That gives 52/9 = 5.778 output, 240/9 = 26.667 profit, regret 16 and change 4.
- 24060 calculator: alternates between all-5 and all-7, giving 53/9 = 5.889 output and 309/9 = 34.333 profit.
- 24061 none: all firms at 7, giving profit 21 and regret 4.
- 24060 none: a constant (6,7,7) split, giving regret (1+2+2)/3 = 1.667.

## Interpretation and scope problems (not code bugs)

**C1 — Medium. The hypothesis had nothing to act on.** The design predicted the table would raise output by reducing apparent restraint. But the control arm produced **above** Nash: 6.719 in rounds 4–12 and 6.722 over all rounds, with three of five games stuck at 7. There was no restraint to reduce, which is the ceiling risk the Opus pre-review raised. REPORT.md never says the control arm over-produced. A plain reading of the result is that the table moved firms from over-producing (about 7) to cycling around a mean of 6. "Calculator lowers output" invites a reading of induced restraint, which is wrong.
- **Remedy:** state in REPORT.md that the control arm sat above Nash, so the directional test could not address the stated mechanism.

**C2 — Medium. Part of the effect, and the "all five negative" claim, depend on the window length.** Lagged best responses produce symmetric two-round cycles (4↔8 and 5↔7) whose full-cycle mean is exactly 6. The rounds 4–12 window has 9 rounds, and in all five calculator games it contains five low-phase rounds and four high ones. The calculator's final round is in the low phase in every game (output 4, 5, 5, 5, 5.33). So the calculator arm's 5.837 is a cycle averaging 6 plus a parity offset of about −0.16. Decomposed:
  - −0.719 comes from the control arm sitting above 6;
  - −0.163 comes from the window parity.

  Over all 12 rounds the seed differences are −0.722, −1.000, −0.889, −1.000 and **+0.028** for 24064. So "all five negative" and the descriptive lower-tail p = 1/32 hold only because the window has odd length. The verdict survives this: with the opposite phase, the calculator arm would average about 6.11–6.22 and the difference about −0.5 to −0.6, still DUD.
  - **Remedy:** soften "All five differences are negative" in REPORT.md. Show the decomposition and the all-rounds seed signs (4 of 5 negative).

**C3 — Medium. Profit, price and final-round results are partly phase effects.** Over a full cycle, calculator profit is *below* the Nash level of 36: 33 for the 5↔7 cycle and 24 for 4↔8. The window over-weights the high-profit low-output rounds. The calculator's all-rounds profit is 29.217 against 31.778 in the window. The final-round row (output 4.867, price 15.4, profit 45.1) is entirely the low phase, and on its own it looks like collusive restraint.
- **Remedy:** label the final-round row and the profit/price differences as phase-dependent in both REPORT files.

**C4 — Low.** The fall in regret against last round's rivals is zero by construction for any firm that follows the table, so it is a manipulation check, not an outcome. REPORT.md presents it alongside the outcomes. The rise in regret against actual rivals is the mechanical result of all three firms best-responding to the same lagged quantities at once. Both points should be framed that way.

## Code and provenance bugs

| # | Severity | Issue | Remedy |
|---|---|---|---|
| B1 | Low | **The analysis can write to raw data.** `assert_cached_replay` builds a `CalculatorCache`, and the inherited `Cache.__init__` appends a newline to, or truncates, `responses.jsonl` if the last line is torn or unterminated. The analyzer's earlier `json.loads` pass catches a torn line, but not a valid last line missing its `\n`. Replay then modifies the file before the "unchanged" check fires. The check catches it, but only after the raw evidence has already changed. | Replay from a copy in `/var/tmp`, or add a read-only flag to `Cache`. |
| B2 | Low | **Unused cache entries aren't rejected.** Replay never checks that every cached key was actually consumed. Today 368 = 360 + 8, so there are none, but the code doesn't enforce this. | Assert that the set of keys consumed during replay equals the set of cache keys. |
| B3 | Low | **The deadline is not checked after the run.** It is compared as an ISO string. That works for `+00:00` output, including the edge where microseconds are zero, but it is fragile. The analyzer also never checks that every live `call_started_utc` falls before the deadline. | Parse to datetimes and assert this in `validate_game`. |
| B4 | Low | **Invalid retries are not broken down by arm.** Eight retries were fresh model draws; if they fell mostly in one arm, that arm got extra draws. The cause is also unreported (word limit? prose around the JSON?). | Report the retry count per arm and the reason. |
| B5 | Low (documentation) | **The test count is misleading.** The disposition log says "21 tests PASS" as S03 validation, but `test_s03.py` contains 8 tests. | Say "8 S03 tests within a 21-test suite", if that is what ran. |

## Checks that pass

- The table arithmetic, the zero-price floor and negative profits are correct. The table is checked against `payoffs(...)[1][0]` for all 13³ combinations, which is the right element, not the price.
- No current-round information leaks into prompts. Round-1 prompts are identical across arms, and the control prompt equals the treatment prompt minus the table and its caption.
- The parser is strict and catches every malformed type I tried.
- The decision rules use exact fractions, and the reverse label is tested before DUD.
- The sign enumeration keeps ties, and the paired t interval uses the sample standard deviation.
- The bootstrap random generator is deterministic, and the source manifest must match exactly.
- Git status shows the frozen sources (sim/*, `s03_analyze.py`, `DESIGN_S03.md`) unmodified.

## Limitations (already disclosed, not bugs)

- Five seed blocks only.
- Model draws are not controlled, and the shuffled execution slots do nothing in practice, because both games in a block start together.
- The table bundles arithmetic, salience and a myopic cue, so their effects can't be separated.
- No collusion claim is possible from this design.
- The secondaries have no multiplicity correction.

A further limitation: the dynamics are nearly deterministic once round 1 is played, so each game is close to a single random draw. That makes even the reported descriptive intervals optimistic.

## Not reviewed (not supplied)

- `scripts/s03_present.py`, `s03_economics.py`, `s03_progress.py` and `s03_report.py`.
- `logs/s03_analysis_freeze.json`, `logs/s03_economics.json`, `logs/s03_final_reviews.log`, the figure, and the `EXPERIMENTS.tsv` row.
- Whether the config hashes match commit 29a4b3f.

The disposition log says final-claim reviews were "requested below" but records no outcome. REPORT.md should not imply they are complete until the log shows them.
