# S68 adversarial review: one medium bug, no high-severity bugs

I reviewed only the supplied text: `DESIGN_S68.md`, `scripts/s68_context_audit.py` and the two prompt tails. I made no edits and no calls, and I didn't read the filesystem, the raw archives, the parser or the statistics code. This review doesn't cover those.

**High-severity bugs:** none found.

**Medium-severity bugs:**

1. **The decode check in the audit tests nothing.** `decoded` is imported from `s68_replay` but never called. The 16-profile loop builds `opposite = not base`, then `decode = not opposite`, and asserts `decode == base`, which is always true. So the production rule (inverted raw true → reject, false → approve; anchor and repeat unchanged) is never checked. The line `organization_loss == 10*(...)` has the same flaw: it compares an expression to itself.
   - Fix: run `decoded(arm, raw)` for all 3 arms × 16 profiles and assert anchor and repeat pass through unchanged and inverted flips. Then check `outcome(decoded(...))` against the hand-written payoff formula. This should run before calls.

**Low-severity issues:**

2. **The replacement isn't proven to be a single substitution.** `inverted.replace(REJECT_MAPPING, APPROVE_MAPPING) == original` also passes if the instruction string appears more than once. Add `original.count(APPROVE_MAPPING) == 1`, `inverted.count(REJECT_MAPPING) == 1` and `original.count(REJECT_MAPPING) == 0`. The equal-length claim holds (true/false swap: 4+5 = 5+4 characters).
3. **The marker parsing is fragile.** `split(marker)[1].split('\n')[0]` assumes each block is one line of JSON, with no other copy of the marker earlier in the prompt. It works if `json.loads` succeeds, but the `a == b` comparisons add little beyond check 2.
4. **`outcome` is only called with `24480, 9, 'shared'`.** That's fine only if payoffs don't depend on the source or round. Better to evaluate it per case.

**Things I checked that are correct:**
- The expected excess is (q−p)(1−2p): P(anchor ≠ inverted) − P(anchor ≠ repeat) = [p + q − 2pq] − 2p(1−p).
- The HIT condition matches the stated rule. With five blocks and an inclusive one-sided sign test, any zero or negative block gives p ≥ 2/32 > .05. So HIT happens exactly when all five blocks are ≥ .5 (mean ≥ .5). The bootstrap lower bound > 0 and mean ≥ 1/4 then follow automatically, so they add nothing.
- The arm-asymmetric clarification is avoided: both arms append the same note.
- Anchor and repeat are byte-identical requests, and the system prompt is preserved.

**Known limits:**
- The source notes ("Rejecting avoids the 3-point charge") suggest p is near 0. Then excess ≈ q, so a HIT mostly measures mapping-following errors in the inverted arm, not a meaningful polarity effect. The scope text already says this; the report should say it prominently.
- Strict parsing aborts the whole pilot, and parse failures may be more likely in the inverted arm. An abort would lose that signal. Consider registering the abort/failure count by arm as a descriptive outcome.
- The history note only mentions "Completed public rounds". Any booleans inside the statuses or notes snapshot fall outside the clarification. The same applies to both arms, so it isn't a confound.
- The middle view position is identical across both cases in a block. Order, caching and drift confounds remain (acknowledged).
- Stored raw booleans keep their raw polarity. Every downstream consumer must decode with the arm label; one test reading the accepted archive through the reconstruction path would cover this.
- One repeat per case, n = 5 blocks, no tuning or held-out data, unattested provider settings and CLI temperature not forwarded: all disclosed already.

**Verdict:** Fix item 1 and add the counts from item 2 before calls, then commit and push the audit. Wording the scope as "instruction-following under inverted encoding" is enough for the rest.
