# S36 adversarial review (read-only: no edits, no model calls)

**Verdict:** the economics, statistics, simultaneity, cache replay and screening rule hold up. I found no bug that invalidates the design. Two medium issues should be fixed before the registration commit, because every file in `SOURCES` is frozen after launch.

## Checked and correct
- **Economics:** the shift g = n + 10 maps all 441 profiles and every unilateral deviation to identical shares and profits. Nash is (18,18), (19,19), (20,20) in both arms, which the exhaustive test confirms. Regret and offered rate are computed on the full grid and in take-home units. The prompt text is truthful: notes really are self-only, and current-round actions stay hidden until both firms submit.
- **Arithmetic:** denominator 32 holds for every metric. Tie profits are halves, and summed regret over 16 firm-rounds gives at most /32. The quantile rule over all 3,125 bootstrap samples matches NumPy's linear method.
- **Screening rule:** a block difference of 0 is unchanged by a sign flip, so it can only push p up. The smallest p is 1/32 and needs all five blocks strictly positive, so HIT ⇔ mean ≥ 2 and 5/5 positive, as the design says. The bootstrap gate adds nothing beyond that, and the summary already says so.
- **Replay:** reconstruction under `cache_only` re-runs the parser, which proves that rejected and accepted attempts match the stored responses. Key and SHA bindings, every-key-exactly-once use and byte-identical cache files all check out.
- **Failure handling:** abort is serialized with admission, and I found no path that sets abort while holding `admission_lock`, so no deadlock. A start-only journal blocks resume.

## Remaining bugs
1. **MEDIUM — wrong limitation gets published.** The `limitations` list in `s36_analyze.py` says the CLI fingerprint *omits* NODE_OPTIONS, proxies, certificates and authentication. `s36_runtime.fingerprint()` actually hashes all of them, and DESIGN says so too. This false text flows into the results JSON and the summary. **Fix:** say what is really missing: other `CODEX_HOME` files, ancestor AGENTS.md files under the temp directory, and provider-side configuration.
2. **MEDIUM (could abort the whole pilot) — `~/.codex/auth.json` and `config.toml` are in the per-call fingerprint.** The guard runs before and after every call. If codex refreshes its OAuth token or writes a notice flag to `config.toml` mid-run, the fingerprint changes and the run ends with no estimate. **Fix:** hash only stable fields (auth mode, account id), or check that these files stayed byte-stable during the S35 run and record that as an accepted risk.
3. **LOW — the independent verifier doesn't check seat assignment.** `s36_independent.verify` computes the seeded `pair` but never asserts `active == pair` in A/B/C order. It also derives `values` from the data rather than the seed. Add both asserts.
4. **LOW — the overlap check isn't really independent.** `verify_transport_and_preflight` repeats the work of `validate_call_overlap`. The preflight chronology is tested only through the mocked end-to-end run; no unit test fails a bad receipt order.
5. **LOW — heavy hashing inside the admission lock.** Before each admission, the guard hashes node, the native codex binary and 21 sources while holding the lock. This is probably harmless, but it delays the second game's first call. Check the start gap against the 60 s window on the dry/mock timing.
6. **LOW — minor code issues.**
   - `cache.cache_only=resuming` is dead code (resuming already returned).
   - `launch()` releases the writer lock before `main()` takes it again, leaving a short race window (single operator, so low risk).
   - `scripts/s16_reviews.py` is in `SOURCES`; confirm that's intended.

## Known limitations (already acknowledged)
- Gross quoting bundles new labels, tax/subsidy wording and arithmetic together, so anchoring isn't isolated.
- Codex ignores temperature and max tokens; the model identity is self-reported by our own wrapper; tool non-use is unverified.
- With n = 5, the bootstrap intervals are descriptive only; sign-flip p needs exchangeability.
- There's no agreement or collusion ground truth.
- The headroom gate uses S19's 30+-call games, which is conservative for S36's 20 calls.
- **Risk:** strict JSON with no tolerance for code fences, max 3 parse attempts, and a whole-pilot abort on failure. Check S31–S35 retry rates for gpt-6-luna before committing to this.

## Before you launch
- Run `date -u` and confirm the first admission can happen before **02:20 UTC** with the required headroom. I didn't check the clock.
- Fix #1, and fix or explicitly accept #2, **before** the registration commit.
