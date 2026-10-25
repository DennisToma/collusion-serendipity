# S45 review: four bugs to fix before launch

I read the files only. I made no edits, made no model calls and did not run the tests.

## Checks that pass
- **16-profile economics:** For each directed recommendation, a SUPPORTED post nets the reviewer +1 and an UNSUPPORTED post nets −2, so silence beats posting an unsupported product whatever the partner does. The design's 6/0/8/9 figures are correct and the stage equilibrium is unique. `outcome()` and the exhaustive test agree.
- **Simultaneity:** Notes go into `pending` and are released only after both sellers submit. The second seller's prompt never contains the first seller's current-round output.
- **Visibility:** Round t sees notes with `round<=t`, so only notes written up to the previous round. Reasoning is never replayed. In round 0 the prompts differ only by the readability sentence.
- **Statistics:** The bootstrap percentile uses linear interpolation at p·3124, which matches `np.quantile`. The sign-flip test reaches p=1/32 only when all five differences are strictly positive, because a zero difference gives 2/32. HIT/DUD/ODD order and thresholds match the design. The ISO-string time comparisons sort correctly, including timestamps with and without microseconds.
- **Raw provenance:** The cache is bound to the request audit through key and response hashes, and is checked again in replay and by the independent verifier.

## Bugs and fixes
1. **A token refresh can kill the run or a finished dataset.** `fingerprint()` hashes `~/.codex/auth.json`, and it runs before every new call and again at completion. If Codex refreshes its login token:
   - during the run, the one-shot launch aborts and cannot be resumed;
   - after the last call, `completion_observation` raises before exports are written and before the journal records `complete`. A full 200-decision dataset then becomes permanently "interrupted".
   
   **Fix:** don't hash the contents of `auth.json` (record that it exists, or the account ID). Alternatively, record the completion check as an observation without failing on it.
2. **Temperature and token limit are never sent.** `_codex` ignores `temperature` and `max_tokens`. The design's "requested temperature 1 / default 512 tokens" is only a local label. **Fix:** reword the design and summary to "recorded locally, not transmitted".
3. **Analysis enforces a timing condition the launch never checks.** `verify_transport_and_preflight` requires deadline − first admission ≥ required headroom. The dispatch guard only checks at its own precheck time, which is slightly earlier. A run that just squeaks through could be refused at analysis. **Fix:** check the same inequality in the guard against the admission timestamp, or drop it from the analysis.
4. **Malformed output can end the whole pilot instead of triggering a retry.** `parse_action` doesn't catch `RecursionError`, so deeply nested JSON aborts the run. The independent verifier has the same gap. **Fix:** add `RecursionError` to both except clauses.

## Smaller issues
- The model/backend mismatch check can never fire: `_codex` returns the model name it was asked for. Don't count it as route verification.
- `cache.cache_only=resuming` never takes effect, because resume returns before the cache is built. Replay is protected by the patch on `llm.chat` instead. Remove the line or document this.
- The test checks the payoff formula but doesn't assert dominance, uniqueness or the 6/0/8/9 values the design promises. Add those assertions.
- Freeze risk during the run: all 20 source files are re-hashed before every new call. Any edit aborts the run, including a `uv add` or `uv run` re-lock touching `pyproject.toml`/`uv.lock`, or a launch note added to `DESIGN_S45.md`. Don't touch them until the run completes.
- Hashing the node and codex binaries happens under the admission lock on every call. That delay isn't in the headroom estimate from S19.

## Limitations (not bugs)
- The five outcomes carry only two independent quantities: consumer loss is exactly 10 × the unsupported rate, combined profit is 9 × supported + 6 × unsupported, and the two bonus fields are the same number. "50 metric cells / 15 summaries" overstates the evidence.
- Shared-minus-self combined profit equals 9×(change in supported rate) + 6×(change in unsupported rate). The profit gate can only fail if supported recommendations fall by more than ⅔ of the rise in unsupported ones, so it confirms almost nothing.
- Per-seller schedules are balanced, but the number of rounds where both products are UNSUPPORTED (the mutual-posting opportunities) varies by seed. It is matched across arms but not across blocks.
- Apart from the codex model name and the client timestamps, nothing about the provider side is attested: no stderr or session ID is kept, tools are restricted only by instruction, and provider draws are uncontrolled.
- The arms differ in more than readability: delivery, prompt length, expectations and downstream histories change together. Public actions allow reciprocity in both arms.
- The sign test assumes symmetry. With n=5, a HIT needs all five blocks positive.
- "Your only memory is the provided history" contradicts the notepads; it's minor wording but it does conflict.

**Verdict:** Fix #1 before launch. It is the only bug that can destroy valid data after the fact. #3 and #4 are quick fixes worth making. #2 and the redundant outcomes need corrected wording, not code.
