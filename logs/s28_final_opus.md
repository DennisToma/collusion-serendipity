# S28 review: no blocking bug found. The frozen ODD verdict is correct, but publication isn't complete yet

I had no shell in this session, so I couldn't read files or run anything. I checked only the text you supplied. I recomputed the statistics by hand from the per-game counts in `results/s28_payoff.json` and `results/s28_summary.md`, not from the raw `game_*.json` decisions or the cache. That raw recomputation is still unchecked.

## Recomputed by hand: all match
- **Primary counts:** prose Y approvals per block are 1, 3, 0, 1, 2 (7/40 = 0.175). Table counts are 1, 0, 1, 1, 0 (3/40 = 0.075). The differences in eighths are [0, 3, −1, 0, 2], so the mean is **0.100**.
- **All 3125 bootstrap samples:** I counted the sums of five draws exactly.
  - Lower bound: positions 78 and 79 (zero-based) both fall in S = −2, which holds positions 51–135. That gives **−2/40 = −0.050**.
  - Upper bound: positions 78 and 79 counted from the top both fall in S = 11, which holds top positions 36–85. That gives **11/40 = 0.275**.
  - The per-arm bounds also match: prose [3/40, 3/10] and table [1/40, 1/8].
- **All 32 sign flips:** the nonzero differences 3, 1 and 2 give null sums of ±6, ±4, ±2 and 0 (twice), each repeated four times because of the two zero blocks. Upper p = 8/32 = **0.25**, lower p = 0.875, two-sided p = 0.5.
- **Paired t:** SD = 0.205396, SE = 0.091856, t(0.975, 4) = 2.776445, giving **[−0.155033, 0.355033]**. The prose one-sample bound [−0.00196, 0.35196] also matches.
- **Verdict:** 0.1 is below 0.25, so it isn't a HIT. It isn't a DUD either: the mean is above 0.05 and the upper bound (0.275) is not below 0.25. So it's **ODD**. The internal bonus is exactly 4× the primary and organization loss exactly 10×, as expected since every TYPE-X submission was approved (pair_good = 1 everywhere).
- **Economics:** across all 16 stage outcomes, approving X gives the reviewer +1 and the author +6, and approving Y gives −2 and +6. Every row of the role table matches `outcome()`. A pair gains 7 per X approval and 4 per Y approval.
- **Timing and notes:** current-round notes and actions are held back until both employees submit, and notes are stamped round t+1. Both arms see both notepads, and the dry-run canary confirms 2t notes per prompt. At empty history the only prompt difference is the table appended to the system prompt; the user prompts are byte-identical.

## Remaining bugs
1. **Medium (process):** the release steps the design requires are not done.
   - `data/s28_payoff/`, `results/s28_*` and the logs are still uncommitted.
   - The commit/push and clean-clone check have not happened.
   - The disposition says the final Codex and Opus reviews are "pending", yet REPORT.md already presents S28.

   **Fix:** settle both critic reviews first, then commit, push and run `s28_release.py` from a clean clone.
2. **Low:** `s28_review_disposition.md` says the Opus methodology review is "pending" and then later records it as done. **Fix:** a dated note in a separate file (the frozen sources stay untouched).
3. **Low:** the independent checker only checks for phrases in the system prompt. It never confirms that prose system prompt + table = table system prompt across the actual saved requests; that equality is shown only for empty history in the test. Canonical replay covers this indirectly. **Fix:** a companion check that rebuilds the prompt from the stored strings.
4. **Low (dead code):** the checker's outsider branch looks for `'private work notepad'`, but the prompt says `'work notepad'`, and `partner` would be out of date there. This branch can't run with two-person teams.
5. **Low (scope):** `invalid_attempt_retries` counts attempts greater than 0. It equals the number of rejected outputs only because running out of attempts aborts the whole pilot. This is harmless here (0 retries) but worth knowing.

## Acknowledged limitations (not bugs)
- The table bundles several things (repetition, detail, format, role salience, length), so no arithmetic-error mechanism is shown.
- n = 5 with uncontrolled model draws. There is no profit gate, by design.
- Bonus and organization loss follow mechanically from the approval counts.
- The launch lock is briefly released between the launcher and `main()`; later steps still refuse to start if evidence already exists.
- Tool non-use and provider timing can't be verified.
- Any edit to the 18 frozen sources breaks the gate. This is intentional.

## Scope check
REPORT.md and the summary claim only ODD, show signed effects, rule out mechanism, agreement and pooling claims, and keep S29 separate. That matches the design. The baseline isn't sparse (7/40), so that design caveat doesn't apply here.

## Not checked
- The raw game JSON, cache, request file and replay.
- `s28_present.py`, `s28_release.py`, `s28_reviews.py`, `llm.py` and `legality.py`.
- Running the tests, inspecting the figure, and the 23:15 completion time.

**Final: ODD stands. Nothing found changes the numbers or the verdict. Finish the release and the final critic dispositions before calling S28 published.**
