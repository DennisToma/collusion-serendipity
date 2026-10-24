# S09 adversarial review: memory-erasure replay

I had no shell or file-read tools in this session, so I could not open the raw games, `raw/*.jsonl`, `.gitignore`, `llm.py`, `scripts/s02_analyze.py` or git state. I recomputed everything from the per-game records in `results/s09_replay.json` and checked them against the pasted code. I made no edits and no model calls.

**Bottom line:** the DUD verdict follows the registered rule, and every number I could check matches. No code bugs remain that would change the result. The remaining problems are about evidence (items 1–2) and claim wording (items 3–4).

## Numbers I recalculated (all match)

- **Primary measure (pair output per firm, rounds 7–12):**
  - Retain per seed is [6, 5.5, 6, 6, 6], mean 5.9. Erase is 6.0 in every block.
  - Erase minus retain is [0, .5, 0, 0, 0], mean **+0.100**. Per-block numerators are [0, 6, 0, 0, 0] and 6/60 = 0.1.
- **Sign-flip test:** the null sums are ±6, so the upper p is 16/32 = **0.5** and the lower p is 1.0.
- **Paired t interval:** sd = √.05, se = .1, and t(.975, 4) = 2.7764, giving **[-0.178, +0.378]**.
- **Bootstrap interval:** the number of times the 0.5 value is drawn is binomial(5, .2), and P(k ≤ 3) = .9933, giving **[0, 0.3]**. The round-7 interval works the same way: [0, 0.6], mean .2, mean absolute difference .2.
- **Secondary outcomes:**
  - Paired t intervals all match: price [-.752, .419], pair profit [-1.560, 1.160], outsider profit [-4.523, 2.189], outsider output [-.126, .059], message words [-8.237, -4.096].
  - Bootstrap bounds for retain, price, pair profit and outsider profit also match.
  - I did not recompute the message-words bootstrap interval.
- **Per-game internal consistency:** seed 24081 retain fits the pair producing 5 for three rounds and then 6: price 13, pair profit 38, outsider profit 42. Seed 24083 retain fits the outsider producing 7 in one round: pair profit 35, outsider 35.83, price 11.83.
- **Verdict:** 0.1 falls in (−1, .25], so DUD. 183 cached responses = 180 decisions + 3 retries.
- **Timing:** the earliest call was 17:18:36.692, 0.6 s after the recorded push. The last completion was 17:30:18, before the 17:48 deadline. REPORT is stamped 17:31.
- **Treatment timing in code is correct.** The erase filter `round > 6` removes every message sent in rounds 1–6, including the round-6 message the original S07 agents read at round 7. At round 6 (0-indexed) the chat holds only messages from rounds ≤ 6, delivery happens after all actions, and the outsider's prompt is identical in both arms.

## Remaining issues (not covered by earlier fixes)

1. **The registration-before-calls evidence is thin.**
   - The push proof is a self-written `logs/s09_registration_push.json`, and in the session snapshot it was untracked.
   - The margin before the first call is about 0.6 s.
   - Fix: commit the log and cite independent evidence, such as the remote's push timestamp for 4474418.
2. **None of the S09 outputs were committed in the snapshot.** `data/s09_replay/`, `results/`, the figure and the logs all showed as untracked, while REPORT.md already links to them.
   - Analysis and release both need `raw/responses.jsonl` and `raw/requests.jsonl`.
   - Check that `raw/` is not gitignored. If it is, the "cache-only replay" claim can't be reproduced from the repo.
   - Note that after 17:48 the generator can never make a new call, so "Reproduce: `sim.replay`" only works from the committed cache. The docs should say so.
3. **"Future messages may restore / repair missing information" is wrong for this design.** This wording appears in DESIGN_S09, the summary and REPORT.
   - Both firms are erased together, so after round 7 neither one holds the erased content.
   - New messages can only rebuild coordination from the public history, not restore what was erased.
   - Reword to "agents can renegotiate from public history." The current wording makes the effect sound larger than it could be.
4. **"DUD" overstates what was learned.**
   - The S07 neutral continuations (pair output about 5.8) were seen before S09 was designed, so the retain arm was expected to sit near Nash.
   - A HIT needed erase output of at least about 6.9 in all five blocks, which is above the static best response. The screen had almost no chance of firing.
   - 4/5 blocks show exactly zero difference, and erase output appears to be exactly 6 throughout. I inferred that from means of 6.0, price 12.0 and profit 36.0 with collapsed intervals; please confirm from the raw games.
   - REPORT does mention the 6.9 requirement, but the table label should read like S04's: "DUD (screen had no headroom; uninformative)." It should not read as evidence against an effect of message memory.
5. **Minor: the "independent" checker isn't fully independent.** `s09_independent.py` reuses the same RNG seed and draw order, so it confirms the computation rather than checking it by a separate method. Call it a "recomputation check."
6. **Minor: the one consistent effect is a manipulation check and could be named as one.** Message length fell by 6.2 words in all 5 blocks, which shows the erasure changed agent behaviour. It is correctly not promoted. Saying this explicitly would also show the null result on output isn't caused by the treatment failing to land.

## Already acknowledged limitations (not counted as bugs)

- n = 5, using prefixes already observed, with no independent replication.
- The sign-flip test assumes the two arms are exchangeable.
- Bootstrap and t intervals are fragile, and the zero-width intervals mean nothing.
- The empty-inbox cue can't be separated from message meaning.
- No agreement or execution labels, so no claim of collusion or profit.
- The read-only sandbox does not prove agents couldn't read S07 files. Any such leak would only push results toward the null here.
- The deadline doesn't bound transport retries already in flight.
- The Codex design review finished after launch, though before anyone looked at the results.
- The final-round message counts include messages that were never delivered.
- The retain arm's 3 retries mean the two arms were filtered for valid output slightly differently.
