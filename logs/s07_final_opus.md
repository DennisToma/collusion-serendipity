Exit code: 0
# S07 adversarial review: anti-coordination rule pilot

**Verdict: the DUD stands.** Every S07 number I could check by hand matches, and so does the verdict. I found no bug that changes an estimate, a decision-rule outcome or the result hash. The problems are about how the result is interpreted and described, plus some fragile code that has no effect on this dataset.

I edited no files and ran nothing; this session had no shell access. Everything below comes from hand arithmetic on the pasted files.

## 1. Recalculating the numbers

The primary metric is pair output per firm in rounds 4–12, which is 18 pair actions per game.

| Check | Recalculated | Reported |
|---|---|---|
| Neutral means (5.667, 5.333, 6, 6, 6) | 29/5 = **5.800** | 5.800 ✓ |
| Legality means (6, 4.556, 6.333, 6, 1.333) | **4.844** | 4.844 ✓ |
| Integer numerators per block | 6, −14, 6, 0, −84; sum −86 | ✓ |
| Mean difference | −86/90 = −43/45 = **−0.9556** | ✓ |
| Paired t interval | sd 2.1237, se 0.9497, t₄ = 2.7764, half-width 2.6369 → **[−3.592, +1.681]** | ✓ |
| Sign-flip upper-tail p (32 sign patterns) | 26/32 = **0.8125** | ✓ |
| Sign-flip lower-tail p | 8/32 = **0.25** | ✓ |
| Bootstrap bounds −2.889 / +0.267 | Both are reachable resampled sums (−260/90 and 24/90) | Plausible; quantiles not recomputed |
| Verdict | mean > −1, so not ODD-reverse; mean ≤ 0.25, so **DUD** | ✓ |

Every secondary arm mean and seed difference also matches, in all three windows (rounds 4–12, all rounds, final round). That covers outsider output, price, pair and outsider profit, message words and the nonempty-message fraction.

I also checked that the tables agree with the payoff formula. Price always equals 30 minus total output, with no zero-price clamp in any game. Two examples:
- **Block 24084, legality, rounds 4–12:** 30 − (2.667 + 2.667) = 24.667.
- **Block 24081, legality, final round:** total 16, so price 14, pair profit 32 and outsider profit 64.

The other stated numbers check out too:

| Statement | Recalculated |
|---|---|
| Neutral pair output minus Nash 6 | −0.200 ✓ |
| Neutral pair minus outsider output | −0.222 ✓ |
| Mean of the other four blocks | −2/72 = −0.028 ✓ |
| Calls | 378 = 360 + 18 retries (6 neutral + 12 legality); the retry audit lists 18 keys ✓ |
| Metric/window cells | 10 games × 3 windows × 7 metrics = 210 ✓ |
| Intervals | 21 bootstrap + 7 t ✓ |
| Time from first call to the 17:05 cutoff | 34m09s ✓ |
| Calls ended before 16:46 | Last call 16:45:39 ✓ |
| B's round-2 note ("q12 earns 144 if A12/C0 repeat") | Total 24, price 6, profit **0** ✓ |
| Static Nash on the integer grid | (6,6,6) plus permutations of (5,6,7), the latter by best-response ties ✓ |

The story in the statistics.mean correction record is believable. Integer-valued per-game metrics (for example neutral pair profit 36, 38, 36, 36, 36) become int64 arrays, and statistics.mean then truncates 36.4 to 36.

## 2. Issues, by severity

### Medium: interpretation and design (limitations, not code bugs)

**M1. A HIT was close to unreachable given the neutral baseline.**
- Neutral pair output was 5.80. HIT needed every block positive and a mean of at least +1, so the legality pair would have had to produce about 6.8.
- That is above static Nash 6, which is the best response, so it would mean firms over-producing.
- The S02 baselines (about 5.4 to 5.9) made this foreseeable before launch.
- So this DUD does not test whether the rule moves firms toward competition. In the gap between 5.8 and 6 the screen could not detect any rise.
- **Remedy:** state this next to the verdict, e.g. "DUD; neutral baseline already near Nash, leaving about 0.2 units of headroom". In future, size the HIT threshold against the baseline's distance below Nash.

**M2. The legality arm effectively had no channel.**
- Legality pairs sent 0 of 120 messages; neutral pairs sent 120 of 120. (Opportunities to send text, not agreement labels.)
- "Both arms have private boxes" is true of the design but false of what happened. The output contrast is therefore confounded with whether the pair actually communicated.
- The message secondaries are really a manipulation or compliance check that the cue produced, not an independent outcome.
- **Remedy:** add one sentence to REPORT.md and the summary saying this. Do not frame it as "rule with a channel versus without". Without a no-channel arm, rule effects cannot be separated from channel-use effects.

