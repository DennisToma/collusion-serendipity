# S40 adversarial review (from the supplied text only)

I made no edits, ran nothing and made no paid calls. I reviewed only the text you supplied, not the raw archive.

## Remaining bugs (fix or verify before launch)

1. **The clean-clone check probably fails on the lock file.** `run()` always creates `data/s40_memory/.writer.lock`. Both `check()` and `clean_clone()` call `run()`, and `clean_clone()` then requires an empty `git status --porcelain`. Unless `.writer.lock` is committed or gitignored, the clone check will fail. `check()` already skips that file when hashing, which shows it exists in the archive directory.
2. **The launch receipt must be committed, and nothing checks that it is.** On live data, `validate()` reads `logs/s40_launch.json`. That file is written after the registration commit, so it has to land in a later commit before the clone check. Make the release step check that it is tracked, so the failure doesn't show up late as a missing file.
3. **The parser checks the range, not the wage grid.** `strict()` accepts any integer from 10 to 30. If the prompt's wage grid is coarser than every integer, an off-grid quote would be accepted and averaged. Either check grid membership against the prompt or confirm the grid really is every integer from 10 to 30.
4. **"Active" in the selection rule is never checked.** The design says "first active firm", but the code takes `rows[0]['agents'][0]` and only checks that the roster stays the same. Either check activity in round 10 or change the design wording to "first roster firm".
5. **The closing marker can be ambiguous.** `select_cases()` checks that `Notes file snapshot:` appears once, but not that `\nReturn strict JSON only` appears once after it. The replay script cuts at the first occurrence while `s40_independent.py` uses `split`, so the two would disagree or crash if it appeared twice. The risk is low because JSON escapes newlines inside strings, but one extra check removes it.

## Checked and found correct

- **Scope of the change:** the erase prompt differs from the retain prompt only in the notes array. The retain prompt is exactly the archived prompt, and both arms use the archived system prompt.
- **Unit:** the outcome is the offer minus 10. The two cases in each seed are averaged first, then the five seed blocks. No worker payment is used.
- **Route:** the fallback model name is patched for the run, so each request makes exactly one gpt-6-luna call.
- **Bootstrap:** the percentile positions match numpy's linear method.
- **Sign test:** the test counts ties as at least as extreme. With all five blocks positive, p = 1/32 ≈ 0.031.
- **Verdict rules:** HIT always takes precedence over DUD, and the unit tests cover the edge cases.
- **Contrast arithmetic:** block values are multiples of 0.5, so converting them to exact fractions loses nothing.
- **Concurrency check:** at equal timestamps an end is counted before a start, so back-to-back calls don't register as overlap.
- **Seed-block barrier:** the check works, including against the start event for the first block.
- **Headroom:** checked at registration, execution start and first admission, and the same checks run again at validation.
- **Failures:** the abort flag is set under the admission lock before the failure is logged. Every returned response is saved before parsing, and the archive never resumes.
- **Integrity:** sources are rehashed at every admission. Committed hashes are checked with `git show`, and the run's case file must be byte-identical to `data/s40_cases.json`.

## Limits you already state (not bugs)

- The source histories were chosen after seeing S37's floor results. With only five blocks, a HIT needs all five block differences positive, so the bootstrap condition adds no independent evidence.
- Because the cases start at the floor, a negative effect is hard to see whenever the retain arm also stays at 10. This doesn't break the sign-flip test, but the signed estimate can't move evenly in both directions.
- Erasing the notes also changes prompt length, how complete the information is, and agreement with the system's "complete notepad" promise. The public history still shows the same actions, so a null result can't rule out a role for memory.
- The rival firm isn't simulated, so the outcome is an offer, not a realized wage.
- Temperature and max_tokens aren't enforced by the CLI. The reported model name only shows the requested route, not the model actually served.
- If the usage-log write in `llm.chat` fails, a returned output can be lost before the script sees it. The run then stops with no effect estimate.
- An auth-token refresh changes `auth.json` and will abort the run (an accepted risk). The fingerprint also depends on the working directory, so the source and replay "fingerprint equal" flag may come out False even with identical CLIs.
- In-flight calls can finish after 03:30, and a slow run is an operational failure.
- `s40_independent.py` only redoes the arithmetic from the raw rates. It isn't independently written, and it doesn't recheck schedules or hashes.
- The two-firm prompt context and five seeds limit how far the result transfers. There is no claim of agreement, intent or coordination.

**Verdict:** the design is sound for its stated narrow claim. Fix bugs 1 and 2 before release, and settle 3 and 4 before launch, because they change what gets measured or what the design says.
