# S41 adversarial review (code reading only)

I only read the code you pasted. I ran nothing: no tests, no dry replay, no git, no clock check. Nothing was edited and no models were called.

**Verdict:** I found no bug that would block launch or invalidate the results. Five low-severity issues remain. Launch is conditional on two checks.

## Checked and correct
- **Economics:** Payoffs use exact fractions. The full search over every wage pair and deviation should give coarse equilibria at (18,18), (19,19), (20,20) and fine at (19,19), (19.5,19.5), (20,20). All are weak equilibria. A firm paying 0 beats a firm paying 1 is impossible, so asymmetric pairs drop out correctly.
- **Simultaneity:** A round's wages and notes are added to the history only after both firms answer, and each firm sees only its own notepad.
- **Parser:** Bools, duplicate keys, NaN, ±inf (including `1e400` → inf), off-grid values and out-of-range values are all rejected. Integral floats are accepted in both arms.
- **Exact arithmetic:** Every metric is a multiple of 1/64. The bootstrap quantile matches numpy's linear method exactly. The sign-flip test uses integers.
- **Screening rule:** At n=5, `p_upper ≤ .05` happens only when all five differences are strictly positive (p = 1/32). That makes the bootstrap gate redundant, which the summary already says.
- **Cache keys:** Run ID, condition and attempt number are all in the key, so the two arms can't share cached answers and dry/live are kept apart. Replay must use every key exactly once and must leave the cache files byte-identical.
- **Failure handling:** Failures shut down safely. A failed admission is recorded under the lock, transport errors and preflight failures stop the run, crashes mid-run cannot be resumed, and the partner game's data is kept.

## Remaining bugs
1. **Low – race between launch and main.** `s41_launch.launch()` releases `.writer.lock` and checks `raw/` before `main()` takes the lock again. Fix: hold one lock for the whole launch-plus-run, or move the check inside `main` under the lock.
2. **Low – mislabelled interval.** The per-arm `fine`/`coarse` summaries store a one-sample t interval under the name `paired_t_ci95`. Fix: rename it, or document it in the results file.
3. **Low – misleading figure band.** The figure shades 18–20 as "Coarse static Nash wage range" but shows nothing for the fine arm (19–20). Fix: label the band "Nash wages, both arms (fine ≥19)".
4. **Low – dead code.** In `main`, `cache.cache_only=resuming` is always False when it runs, because the resume path returns earlier. Remove it.
5. **Trivial – negative zero.** `-0.0` passes the parser and would show up as `-0.0` in the history shown to models. The payoffs are unaffected. Fix: normalise to `+0.0`.

## Before launch (preconditions, not bugs)
- **Untracked files:** All S41 sources are untracked in the session-start git status. `launch()` will refuse until they are committed and pushed with `HEAD == origin`.
- **Time:** The run needs 7.5 × the longest archived S19 block before the 05:00 UTC cutoff. I didn't check the clock, so the run may simply refuse to start.

## Known limitations (already noted, not bugs)
- **Fragile run:** One transport failure, three invalid parses on any single decision, or a codex auth refresh changing `auth.json` (which is fingerprinted on every admission) stops the run with no estimate. Since auth refresh is plausible over several hours, the chance of an abort is high.
- **Changed equilibria:** The fine grid changes the set of equilibria, not just the numbers shown. The lowest equilibrium wage moves from 18 to 19, which is below the threshold of 2.
- **Ceiling:** If the coarse arm averages above 18, a HIT is impossible. Earlier pilots saw wages around 10, so a HIT can still happen.
- **Retry selection:** Retries resend the identical prompt with no feedback, so accepted answers are filtered for being valid. Coarse histories show values like `10.0`, which might prompt more off-grid attempts and different retry rates between arms. Retry counts are reported.
- **Weak pairing:** Seeds fix firm identities and timing, not the model's samples. Sign-flip calibration needs exchangeability, n=5, and there is no correction for multiple pilots.
- **Unattested settings:** The local clock, the codex sampling and token settings, tool non-use and the provider are not attested. Only the admission journal is fsynced.

**Bottom line:** No high- or medium-severity bugs. Fix items 1–3 if the sources are reopened; otherwise record them as known issues.
