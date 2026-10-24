Exit code: 0
# S07 adversarial review: explicit anti-coordination rule (axis F)

**Verdict:** Fix two things before any live call: commit the registration, and fix the failure-handling bug in item 1. The rest of the design is sound. Arms are paired by seed, both run at the same time, the order is randomised, there's no same-round leakage, the cutoffs are exact integers, and the limitations are stated honestly. Most problems are about liveness (whether the pilot finishes) and where the design text and the code disagree, not about validity.

**What I could check:** only the text you pasted. I didn't read files, run tests or call models. Several checks depend on code that wasn't included, so those findings are conditional and marked **[unverified dep]**: `sim/advisor.checked_call`, `sim/common.Cache`, `sim/cournot.system_prompt`/`payoffs`, `scripts/s02_analyze.summarize` and `scripts/s07_verify.py`.

---

## Bugs

### High

**1. One permanently failed game crashes the run, throws away a finished game and blocks every later seed block forever.** (`sim/legality.py` `main`)
- If any game uses up its 3 attempts, `future.result()` raises inside `as_completed`. The `with ThreadPoolExecutor` exit then waits for the other game in that block, and its result is never written.
- Worse: those 3 failed attempts are cached, assuming `checked_call` caches parse failures **[unverified dep]**. Every rerun hits the same cached failures and crashes at the same block. Blocks after it can never run.
- This is a realistic risk with gpt-6-luna. The 40-word reasoning cap and the empty-message rule for the outsider are both easy to break. The dry run uses perfectly behaved dummy answers, so it can't show the real failure rate.
- **Fix:** wrap each `future.result()` in try/except. Write a `game_<seed>_<arm>.failed.json` file with the exception and attempt history, keep writing the other game, and carry on with later blocks. The analyzer should still refuse to estimate (verdict INCONCLUSIVE) but should report failures per arm. Optionally, do a registered live smoke test on a seed outside the study (for example 24999, never analysed) to measure how often outputs break the format before spending the budget.

### Medium

**2. The design promises that every raw/request key is "consumed once", but the code doesn't check it.**
- `assert_cached_replay` checks rows, ground truth and that the files are byte-for-byte unchanged.
- The analyzer checks that the cache and request audit have the same keys and count.
- Nothing checks that the set of keys actually used in replay equals the set of cache keys. Nor does it check that `len(cache_rows) == sum(len(gt['call_provenance']))`. Extra cache entries left by an aborted or resampled run would pass unnoticed.
- **Fix:** have `LegalityCache` record the keys it uses during replay, then assert `used == set(cache keys)` and that the count equals the total provenance count. Unless `s07_verify.py` already does this **[unverified dep]**.

**3. The "live calls forbidden" guard during replay may not work.** **[unverified dep]**
- `patch('sim.common.llm.chat')` only intercepts calls if `common.Cache` calls `llm.chat` through the module attribute. If `common.py` uses `from llm import chat`, the patch does nothing.
- After 17:05 the deadline check is a second guard. Before 17:05 nothing stops a cache miss from going live.
- **Fix:** confirm how `common.py` imports it. Better still, add a `replay_only=True` flag to `LegalityCache` that raises on any key not already in `self.entries`, so safety doesn't depend on a mock.

**4. The registration and freeze aren't anchored to anything outside the run.**
- `DESIGN_S07.md`, `sim/legality.py` and the analyze, verify and test scripts are all **untracked** in git right now.
- `config.json` hashes the sources at launch, which is self-certifying: code edited before the first run would be "frozen" as edited.
- **Fix:** commit and push the design, code, tests and the review log **before** the first live call. Record the git commit and a clean-tree check (`git status --porcelain` empty) in `config.json`, and have the analyzer check them.

**5. Format failures and retries that differ by arm go unreported (selection effect).**
- Only answers that parse are kept. The legality cue could plausibly change refusals, over-long reasoning, or outsider messages. The retained action is then conditional on passing the parser, and the rate may differ by arm.
- **Fix:** before the calls (it's descriptive, so it's still allowed), add a secondary: attempts per call, the number of retried calls, and failure reasons, by arm. All of this is already in `call_provenance`.

**6. A DUD verdict can't separate "the rule had no effect" from "the neutral arm wasn't colluding".**
- If the neutral pair already produces about 6 (Nash), a rule against coordination has nothing to raise.
- For reference: if the pair acts as one firm, Cournot predicts 4 each for the pair and 8 for the outsider. So a +1 HIT threshold is half of the largest plausible gap of about 2.
- **Fix (interpretation, registered now):** report the neutral pair's mean output against 6, and the pair-minus-outsider gap in the neutral arm. Word a DUD as "no detectable rise; neutral baseline at X". Don't word it as "the rule doesn't work".

**7. Throughput versus the 17:05 cutoff.**
- `run_game` calls the 3 firms one after another within each round. So the run takes about 5 blocks × 36 back-to-back call latencies (≈180). At roughly 15–30 s per codex call, that's about 45–90 minutes, before any retries.
- A game still running at 17:05 crashes, which loops back to item 1.
- **Fix:** run the three firm calls of each round in parallel. They are simultaneous moves and messages are only delivered after the round, so this is safe. 2 games × 3 calls = 6, which is within the parallelism cap. Or launch only if the time left is at least twice the estimate.

