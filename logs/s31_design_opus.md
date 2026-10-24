# S31 review: no blockers; three low-severity bugs, all fail-closed

I reviewed only the files you pasted. I didn't run, edit or call anything. `scripts/s31_present.py`, `scripts/s31_reviews.py`, `llm.py` and `sim/legality.py` weren't included, so they're unreviewed.

## Checks that passed (by reading the code)
- **Economics:** The 441-outcome enumeration gives pure equilibria (18,18), (19,19), (20,20), all weak where claimed. Joint profit is highest at (0,0), with 10 each. Deviating to wage 1 from (0,0) earns 19. Worker earnings plus total employer profit always equals 20. The test checks all of this.
- **Simultaneity and visibility:** Notes written in a round are buffered and only released after both employers submit. The self arm sees only its own notes. The only difference between the two prompts is the readability sentence, and a test checks that.
- **Arithmetic:** Every metric times 32 is a whole number. The values are exact binary fractions, so converting through float and back to `Fraction` loses nothing. The bootstrap quantile matches NumPy's linear method. With five blocks, the sign-flip p ≤ .05 rule does force all five differences to be strictly positive. The HIT/ODD/DUD logic matches the design, and the profit gate equals the primary mean exactly, which the independent check asserts.
- **Cache and replay:** The cache key covers every request field, including the attempt number. Cache-hash and request-audit mismatches are refused at startup. Replay patches out live calls and must use every key exactly once.

## Remaining bugs
1. **Low: a valid run could be marked INVALID at the deadline.** The deadline gates *admission*, but `validate_game` also asserts each call's `call_started_utc < DEADLINE`. That timestamp is set inside `Cache.call` a few milliseconds after admission. A call admitted at 00:29:59.99x could fail validation. **Fix:** check only `admitted_utc` and let start/completion times run past the deadline, as the design says.
2. **Low: interruptions leave no failure record.** `future.result()` only catches `Exception`. A `SystemExit` or `KeyboardInterrupt` from a worker skips the `failure_*.json` marker. It still fails closed, because the execution journal has no `complete` event, but there's no record of the cause. **Fix:** catch `BaseException`, write the marker, then re-raise.
3. **Low, documentation:** The design says a failure "preserves all prefixes". On abort, the partner game is aborted at its next request and its game file is never written; its partial history survives only in the raw cache. **Fix:** reword the design, or dump partial games on failure.
4. **Low, dead code:** `cache.cache_only=resuming` is always False at that point because the resume path returns earlier. Harmless. Completion also checks source drift twice.

## Unverified risks — confirm before launch
- **Clean-clone replay:** this needs `data/s19_labels/raw/responses.jsonl`, all S19 game files and `data/s31_labor/raw/*` to be in git. Your rules say to gitignore raw caches over a few MB. If any of these are ignored, the remote clean-clone `analyze` will fail. Check with `git check-ignore`.
- **Untested paths:** The tests don't exercise `analyze` or `assert_cached_replay` on a dry archive, the deadline guard, failure markers or the launch receipt. The planned 200-key dry replay plus a dry `analyze --allow-dry` run is the only end-to-end check, so run both before launch.
- **Not yet frozen:** all S31 files are untracked. `launch()` enforces commit and push, but that has to happen first.
- **Model check:** the route check compares the model name reported by `llm.py`. If `llm.py` echoes the requested model instead of the actual one, the check is a formality (this is already listed as a limitation).

## Acknowledged limitations (not bugs)
- The profit gate is mechanical: it's just 20 minus worker earnings.
- Shared delivery and the readability statement are bundled. Public wage signalling exists in both arms, so both arms can settle on low wages, which pushes the result toward DUD.
- n=5 with no multiplicity correction; exploratory only.
- Codex doesn't enforce temperature or token limits; tool use is restricted by instruction only.
- Timing and model metadata are recorded locally, not attested by the provider.
- Low wages don't imply an agreement.
- Stage regret is a one-shot measure in a repeated game.
- The labor market is synthetic, with homogeneous employers.
- Dry runs only produce wages 0–12 (plumbing test only).

## Verdict
None of these bugs is a blocker, and all of them fail closed. Fix #1 and #2 and settle the gitignore question before you commit the freeze. After that, running the planned dry replay is the remaining gate.
