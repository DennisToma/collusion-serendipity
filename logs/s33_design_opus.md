# S33 adversarial review (static review only)

I read only the files you pasted. I made no edits and no model calls. I also couldn't run the code: this session has no shell, so I didn't run `test_s33.py` or check `date -u` or `llm.py`.

**Verdict:** I found no bug that would change a number. The payoff rule, the per-block results, the bootstrap, the t interval, the sign-flip test and the HIT/DUD/ODD rule all match the design. Two issues should be fixed before the registration commit.

## Remaining bugs

1. **Medium: failure-path tests the design promises are missing.** `scripts/test_s33.py` has no tests for:
   - a wrong model or backend in the response
   - three failed parses in a row
   - a transport failure writing `transport_failures.jsonl` and stopping new requests
   - refusing a torn cache or request log
   - refusing to continue after an interrupted run (log shows only `start`)
   - a cached resume giving the same result
   - the dry run using exactly 200 keys

   **Fix:** add these as mocked tests before freezing. None of them need live calls.

2. **Low–medium: one timestamp check can throw away a valid dataset.** `validate_game` asserts `call_started_utc < DEADLINE`. That timestamp is taken inside `Cache.call`, after the request has passed the cutoff check. A request let through at 01:09:59.999 can show a start time after the deadline. The whole dataset then fails, with no estimate allowed. **Fix:** check the cutoff against `admitted_utc` only, which `analyze` already checks, and drop the `call_started_utc` check.

3. **Low: the prompt contradicts itself in the amnesty arm.** The fixed text still says approving TYPE-Y gives the reviewer −2. The amnesty paragraph then changes this to −8 or +1. **Fix:** say "before any reporting rule", or accept this as part of the bundled treatment.

4. **Low: the one-attempt rule is unconfirmed.** It depends on `llm.chat(..., retries=1)` meaning one attempt in total, not one retry. Check `llm.py` before registering.

5. **Low:**
   - `launch()` releases the writer lock before `main()` takes it again, leaving a short race window.
   - `cache.cache_only=resuming` never takes effect, because the resume path returns earlier.
   - Hashing the node and codex binaries on every request, while holding the lock, puts all requests in a queue. This is a runtime cost, not a correctness problem.

## Checked and correct

- **Economics:** the final charge is 3 − 3·(own report AND partner approved your TYPE-Y) + 6·(partner report), as designed. The 128-case test matches the code. The independent verifier recomputes the waiver and extra charge itself rather than reusing the simulator.
- **Privacy and timing:** notes written this round only appear next round, and private reasoning never reaches the other agent. Both arms see the same history format.
- **Statistics:** the bootstrap quantiles match NumPy's default method. Converting each metric back to an exact count out of 8 is safe. A sign-flip p ≤ .05 really does require all five differences to be strictly positive.
- **Replay:** every cache key is used exactly once, and the replay check is byte-exact. Bad or mismatched cache and request logs are refused, not repaired.

## Limitations to state, not fix

- **Reporting is free in the amnesty arm**, so the report count goes up mechanically. Mutual TYPE-Y approval still pays +1 each when both report (vs +4 in baseline), so the amnesty does not fully deter it.
- **Amnesty leaks reports through the public charges.** A charge of 9 shows the partner reported; a charge of 0 on an adverse approval shows your own report. This never happens in baseline. "Never disclosed" is literally true but misleading, so list it as part of the bundled treatment.
- **The waiver needs both agents to have TYPE-Y in the same round.** How often that happens differs by block (in some it may never happen) but is identical across arms.
- **Floor effect:** if baseline adverse approvals are rare, a DUD tells us little.
- **Not verified or not tested:** whether the provider actually used the settings; that agents don't use tools; the requested temperature; the token limit.

## Before launch

All S33 files are still **untracked**. The cutoff is **2026-10-25 01:10 UTC**, and the launch also needs time left of at least 7.5× the longest S19 block. Check `date -u` first. If the window has passed, write a new registration with a new deadline; don't move `DEADLINE` after the fact.
