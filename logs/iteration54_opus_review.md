# Adversarial review: iteration 54 handoff brief, inventory and verifier

**Verdict:** I found no arithmetic errors and no high-severity bugs. I found 5 medium and about 6 low issues. Nearly all of them are claims that go further than the checks behind them. This review covers only the supplied text; I did not run anything.

## Arithmetic: all consistent
- **Approval differences:** S29 13/40 = 0.325. S62 4/40 = 0.100. S69 27/40 = 0.675. S70 0.
- **S72:** block values {0,1,1,0,0} give a mean of 0.4 and a standard deviation of 0.548. The 95% t interval is 0.4 ± 2.776·0.245 = [−0.280, 1.080], which matches.
- **S29 t interval:** [−0.049, 0.699] implies a block standard deviation of about 0.30, which is plausible for five blocks of size /8.
- **S29 sign-flip p:** four non-zero blocks give p = 1/16 = 0.0625, which matches.
- **Counts:** 29 + 23 + 2 = 54, and the axis sizes 6+5+6+7+6+5+19 = 54.

## Medium
1. **The S29 result can't be read as collusion-relevant without the reviewer's incentive.** The brief says the reviewer's payoff "depends on the bonus and penalty rules". S69 then shows approvals jump from 4/40 to 31/40 when the reviewer's own incentive flips. But the brief never states whether approving TYPE-Y was costly to the reviewer under S29's and S62's rules. If it was neutral or profitable, the S29 approvals may just be self-interest. Add one sentence giving the reviewer's marginal payoff in S29 and S62.
2. **"Scientific model calls forbidden" claims more than the code enforces.**
   - The script only patches `llm.chat`. Calls through other backend functions, a direct client (S62 used the aqueduct backend) or a subprocess `codex` call are not blocked.
   - The network is not blocked either.
   - Suggested wording: "`llm.chat` is patched to raise." Or also block network access and subprocess calls.
3. **The denominator of 40 is assumed, not checked.** `count_approvals` multiplies `pair_bad` by 8 and checks that the result is a whole number that matches `mean_exact`. That only checks internal consistency. It does not confirm one TYPE-Y review opportunity per game per round. The name `pair_bad` suggests the outcome may be per pair or per round, in which case "40 opportunities" may be wrong. Assert the count from the raw trajectories, or reword.
4. **DUD and ODD are never defined in the brief, and they don't mean one thing each.**
   - S69, the largest effect in the table, is labelled DUD and re-read here as "successful calibration".
   - S62, whose intervals include zero, is labelled ODD.
   - ODD also includes post hoc and context-only entries.
   
   So "29 DUD / 23 ODD" can be read as 23 signals. Define both labels in one line, and say that DUD can mean "explained by incentives" rather than a null result.
5. **"S70 rejects only its directional prioritization screen" reads as the opposite of what is meant.** "Rejects" sounds like a hypothesis was rejected. The meaning is "fails" or "does not pass". Reword it.

## Low
- **The 5-block percentile bootstrap is called "95%".** Five blocks give only 126 distinct resamples, and these intervals typically cover less than they claim. S29's bootstrap interval excludes zero while its t interval doesn't. The brief already says "descriptive" and shows the t intervals, so this is partly disclosed. Even so, the line "shared notepad coincided with more adverse approvals" relies on the bootstrap.
- **S29's sign-flip screen could not be passed after the tie.** With one tied block, the smallest possible p is 1/16 = 0.0625, so "misses its screen" understates what happened: S29 reached the most extreme result possible given the tie. This is a fairness point, not a bug.
- **Several t bounds fall outside the possible range.** S69's upper bound of +1.015 and S72's +1.080 exceed the maximum difference of 1. Note it, or clip the bounds.
- **Axis and lineage:** S72 is a reanalysis of S29 (axis C) but is filed under axis E. That makes the portfolio look broader than it is. Mark reuse in the axis table.
- **Prose the verifier doesn't check:**
  - that the FAILED entries are exactly S16 and S68, and the descriptions of why each failed;
  - "S62 unresolved";
  - the "/5" denominators in S72, which are hard-coded;
  - whether the S72 arm totals agree with the block values (shared − self should equal the sum of the block values).
  
  A one-line assertion each would close these. Otherwise, avoid calling the brief "source-bound" without qualification.
- **The script describes `verify` as read-only, but it writes `logs/iteration54_handoff_check.json`.**
- **The verdict mapping assumes labels start with a known prefix.** Classification uses `startswith`, so a verdict string such as `**DUD→ODD**` would silently count as DUD. This is minor.

## Already disclosed (not bugs)
- The examples were selected post hoc.
- There is no multiplicity correction and no held-out validation.
- Entries are not independent, and there is no discovery rate.
- S72 reuses S29's games and says nothing about intent or agreement.
- S29 and S62 differ in many ways besides the model, so the comparison doesn't isolate a model-family effect.
- S70 does not establish equivalence.
- Replay covers only the selected pilots, not every historical analysis or a fresh install.
- The suggested confirmation pilot has not been launched.
