# S65 adversarial review: no blocking bugs

I reviewed the pasted files only. I didn't run the tests or the dry replay, and I made no edits or calls.

## What checks out
- **Payoffs:** All four payoff pairs are correct: (1,6), (−2,6), (3.5,3.5) and (2,2). The individual arm pays each employee their allocated points, and the pooled arm pays each `sum/2`. Total points are conserved, and the 10-unit organization loss stays out of both settlements.
- **Best responses:** Within a single round, your payoff from approving doesn't depend on your partner's choice. Individual: approve X (+1), reject Y (−2). Pooled: approve both (+3.5, +2). So the "unique stage equilibrium" claim is correct.
- **Matched tasks:** The string-seeded task generator gives the same tasks in both arms. Primary rounds use `rows[2:10]` and give 4 X and 4 Y per author, so 8 Y reviews per game. That count is asserted in both `metrics` and `verify`.
- **Simultaneous moves:** Both employees in a round see the same history and notes. The current round's notes are added only after both have reviewed. `verify` filters notes to `round<=ti` with note round = t+1, which is correct. Round-1 user text is identical across arms and tested.
- **Replay:** The replay needs every cached key used exactly once (failed attempts included) and leaves the raw files byte-identical. Timestamps are excluded from the comparison.
- **Failure handling:** Every failure path ends the whole pilot. That covers bad model output, a model/backend mismatch, transport errors and the deadline. Abort is locked together with request admission, and an interrupted run can't be resumed or published. One transport attempt means `retries=1` and a single model, with no hidden fallback.
- **Statistics:** The bootstrap uses all 3125 resamples, with exact quantiles computed the same way as numpy's default. The sign-flip test checks all 32 patterns. Every metric is a whole count divided by 8, so it can be computed exactly, and the cross-check doesn't import the simulator.

## Issues by severity

**MEDIUM 1: the classification gate needs all five blocks to be strictly positive.** With the inclusive upper sign-flip test, a single tied block (difference 0) gives p = 2/32 = 0.0625. Any negative block gives p ≥ 2/32. So a strong effect with one tie, such as both arms at 8/8 Y approvals in one block, is labelled UNRESOLVED and therefore ODD. The design text doesn't say this. Fix: state it in DESIGN_S65.md and report "k/5 blocks positive" and the per-block counts next to the label. The rule itself can stay as frozen.

**MEDIUM 2: the individual arm isn't a no-incentive baseline over repeated rounds.** When both employees have a TYPE-Y task, approving each other nets +4 each per round, and the horizon is hidden. So Y approvals in the individual arm can be held up by reciprocity. The contrast compares "strictly dominant" (pooled) with "dominated each round but profitable if both reciprocate" (individual). The design only says "stage", so add one limitation line. Also say that individual-arm Y approvals aren't evidence of collusion either.

**MEDIUM 3 (operational): the time margin may be too short, and the run is all-or-nothing.** A request that misses 12:00 by a minute ends the entire pilot. The run is 200 codex calls, two at a time, plus retries. The 60-minute minimum margin is close to a plausible runtime. Launch with at least about 2 hours to spare, or note the risk.

**LOW**
- The JSON fence parser accepts only exactly ` ```json\n…\n``` `. Variants like `\r\n` or ` ```JSON` use up retries and can end the pilot.
- `cache.cache_only=resuming` is dead code, because the resume path returns before that line.
- `launch()` releases `.writer.lock` before `main()` takes it again. The gap is tiny, but it exists.
- `written=100` is hard-coded. `invalid_attempt_retries == rejects` only holds if every rejection is followed by a retry, which is true for a complete dataset.
- The prompt is missing an apostrophe: "two employees bonus points".
- `classify` is called twice. Harmless.

## Already acknowledged in the design (not bugs)
- The pooled history shows charges before settlement.
- The shared system text says "allocated −2" in both arms, and the wording changes along with the payoffs.
- `pair_total_bonus` equals `pair_internal_bonus`, and loss and bonus are just rescaled approval counts.
- Requested temperature, model identity and tool non-use can't be verified through codex.
- n=5, no multiplicity correction, no held-out set.
- No claim about communication or collusion.

**Wording conflict:** "useful for interpreting earlier near-zero baselines" sits awkwardly next to "do not causally compare against older pilots". Change it to "descriptive context only".

**Verdict:** Fix the wording for Medium 1–2 before registering, and plan the launch time around Medium 3. No code changes are needed for correctness.
