**Verdict: I found no remaining blockers.** I checked only the source in your message. I didn't run the tests or touch the repo, and made no calls.

**Requested fixes, confirmed**
- **Dry offset:** the dry adapter adds 10 once (`quantity+10`), and `s37_independent` does the same. Nothing else adds an offset.
- **KEYS:** every loop now uses all five `KEYS`, so `KEYS[:-1]` is gone.
- **Preflight order:** `main()` calls `cache.before_live()` before the `ThreadPoolExecutor` starts, after the `start` journal entry. On that first call it checks HEAD and the registered sources, runs `runtime_precheck`, and writes `raw/dispatch_preflight.json` once with mode `'x'`. The first real admission then re-checks headroom from that receipt while holding `admission_lock`. `verify_transport_and_preflight` enforces the order launch → start → dispatch check → first admission.
- **Parsers and stage enumeration:** both parsers accept 10..30, and the −1..31 sweep tests them. The exhaustive test covers 441 profiles × 2 firms × 21 deviations = 18,522 and gets Nash at (28,28), (29,29), (30,30). The analyzer's regret loops over 10..30 and the independent one over net 0..20, which is the same set. The narrower dry grid doesn't affect any of this.
- **Synthetic labels:** dry text is exactly `'dry'` / `'dry note'`, and the replay check matches it. The mocked live run uses rate 20, which gives 200 calls and a DUD verdict. Dry output can't be published to the canonical paths.
- **Frozen screen:** `classify` in both scripts matches DESIGN: HIT checked first, the same DUD condition, and a denominator of 32 (regret half-integers /16 → /32).

**Acknowledged limitations (not blockers)**
- The independent prompt check copies the literal prompt, so it doesn't count as independent authorship or semantic validation.
- Provider settings, the model actually served and tool non-use are unattested.
- A heavy-preflight failure leaves a start-only journal, which blocks any rerun. That fails closed.
- Two minor test nits: an unused import in `test_zero_actual_overlap_rejected`, and `written=100` is hardcoded but correct.
