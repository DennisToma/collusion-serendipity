# S47 adversarial review: supplied text only

I made no edits and no paid calls. The raw archive (`responses.jsonl`, `requests.jsonl`, `accepted.jsonl`, `execution.jsonl`, `schedule.json`, the launch receipt) wasn't supplied. So everything below is rebuilt from the 20 per-case quotes in `results/s47_example.json`, and I can't vouch that those quotes match the raw responses.

## Independent reconstruction: all checks match

- **Block means (15 cells):**
  - Low example: 10, 10, 10, 10, 10.5 (the only non-10 offer is 24924_control_B at 11).
  - High example: all five blocks are 10.
  - High minus low: 0, 0, 0, 0, −0.5. Mean is **−0.1**.
- **Bootstrap, all 3125 ordered draws:** the draw mean is −0.1 × (number of times the −0.5 block is picked). Sorted ascending, the draws with 5, 4 and 3 picks fill positions 0–180. The 2.5% position is 78.1, which gives **−0.3**. The 1024 zero-pick draws fill positions 2101–3124, so the 97.5% position (3045.9) gives **0**. Result **[−0.3, 0]**, which matches.
  - The low arm by the same method gives [10, 10.3]; the high arm gives [10, 10]. Both match.
- **Paired t interval:** SD = √0.05 = 0.2236 and SE = 0.1. With a t multiplier of 2.776 (4 degrees of freedom) the interval is **[−0.378, +0.178]**, which matches.
- **Sign flips, all 32:** the possible signed sums are ±0.5, sixteen of each. That gives upper p = 32/32 = **1**, lower p = 16/32 = **0.5** and two-sided p = **1**. All match.
  - The low arm's upper p of 1/32 = 0.03125 is also correct. It is a generic test against zero, as the report already says.
- **Verdict:** the mean is ≤ 0, so it is **DUD** by the registered rule. Correct.
- **Secondary counts:** offers at 0 are 0/0. Matches to the archived offer are 9 (low) and 10 (high). Correct.

## Design and code checks: no bugs found

- **Only the example numeral differs.** The two prompts are built identically apart from `{"rate": 0, …}` versus `{"rate": 20, …}`. The warning text is identical in both. The test checks that both prompts are equal once the example is swapped for a placeholder. The one-character length difference is acknowledged in the design.
- **Payoff table:** it has 21 ascending rows with the right share rule (0 below the top rival offer, split equally on ties). The test checks it against the simulator's own payoff function for every possible rival combination. Rival offers come from round 9 and equal the last public quotes; the quote offset is 0.
- **Case selection:** it is the first agent in the sorted assigned pair, which is the same as "first incumbent alphabetically". It does not depend on actions, and it reproduces each case's previous profit and labor share and its archived round-10 action.
- **Unit:** every output labels the outcome as a focal offer, not realized pay. The figure title says so too.
- **Transport:** `retries=1` plus `_codex`'s deduplicated model list means one attempt per call. Strict parsing rejects booleans, floats, NaN, duplicate keys and code fences.
- **Integrity:** registration happened at 05:13:15 UTC, giving 77 minutes of headroom before the 06:30 cutoff. Its source hashes equal the config hashes, and the commit equals the remote. I could not check the actual call times, concurrency or barriers because the logs weren't supplied.

## Gaps and acknowledged limits (not bugs)

1. **`source_fingerprint_matches: false`.** The local inputs to the Codex command-line tool changed between S42 and S47, although the version is the same. `results/s47_summary.md` discloses this, but the S47 paragraph in `REPORT.md` doesn't. That is a minor disclosure gap.
2. **Unfinished steps.** There is no `logs/s47_remote_clean_clone.json`, and the S47 results are uncommitted. The fresh origin-clone reproduction the design requires is still pending.
3. **Responses barely vary.** 19 of 20 fresh offers equal the archived 10, even though the table shows that offering 11 gives a higher one-round profit. With so little variation, the experiment can only detect a large effect. The DUD rules out the registered two-unit increase on these draws. It does not show equivalence or a smaller effect, and it says nothing about anchoring or any other mechanism.
4. **Not separable.** The numeral's length, position and salience change together with it.
5. **Limits already stated in the design:**
   - Cases were chosen post hoc, and they are the same ten histories used in S43/S44.
   - There are only five blocks.
   - The fresh outputs are uncontrolled model draws on one model.
   - The model's identity and settings are unattested, and the temperature and token settings aren't sent to the CLI.
   - The independence script was written by the same author.
   - Tools are restricted by instruction only, not disabled.

**Bottom line:** I found no bugs. The DUD verdict follows correctly from the supplied quotes. Before release, complete the origin-clone reproduction and add the fingerprint mismatch to the S47 paragraph in `REPORT.md`.
