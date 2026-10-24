# S27 independent adversarial review

**Scope:** I reviewed only the pasted files. No edits, no model calls, and no tests run. I couldn't open `llm.py`, the S16/S24 scripts, `s27_independent.py` or the `data/s19_labels` files, so two of the items below need checking against those files.

**Verdict:** No blocking bug found. The economics, how type schedules match across arms, the exact statistics and the fail-closed lifecycle hold up. Resolve item 1 below before the registration commit, because changing the design file afterwards changes the frozen source hashes.

## Remaining bugs

1. **Medium: the design claims `max_tokens` 1024, but the code never sets it.** `Cache.call` only adds `max_tokens` when the model name starts with `glm`, and the comment there mentions a 512-token default. The pinned token limit stated in the design isn't what the code requests.
   - **Fix:** change the design to "backend default (unverified)", or pass 1024 explicitly and add it to the payload key and the config. Then check the `llm.py` default and whether codex honours it.

2. **Medium: the "conservative" runtime gate is never checked.** The gate is 1.5 × 5 × the longest S19 block. The code never compares S19's calls or decisions per game with S27's: the three-person arm needs at least 30 calls per game, all in sequence, plus retries. If S19 games had fewer sequential calls, the headroom is too small. Too little headroom ends the run without an estimate; it doesn't bias the result.
   - **Fix:** record S19 calls per game in `runtime_precheck`, and require at least 30 or scale the gate by the call ratio.

3. **Low: the prompt says "expected" for a fixed charge.** It reads "expected reviewer bonus -2 … expected 3-point charge", but the same prompt calls the charge deterministic.
   - **Fix:** "approving TYPE-Y nets the reviewer −2". This is the cheapest wording fix to make before freezing.

4. **Low: a misleading comment in `s27_analyze.py`.** It says "good rate (1/24)", but every metric uses denominator 8. The arithmetic is right; only the comment is wrong.
   - **Fix:** delete it.

5. **Low: dead code.** `cache.cache_only=resuming` is always False, because the resume path returns earlier. The `cfg['dry']` check in the final source loop is also redundant.
   - **Fix:** remove both, or keep them as harmless.

6. **Low: the HIT rule is stricter than the design says.** With five blocks, the upper sign-flip p is either 1/32 (≈ .031) or at least 2/32. A block difference of zero gives exactly 2/32. So `p ≤ .05` is met only when all five differences are strictly positive.
   - **Fix:** say this in the design and the report.

## Checks that passed

- **Economics:** approving X pays the reviewer +1; approving Y nets the reviewer −2; the author gets 6 either way. Mutual Y approval gives each partner 4, and rejecting alone saves 2. Within the pair, an approved X is worth 7 and an approved Y is worth 4. The tests check every combination of reviews and types, and pair payoffs match across arms when outsider edges are off.
- **Simultaneity:** prompts use only past rows and past notes. Notes from the current round are held back and shown the next round. Reasoning is never replayed, and the outsider sees no notes.
- **Statistics:** all 3,125 bootstrap resamples are enumerated, with exact rational quantiles. The 8-unit numerators are exact, and the HIT/ODD/DUD order matches the design.
- **Cache and replay:** torn or duplicate cache lines are refused, keys and response hashes are checked against each other, and replay must use every key exactly once without changing the files.
- **Deadline:** comparing ISO timestamp strings works because both use the `+00:00` UTC format. Fractional seconds sort correctly at the boundary.
- **Failure handling:** a failure in one game stops further admissions, both games get failure markers, and resuming or publishing is refused.

## Acknowledged limitations (not bugs)

- Team size bundles several things: the outsider, the action count, the history size and total income.
- Organisation loss and pair total bonus change mechanically between arms.
- The bonus gate is mechanically tied to approvals.
- A call admitted just before another worker fails can still finish (the gap between admission and dispatch).
- The timing and remote-push evidence come from local client records only.
- Provider sampling, internal retries and tool non-use can't be verified.
- Required empty outsider notes may cause more invalid-output retries in the three-person arm. This is only reported descriptively.
- Five blocks, one model, synthetic task types, and adverse approvals don't show an agreement.
