# S40 adversarial review (supplied text only)

I reviewed only the text you supplied. I ran nothing, made no edits and made no calls. The design's causal scope and its main unit are both correct. The analysis uses the focal offer (quote − 10), not realized pay, and the rival is not re-simulated. The counts and sizes add up: 10 cases × 2 = 20 decisions, 5⁵ = 3125 bootstrap draws, 32 sign flips, and the linear percentile matches numpy's `linear` method. The schedule never has more than 2 calls in flight.

## Concrete remaining bugs and gaps

1. **The HIT rule is stricter than written.** With 5 blocks, the smallest possible sign-flip p is 1/32. A block that equals exactly 0 gives a tied flip, so p ≥ 2/32 > .05. In practice, HIT therefore requires all five blocks to be above zero, which is likely to fail with floor ties. DESIGN_S40.md doesn't say this. State it before launch; don't change the rule.
2. **The live-only code is never tested.** The dry tests skip `registration()`, the `launch_observation()` checks at admission and after each call, the `transport_failures` handler, the deadline gate, the `open('x')` receipt, and a real timing-barrier violation. The schedule mutation test only changes `schedule.json`, not the timestamps. Because the receipt allows only one launch, any bug here uses it up. Add a free mocked-live test by patching `chat`, `registration` and `launch_observation`.
3. **The clean-clone check can fail on files outside git.** `validate` needs `logs/s40_launch.json` to be committed. Also, `check()` → `run()` creates `data/s40_memory/.writer.lock` inside the clone. If that file is neither tracked nor gitignored, the empty-`git status --porcelain` assert fails.
4. **Firm selection doesn't match the wording.** The design says "first active firm", but the code takes `rows[0]['agents'][0]` and never checks the firm is active in round 10. Either add the check or change the wording.
5. **The erase arm isn't fully proven isolated.** Nothing checks that note text is absent from the system prompt or the public-history prefix. Add an assertion that no note string appears outside the snapshot.
6. **Timestamp ordering uses string comparison.** It works only because every stamp is `isoformat()` with `+00:00`, including those without microseconds. Compare parsed datetimes instead.
7. **The dry-publication guard depends on the working directory.** In `s40_present.py` it builds the guarded paths from the current directory, not `ROOT`.
8. **The independent check parses more loosely.** `s40_independent.py` uses plain `json.loads`, so duplicate keys and extra fields are not re-checked.
9. **20 minutes of headroom may not be enough.** The run has 10 back-to-back call slots, each with a 600 s worst-case timeout. If the deadline passes mid-run, the whole pilot aborts and produces no estimate. Consider requiring more headroom.
10. **Request parameters aren't compared to the archive.** The archived `max_tokens` and S37's CLI version and fingerprint are never compared with S40's. A retain arm that fails to reproduce the floor could come from runtime drift, not sampling. Report the CLI versions side by side.

## Limits the design already acknowledges (not bugs)

- The cases were chosen after seeing S37 outcomes and are enriched for the floor: this is a challenge, not held-out discovery or a replication.
- Erasing the notes also changes prompt length, note availability and completeness, and contradicts the system's complete-notepad promise.
- Public history still shows the earlier actions, so a null result can't rule out a role for memory.
- The outcome is the offer, not the realized wage. The rival isn't re-simulated, and nothing goes past the one decision.
- Sampling, temperature and token limits aren't controlled. Provider, full effective config and tool non-use aren't attested, and an auth refresh can cause an abort.
- Five blocks give degenerate or descriptive bounds that aren't calibrated or adjusted for multiple tests. Coded and payroll are pooled within each block, and arm order is random rather than counterbalanced.
- No claims about agreement, intent or coordination, and no pooling with S37.

**Verdict:** fix item 2 (mocked-live test) and item 3 (receipt and lock-file state in git), and add the item 1 statement, before the one-shot launch. The rest are small fixes or need checking.
