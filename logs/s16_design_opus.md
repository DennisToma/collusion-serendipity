# S16 adversarial review (static read only)

I read `DESIGN_S16.md`, `sim/notes.py`, `scripts/s16_analyze.py`, `scripts/test_s16.py`, `scripts/s16_independent.py` and the inherited `common`/`advisor`/`legality` code. I didn't run the tests. I didn't see `s16_launch.py`, `s16_progress.py`, `s16_release.py`, `s16_reviews.py`, `s16_economics.py` or `s16_request_audit.py`, so anything that depends on them is marked as unverified. The S16 files are still untracked in git, so no calls have been made yet and anything below can still be fixed before registration.

## Things that checked out
- **Timing:** notes written in round t only become visible in round t+1. Current-round bids and notes stay hidden until everyone has submitted, and reasoning is never replayed.
- **Arm differences:** the outsider's prompts are the same in both arms. The only system-prompt difference is the one visibility sentence.
- **Provenance:** the code refuses to repair a torn cache before the base class could truncate it. It checks that responses and requests match and that each key matches its payload hash. Replay must use every key exactly once, which also checks model and backend through the payload.
- **Inference:** sums, the bootstrap bounds (which match numpy's linear quantile) and the sign-flip test use exact integer/fraction arithmetic. `classify` uses the exact bounds. The profit gate is exact and matches the independent checker. HIT is evaluated before DUD, and the test cases cover this.
- **Interrupted runs:** the start/complete journal, failure markers and cache-only resume all fail closed as the design describes.

## Remaining bugs (most important first)
1. **Prespecified descriptives aren't computed by the frozen analysis.** The design promises note sent/nonempty/available counts and retries by arm and role. `s16_analyze.py` doesn't produce any of them, and neither does the independent checker. If a presentation script outside the manifest computes them, they're unfrozen and unchecked. Fix: add them to `analyze()` and to `check()`.
2. **The manipulated sentence is ambiguous.** The shared arm says "Both files are readable by you and this firm." "This firm" has no clear referent and could be read as the agent itself. That makes it unclear whether each member knows its own notes go to the partner. Fix: "Your file and firm {partner}'s file are both readable by you and by firm {partner}." Do this before registration and update the canary test.
3. **A race at the deadline can reject a complete dataset.** `TenderCache.call` checks `now() < DEADLINE` before `super().call`, but `call_started_utc` is recorded later inside `Cache.call`. A call that passes the check at 20:14:59.99 can be stamped 20:15:00.01. `validate_game` then fails its `call_started_utc < DEADLINE` check and the whole run can't be published. The chance is small, but the effect is total. Fix: take the timestamp once and use it for both the check and the record, or compare against the check time in the analysis.
4. **"Push before calls" isn't enforced or checked.** `main()` only requires the sources to be clean against HEAD. Neither `main()` nor `analyze()` checks that the registration commit is on origin, or that it predates the journal start. This may be done in `s16_launch.py` (unverified), but that file isn't in the manifest. Fix: in `main`, check `git merge-base --is-ancestor HEAD origin/main` (or similar) before writing the journal start, or record the push evidence.
5. **Minor:** `analyze()` never compares `cfg['environment']` with the current environment. It also doesn't check that `registration_commit` is an ancestor of HEAD. A "byte-identical rerun" could therefore run under different numpy/scipy versions without being noticed.

## Operational risks (not bugs)
- **Strict parsing with identical retries.** A model that keeps wrapping its JSON in a code block, or keeps writing more than 40 words of reasoning, fails all 3 attempts and aborts the whole pilot. A dry run can't detect this. It's tolerable if S14 used the same parser on the same model without failures.
- **The 20:15 UTC cutoff.** There are at least 360 sequential calls, two games at a time, across five blocks with a barrier between each. A late launch will very likely hit the cutoff and produce an unpublishable run. Check the launch time against the expected per-call time first.
- **The abort stops the partner game too.** A failure in one game stops the other game in its block at its next uncached call. So "completed partner retained" only holds if the partner had already finished.

## Acknowledged limitations (correctly scoped, not reported as bugs)
- The treatment bundles access wording, partner content, context length and endogenous writing. It doesn't show an actual agreement.
- With n=5, HIT effectively needs all five block differences to be positive: a single zero gives p = .0625. DUD doesn't mean equivalence.
- The sign-flip test assumes the paired slots are exchangeable. Seeds don't control API sampling. The randomized submission order is effectively a no-op, since both games start within microseconds of each other.
- Model, backend and temperature come from what the client reports, not provider proof. Both games share the same service and can interfere.
- One model, homogeneous costs, split ties, full public bid disclosure, and multiple exploratory pilots with no pooling.

**Scope of claims:** the design wording is appropriately limited. Keep REPORT wording to "partner-readable notes (bundled)" rather than "communication causes collusion". Don't present a HIT as confirmatory.
