# S24 independent adversarial review (static)

I reviewed only the source supplied in the message. I made no edits and no model calls, and I did not run anything, so no claim below has been checked by execution. I could not see `s24_present.py`, `s24_independent.py`, `s24_checked_independent.py`, `s24_release.py`, `s24_reviews.py`, `test_s24_publication.py`, `llm.py` or `sim/legality.py`.

## Remaining bugs

**1. HIGH: a pre-launch test fails as written.** `test_identity_wording_and_hidden_draws` requires `'probability 1/4'` and `'12-point'` in the AI-arm system prompt. Those strings are left over from S22's stochastic charge. S24 uses the same deterministic 3-point charge in both arms, so this test fails for `cond=='ai'`. If anyone has reported the S24 tests as passing, they were not run against this code. **Fix:** require `'deterministic 3-point'` in both arms, check that the two arms' prompts are identical apart from the identity phrase, rerun the full suite, and record its output before registering.

**2. LOW–MEDIUM: a promised equality check is missing.** The design says the expected-score fields are "exact duplicates" of realized bonuses and that this is verified. `metrics()` computes both `pair_score` and `pair_expected_score`, but nothing asserts they are equal. The HIT gate reads `pair_expected_score`. The two values should match mathematically, but the stated verification doesn't exist. **Fix:** in `metrics`, assert `pair_expected_score == pair_score` and `outsider_expected_score == outsider_score`.

**3. LOW: confusing prompt wording.** The prompt says "expected reviewer bonus -2 … minus an expected 3-point charge" right after calling the charge deterministic. The wording is the same in both arms, so it doesn't confound the contrast, but it could make the economics less clear to the model. Leave it as frozen, but list it as a limitation.

**4. LOW: lock gap at launch.** `launch()` takes `.writer.lock`, releases it when its `with` block ends, and only then does `main()` take it again. That leaves a short window for a second writer. The one-shot receipt (`open('x')`) and the guards that refuse prior data make this mostly harmless. **Fix:** keep holding the lock through `main()`.

**5. INFO: dead or hard-coded code.**
- `cache.cache_only=resuming` never runs, because the resume path returns earlier.
- `written=100` is hard-coded. It is correct (5 games × 20 notes), but it should be derived from the data or asserted.
- `analyze` imports `prompts` but never uses it.
- The source-hash loop checks `cfg['dry']` twice.

**6. INFO: timestamps are compared as strings.** This works because every timestamp is an ISO string with a `+00:00` suffix, including when microseconds are omitted (`'+' < '.'` keeps the order right). It breaks silently if a timestamp ever arrives in another format. Comparing parsed datetimes would be safer.

## Checks that came out clean

- **Economics:** the exhaustive 2³×2⁶ test matches `outcome`. The payoffs check out:
  - reciprocal partner TYPE-Y approvals give each partner 6 − 2 = +4 and cost the organization 20;
  - a unilateral deviation saves 2;
  - the stage optimum is to approve X and reject Y.
- **Simultaneity and visibility:** prompts see only completed `rows`. Current-round notes are held back until all three reviews are in. Reasoning is never replayed. The outsider gets no notes.
- **Cache and replay:** the cache key includes dry/live status, run_id (which contains the condition) and attempt number. Replay checks every key exactly once, keeps the original bytes, blocks live calls, and compares full ground truth minus the start/end times.
- **Arithmetic:**
  - Recovering exact counts with denominators 8 and 24 is valid for every metric, including organization loss (5k/4).
  - The bootstrap over all 3,125 resamples uses linear-interpolation percentiles.
  - The one-sided sign-flip p-value is 1/32 only when all five blocks are positive; a single tie raises it to 0.0625. The design states this correctly.
- **Screening rule:** HIT is checked before DUD, and a reverse effect counts as DUD. Both match the design.
- **Failure handling:** a failure stops admission of new calls, leaves failure markers, and refuses to resume after an interruption or a torn cache.

## Acknowledged limitations (not bugs)

- With n=5 and no held-out data, exactness depends on the sign-flip exchangeability assumption.
- The identity cue covers self, partner and outsider together, and the prompt still says "employee". Results cannot isolate a mechanism.
- The bonus gate mostly repeats the primary metric: any partner TYPE-Y approval raises the pair's total by 4. It is not independent evidence.
- Model, backend and sampling details are client metadata only.
- The three agents in a round are queried one after another, not concurrently. Because no agent sees another's current reviews, this does not break simultaneity.
- Adverse approvals are not evidence of an agreement.

## Verdict

The design and harness are sound. Do not register or launch until bug 1 is fixed and the full test suite has been run and its output recorded. Add the equality assertion from bug 2 in the same frozen commit. Everything else can be listed as a limitation.
