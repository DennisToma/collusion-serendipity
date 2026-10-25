# S38 adversarial review

I reviewed the pasted files only. I made no edits, ran no code and made no model calls.

**Verdict:** I found no bug that would invalidate the estimates. The economics, simultaneity, replay binding, the arithmetic in 1/32 units, and the HIT/DUD/ODD rule all check out. The issues below are confounds, operational risks and small integrity gaps.

## Confirmed correct
- **Economics:** The only pure Nash wage pairs are (18,18), (19,19) and (20,20). Firm profit plus worker pay is always 20. Every metric is an integer count over 32: profits are half-integers, regret is divided by 16 and offered wage by 16.
- **Float round-trip:** Converting values to float and back to Fraction via `str` is exact for k/32.
- **Screening rule:** At n=5 a HIT needs all five block differences strictly positive (p_upper = 1/32). The bootstrap gate adds nothing beyond that, which the summary already says. The bootstrap quantile method matches NumPy's linear method. HIT and DUD can never both apply, because a HIT means mean ≥ 2 and the upper bound is at least the mean.
- **Simultaneity:** Notes are buffered in `pending` and wages are only made public after both firms submit. Reasoning is never replayed into prompts.
- **Fail-closed paths:** The torn-cache check runs before the base class's auto-repair. A missing admission, request or response blocks the run. An interrupted journal blocks resume. Failure markers block analysis.

## Remaining issues

1. **Medium, causal scope:** The known arm's sentence adds the number "10" and the word "final"; the hidden arm's sentence says the end is "not disclosed", which itself signals a fixed endpoint and uncertainty. A wage effect could come from the number acting as an anchor or from how salient each wording is, not from knowing the horizon. The current limitations don't list this.
   - **Fix:** the limitations list lives in `s38_analyze.py`, which is a frozen source. Add this before the registration commit, or state it in REPORT.md.

2. **Medium, operational:** The parser accepts strict JSON only and won't strip code fences. One decision that fails three times aborts all ten games with no estimate. The auth token file `~/.codex/auth.json` is part of the checked fingerprint, so a routine token refresh also aborts the run.
   - **Fix:** before launch, check the archived invalid-response rate for gpt-6-luna in S36, and refresh the codex login right before launching.

3. **Low, failure atomicity:** `llm.chat` sleeps 5 s after a failure even with `retries=1`. The abort flag is only set after `llm.chat` returns, so the partner thread can start new calls after the transport has already failed. The data stays safe (the whole pilot aborts) but the claim that failure is serialized with admission is overstated. Wording fix only.

4. **Low, durability:** Only the admission journal is fsynced. Responses, requests and the transport-failure log are not. A crash still fails closed, but the failure record could be lost.

5. **Low:** `launch()` releases the writer lock before `main()` takes it again, leaving a brief window. `started_utc` uses a string `min` over ISO timestamps. That works with the current formats, and `analyze` rechecks it with real datetimes, but it is fragile.

6. **Cosmetic:**
   - The error "partners preserved" is misleading: the partner game also aborts and is never written; only raw prefixes are kept.
   - The overlap check runs twice.
   - Dry runs only produce wages 0–12, so the dry and mocked end-to-end runs never reach the 18–20 equilibrium region or a HIT verdict. The exhaustive economics test and `test_exact_screen` cover those separately.

7. **Low, metrics:** Total firm profit is exactly 20 minus the primary wage, so it is not independent evidence. The summary notes this; it should be kept out of any "multiple metrics agree" claim.

8. **Must fix before launch:** Git status shows every S38 file as untracked (`??`), so launch will correctly refuse to start. All sources in the manifest (including `sim/legality.py`, `sim/__init__.py`, `scripts/s16_reviews.py` and `CLAUDE.md`) and `data/s19_labels` must be committed and pushed before launch; otherwise a clean clone can't re-run the analysis.

9. **Timing:** New calls stop at 03:00 UTC, and the first call needs 7.5× the longest archived S19 block of headroom before that. I didn't check the clock; run `date -u` first. If the window has passed, record a no-run rather than moving the cutoff.

## Already acknowledged limitations (not bugs)
- Temperature and token limits aren't enforced through Codex, and the provider and effective configuration aren't attested.
- The sign-flip test is only valid if paired differences are exchangeable or symmetric.
- Multiple stage equilibria mean even a known horizon doesn't force wages up in early rounds.
- What the hidden arm believes about the horizon is unobserved.
- Five blocks, exploratory, no multiplicity correction.
- No agreement or coordination labels.
- Tool non-use is only enforced by instruction.

**Before committing the registration:** add the anchoring/salience limitation (issue 1) and complete the checks in issues 2, 8 and 9.
