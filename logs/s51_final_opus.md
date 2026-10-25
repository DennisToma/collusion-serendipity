# S51 adversarial review

I reviewed only the supplied text. I made no edits and no paid calls. The raw `responses.jsonl` was not available, so I rebuilt the result from the 20 per-case booleans in `results/s51_penalty.json`. I did not see `s51_reviews.py` or `s16_reviews.py`, so those two files are unreviewed.

## My reconstruction of the numbers

| | Block values (24480–24484) | Mean | Bootstrap 95% | Paired t 95% | Upper / lower / two-sided p |
|---|---|---|---|---|---|
| Baseline (charge 3) | 0, 1, 1, 0, .5 | .5 | [.1, .9] | [−.121, 1.121] | .125 / 1 / .25 |
| Strong (charge 9) | .5, 1, .5, 0, .5 | .5 | [.2, .8] | [.061, .939] | .0625 / 1 / .125 |
| Contrast | −.5, 0, .5, 0, 0 | 0 | [−.3, .3] | [−.439, .439] | .75 / .75 / 1.0 |

- **Bootstrap:** I enumerated all 3125 draws by hand on the doubled scale. For the contrast, the cumulative counts are S ≤ −4: 16 and S ≤ −3: 111. Positions 78 and 79 (78.1 interpolated) both fall at −3, giving −.3. The baseline and strong bounds work the same way.
- **Sign flips:** for the contrast, flipping only the two nonzero blocks gives 3/4, 3/4 and 1, which matches all 32 enumerations.
- **Counts:** 5/10 approvals in each arm, and 8/8 matches with the archived actions. Both match.
- **Verdict:** DUD is correct, triggered by mean ≤ .05. The design's claim that a HIT needs all 5 blocks strictly positive is right: any zero or negative block gives at least 2 of 32 flips at or above the observed sum, so p is above .05.

## Design checks
- **Case selection:** `max(t∈2..9 with partner not passed)` uses task status only, and the independent script re-derives it from the S29 RNG. It is not selected on outcomes.
- **Penalty change:** the 3→9 charge and −2→−8 net come from replacing one text block exactly once. The same notice goes into both arms, the user bytes are identical, and the tests check that "3-point" no longer appears anywhere in the strong system prompt.
- **Payoff arithmetic:** when both partners are Y and approve each other, each gets 4 under baseline and −2 under strong. Correct.
- **Action binding:** strict unique-key parsing, the partner is the only key, the value must be a real boolean, and accepted outputs are journaled.
- **Run integrity:** the attempt file was written before registration at 05:40:58, 79 minutes before the deadline. Sources match the registration commit and remote. The response sweep confirms at most 2 calls ran at once and that the block barriers held. One call through `retries=1` and a single model means one logical transport attempt; any retries inside the CLI are not attested.

## Bugs (none change the estimate)
1. **REPORT.md omits that the upper bound is .3, which includes the .25 target.** The S48 paragraph says this; the S51 paragraph and summary only say generically that a DUD "may leave .25 unresolved". It should say plainly that a .25 reduction is not excluded.
2. **"The rules just stated" has an unclear referent.** The notice is appended after the notepad paragraph, so a reader may take "rules" to mean the notepad rules rather than the charge. Both arms share it, but it is an imperfect common notice.
3. **Benign side effect:** a live run into a new directory after the attempt has been reserved writes a `failure.json` there.
4. **Release order:** `logs/s51_attempt.json`, `logs/s51_launch.json` and `data/s51_penalty/` are still untracked, but `validate` and the clean-clone check need them. They must be committed before running the clone check.

## Limitations the materials already acknowledge (correctly)
- Baseline is not the exact archived prompt.
- Dated notes (6/10 cases) and historical charges still show the old 3-point policy.
- Only the focal agent is rerun.
- No mechanism, equilibrium or long-run effect is identified.
- Reported model/backend labels are the requested ones, not attested served identity.
- Source CLI and runtime equality are unknown.
- The fresh baseline did not vanish (5/10).

## Limitations not stated
- **The payoff argument mostly covers the wrong cases.** The both-Y identity applies to only 3 of 10 cases (24480_C and 24483_B/C), and all of those reject in both arms. In the other 7 cases the focal agent is X, so the relevant comparison is "I approve your Y, you approve my X": that nets −2 per round under strong versus +4 under baseline. Also, the partner gains 1 by approving the focal agent's X anyway, so a threat to retaliate costs the partner something.
- **The two non-tied blocks move in opposite directions.** 24480_B approves under charge 9 but not under charge 3, an action that is dominated at the stage level. 24482_A goes the other way. This fits sampling noise from one draw per arm; the run has no test-retest data.
- **The same 10 histories have now been used for S48, S50 and S51.** Treat any pattern across these pilots as exploratory only.

**Verdict:** the integrity checks and statistics reproduce exactly. DUD stands with the scope limits above, and REPORT.md needs the one wording fix in bug 1.
