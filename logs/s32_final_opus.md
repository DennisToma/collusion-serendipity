# S32 independent review: the ODD verdict stands, with no blocking bugs

I made no edits and no model calls. I had no shell in this session, so I recomputed everything by hand from the per-game metrics in `results/s32_resource.json`, not from the raw rate choices.

## Arithmetic, checked independently
- **Per-block primary differences (human minus compute):** 10−10, 19.75−10, 19−19, 19.875−10 and 19−19.625. In units of 1/32 these are [0, 312, 0, 316, −20]. They sum to 608, so the mean is 608/160 = **19/5 = 3.8**. This matches.
- **Sign flips (32):** the two zero blocks contribute a factor of 4. Of the 8 sign patterns on 312, 316 and −20, only 648 and 608 are ≥ 608, so upper p = 2/8 = **0.25**. Lower p = 7/8 and two-sided p = 4/8. All match.
- **Bootstrap bounds (3,125 ordered resamples):**
  - Lower position is 78.1. 51 resamples sum below −40, and the 80 resamples at exactly −40 cover indices 51–130. So the lower bound is −40/160 = **−1/4**.
  - Upper position is 3045.9. The top 32 resamples are all-high, then 10 resamples sum to 1264 (indices 3083–3092) and 40 sum to 1260 (indices 3043–3082). So the upper bound is **63/8**. Both match.
- **Paired t interval:** the standard deviation is 5.4947 and t(4) = 2.7764, giving **[−3.023, 10.623]**. This matches.
- **Verdict:** the lower bound is not above 0 and p = 0.25 > 0.05, so it is not a HIT. The mean is above 0.5 and the upper bound is above 2, so it is not a DUD. **ODD is correct.**
- **"HIT is equivalent to all five differences strictly positive":** proven. A zero block ties its own flip and a negative block's flip beats the observed sum, so p = 1/32 exactly when every block is positive. That also forces every bootstrap mean above 0, so the bootstrap gate adds nothing.

## Economics, rules and simultaneity
- **Pure equilibria:** (18,18), (19,19) and (20,20) are the only ones, and they are weak. Asymmetric profiles fail because the lower firm can match or overbid, and (20,19) fails because the high firm drops to 19. Profiles of 17 or below fail because raising by one pays more than splitting.
- **The 10/10 profile:** each firm earns 5 and has a regret of 4. This matches stage_regret = 4.0 in every 10/10 game, so it is a non-equilibrium focal outcome.
- **Single-phrase contrast and visibility:** the system prompts differ only in the identity sentence. Each user message gets only that firm's own notes, the same way in both arms. Notes are appended only after both firms submit, so neither firm sees the other's current choice. The test file and `expected_prompts` both encode this.

## Remaining issues
1. **Medium, interpretation.** The primary is driven by whether a pair stays at the 10/10 focal point; compute stayed there in 2 of 5 blocks. So "higher human payment" really means "less firm-side coordination at 10," not "labor valued more." Remedy: one sentence in REPORT/summary saying so.
2. **Medium, blinding.** The disclosure says prefix rates and notes were exposed to the manager while the games ran. I did not read `logs/s32_review_disposition.md`. Remedy: state explicitly that no abort, continue or analysis decision depended on what was seen.
3. **Low, secondary outcome.** The stage_regret bootstrap interval [−2.875, −0.0375] excludes 0 while its sign-flip p is 0.0625. Remedy: label it "not promoted" in the summary.
4. **Low, fingerprint coverage.** The fingerprint misses AGENTS.md files in the parent directories of the temp working directory, Codex profile/auth/rules files, and changes between the guard check and the actual subprocess call. This is consistent with the stated "prospective, known inputs" scope; it would only matter if an attestation claim were made.
5. **Cosmetic.** The source-drift check at completion is duplicated, and the `if cfg['dry']: continue` in the analyzer is redundant.

## Acknowledged limitations (not bugs)
- n = 5, with a sign-flip test that assumes exchangeable differences.
- Seeds fix only the pair labels, so pairing is by timing only.
- Firm profit is mechanically 20 minus payment, so it is not separate evidence.
- Provider execution and tool non-use are not attested; draws are uncontrolled.
- No fairness or agreement inference is drawn.

## Not checked
- Raw `responses.jsonl` and `requests.jsonl`, the game files, and the replay.
- The S19 runtime receipt contents beyond its arithmetic (4291 s remaining vs 1175 s required is consistent).
- Whether the tests pass, the remote clean clone, and byte-identical regeneration.
- The disposition log and the other critics' reviews.
