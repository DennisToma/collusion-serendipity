# S40 adversarial review (supplied text only)

**Scope:** I could not see the raw archive (`data/s40_memory/*.jsonl`). So the 20 quotes I rebuild from come from `results/s40_memory.json`'s `cases` list, not from `responses.jsonl`. I made no edits and no calls, and read no other reviews.

## Independent reconstruction of the primary
- **20 quotes:** all 20 are 10, and each case's archived quote is also 10. Normalized offers are all 0.
- **15 block cells** (5 seeds × retain, erase and contrast): each cell is (0+0)/2 = 0, so every cell is 0.
- **3125 bootstrap draws:** every resampled mean is 0. With linear percentiles, position 0.025·3124 = 78.1 and 0.975·3124 = 3045.9 both fall on 0, giving [0, 0]. The interpolation rule (p·(n−1)) matches numpy's `linear` method.
- **32 sign flips:** every flipped sum is 0 ≥ 0, so p = 32/32 = 1.0.
- **Paired t:** the standard deviation is 0, so the interval is [0, 0].
- **Verdict:** the mean is ≤ 0, so it is a **DUD**. This matches the result file, the summary and REPORT.md.

## Checks that pass, on the code as supplied
- **Correct unit:** the primary is the focal firm's offer minus 10, taken from the parsed `rate`. Nothing is re-simulated, and the files say "offer, not wage".
- **Source-case selection:** one request per run with payload `[run,9,agent,0]`. The agent is fixed from `rows[0]`, and the roster is the same in every round. The archived action must equal the archived parsed rate. The selection is not action-searched, but every case turns out to be at the floor, and the design says so.
- **Intervention isolation:** only the JSON after `Notes file snapshot: ` changes, to `[]`. The marker and ending must each appear once. The retain prompt is byte-identical to the source.
- **Failure and cache handling:** responses are saved before parsing. Any failure is terminal, with no resume or redraw. The one-shot receipt uses `open('x')`. Validation requires exactly the events `start`, `complete`.
- **Schedule:** one thread pool per block gives the barrier between blocks. Arms within a case run one after the other. The overlap sweep caps concurrency at 2, and at equal timestamps −1 sorts before +1, so touching calls don't count as overlapping.
- **Registration:** HEAD must equal the remote, sources must be clean and tracked, and hashes come from `git show <commit>`. The receipt was observed at 02:47:16, which is 42 min before the 03:30 deadline. The `fixed_model` patch makes `_codex` try a single model with `retries=1`.

## Concrete remaining bugs or risks
1. **Clean-clone check depends on `.writer.lock`.** `run()` opens `data/s40_memory/.writer.lock` with `'w'`. If that file is neither committed nor gitignored, `git status --porcelain` in the clone is non-empty and `clean_clone` fails. If it is committed, it gets rewritten. I can't tell which from the supplied text; it needs checking.
2. **The zero-width t interval is shown as a real interval.** When the standard deviation is 0, the t interval is undefined, but it is printed as [+0.000, +0.000] next to "paired t95%". It should be labelled "degenerate, SD = 0".
3. **"Archived-match" counts add no information here.** Every archived quote is 10, so the archived-match counts are just the floor counts. The summary presents them as two separate facts.
4. **The route check proves nothing.** `response['model']=='gpt-6-luna'` always holds, because `_codex` returns the model name it requested. This is acknowledged as route identity, but the validate assertion adds no evidence.

## Acknowledged limits (stated in the files, not bugs)
- **Floor censoring:** both arms sit at the minimum, so the test is structurally one-sided. Only an increase could be seen, and the DUD means only that no upward movement was observed.
- **Bundled changes:** erasing the notes also changes prompt length and contradicts the system prompt's complete-notepad promise.
- **No memory claim:** public history still reveals earlier wages, so this does not show memory is irrelevant.
- **Different environment:** the source/replay fingerprint mismatch is reported (`False`). The served model and the complete effective configuration are not attested.
- **Possible lost output:** `llm.py` can drop an output if its accounting write fails, and that would end the run as a transport failure.
- **Weak inference:** with n = 5, bootstrap positivity is implied by the sign-flip gate rather than being separate evidence, and the bounds are descriptive only.
- **Same-author checker:** `s40_independent.py` is not independently authored, so it is not a fully independent check.

**Bottom line:** I found no bug that changes the S40 DUD verdict or the reported numbers. Items 1–2 should be checked or fixed before final release.
