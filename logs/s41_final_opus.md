# S41 adversarial review

I had no local repo access in this session (only the Drive/Docs connectors), so everything below is checked against the files you pasted. I did not re-parse the raw `game_*.json` or `responses.jsonl` files. I rebuilt the statistics by hand from the per-game metrics.

**Verdict:** I found no bug that changes the frozen result. **ODD is correct.**

## Arithmetic, recomputed by hand
- **Paid wage, rounds 3–10:**
  - Coarse: 10, 6.125, 10, 10, 10 → 9.225.
  - Fine: 10, 10.4375, 10, 10.5, 10 → 10.1875.
  - Block differences ×64: 0, 276, 0, 32, 0. Mean 77/80 = 0.9625. All match.
- **Bootstrap over all 3,125 resamples:** 3⁵ = 243 resamples use none of the nonzero blocks, so the 2.5% position (78.1) gives a lower bound of 0. For the upper bound, the positions 3045 and 3046 are the 80th and 79th values from the top. The top values have counts 1, 5, 15, 10, then 60 at 860/320. Both positions land on 860/320 = **43/16 = 2.6875**. Matches.
- **All 32 sign flips:** a sum of at least 308 needs both nonzero blocks positive. The three zero blocks can take either sign, so 8/32 = **0.25**. Lower-tail p = 1 and two-sided p = 16/32 also match.
- **Paired t:** SD 1.8852, SE 0.8431, t₄ = 2.7764, giving **[−1.378, +3.303]**. Matches.
- **Screening rule:** the mean is below 2, so it is not a HIT. The mean is above 0 and the upper bound is at least 2, so it is not a DUD. That leaves **ODD**. The claim that at n=5 a HIT is the same as "mean ≥ 2 and all five differences strictly positive" is right: p = 1/32 is impossible if any difference is zero or negative.
- **Secondary outcomes:** firm profit is exactly the complement of the wage. The offered-wage p of 1/32 is correct and is correctly not promoted.

## Economics, prompts and visibility
- Checking every unilateral deviation by hand, coarse play has equilibria at 18, 19 and 20, and fine play at 19, 19.5 and 20. Pairs with different wages are never equilibria.
- Both arms use the same payoff formula, and the result is reported as fine minus coarse.
- The two prompts differ only in the wage-increment sentence. The user schema is identical.
- Both arms use the same parser logic, and the independent parser matches it. Integer-valued floats are accepted, bools are rejected, and `1e999` is rejected by the range check.
- Wages are stored as floats and negative zero is normalised. The terminal-wage diagnostic is computed the same way in both arms.
- Notes are self-only through the author filter. Current-round notes and wages are added to history only after both firms have chosen, so the moves are simultaneous.

## Failure handling and fingerprint guards
- Every new request goes through one lock. There is one transport attempt per request and an abort is permanent.
- The CLI fingerprint baseline is deep-copied, so it cannot change during the run.
- A dispatch receipt is written before the first request, and the code is checked against what is stored in git.
- Replay uses the cache only, consumes every key exactly once, and checks that the files are byte-identical afterwards.

## Remaining issues
1. **Medium: the archive is not committed yet.** At session start, git status showed `data/s41_ticksize/`, `results/s41_ticksize.json`, `logs/s41_*` and `scripts/s41_publish.py` as untracked, while REPORT.md already cites them. So the fresh-origin-clone check cannot have passed yet. **Fix:** commit and push, re-run the release script in a fresh clone, and only then keep the REPORT row.
2. **Low: stage regret is grid-dependent.** At the same tied (10,10) profile, regret is 4 on the coarse grid and 4.5 on the fine grid. So the −0.15 difference mixes the grid itself with behaviour. **Fix:** add a footnote, or report regret on a common grid.
3. **Low: the result rests on one block.** Three of five blocks are identical (split at 10). The +0.96 comes mostly from block 24881, where the *coarse* arm fell to 6.125 (final-round wage 4), plus two +0.5 steps in the fine arm. **Fix:** say this in the REPORT row, as was done for S07.
4. **Low: the runs look nearly deterministic.** Several games have identical metric vectors across seeds, such as fine regret of 4.53125 in three blocks. This suggests the requested temperature isn't taking effect. If so, the blocks are close to replicates and the resampling bounds overstate how informative they are. **Fix:** add this to the limitations.
5. **Disclosure:** `llm.py` fixes Codex reasoning effort at `low`. The source hash covers this, but neither DESIGN nor the REPORT mentions it.

## Limitations the project already states
- The action set, equilibria and numerical salience change together.
- Sampling settings and token limits aren't enforced, and the provider is not attested.
- The admission journal is only partly fsynced; tool restrictions are instruction-only.
- The sign-flip test relies on an exchangeability assumption, and n=5 with descriptive intervals.
- Both arms sit far below the Nash range at about 10, but low wages alone don't show coordination.

## Not checked
- Raw rate choices and the game JSON files.
- `s41_economics.py`, `s41_exact_check.py`, `s41_release.py`, `s41_publish.py`.
- The test run, figure contents, gitignore and repo size, and fresh-clone reproduction.