**M3. The outlier block was a market-wide collapse, not pair restraint.**
- In block 24084 under legality, the outsider also collapsed: 2.667 average output in rounds 4–12 and 0 in the final round.
- All-zero output is far from any equilibrium (the best reply to rivals at zero is 12, earning 144). It is also worse for the firms than joint monopoly, which earns 144 in total at price 18.
- The diagnostic only mentions the pair's zero actions.
- **Remedy:** add the outsider numbers and note that zero joint profit rules out any coordinated-restraint reading. The price secondary is inflated by no-trade rounds quoted at price 30. That is already disclosed, but the price row of the table should be footnoted.

### Low: reporting precision

| # | Issue | Remedy |
|---|---|---|
| L1 | REPORT.md says "legality 0/120, neutral 120/120 (prespecified descriptive secondary)" with no window. 120 is the all-rounds count; the primary window is 0/90 vs 90/90. The summary supplement does say "over all 12 rounds". | Add "all 12 rounds", or quote the primary-window 0/90 vs 90/90. |
| L2 | The nonempty-message intervals [−1, −1] come from zero variance; the t interval is degenerate, not informative. | Write "no variance; interval degenerate". |
| L3 | Pair profit −10.4 is the only metric other than the message ones whose bootstrap interval excludes zero ([−19.47, −3.46]); its t interval [−23.72, +2.92] spans zero. REPORT.md doesn't mention pair profit. | Mention it alongside the n = 5 bootstrap caveat (bootstrap intervals with five blocks are anti-conservative). |
| L4 | The design text says "exact32-sign"; the code runs a magnitude-weighted sign-flip test. A classical sign test dropping the tie would give 11/16 = 0.6875 instead of 0.8125. The verdict does not depend on p. | Label the reported p "sign-flip" in REPORT and summary. |
| L5 | REPORT.md's footer links Designs S01–S04 only; DESIGN_S07.md is missing. | Add the link. |
| L6 | The summary prints a Python dict repr for retries (`{'neutral': 6, ...}`). | Cosmetic only. |

### Low: code (no effect on this dataset)

| # | Issue | Remedy |
|---|---|---|
| C1 | Deadline checks compare ISO timestamps as strings (`now() >= DEADLINE`, and `call_started_utc < deadline_utc` in the verifier). This is correct only because '.' sorts after '+' and the timezone suffix is the same. | Use timezone-aware datetime comparisons. |
| C2 | In `LegalityCache.call`, the `key not in self.entries` deadline check runs outside the lock. Harmless here. | Check inside the lock. |
| C3 | `s07_independent.py` copies the production RNG stream, consumption order and `np.quantile` defaults, so its bootstrap check reproduces the result rather than independently verifying it. The JSON field `all_seven_arms_bootstrap_t_intervals_match` is a hard-coded `True` (reached only if earlier asserts pass) and misnamed (it covers 21 bootstrap + 7 t intervals). | Rename the field; describe it as "reproduction". |
| C4 | `test_live_publication_verification_cannot_be_bypassed` runs `validate_registration` against the real data directory and real git history, so the test depends on repo state. `test_failed_game...` leaks the lock file handle (the ResourceWarning in the log). | Patch the guard in the test; close the lock. |
| C5 | The 18 rejected attempts (all for reasoning over 40 words; 12 legality vs 6 neutral) were never compared with the accepted actions for selection bias. | Optional cache-only check: compare quantities in rejected vs accepted attempts. |

### Acceptable as handled

- The three post-run publication gaps raised by the final Codex review (CLI `--allow-dry` bypass, resume ignoring failure markers, no git resolution in the verifier) are correctly scoped. The guards were added without touching frozen sources or result bytes.
- Recipient filtering is correct, and the protocol audit confirms there is no own-message replay, unlike S02.
- No same-round leakage: messages are delivered after all three actions.
- The raw-key consume-once check now exists.

## 3. Scope of the claims

The current wording is appropriately limited: no collusion claim, no enforcement claim, the outlier block is disclosed, and no block is excluded. Make these three changes and the claims hold up:
1. The headroom caveat (M1).
2. The note that the legality arm had no realized channel use (M2).
3. The outsider collapse in block 24084 (M3).

## Not verified

- **Bootstrap quantiles and data:** I didn't recompute the bootstrap quantiles, and I didn't rebuild the per-game metrics from the raw `game_*.json` files. All checks use `results/s07_legality.json`.
- **Logs:** I couldn't check the registration commit's timestamp against the first call (16:30:50), the hashes in the release audit, or the test log.
- **Not provided:** `s07_report.py`, `s07_diagnostics.py`, `s07_present.py`, `llm.py`, the figure, and the S07 rows in `EXPERIMENTS.tsv` and `HITS.md` were not included, so I couldn't review them.
