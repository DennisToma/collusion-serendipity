# S35 adversarial review: one blocking gap, no fatal bugs

I reviewed only the pasted source. I didn't run the tests, make edits or call any model.

**Checked and correct:**
- **Economics:** payoffs, tie splitting and the equilibrium sets are right. Symmetric equilibria are (18,18), (19,19), (20,20); asymmetric are (19,20) and (20,20).
- **Prompts:** the two arms' prompts differ in exactly one revenue entry.
- **Simultaneity:** both firms are prompted from the same history; notes are only added after both submit; each firm sees only its own notes; reasoning is never fed back.
- **Arithmetic:** every metric is an exact multiple of 1/32. The quantile method matches NumPy's default. With n=5, the sign-flip p-value is ≤.05 only when all five differences are strictly positive (p=1/32), so the bootstrap gate adds nothing.
- **Cache and replay:** replay must use every key exactly once, the raw bytes must be unchanged, and torn or mismatched files are rejected. No lock path can deadlock.

## Bugs, by severity

1. **Medium-high: the final publication check has never been run.**
   - `analyze()` runs its whole live-only branch only for live data. That branch covers the launch, dispatch and completion receipts, the S19 runtime recompute, `verify_transport_and_preflight`, the block-overlap check and the merge-base check. Dry runs skip it.
   - `test_zero_actual_overlap_rejected` imports `verify_transport_and_preflight` but calls `validate_call_overlap`, which `analyze()` never uses.
   - Under your no-rerun rule, one hidden error in this branch would make a perfectly good live dataset unpublishable, with no way to recover.
   - **Fix:** before registering, run a full simulated live test. Mock `llm.chat` to return non-dry responses with the right model and backend, fix the clock before the cutoff, and supply fake launch receipts and S19 files in a temporary git repo. Run `main → analyze → independent → present` end to end. Also have `verify_transport_and_preflight` call `validate_call_overlap` so the tested code is the code that runs.

2. **Medium: one bad decision can abort the whole pilot.** If any one of the 200 firm-round decisions gets 3 invalid replies, all five blocks are lost. With a per-attempt invalid rate p, the abort chance is 1−(1−p³)²⁰⁰: about 2.5% at p=.05 and about 18% at p=.10. A reply wrapped in a ```` ```json ```` code fence counts as invalid.
   - **Fix:** before launch, measure gpt-6-luna's invalid-reply rate from the S31–S34 caches and record it. If it is above about .05, decide now whether the risk is acceptable.

3. **Low: misleading variable names in `analyze()`.** `control` holds the asymmetric arm and `treatment` the symmetric one. The sign of the difference is still correct (asymmetric − symmetric, which the independent check confirms), but rename them.

4. **Low: the independent check under-reports what it checks.** It reports `sign_sets=5`, but it actually checks 15 sign tails, which is what the design promises. Report 15 under its own label.

5. **Low: brief lock gap at launch.** `launch()` releases `.writer.lock` before `main()` takes it again, leaving a short window for a second writer. The launch receipt is single-use, so the impact is small. Keep the lock held through `main()`.

6. **Low:**
   - Failure markers are written non-atomically.
   - Several time checks compare ISO strings instead of using `utc()`. They work today because one function produces every timestamp, but that is fragile; use `utc()` everywhere.
   - The final `cfg['dry']` loop in `analyze()` is redundant.

## Known limitations (already acknowledged, not bugs)
- Codex ignores the temperature and token limits; which model actually served, and whether tools were used, can't be verified. The read-only sandbox still lets the model read the filesystem.
- Changing one productivity value bundles different incentives with a role difference (high vs. low firm), so a HIT can't separate ordinary best-response from collusion. Low wages don't show agreement.
- The fixed cap of 20 binds the high-productivity firm. The ≥4 screen is a heuristic, not a decomposition of equilibrium selection.
- With n=5, the bootstrap intervals are only descriptive and undercover. The sign-flip test needs exchangeable or symmetric differences. There is no power guarantee.
- The headroom rule assumes S19 timing carries over; S19 games had ≥30 calls vs. 20 here, so it is conservative.
- The 01:50 UTC admission cutoff is self-imposed. If the launch slips past roughly 01:50 minus the required headroom, the pilot can't run at all.

**Verdict:** I'm not cleared to launch until bug 1 is fixed, because it decides whether a live archive can ever be published. Bug 2 needs a recorded go/no-go decision. The rest are cosmetic or limitations the design already states.
