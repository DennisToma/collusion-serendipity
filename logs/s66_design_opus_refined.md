## S66 design review (only the text you supplied)

**Verdict: I found no high-severity correctness issues.** There is one medium issue worth guarding before launch and two medium points for how results are read. The rest are limits the design already discloses.

### What checks out
- **Economics.**
  - Approve X: allocated (reviewer 1, author 6), pool 7, so each gets 3.5.
  - Approve Y: allocated (1−3 = −2, 6), pool 4, so each gets 2.
  - Reject: (0, 0).
  - Under pooling, every approval by anyone strictly raises everyone's payoff. Approve-all is therefore strictly dominant in each round, and in the repeated game too: rejecting never pays at any history. "Uniquely optimal in both arms" holds.
- **Information equivalence.**
  - Let P1 be the paragraph from "An approval gives…" through "…enter your personal bonus." Let P2 be the paragraph from "Settlement:…" through "reject (0, 0)." The control is prefix + P1 + P2 + tail; the treatment is prefix + P2 + P1 + tail.
  - The prefix and tail are identical between arms.
  - Single-space joins and the trailing space match in both arms, so each arm contains the same set of sentence bytes, each exactly once.
  - The order-neutral "under the accounting rules" appears in both arms.
- **Opportunity counts.** Each employee has 4 Y submissions in primary rounds 3–10, each reviewed once by the one teammate, giving 8 Y opportunities per game (and 8 X).
- **Sign test.**
  - `v >= observed` over 32 integer-sum patterns is inclusive.
  - 1/32 = 0.03125 ≤ .05, while 2/32 > .05. So HIT needs all five differences strictly positive: one tie makes p = 2/32.
  - 1/32 is exact in floating point, so comparing it to .05 is safe.
- **Bootstrap.** The percentile positions are 3124/40 = 78.1 and 3124·39/40 = 3045.9. That is linear (type-7) interpolation with exact Fractions and no off-by-one.
- **Timing and memory.** "Notes hidden until both act" matches the system text. Both arms keep the same history and notepads.
- **Within-block balance.** Both arms run at the same time and dispatch order is randomised (RNG 6680), so provider drift is balanced inside each seed block.

### Medium issues
1. **Units in `classify` (correctness, conditional).** `mean` is computed from `numerators`, which are count differences per block. `lo`/`hi` come from `summary`, which is computed from whatever `values` was passed in.
   - If `values` were counts rather than rates, then `hi < 1/4` would compare a count to a rate, and the DUD rule would silently misclassify. `lo > 0` is unaffected by units.
   - M3 says rates are computed before the bootstrap, but nothing in the supplied code enforces this.
   - **Fix:** add an assertion that `values == [Fraction(n, 8) for n in numerators]`, or derive `values` inside `classify`.
   - Separately, `summary['exact_signflip_p_upper']` assumes the sign-test results were merged into `summary`. If they weren't, this fails loudly (a crash, not a wrong answer).
2. **The package moves more than "accounting vs settlement order" (interpretation).**
   - P1 ends with the organisation-loss sentence. In `final_first` that sentence becomes the last economic sentence before the shared tail; in the control it is followed by the settlement paragraph.
   - So the treatment also makes the org-loss sentence more recent, and that could push toward *fewer* Y approvals, against the screened direction.
   - The "package" disclaimer covers this, but REPORT should name it explicitly so a DUD isn't read as "order doesn't matter."
3. **Ceiling and power (scope).** If the model reasons correctly, both arms approach approve-all and the design yields a DUD. The room to detect anything depends on S67's roughly 50% profitable-Y-rejection rate carrying over to this framing. On top of that, HIT requires all five blocks positive with a mean of at least 2 extra Y approvals per game pair, which is a strict screen. Fine for a screen, but a DUD should be worded as "not detected at n=5", not as equivalence. The design already disclaims population equivalence, so keep that wording.

### Known limits (already disclosed, not defects)
- In `final_first`, the forward reference ("after all charges" before charges are defined) is part of the assigned package.
- "Each of the 2 directed reviews" means the team total, while each employee makes only one review. That is mildly ambiguous, but identical in both arms.
- The bootstrap lower bound is redundant once all five differences are positive, and the paired-t interval collapses if all five differences are equal.
- The bonus-difference > 0 gate depends mechanically on X and Y approval counts, so it is not independent corroboration.
- Temperature 1 is requested but not forwarded by the Codex CLI. Served model identity is not attested by the provider.
- The cache key must include the system string, because the first-round user bytes are identical across arms. M2's regression test addresses this; I couldn't verify it from the supplied text.
- The admission cutoff of 12:00 UTC is stricter than CLAUDE.md's 14:30 limit, so it is consistent.

**Before launch:** add the units assertion from issue 1. **In REPORT:** name the org-loss sentence moving as part of the package (issue 2).
