# S42 review: surprise employer entry

**Verdict: the frozen DUD is correct.** I found no high- or medium-severity bugs. I could not run code in this session and the raw rate choices were not provided. I rebuilt the arithmetic by hand from the per-game cells in `results/s42_entry.json` and the inlined code, without reading the other critics' reviews.

## Arithmetic, recomputed

- **Primary.** All five entry-minus-control differences are exactly 0. All 3125 bootstrap means are 0, so both bounds are 0. All 32 sign flips equal the observed sum of 0, so the upper, lower and two-sided p-values are each 32/32 = 1. The mean of 0 is ≤ 1, so the result is DUD. ✓
- **Offered wage.** In units of 1/12 the differences are −1, −3, −1, −1, −2 (numerators −60, −180, −60, −60, −120; mean −2/15). I expanded (3+x+x²)⁵ to count resamples: 1 at sum −15, 5 at −14, 25 at −13 and 70 at −12. Positions 78.1 and 79.1 both fall at −12/60, so the lower bound is −1/5. The top 243 resamples sit at −1/12, which covers position 3045.9, so the upper bound is −1/12. Sign flips give 32/32, 1/32 and 2/32. The t interval works out to s = 0.0745, se = 0.0333, t₄ = 2.7764, giving [−0.2259, −0.0408]. ✓
- **Stage regret.** All three firms at 10 gives 17/3. A profile like (9,10,10) also gives (9+4+4)/3 = 17/3. The duopoly gives 4, so the difference is 5/3, or 1200/720. Sign-flip p-values are 1/32, 1 and 2/32. ✓
- **Wage, profit and ties.** The tie rate is 1, which matches profiles with at least two firms at 10. Profit plus wage always equals 20. All denominators are multiples of 60, which divides 720. ✓
- **Economics.** I checked these by hand rather than running all 441 and 9261 profiles. Duopoly pure Nash is (18,18), (19,19), (20,20); triopoly is (19,19,19) plus 61 profiles with at least two firms at 20, which makes 62. ✓
- **Runtime gate.** 1.5 × 5 × 156.728 = 1175.46 s required. Remaining time was 04:15:00 − 03:03:54.009 = 4265.99 s. ✓
- **Screen.** At n = 5, upper p ≤ .05 forces p = 1/32. That requires all five differences to be strictly positive, which also makes the bootstrap lower bound positive. The design's "redundant gate" statement is correct. ✓

## Protocol checks

- **Entry timing.** `turn>=5` means entry at round 6. The primary uses `rows[6:10]` (rounds 7–10), pre-entry uses `rows[:5]`, and the terminal wage uses `rows[-1]`. ✓
- **Same prompts before entry.** Pre-entry prompts are identical across arms; a test asserts this. ✓
- **Simultaneity.** Notes are added to the shared list only after all firms in a round have chosen. ✓
- **Entrant visibility.** The entrant sees all public history and an empty notepad, and notepads are self-only in both arms. ✓
- **Contrast direction.** Entry minus control in both scripts. The independent script names the lists `no` and `yes`, which is confusing but correct. ✓
- **Parsers.** The two parsers are logically equivalent, except that `unique_object` and `reject_constant` in `sim/legality.py` were not shown. ✓
- **Verdict and report.** The frozen verdict logic is mirrored independently. The REPORT row and summary match the JSON and describe the SD=0 degeneracy honestly. ✓

## Remaining issues (all low severity)

1. **Weak advance cue.** The system prompt says "All currently active firms…" from round 1 in both arms. It doesn't bias the comparison, but it weakens "no advance notice." *Fix:* say so in the limitations.
2. **Fingerprint gaps.** Other files under `~/.codex` (profiles, prompts, skills, files referenced from `config.toml`) are not hashed. *Fix:* hash the whole `CODEX_HOME` tree, or name these gaps explicitly.
3. **Brief lock gap.** `launch()` releases the writer lock before `main()` takes it again, leaving a short window. The one-shot receipt and the exclusive file creation (`open('x')`) make this practically harmless.
4. **No per-firm breakdown.** The shortfall in offered wages (8 units across 5 games) can't be attributed to the entrant or to an incumbent. *Fix:* add a per-firm-role descriptive table. Don't promote it to a result.
5. **Prompt check copies the template.** The independent check reuses the same prompt text, so it verifies how prompts are put together, not their wording. This is already acknowledged.

## Already acknowledged limitations (not bugs)

- Entry bundles several changes and draws are fresh rather than forked.
- The wage of 10 is far below Nash in both arms and is not shown to be collusion.
- Bootstrap and t intervals are degenerate.
- Sign-flip validity needs an exchangeability assumption.
- Per-firm averages cover different populations after entry.
- Risk from `auth.json` refreshes, and provider settings and tool non-use are unverified.

The pre-entry wage (10 vs 10) and the difference-in-differences (0) are trivially zero. They support reading the result as no change from a common baseline and should not be promoted.

## Not checked

- Raw responses and requests, or the per-round rate choices themselves.
- Hashes against the registered Git objects, the origin-clone check, and the test suite (`test_s42`).
- `sim/legality.py`, `sim/cournot.py`, `s42_reviews.py`, `s42_release.py`, and the figure.
- Real timestamps for call overlap and block barriers.
