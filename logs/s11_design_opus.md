# S11 review: delayed market feedback

I found no blocking bugs. The treatment timing, the provenance chain and the main arithmetic all check out. What's left are a few decision-rule and claim-scope problems, and some code paths that only the live run will ever execute. I made no edits and no live model calls. This review is based only on the files you pasted; I didn't run anything.

## Remaining issues (most important first)

1. **A strong reverse effect can be labelled DUD.** `classify` requires all five seed differences to be negative for ODD-reverse. Anything else at or below 0.25 becomes DUD. So a mean of −3 with four negative seeds and one positive seed is reported as "nothing here." A positive mean of 1 or more without unanimity goes to ODD, so the two directions are treated unequally. The code matches DESIGN_S11.md, so this is a rule defect, not an implementation bug. If you keep the rule, REPORT should give the mean whenever the label is DUD, so a large negative result isn't buried.

2. **A HIT is the outcome naive best response predicts, so it isn't surprising.** In the symmetric case, best response gives q(t+1) = 12 − q(t), which alternates and changes by 4 each round. With a 2-round lag it gives q(t) = 12 − q(t−2), which takes pairs of steps: change 0, then |12 − 2a|. That roughly halves the primary metric. DESIGN mentions this. But a HIT handed to HITS.md under the "serendipity" framing would mostly confirm stale-information arithmetic. It shouldn't be read as evidence about learning, stability or collusion. Put that caveat on any HIT entry itself.

3. **Two of the three HIT conditions add nothing.** Sign-flip p ≤ .05 with n = 5 is only reachable when all five numerators are strictly positive (p = 1/32). One zero or negative seed gives p ≥ 2/32. Once all five are positive, every bootstrap resample is positive, so the bootstrap lower bound is above 0 automatically. In practice HIT means "all five seeds positive and mean ≥ 1." State it that way in REPORT rather than implying three independent checks.

4. **The primary bootstrap doesn't start from a fresh RNG 2411.** One `rng` is shared across all metrics, and `absolute_change` is the 7th key, after 18 earlier `summarize` draws. The independent script copies this order, so it reproduces the number but doesn't validate the claim in DESIGN. By point 3 this can't change the verdict. It is still a mismatch between DESIGN and code. Either describe it accurately or report the exact 3,125-resample interval from `s11_independent.py`.

5. **Several fail-closed paths only run for the first time on live data:**
   - The `git show registration_commit:...` hash check is skipped in dry mode. A shallow clone or a path change would only show up after paid calls.
   - "Pushed" is never checked, only "committed and matches HEAD." DESIGN says "committed pushed source manifest."
   - Nothing compares the registration commit time with the first `call_started_utc`, so "registered before live calls" isn't proven by the code.

6. **Tamper-test coverage is thinner than DESIGN claims**, at least in `test_s11.py` as pasted. It covers a torn cache, duplicate keys and the deadline. It doesn't cover:
   - replay detecting an orphan key or a changed response or request
   - a model/backend route mismatch
   - source drift
   - a cached key passing after the deadline (only the refusal is tested)

   `test_simultaneous_prompts` calls the same prompt twice and compares the results, so it can't fail. Simultaneity actually holds because `prompt` only uses earlier rows, but the test doesn't show that. Check whether the missing cases appear in `logs/s11_tests.log` or the dry-run scripts. If not, either add them or reword the DESIGN claim.

7. **Run risk: one failure ends the whole pilot.** That covers three strict-JSON failures in a row (for example the model wrapping JSON in code fences), a route mismatch, or hitting the 18:35 deadline. Completed blocks are kept on disk, but the analysis refuses anything under 10 games. Each game makes about 36 sequential codex calls, so five blocks could take around two hours. Check the start time against the deadline before launching.

8. **Minor wording points:**
   - The immediate arm is told feedback comes "with a 1-round lag." That is accurate, but it frames the control as lagged too.
   - `config.temperature_requested` is hard-coded as `1` instead of `TEMPERATURE`. Harmless, because the cache key uses `TEMPERATURE`.

## Already acknowledged (not bugs)

- n = 5, exploratory, many pilots tested with no correction across them; bootstrap and t intervals are fragile.
- The seed number only affects the run ID and cache key, never the prompts. Seed blocks are pairs run at the same time, and the sign-flip test assumes the two arms are interchangeable. DESIGN says blocks don't control API draws.
- Timing and warm-up are bundled: in the delayed arm, round 2 has no table and no "Your goal remains…" line. Own past action and profit are delayed too.
- The t−1 regret is a diagnostic that uses information the delayed arm didn't have.
- Model labels come from the client; temperature and sampling seeds aren't controlled; API calls may interfere; there's no OS isolation.
- Calls already in flight may finish after 18:35.
- No agreement or execution labels, and no conclusion about collusion.
- Primary and secondary contrasts use opposite signs. That is documented in the result JSON, but watch for it in REPORT text.

## Checked and correct

- **Timing:** at round t, immediate sees rows[:t] and delayed sees rows[:t−1]. Tables use the latest visible rival total. The "(N)" round label in the prompt is correct, and the counterfactual-hidden-row test is meaningful.
- **Primary metric:** 27 transitions (rounds 4–12 against the round before, 3 firms) for each game. The mean of per-round means equals the total divided by 27, and the integer numerators are checked exactly as fractions in the independent script.
- **Deadline:** the ISO-string comparison is correct around 18:35:00, including the microsecond-free case.
- **Provenance:** a cache key gets a request-audit row on resume. Replay rebuilds every exact prompt, consumes each key once, finds no orphans and leaves the files byte-identical. Exports are checked against the schedule order, and the requests/raw/game chain checks the tables. The torn-cache check runs before the parent class's automatic repair. A failure marker blocks both resume and analysis.
- **Independent script:** recomputes per-game metrics from the raw rows, the tables, the paired-t interval, the sign-flip test and the verdict without using the production metric helpers.
