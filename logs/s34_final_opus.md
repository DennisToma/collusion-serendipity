**S34 adversarial review**

My Bash calls returned no output, so **I could not read the raw `game_*.json`, `requests.jsonl` or `responses.jsonl` directly.** The arithmetic below is recomputed by hand from the per-game counts in `results/s34_salience.json` and the code shown. It is not an independent raw re-read. Treat raw-level claims as unchecked by me.

**Arithmetic (all reproduced)**
- **Y approvals out of 8:**
  - Plain, seeds 24680–84: 2, 3, 2, 1, 0 → 8/40 = 0.200.
  - Flag, same seeds: 0, 3, 1, 2, 1 → 7/40 = 0.175.
  - Differences: +2, 0, +1, −1, −1 → mean 1/40 = 0.025.
- **Bootstrap over all 3125 samples:** the per-block differences take the values −1 (weight 2), 0, 1 and 2 (weight 1 each).
  - Low end: 32 samples sum to −5 and 80 more to −4. Ranks 78 and 79 both fall at −4/40, so the lower bound is **−0.100**.
  - High end: 146 samples sum to 6 or more and only 61 to 7 or more. Ranks 3045 and 3046 both fall at 6/40, so the upper bound is **0.150**.
- **Sign flips (32):** 8/16 × 2 = **p = 0.5**. Only 3 of 5 blocks are positive, so the five-positive gate fails.
- **Paired t:** sd 0.16298, se 0.07289, t₄ = 2.7764 → **[−0.1774, 0.2274]**.
- **Verdict:** 0.025 ≤ 0.05 and 0.15 < 0.25, so **DUD** is correct under the frozen screen.
- **Secondaries follow from the actions:** pair bonus is (56 + 4·Y)/8 and organization loss is 10·Y/8. Both match the results file.
- **Headroom:** 1.5 × 5 × 156.728 = 1175.46 s required versus 3577.37 s remaining. Commit time precedes launch, which precedes first admission.

**Code checks (no bugs that change the result)**
- **Economics:** `outcome` never reads the reports beyond validating them. The test covers all 4 types × 4 actions × 4 flag combinations.
- **Simultaneity:** both agents get prompts built from the same `rows`/`chat`. Notes are added to `pending` only after both decide. The independent check `round ≤ ti` matches, because notes are stamped `t+1`.
- **Privacy:** `observable_row` drops `report`. The prompt history has no report field. Reasoning is never replayed.
- **Arm-specific schema:** the parser requires exactly the `report` key in flag and forbids it in plain. Shared-note text appears in both arms; the test confirms the only differences are the flag paragraph and the field.
- **Failure handling:** aborts are recorded at admission time, there is a deadline check before admission, exhausted parsing writes a failure marker, and there is no partial estimate.

**Remaining issues**
1. **Medium (interpretation): the flag was never used.** The flag arm's report count in rounds 3–10 is **0/80**. As a field it was inert, not just payoff-inert. That bounds any "salience of reporting" reading. REPORT.md should state it plainly rather than leave it as a 0.000 row. I could not check warmup rounds.
2. **Medium (release): unconfirmed commit and links.** At session start, the S34 data, results, figure and logs were untracked or modified. The design's required commit/push and clean-clone reproduction is unconfirmed. `results/s34_summary.md` links `logs/s34_review_disposition.md`, which was not in that file list and may be a broken link. Verify both before calling S34 released.
3. **Low: "one transport invocation" not verified.** `llm.chat(..., retries=1)` is asserted at the call site only. Whether `retries=1` means one attempt inside `llm.py` is not shown.
4. **Low: hardcoded note count.** `notes.written=100` is a constant. It is only indirectly justified by `len(notes_file)==20` per game.
5. **Low (cosmetic):** the second deadline check in `TenderCache.call` and the `dry` branch in the final source loop are redundant. "plain baseline20% limits…" should read "the plain baseline of 0.20 caps any reduction below the 0.25 HIT threshold".

**Acknowledged limitations (not bugs)**
- With a baseline of 0.20, a HIT was impossible by construction.
- n = 5, with no equivalence or multiplicity claims.
- Wording and schema effects are bundled.
- Provider execution, effective configuration and tool non-use are unattested.
- Codex does not enforce sampling settings.
- Approvals do not verify agreements.

**Unchecked by me:** the raw review decisions themselves, the 200 response bindings, actual flag values in warmup, request-time chronology, byte-identical replay, the test suite, and the remote state.

**Bottom line:** DUD, and the statistics are correct. The scope should add that the flag was never used in the primary rounds (0/80), and release status still needs confirming.
