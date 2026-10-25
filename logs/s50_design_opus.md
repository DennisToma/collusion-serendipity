# S50 adversarial review (based only on the text you supplied)

**Verdict:** I found no blocking code bug. The design is sound enough to register once you have checked the items in sections 1 and 2.

## 1. Bugs and design defects to fix or check before registering

1. **The user prompt may still imply more rounds.** Your checks confirm the system prompt has exactly one copy of the hidden-horizon sentence. Nothing checks the user prompt, though. It might contain text like "round k", "notes are read next round" or "over many rounds". The `note` field is also still required, which conflicts with the notice's "no later note reads". Fix: add a canary that searches `original_prompt` for continuation wording, or report the conflict in the write-up. Without one of these, "only the horizon sentence changes" is not fully true for the content the model sees.
2. **Most of the HIT and DUD gates do no work at n=5.**
   - HIT: the sign-flip test only passes if all five block differences are above zero. Then every block is at least 0.5, so the mean ≥ .25 and bootstrap-lower > 0 gates follow automatically. HIT is simply "5/5 blocks positive."
   - DUD: block means come in steps of 0.1, so "mean ≤ .05" really means "mean ≤ 0."
   - State both equivalences in the design so readers don't count three separate tests.
3. **A failed registration attempt permanently blocks the pilot.** `registration()` runs while `new` is true. If it fails (say HEAD ≠ remote because of a race with the wrapper's push), `failure.json` is written, and that blocks the pilot forever even though no model call was made. The deadline makes this costly. Either accept it explicitly in the design or move registration ahead of the failure-writing scope.
4. **The clean-clone reproduction may fail.** `validate()` → `select_cases()` reads `data/s29_notepad/raw/*.jsonl`, and `clean_clone` rebuilds from origin. If those raw files are gitignored (CLAUDE.md says to gitignore large caches), the reproduction will fail. I couldn't check this because the raw archive wasn't supplied.
5. **Small permissive edge in the concurrency check.** When timestamps are equal, the sweep sorts −1 before +1, so calls that touch end-to-start pass. This is harmless under a 2-worker pool; just know the check isn't strict at the boundaries.

## 2. Verified correct (from the supplied code)

- **Selection uses only task status.** The last primary row index (rounds 3–10) with the partner not passed is chosen. The independent script rebuilds this from the S29 task RNG, the archived approval is checked against the parsed source response, and public-history length equals the turn.
- **The intervention is a single replacement** (one occurrence, verified to undo cleanly). Prompt, backend, model, tier and settings are identical across the two arms.
- **The response parser is strict:** one partner key, an actual boolean, no duplicate keys, no NaN.
- **There is exactly one model call per decision:** `retries=1`, and `fixed_model` collapses the codex list to a single model. Responses are fsynced before parsing, any failure aborts everything, and the external receipt makes the launch one-shot.
- **Block statistics are right:** 3125 bootstrap draws match numpy's linear percentiles; the exact rational bounds use doubled-integer sums over 10; the 32 sign flips include the identity; exact-zero blocks create ties, which correctly block a HIT.
- **The stage payoffs check out:** mutual approval of TYPE-Y gives 6 − 2 = 4 each, and rejecting saves 2 whatever the incoming review is.

## 3. Limitations you already acknowledge (adequately disclosed)

- The final-round notice changes several things at once: the endpoint, the common-knowledge statement, and the removal of "over many rounds", plus wording, length and salience.
- Only the focal agent is rerun. The partner never sees the notice and no actual final-round game is played. Earlier histories were generated under the hidden horizon.
- Picking each employee's last opportunity skews cases toward late rounds, which mixes in end-of-game history effects.
- If the fresh hidden baseline vanishes, the result reads DUD but is uninformative. I'd suggest labelling a hidden approval count of 0/10 as "baseline floor; DUD uninformative" in the summary, not just in the limitations prose.
- Temperature and max-tokens aren't really passed through codex. Provider identity, tool non-use and the S29 runtime fingerprint are not attested.
- One model, 20 draws, no confirmation run, no claims about mediation, long-run effects or collusion.

**Bottom line:** Items 1 and 4 are the substantive risks. Item 1 bears on whether "only the horizon sentence changes" is true. Item 4 bears on whether the release can be reproduced. Items 2, 3 and 5 are disclosure or operational fixes.
