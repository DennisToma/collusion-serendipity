# S44 adversarial review (from the supplied text only; no raw archive, no edits, no calls)

**Verdict:** I found no blocking bug in the supplied design or code. It is fit to launch, subject to two minor items below.

## Checks that pass
- **Causal scope.** The design limits itself to a row-order screen. It makes no claims about anchoring, collusion or population prevalence, and the outcome is the focal offer (0–20), not realized worker pay. `s44_present.py` labels it the same way ("offer, not realized wage").
- **Source-case selection.** The 225 requests and 225 responses match one-to-one: equal counts, a duplicate-free key set and set equality. The focal firm is `sorted(assigned_pair)[0]` at payload `[run,9,agent,0]`, so selection never looks at an action. The code checks that the response hash matches, that round-9 public quotes equal `rows[8]` prices, that recomputed round-9 share and profit equal the archived values, that the archived quote equals the round-10 action, and that the 9 notes all come from the focal owner. Selection is post hoc, as stated.
- **Intervention isolation.** Both arms share the system prompt, the prefix (history and notes), the header, the rival list (no firm IDs) and the tail. Only the order of the 21 rows reverses. The test checks reversal equality and that the prompts are identical once the rows are removed. No recommendation is given.
- **Payoff table.** Shares are 0 below the top offer and 1/(1+ties) at or above it. This is checked against `sim.entry.outcome` for all 462 rival profiles × 21 wages, and `s44_independent.py` recomputes it with a separately written formula.
- **Schedule and arithmetic.** 5 blocks × 2 parallel workers × 2 sequential views = 20 calls, with at most 2 in flight. First-view order is exactly opposite within each block. The validator checks view order, seed barriers and concurrency, and timing-mutation tests exercise all three.
- **Inference.** Values are on a half-unit scale, and the bootstrap and sign-flip results are enumerated exactly. A HIT needs an upper p of 1/32, so it needs all five blocks strictly positive: a zero block gives p = 2/32 > .05. This matches the design. The HIT-first order and the DUD/ODD rules are coded correctly.
- **Failure, cache and registration integrity.** One-shot `open('x')` receipt, writer lock, abort on first failure, raw responses fsynced before parsing, no resume of a partial archive, and HEAD equal to `ls-remote` plus a clean `git diff` before any call.

## Remaining concrete bugs and risks (minor)
1. **Writer lock vs. clean clone.** `run()` creates `data/s44_payoff/.writer.lock` during the release check. If that file is neither committed nor gitignored, the `git status --porcelain` assertion in `clean_clone()` fails. I couldn't verify which it is from the text.
2. **Zero-length intervals.** The concurrency sweep drops intervals where start equals end. With coarse timestamps, a call could escape the concurrency check. This is unlikely to matter.
3. **Environment not registered.** The `environment` versions (python, numpy, scipy) are recorded in `config.json` but not in the registration receipt. The runtime fingerprint is also unregistered; it is only compared with S42's.
4. **`fixed_model()` is a no-op.** `CODEX_CHEAP` is already `gpt-6-luna`, so the context manager changes nothing. It is harmless, but it is not evidence that the model was pinned.
5. **Cross-pilot fragility.** `CLAUDE.md`, `llm.py` and `uv.lock` are in `SOURCES`. Any later edit by another iteration or the director makes `validate` fail at HEAD. The design acknowledges this ("return to the frozen checkout"), but the release check must run before any such edit.
6. **Spurious fail-closed.** `auth.json` is fingerprinted. If the Codex token refreshes mid-run, the pilot aborts as "drift" without any real change in the science.

## Acknowledged limits (not bugs)
- Provider identity, settings and tool non-use are not attested; temperature and max_tokens are not transmitted to Codex.
- n = 5 blocks; descriptive bootstrap bounds can degenerate; the sign-flip test assumes symmetry.
- Row order changes both position and recency at once; there is shared-service interference; selection is post hoc and not held out.
- A directional DUD does not exclude an opposite-direction effect.
- `s44_independent.py` was written by the same author, so it is a separate reconstruction, not independent verification.
- Timestamps come from the local clock, not a server attestation.
- Reproduction depends on the frozen checkout and the existing venv.
