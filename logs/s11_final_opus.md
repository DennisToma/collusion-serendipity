# S11 review: delayed market feedback

**Verdict.** S11's own frozen rule labels it **ODD**, and I agree. I found no code bug that changes any S11 number or the verdict. I did find one release-blocking problem and three smaller gaps, all listed below. The claims mostly stay within scope, with two wording fixes needed.

**What I could and couldn't check.** This session had no shell or file-read access, so I couldn't open the raw `game_*.json` files or `requests.jsonl`. I recalculated everything from the per-game values in `results/s11_delay.json`. Whether those values match the raw games rests on `s11_independent.py` and the replay check. I didn't review `s11_present.py`, `s11_retry_audit.py`, `s11_integrate.py`, `s11_progress.py`, `s11_reviews.py`, the S11 rows in `EXPERIMENTS.tsv`, or the final critic logs.

## Numbers I recalculated (all match)
- **Primary metric.** The per-block differences are [11, −25, 57, 27, 52]/27 = 122/135 = **0.9037**. The arm means are immediate 328/135 = 2.4296 and delayed 206/135 = 1.5259.
- **Sign-flip test.** The upper tail needs the flipped subset to sum to ≤25. Only ∅, {11} and {25} qualify, so p = **3/32 = 0.09375**. The lower tail is 30/32 = 0.9375. The exact Wilcoxon test gives the same 3/32.
- **Paired t interval.** The numerator SD is 33.36, giving **[−0.630, 2.438]**.
- **Verdict rule.** The mean is below 1, so it can't be a HIT. It is above 0.25 and not ≤ −1, so it is ODD.
- **HIT equivalence at n=5.** I confirmed it. p ≤ .05 can only mean p = 1/32, which happens exactly when all five differences are strictly positive (a zero or negative difference adds a sign pattern that ties or beats the observed sum). All positive then forces the bootstrap lower bound above zero.
- **Secondary outcomes.** Every arm mean, every per-block difference, and the quantity t interval [−0.206, 0.147] match.
- **All-round and final-round tables.** These match too, as do the counts 240 cells, 24 bootstrap intervals and 366 = 360 + 6 retries.
- **Analytical reference.** The q4/q8 toy example checks out: immediate cycles 4,8,4,8 and delayed runs 4,4,8,8, giving a 20/9 reduction.
- **Not recomputed:** the bootstrap quantiles. I only confirmed they are reachable (−12/135 and 245/135).

## Timing and provenance checks that passed
- The delay is applied correctly. Delayed round 2 sees nothing, and the hidden row cannot reach the prompt through history, the calculator table, reasoning or retries.
- The primary window has 27 transitions, starting with round 3 → round 4.
- The bootstrap random draws run in the order the design specifies.
- The deadline check compares timestamp strings, and that is correct, including at the exact deadline instant and with fractional seconds.
- The abort flag, refusal of a damaged or mismatched cache, and "use every cached response exactly once" all hold.
- Release re-runs the analysis and reproduces the frozen files byte for byte.

## Remaining problems
1. **The S11 release isn't committed yet (medium, blocks release).** When this session started, all of these were untracked:
   - the data (`data/s11_delay/`), the frozen result, the summary and the figure;
   - all S11 logs;
   - five scripts the review log cites: `s11_transport_audit.py`, `s11_reference.py`, `s11_retry_audit.py`, `s11_integrate.py` and `s11_progress.py`.

   `s11_release.py` and `s11_reviews.py` also had uncommitted changes. Until all of this is committed, `--clean-clone` can't pass on S11, because the clone has no data and the live run refuses to proceed. The audits the review log cites also can't be reproduced. Commit everything, then run `s11_release.py --clean-clone` and log the result.
2. **The final reviews have no recorded disposition (low–medium).** The design says "both final critics requested. Report every result." The review log stops at the pre-launch checks, and `logs/s11_final_opus.md` and `logs/s11_final_reviews.log` exist but nothing is concluded from them.
3. **The presentation script isn't in the frozen file list (low).** `s11_present.py` writes `s11_summary.md` and the figure, but it isn't in the hashed list of frozen sources. The clean-clone run only checks that it gives the same output twice, not that it predates the results.
4. **No independent check that the requests were actually delayed (low).** The evidence chain is: the unit tests check `prompt()`, then the replay shows every cached request matches `prompt()`. That chain is sound, but `s11_independent.py` re-checks only the calculator tables, not the history text sent to the model. A short offline parse of `requests.jsonl`, confirming that delayed round t lists rounds 1..t−2, would close the gap without depending on production code.

## Problems with inference and claim scope (not acknowledged, or only partly)
- **The ODD label rests on two blocks.** Without block 24112 the mean is 0.60. Without 24112 and 24114 it is 13/81 = 0.16, which would be **DUD**. The 24112 immediate game is exactly the analytical q4/q8 cycle for all 12 rounds (change 4, stage regret 16 in every round, lag regret 0). An exact unpaired permutation test, not prespecified, gives 15/252 = 0.060. That is still not under .05, so nothing changes, but it shows the pairing adds little.
- **"Paired seed blocks" overstates what the pairing does.** S11's game code never uses the seed for anything except the run ID, so the pairs share only their timing, concurrency and backend state. Call them "time-matched pairs" so the term doesn't suggest more control.
- **The lag-conditioned regret result is mechanical.** The summary table shows it as delayed − immediate +4.73 with both intervals excluding zero. For the delayed arm, that regret is measured against feedback those firms never saw. The text does say this, but the table row reads like a finding. The useful check, regret against the table each firm actually received, is missing.
- **"Delayed best response predicts slower cycles" holds only when the cycle starts away from Nash.** From q6, both lags just sit at Nash. Add that condition to the wording.
- **Final-round delayed output is a lead to leave alone.** Mean quantity is 4.93 delayed vs 5.47 immediate; one block ends at q4/P18 and three at q5. This is one round, descriptive only and not prespecified. `REPORT.md` correctly doesn't promote it. Keep it that way, and don't let it slip into HITS.

## Limitations already acknowledged (correctly)
- n=5, exploratory; bootstrap intervals are descriptive and the t intervals fragile.
- The treatment is a bundle: all feedback is delayed (own actions included) and delayed round 2 has no table.
- The short 9-transition window is sensitive to where a cycle starts.
- Slower consecutive changes don't mean convergence or less collusion.
- Seeds don't control API draws, and the two concurrent games can interfere with each other.
- Retries are uneven (2 immediate vs 4 delayed).
- Model and temperature labels come from the client and aren't attested; there's no OS isolation.
- The Opus design review saw an earlier code snapshot than the one frozen.
- No pooling with S03.