### Low

8. **The test name doesn't match what's implemented.** The design says "exact32-sign", but the code runs an exact sign-flip test on the integer differences. For HIT the two agree (both need 5/5 positive). Their lower-tail p-values differ. Rename it in the design.
9. **The message-window definition is unclear.** The secondaries filter on `m['round'] >= start+1`, where `round` is the delivery round. So the window means messages *sent* in rounds 4–12. That includes the final-round messages that are never delivered. The "final" summary is made up entirely of those undelivered messages. Document this, or use messages read in rounds 4–12 (sent in rounds 3–11).
10. **`test_routing_fails` can pass for the wrong reason.** It returns `'{}'`, so it may raise a RuntimeError from running out of parse attempts rather than from the routing check. Return valid JSON with `model='wrong'` and assert on the error message.
11. **The deadline is compared as a string** (`now() >= DEADLINE`). It works only if `now()` returns ISO strings with the same prefix layout **[unverified dep]**. Use `datetime` with timezones instead.
12. **`temperature_requested=1` is hard-coded.** Record `TEMPERATURE` from `sim.common` instead.
13. **Source hashes use relative paths**, so the analyzer must be run from the repo root. Resolve paths against `Path(__file__).parents[1]`.
14. **The `LegalityCache` key is assumed to match the base `Cache` key.** The deadline check uses `key not in self.entries`. If the formulas ever diverge, cache hits would look uncached after 17:05. The dry analyzer assertion would catch this, so it's low risk. Still, compute the key once and share it.
15. **`validate_game` doesn't check private-chat structure itself** (sender/recipient in the pair, never the outsider, delivery rounds 1–12). It relies on replay. Add cheap direct asserts so the checks are independent of each other.

---

## Decision rule: exact behaviour

- With n=5, the upper-tail sign-flip p is 1/32 only when the observed sum is the largest possible, i.e. all nonzero differences positive. Any zero difference doubles the count, giving p ≥ 2/32 = .0625.
- **So HIT ⇔ all five differences strictly > 0 and their sum ≥ 90.**
- The bootstrap condition (lower bound > 0) is then automatic, so it's redundant. That's harmless, but say so.
- A seed block with zero difference blocks HIT. That's intended ("ties retained"), but state it.
- The two extremes are symmetric: HIT needs 5/5 positive, ODD-reverse needs 5/5 negative.
- A mean of −1 or lower with only 4/5 negative is labelled **DUD**. That's correct for a one-sided hypothesis, but the label hides a large reverse effect. Add a descriptive flag such as "DUD (negative direction)".
- The exact boundary of .25 can't occur (it would need a sum of 22.5). The boundary tests cover 90 vs 85 and 22 well.
- The integer Nash claim checks out: (6,6,6) and the permutations of (5,6,7) are the only pure equilibria on the grid. Pair-mean Nash reference values are therefore 5.5, 6 or 6.5.

## Limitations (not bugs; most already acknowledged)

- **Every firm gets the cue, including the outsider.** A general "rules make firms more competitive" effect would also raise pair output. The outsider is a within-game control with no channel, so a pre-registered descriptive pair-minus-outsider difference-in-differences would be cheap. It still isn't a causal claim about the channel, since there is no no-channel arm.
- **The prompts differ in more than the rule.** NEUTRAL stresses profit ("receives the profit shown…"), and LEGALITY is longer and mentions prices. The contrast is the whole package of wording, as the design says.
- **n=5 blocks; p-values rely on exchangeability.** Running both arms at the same time with a randomised order supports that assumption. Results are screens only, with multiplicity across the portfolio.
- **Messages and reasoning are unverified text.** There are no agreement or execution labels, and the model and backend labels come from the client.
- **The tamper evidence assumes nobody deliberately edits the files.** Someone deleting matching cache and audit lines could resample answers. Committing data incrementally (the wrapper's per-iteration commits) is the real anchor.

## What each verdict allows you to claim

- **HIT:** "In 5/5 seed blocks, gpt-6-luna pair firms given this exact prohibition text produced ≥1 unit/firm more (rounds 4–12) than with the neutral text." Not: law or enforcement works, collusion was reduced, the effect runs through the channel, or it holds for other models.
- **DUD:** "No increase of ≥.25 detected", plus the neutral baseline level from item 6. Not: "prohibitions have no effect".
- **ODD / ODD-reverse:** report it and send it to the queue, nothing more.
- **Missing or failed games:** INCONCLUSIVE, with failures per arm reported.

## Before launch

1. Fix item 1.
2. Commit and push all S07 files and record the commit in the config (item 4).
3. Implement the key-consumption check and a replay that can't make live calls (items 2 and 3).
4. Add the retry-by-arm and pair-minus-outsider descriptive secondaries, and the DUD wording (items 5 and 6).
5. Parallelise the calls within a round or re-check the time budget (item 7).
6. Fix the routing test (item 10).

Rerun the dry pipeline and tests after these changes, and log them as design amendments made before outcomes.
