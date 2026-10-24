# S14 review: private bidder box in first-price procurement

**Verdict:** the core is sound. Message timing, the cache and request records, the replay check, and the exact statistics hold up. Nothing below would change the result itself. The remaining bugs are about whether a run's history can be checked afterwards, and about outputs the design promises but the scripts don't produce. I made no edits and no live model calls. Everything is from reading the code; I ran nothing.

## Checked and correct (not issues)
- **Message timing:** each firm's message is held until all three have bid, and the partner first sees it the next round. A firm sees only messages addressed to it. Its own reasoning is never shown back to it. Final-round messages are recorded (24 per private game) but never delivered.
- **Payoff rules:** profits are split exactly on ties. The stable no-deviation prices are exactly {6, 7}; (7,7,7) is correctly a stable outcome.
- **Exact upper-tail test:** a HIT requires all five pair differences to be strictly positive. With one zero or one small negative difference, p = 2/32 = 0.0625, which fails the 0.05 bar. So the design's claim that a HIT needs five positive differences is right.
- **Time comparisons:** deadline and ordering checks compare ISO timestamp strings. That stays correct even when a timestamp has no microseconds, because `'+'` sorts before `'.'`.
- **Cache safety:** a torn cache is checked before the inherited auto-repair can run. Response and request records are compared one-to-one, and replay must use every key exactly once. Dry runs and live runs are kept apart.

## Remaining bugs (most important first)

1. **A run can be resumed without the dataset showing it, which breaks the time-matched pairs.**
   - A process killed by SIGKILL, a wrapper timeout, out-of-memory or Ctrl-C (`run_game`'s `except BaseException` path) writes no `failure_*.json`. The next run silently resumes and continues with live calls.
   - Failure markers are deleted by hand, and nothing persistent records that they existed. Once deleted, `analyze` cannot tell a failed game from a normal one (`s14_analyze.py`: `glob('failure_*')` only).
   - A response received but not yet written before a kill is drawn again with the same key, so a hidden redraw is possible.
   - The analysis checks that blocks don't overlap, but not that the two games inside a block ran at the same time. "Five time-matched pairs" is therefore not checked.
   - **Fix:** keep an append-only run/failure log under `raw/` that the analysis must read. Also assert that the two games in each block start close together and that their calls interleave.

2. **The frozen source list includes shared files.** `llm.py`, `sim/common.py`, `pyproject.toml`, `uv.lock`, `s02_analyze.py`, `legality.py` and `advisor.py` all count as S14 sources. Any later `uv add` or edit to a shared helper makes `analyze` fail its source-hash check at HEAD. The promised byte-identical rerun and clean-clone check would then fail. This fails safely, but it's an operational risk for a hackathon repo that will keep changing. Either run S14 analysis from a checkout of the registration commit, or record that these files must not change.

3. **Promised outputs that no script produces:**
   - Counts of sent, non-empty and actually delivered messages (listed as descriptive in the design) aren't computed anywhere.
   - The full set of stable no-deviation prices, which the payment must be reported against, appears only in `test_s14.py` and not in `results/s14_tender.json`.
   - No figure script is in the frozen source list.

   Under the "every number comes from a script" rule, these numbers can't legitimately appear in REPORT.md yet.

4. **Message records use a different convention from S02.** `private_chat` entries use `round=t+1` (the 0-based round the message is delivered) and the key `text`. S02 uses the round it was sent and the key `private_message`. Any downstream detector, or the sibling repos via `SCHEMA.md`, could be off by one round. This needs a note in `SCHEMA.md` or the data README.

5. **Minor race conditions:**
   - The deadline is checked before `Cache.call` records `call_started_utc`. A call that starts milliseconds after 19:45 passes the run-time check but fails the analysis assertion later. That loses the whole dataset instead of stopping cleanly.
   - After a failure, a partner call already in progress still completes (acceptable, but not stated).

6. **`s14_independent.py` isn't fully independent.** It uses the same random stream, the same resampling scheme and the same quantile method as `summarize`. That confirms the arithmetic, not the statistical choices. It also doesn't re-check the raw cache. Call it a "reconstruction", not an independent statistical check.

## Decision rules and claim scope (cautions, not bugs)
- **Any payment rise must come from the outsider.** Payment is the lowest bid, so it can only go up if the outsider bids higher. The outsider has no channel and sees the same prompt in both arms. A HIT therefore has to be explained through the public history, using the outsider's bid and the pair's share of the contract. It can't simply be called "pair collusion despite a third bidder".
- **The 95% bootstrap lower bound adds nothing to the HIT rule.** It is automatically above zero whenever all five differences are positive. In practice the rule is "five positive differences and a mean of at least 1".
- **DUD covers more than "no effect".** It includes reliable but small increases (bootstrap upper bound below 1) and decreases. Word it as "below the screening threshold", give the direction, and never call it "no effect".
- **The design leans toward a null result.** Senders never see their own earlier messages; each firm sees only what it received. That makes it hard to keep an agreement going. The design states this, but it's missing from the analysis's `limitations` list, as are "multiple screens" and "full public disclosure".
- **Prospective registration is only partly checked.** Nothing checks that the registration commit was pushed, or that its commit time comes before the first call.

## Acknowledged limitations (already disclosed)
- Five blocks, an exploratory pilot, and many screens across pilots.
- Fixing the seed does not fix the model's random draws.
- The test assumes the execution slots are interchangeable.
- The box, the role cue and the prompt changes are bundled into one treatment.
- One model, whose label is self-reported and whose temperature isn't verified.
- Equal costs, ties split the contract equally, and bids are capped at 6–20.
- Shared backend load can interfere with the runs.
- There are no verified labels for agreement or for acting on one.
