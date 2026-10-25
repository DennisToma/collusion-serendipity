# S35 adversarial review

**Verdict: ODD is correct and reproduces. I found no high-severity bugs in the code shown.** This session had no shell or local file tools, so I recomputed everything by hand from the per-game metrics you pasted. I did not reconstruct the raw rate choices.

## Arithmetic, recomputed independently

- **Arm means and primary.** The asymmetric arm averages 97.25/5 = 19.45 and the symmetric arm 59/5 = 11.8. The block differences are 10, 9.125, 0, 9.125, 10, so the primary mean is 153/20 = 7.65. The numerators over 32 are 320, 292, 0, 292, 320. All match.
- **Bootstrap, all 3125 ordered samples, by count.** Each block is drawn with probability 1/5 for the 0, 2/5 for a 9.125 and 2/5 for a 10.
  - Lower bound: 0.025 × 3124 = 78.1. Sorted positions 78 and 79 both fall in the 3.825 band (positions 61–140), so the lower bound is 153/40. ✓
  - Upper bound: 0.975 × 3124 = 3045.9. Positions 3045 and 3046 fall in the 9.825 band (positions 2933–3092), so the upper bound is 393/40. ✓
- **Sign flips (32 patterns).** Because one difference is zero, two patterns reach the observed sum: upper p = 2/32 = 0.0625, lower p = 1, two-sided p = 4/32. ✓
- **Paired t.** Standard deviation 4.2988, standard error 1.9225, t(0.975, 4) = 2.7764, giving [2.312, 12.988]. ✓
- **Screen.** The mean is at least 4 and the lower bound is above 0, but p = 0.0625 > 0.05, so it is not a HIT. Neither DUD condition holds, so the result is ODD. ✓ The summary is right that, with n = 5, the screen is equivalent to all five differences being strictly positive. Once any block ties, HIT is impossible because p can be no lower than 2/32.
- **Per-game consistency.** Each game's wage, offered rate, profit, tie and regret values can be produced by a valid rate sequence. Example: seed 24721 asymmetric fits six ties at 19, one tie at 20, and one round at (19 low wins, 18). Every metric total divides evenly by 32.

## Economics

I enumerated the equilibria by hand.
- Symmetric 20/20: (w,w) is an equilibrium only if 19 − w ≤ (20 − w)/2, which means w ≥ 18. Rate pairs that differ are never equilibria. That leaves (18,18), (19,19), (20,20). ✓
- Asymmetric: tied rates below 20 fail because the high firm gains by raising one unit. That leaves (19,20) and (20,20), both paying 20. ✓

## Truth, simultaneity and visibility

- Both prompts are built from the state before the round. Notes are added only after both firms submit.
- Each firm sees only its own notes in both arms: `prompts` filters on author, and the independent verifier checks all 200 snapshots.
- With an empty history, the user prompts are identical across arms and the system prompts differ only in the revenue map (checked by test).
- Replay, all three parser attempts, abort on any failure, refusal of a torn cache, refusal to resume an interrupted run, and the immutable CLI baseline (deep-copied before use) all look sound.

## Remaining issues

1. **Medium — interpretation of the result.** In 4 of 5 blocks the symmetric arm sits at a (10,10) tie. That is neither an equilibrium nor joint-profit-maximising (that would be a wage of 0), and each firm gives up 4 per round. The asymmetric arm is at or near equilibrium. So the +7.65 mostly measures the symmetric arm falling *below* the competitive wage, not asymmetry raising wages. **Fix:** add one sentence to REPORT.md and the summary. The pattern matches S31's degenerate 10.000, but don't present S35 as a replication of it.
2. **Low–medium — gaps in the CLI fingerprint.** It doesn't cover `NODE_OPTIONS`, proxy variables (`HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`), `SSL_CERT_FILE`, `~/.codex/auth.json`, other files under CODEX_HOME, or any AGENTS.md above the temp directory. That contradicts the stated scope of covering "routing inputs". **Fix:** list these as unfingerprinted in the limitations. Re-hashing now would only show the current state, not what was true during the run.
3. **Low.** `notes.written=100` is hard-coded, not counted. It is implied by the assertion of 20 notes per game, but should be counted or labelled as asserted.
4. **Low.** `cache.cache_only=resuming` never takes effect because the resume branch returns earlier. The replay patch targets `sim.common.llm.chat`; that still works because it is the same module object.

## Already acknowledged (not bugs)

Five blocks with no power guarantee; the sign-flip test needs exchangeability; productivity changes both incentives and wording; the cap of 20 compresses the asymmetric arm; model and provider are self-reported; tool non-use is not verified.

## Not checked

- Raw `responses.jsonl` and `requests.jsonl`, and the game files.
- The 200-key replay.
- Actual call times against the 01:50 cutoff and the 60-second / overlap checks.
- The `s35_exact_check`, `s35_reviews` and `s35_release` scripts.
- Test-suite results, the figure, and the state of origin and a clean clone.
