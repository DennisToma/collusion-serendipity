# S27 independent adversarial review

**Scope and method.** I made no edits and no model calls. This session has no shell, so I could not open raw `game_*.json`, `requests.jsonl` or `responses.jsonl`, and I could not run the tests. I did the recomputation by hand. The inputs were the per-game cells in `results/s27_concentration.json` and the code as supplied.

## Independently verified (PASS)
- **Primary:** In the three arm, partner Y approvals per seed are 0, 0, 1, 1, 1, which is 3/40. In the two arm they are 3, 1, 1, 2, 3, which is 10/40. The per-seed differences are 3, 1, 0, 1, 2 out of 8, so the mean is **7/40 = 0.175**.
- **All 3125 bootstrap samples:** I used the counting polynomial (1+2x+x²+x³)⁵ over the per-block numerator draws. Cumulative counts from the bottom are 1, 11, 56, 181, so linear quantile indices 78.1 and 3045.9 give S=3 and S=12. That is **[3/40, 3/10]**, which matches.
- **32 sign flips:** Only the all-positive pattern reaches 7. The zero block counts twice, giving upper p = **2/32 = 0.0625**. Two-sided is 4/32 and lower is 1.0, both matching.
- **Paired t:** The standard deviation is 0.14252 and the half-width is 0.17696, giving **[−0.00196, 0.35196]**, which matches.
- **Verdict:** The mean is below 0.25, so it cannot be a HIT. The mean is above 0.05 and the upper bound 0.30 is at least 0.25, so it is not a DUD either. **ODD is correct.** The pair-internal gate is 7/10 > 0 but does not matter.
- **Secondary metrics:** Pair-internal bonus equals 7 + b/2 per game (X approval 6+1, Y approval 6−2), which reproduces every cell. Pair-total and organization-loss differences match, and the loss sign test gives 8/32 = 0.25. Pair-total bonus equals pair-internal bonus in the two arm, as expected.
- **Stage economics:** `outcome` gives Y approval a reviewer net of −2 and X a net of +1. Mutual Y approvals give each 4, and unilateral rejection saves 2. Pair-directed payoffs and per-agent type schedules do not depend on the arm. The pair is drawn with `Random(seed).sample` and tasks come from `s27-tasks-{seed}-{agent}`.
- **Simultaneity:** Prompts use only completed `rows`. Notes are appended to `chat` after the round loop, and the snapshot is checked as `round<=t`, which equals 2t entries. Reasoning is never replayed.
- **Replay integrity:** Replay consumes every key exactly once, keys and requests are hashed, the bytes are unchanged, and live calls are patched to fail.

## Remaining bugs and gaps
1. **Medium (process):** `data/s27_concentration/`, `results/`, the REPORT edits and several logs are uncommitted, according to the session-start git status. DESIGN requires a results commit/push and a clean-clone reproduction. Neither is shown as done for S27, so don't treat the release as final until both are.
2. **Low (test gap):** `test_only_roster_count_schema_change_at_empty_history` only asserts that the *system* prompts are equal after edits. For the user prompt it only checks whether `"B"` is present. The claim "all other instructions identical" is never asserted for the user prompt, though reading the code it holds: only the status roster and the review schema differ. The `.replace('six directed', …)` call never matches anything. Fix: assert the user prompts are equal after normalising the roster and schema.
3. **Low (labelling):** In the JSON, the per-arm `paired_t_ci95` intervals are actually one-sample t intervals, not paired ones. Rename them or add a note.
4. **Low (independence):** `s27_independent.py` reads the active roster from the recorded rows instead of deriving it from the condition, and it reimplements the same rule code. It is a partial check, not a fully independent derivation. `validate_game` covers the roster, though.

## Acknowledged limitations (correctly disclosed, not bugs)
- The arm contrast bundles outsider interaction, workload, schema and history size, and income dependence on the partner (the partner is the only income source in the two arm).
- The pair-internal gate is mechanically tied to the primary metric.
- Organization loss and pair-total bonus are not like-for-like across arms.
- n=5 means p ≤ .05 needs all five block differences strictly positive.
- Uncontrolled model draws, tool non-use not verified, and client-side-only timestamps.
- Approvals do not show agreement. The report wording ("descriptive", "ODD", no promotion) fits this.

## Unchecked
- Raw cache, requests and timestamps; the 60-second pairing and overlap checks; the deadline and admission ordering in the actual data.
- `logs/s27_test_suite.json`, `s27_release.json`, `s27_final_opus.md`, and whether a final Codex critic was run.
- The figure and the clean-clone run.

## Final verdict
The **ODD** verdict for S27 and every reported number I could recompute are correct. I found no scientific or statistical bug. Commit, push and reproduce from a clean clone before calling S27 final. The bootstrap interval excludes zero, so the report should keep stating that it is descriptive and does not override the frozen rule (p = 0.0625, mean < 0.25).
