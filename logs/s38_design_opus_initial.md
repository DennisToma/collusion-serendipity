# S38 adversarial review

I read the code statically. I made no edits, ran nothing and made no model calls. I did not receive `s38_reviews.py`, `s38_release.py`, `s38_exact_check.py`, `sim/legality.py` or `sim/cournot.py`, so I did not review them.

## Checks that passed
- **Economics:** the exhaustive 441-profile check gives the pure Nash profiles (18,18), (19,19) and (20,20). Firm profit plus worker pay equals 20 in every round.
- **Simultaneity:** both prompts in a round are built before `chat` or `rows` are updated, so neither firm sees the other's current choice or note.
- **Denominators:** every metric difference is an exact multiple of 1/32. Regret has the finest denominator, which sets this. The `Fraction(str(float))` conversion round-trips exactly for these values.
- **Statistics:** the linear quantile over 3,125 equally weighted bootstrap samples matches NumPy's default. The sign-flip count and p-values are correct.
- **Screening rule:** at n=5, an upper p ≤ .05 holds only if all five differences are strictly positive. That makes the bootstrap-lower gate redundant, as `s38_present` says.
- **Replay:** it reconstructs every key, consumes each key exactly once and checks the raw files are byte-identical afterwards.

## Remaining bugs
1. **HIGH: one test is broken.** `test_raw_quote_and_normalization_tamper_rejected` searches for `game_*_gross.json`, a filename left over from S36. S38 has no such files, so `next()` raises `StopIteration` and the suite fails. This blocks the required "repository tests" step. `test_s38.py` is in `SOURCES`, so the fix must be committed before registration; editing it afterwards makes `analyze` fail its source-drift check forever.
   - Remedy: search for `game_*_known.json`, and remove the dead `_gross` branch from the dry adapter.
2. **MEDIUM: the 03:00 UTC admission cutoff may already have passed.** Today is 2026-10-25 and I could not check the clock. If it is past 03:00, the launch correctly refuses. Moving the cutoff would need a new registration committed before launch, never after.
3. **MEDIUM: guard overhead is large and not in the runtime estimate.** `fingerprint()` hashes the node binary and the native codex binaries twice per call: once while holding `admission_lock` and once after the response. That is about 400 hashes of large files. The first admission also runs `runtime_precheck` and about 22 `git show` calls while holding the lock. All of this slows and serializes both arms, and the S19-based headroom estimate doesn't include it.
   - Remedy: time a mocked run with the real `fingerprint()`, or skip rehashing a binary when its stat (size, mtime, inode) is unchanged.
4. **LOW-MEDIUM: the wrong ancestor directories are fingerprinted.** The code hashes `AGENTS.md`/`CLAUDE.md` above the repo, but `_codex` runs `codex exec -C <fresh temp dir>`. The relevant instruction lookup is under `$TMPDIR` and `/`.
   - Remedy: fingerprint the temp-dir ancestors, or reword the claim.
5. **LOW: the "actual transport" check isn't independent.** `verify_transport_and_preflight` repeats `validate_call_overlap` on the same `call_started_utc` timestamps. Those are recorded before the subprocess starts, so neither check sees the actual transport.
   - Remedy: rename the check, or drop the "actual" wording.
6. **LOW: the reasoning-effort setting is unregistered.** `_codex` hard-codes `model_reasoning_effort=low`, and `DESIGN_S38.md` doesn't mention it. The `model` field in each response is copied from the request, so it does not confirm what the provider actually ran.
   - Remedy: record both points in `DESIGN_S38.md`.
7. **LOW: leftover S36 text in the prompts.** The system prompt still says "Tax and subsidy are automatic…" right after stating that neither exists. It is identical in both arms, so it can't bias the contrast, but it may confuse the model. `s38_present` also says "procurement-equivalent / passive resource".
   - Remedy: fix these before freezing, or list them as a known wart.
8. **LOW: small lock gap at launch.** `launch()` releases `.writer.lock` before `main()` takes it again.
9. **LOW: dry runs only cover wages 0–12.** The dry adapter draws wages from 0..12, so the tamper and replay tests never reach the high-wage tie and Nash region (13–20). The exhaustive economics test does cover it.

## Already acknowledged (not bugs)
- Five blocks only, a descriptive bootstrap that is anti-conservative at this sample size, and no multiplicity correction.
- The sign-flip test is valid only under exchangeability.
- Multiple equilibria mean there is no unique finite-horizon prediction.
- Beliefs are not observed. The "known" prompt also reveals the game length and makes the final round salient, so the contrast mixes those with the endpoint itself.
- Temperature and token limits are not enforced, and actual tool non-use is not verified.
- A legitimate `auth.json` refresh aborts the pilot. This is a real operational risk over a run of several hours.
- No agreement or intent labels.

## Verdict
**Not ready to launch.** Fix item 1 before registration, confirm item 2 against the real clock, and measure item 3. Items 4–7 are wording or registration fixes, which must also be made before the freeze. After that, the core economics, simultaneity, statistics and screening rule hold up.
