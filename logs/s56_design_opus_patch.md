# S56 adversarial review: supplied text only

**Verdict:** The game theory and the summary math are correct. The problems are in what the provenance claims say versus what the code actually checks. I made no edits, tool calls or model calls, and I had no access to the raw archive or to `s14_*`, `llm.py` or `s56_reviews.py`.

## Verified correct
- **Payoffs:** `(min−6)/n` for the lowest bidders, zero for everyone else. The production and independent implementations are written separately, and the bid validation catches `7.0` and `True` before the cache can confuse them with `7` and `1`.
- **Nash census:** I checked by hand that static pure Nash payments are {6,7}. Either two bidders are at 6, or the profile is (7,7,7); (6,7,7) fails because the lone 6 profits by raising to 7.
- **Stable set:** The asserted set `{(a,b,6): min(a,b)=6} ∪ {(7,7,7)}` is right. (8,8,6) and (7,7,6) fail because the outsider gains by raising its bid. (c,c,c) with c≥8 fails because undercutting pays when c>7.5.
- **Pair-total vs strict gain:** These are kept apart correctly. (18,20,20) has positive joint regret but no strict gain; (20,20,10) has a strict gain.
- **Wording:** The report says the stability notion is not a strong equilibrium and that zero joint regret does not rule out a profitable single-member deviation. Both caveats are correct and stated clearly.
- **Bootstrap:** All 3125 resamples, with floor-plus-linear interpolation (same as numpy "linear"). It matches between the two implementations. 8 metrics × 3 = 24 summaries and 48 intervals, all reported the same way.

## Concrete bugs or gaps
1. **The S14 replay isn't implemented in the code shown.** `analyze()` re-runs `s14_analyze` (the statistics) and `s14_independent.check`. Nothing re-executes the game to confirm that every request key reproduces. A cached replay that goes through `llm.chat` would also fail under the patch. Either `check()` does the replay (please show it) or the design overstates.
2. **"Byte-equivalent as parsed JSON" is the wrong description.** Python dict equality treats `1`, `1.0` and `True` as equal. Call it "parsed-JSON equality".
3. **The freeze may miss imported files.** `llm.py` (the patch target), `scripts/__init__.py` and possibly `scripts/s14_analyze.py` are frozen only if they appear in `cfg['sources']`. Assert them explicitly.
4. **Some published fields are never verified independently.** `verify(r)` ignores `registration`, `registration_receipt` and `source_validation`. During `--release` it also checks the in-memory object, not the serialized file, so a JSON round-trip change would slip through. Only the separate `__main__` run reads the file.
5. **The receipt is self-attested and can block retries.**
   - `register_remote` creates the receipt with `open('x')` *before* calling `checked_manifest()`. If that check fails, the receipt stays behind and blocks any retry.
   - At release, nothing re-checks the receipt against the remote.
   - The receipt is never confirmed as committed.
6. **The raw-binding test can't catch a wrong payload layout.** The lookup key is `payload[5:9]` by position, and the synthetic fixture copies the same layout. Also:
   - Only the last attempt's bid is bound to a game row.
   - Request prompts are never compared to game state.
   - Earlier failed attempts are never shown to be invalid.
7. **Profit checks use exact float equality.** `list(map(float,...))==archived` will fail loudly if S14 stored rounded profits such as 4.333. That fails safe, but check it before the release run.
8. **Missing tests:**
   - commit bytes differ, receipt not an ancestor, or remote mismatch;
   - an original S14 result mismatch;
   - the `llm.chat` patch actually firing;
   - production `analyze()` end to end (all tamper tests only exercise the independent verifier);
   - an extra or missing game file (fails with `KeyError` rather than a clear rejection).
9. **Latent:** `cached_decompose` returns a mutable dict and list from the cache. Nothing mutates them today.

## Acknowledged limitations (not bugs)
- Post-hoc, run on data already inspected, n=5 blocks, with degenerate or uncorrected intervals and no equivalence claim.
- Static counterfactuals with no policy rerun and no real transfers.
- Patching `llm.chat` doesn't block OS-level network or process use.
- Provider identity is unattested, and reusing the installed venv is disclosed.
- The bootstrap differs from S14's original 10,000-draw bootstrap, which is disclosed.
- `coalition_stable` and `strict_pair_improvement` are partly determined by `above_nash`, which the report text notes.

**Interpretation risk:** A profile counts as "coalition-stable" only at payment ≤7, which is competitive, near-zero profit. Readers may read a low stable fraction as evidence of collusion. Keep the "context only, no label" wording right next to metric 7 in the summary.

**Priority before release:** fix #1 (implement or show the replay), then #3 and #5, then add the tests in #8.
