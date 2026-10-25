# S38 final review

**Verdict: DUD stands. I found no bug that changes it.** I reviewed only what you pasted. I made no edits and no model calls, and I did not read the other critics' reviews.

## Arithmetic I recomputed by hand from the per-game metrics

- **Primary (r3–10 paid wage):** in every block, known equals hidden. Four blocks are 10/10 and seed 24844 is 0/0. All five differences are 0, so all 3125 bootstrap means are 0 and the bounds are [0, 0]. All 32 sign-flip sums are 0, so the inclusive upper p = 32/32 = 1. Mean ≤ 0 gives **DUD**, which matches the result file.
- **Arm summaries:** both arms are [10, 10, 10, 10, 0]. The bootstrap means are 10 − 2k, with counts 1, 20, 160, 640, 1280, 1024. The quantile positions 78.1 and 3045.9 give [4, 10]. The t-interval uses SD √20 and SE 2, giving 8 ± 2.7764·2 = [2.447, 13.553]. Both match.
- **Offered rate:** numerators 2, −6, −2, 2, 0, mean −1/40. Sign-flip p values: upper 12/16 = .75, lower 7/16 = .4375, two-sided 14/16 = .875. All match.
- **Tie rate and regret:** these match the offered-rate counts. A tie at 10 gives regret 4, a tie at 0 gives 9, and a (10, 9) split gives 4.5 per firm. So block 24841-known = 4.25. Firm profit = 20 − wage holds every round.
- **Screen redundancy:** at n = 5, p ≤ .05 forces p = 1/32, which requires all five differences to be strictly positive. That already implies a positive bootstrap lower bound. The redundancy claim is correct.

## Design and code checks

- **Horizon contrast:** the two system prompts differ by exactly one sentence. The user prompts, `productivity()` (which ignores the arm), and the payoffs are identical.
- **Known-minus-hidden direction:** consistent in the analyzer, the independent verifier, `classify`, and the report.
- **Parsers:** `parse_action` and `accepted` behave the same, including on lists, duplicate keys, NaN and booleans.
- **Terminal-wage diagnostic:** taken from the stored market value, which validation recomputes, and the independent script rebuilds it from raw responses. It is descriptive only.
- **Self-only notes:** visibility is `author == agent` in both arms. Current-round notes and wages are held back until both firms submit. The independent script checks every snapshot.
- **No model fallback:** `retries=1` with `dict.fromkeys([luna, luna])` means one transport attempt and no fallback.
- **CLI fingerprint guard:** it runs inside the admission lock before each admission and again after each response. The baseline is a deep copy, so later config writes can't move it.

## Remaining bugs (all low severity)

1. **Regeneration is fragile.** `analyze` and `present` require the working-tree hashes of `CLAUDE.md`, `pyproject.toml`, `uv.lock`, `test_s38.py` and `s16_reviews.py` to match the frozen values. Any normal later edit, such as a director change to CLAUDE.md or a `uv add`, will break canonical regeneration. **Remedy:** keep the check against the registration-commit `git show` blobs, but either drop the working-tree check for non-scientific files or document this before FINALIZE.
2. **The fingerprint misses some Codex inputs:** `~/.codex/AGENTS.override.md` and other files under CODEX_HOME (rules, skills, profile includes). This is already covered by the "unattested" limitation. **Remedy:** state these by name, or hash the whole CODEX_HOME tree except logs and sessions.
3. **The report sentence "changed mean wages by +0.000" reads as a measured effect.** **Remedy:** say "no block differed; every game sat at 10 or 0 in both arms (a focal, insensitive regime), so the screen had little room to move." Equivalence is already disclaimed.

## Acknowledged limitations (not bugs)

- The known sentence also adds the numeral 10 and final-round salience, so no knowledge or unraveling mechanism can be isolated.
- Hidden-arm beliefs about the horizon are unobserved.
- Sign-flip p values assume exchangeability.
- Codex does not enforce temperature.
- Timestamps bracket `llm.chat`, not the HTTP transport.
- `llm.chat`'s 5 s sleep can delay when the harness sees a failure.
- Only admissions are fsynced.
- Provider identity, the full effective configuration, and actual tool non-use are unattested.
- Identical paired outcomes, especially 24844 at 0/0 in both arms, suggest block-level common shocks or near-deterministic model behaviour. The keys include the system prompt, so the two arms cannot share cached responses.

## Not checked

- Raw responses and game files
- `legality.unique_object` and `reject_constant`
- `s38_exact_check`, `s38_release` and `s38_reviews`
- The figure
- The actual overlap and headroom timestamps
- The S19 data hashes
- Repository test results
- The remote clean clone
- README and HITS wording
