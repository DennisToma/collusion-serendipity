# S50 adversarial review

I worked only from the supplied text: no raw archive, no edits, no paid calls, and I did not read other critics' reviews. I rebuilt the numbers from the 20 booleans in the `results/s50_terminal.json` case table. Those booleans are the stand-in for the 20 raw responses, which I could not check myself.

## Independent reconstruction: all numbers match
- **Block cells (15):** hidden [0, 1, 1, 0, 0] gives 0.4. Final [0, 1, 0, 0, 0.5] gives 0.3. Contrast [0, 0, 1, 0, −0.5] gives 0.1. Approval counts are 4 and 3. Matches with the archived actions are 9/10 hidden and 6/10 final.
- **Bootstrap (3125 ordered draws):** I counted multinomial outcomes on the half-unit scale. For the contrast, ranks 78/79 from the bottom fall in S=−3 (cumulative counts 1, 16, 106), giving −0.3. Ranks 78/79 from the top fall in S=6 (cumulative counts 16, 21, 111), giving 0.6. Hidden is [0, 0.8] and final is [0, 0.7]. All agree.
- **Sign flips (32):** the contrast takes values ±2 ±1 on the doubled scale, 8 flips each. Upper p is 16/32 = 0.5, lower 0.75, two-sided 1.0. Hidden gives 0.25/1/0.5 and final gives 0.25/1/0.5. All agree.
- **Paired t intervals:** contrast and hidden SD = √0.3 and final SD = √0.2, with t(4) = 2.776. This reproduces all three intervals.
- **Verdict:** the mean is below 0.25 and the bootstrap upper bound of 0.6 is at least 0.25, so the result is ODD. That is correct.

## Bugs (none change the result)
1. The response `model` field is set by `_codex` to the model that was requested, not the one that served the call. So `assert response['model']=='gpt-6-luna'` always passes and proves nothing. Provider identity is acknowledged as unattested, but the check should not be presented as route verification.
2. `llm.py` appends to `LOG` from two threads without a lock. This is a cost log, not scientific data.
3. When the single attempt fails with `retries=1`, the code still sleeps 5 s before raising. It never retries, so this is harmless.
4. The release and remote-clone receipts are missing. The git snapshot has no `logs/s50_release.json` or `logs/s50_remote_clean_clone.json`, and the results, REPORT and data are uncommitted. Post-live steps the design registered (release check, commit/push, origin-clone reproduction) can't be confirmed yet.
5. I could not see `scripts/s50_reviews.py`, `scripts/s16_reviews.py` or `sim/notepad.py`, and the source-hash list in S29's `config.json` was not supplied.

## Integrity checks that hold
- **Selection** uses only task status: `max t∈[2,9]` where the partner did not pass, with TYPE-Y asserted. The verifier rebuilds the task schedule from the seed RNG without importing the generator. Each source prompt is regenerated exactly with `prompts()`, and the archived boolean matches the archived action.
- **The intervention** is a single replacement inside the system prompt (`count==1` asserted). The user prompt and request settings are byte-identical across arms.
- **Parsing** is strict: unique keys, exactly one target, a real boolean, and no NaN. The run aborts with no retry. Block barriers, opposite view orders across the two contexts, and the concurrency sweep are all validated. Registration was at 05:25 UTC, giving more than 20 minutes of headroom.

## Acknowledged limitations (handled correctly)
These are the focal-only rerun, the leftover next-round/note cues, the notice bundling endpoint information with common knowledge and salience, temperature and max-tokens being ignored by the CLI, the source runtime not being fingerprinted, the HIT gate reducing to 5/5 positive blocks, and DUD reducing to mean ≤ 0.

## Interpretation risks to keep out of the write-up
- **The fresh baseline did not vanish:** hidden is 4/10 and reproduces 9/10 archived actions. So this ODD result is informative about this baseline, not undermined by a missing one.
- **The effect is not robust:** only 3 cases changed between arms. The whole positive contrast comes from one block (24482: both approvals turned into rejections), and block 24484 moved the opposite way. With one draw per context, a disclosure effect can't be separated from sampling noise.
- **Final-arm approvals are against the reviewer's own interest:** in a known last round, approving TYPE-Y pays the reviewer −2 versus 0 and has no future benefit. The 3/10 final approvals are therefore notable. They must not be explained after the fact (as distrust of the notice, note commitments or altruism) or promoted. The current text correctly avoids doing so.
- **The report's claims are appropriately limited:** ".25 unresolved", no foresight or mediation claims, and only the paired contrast treated as primary. I found no overclaim.

**Recommendation:** keep the ODD verdict as written. Finish and record the release and origin-clone receipts before calling S50 final.
