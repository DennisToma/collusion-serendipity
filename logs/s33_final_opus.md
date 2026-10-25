# S33 final adversarial review

**Verdict: no concrete bugs found, and DUD is the correct classification.** I couldn't run anything (Bash is disabled in this session), so I didn't reconstruct statistics from the raw `game_*.json` files. Everything below is my own hand arithmetic on the reported per-block counts plus a code read.

## Arithmetic I checked by hand (all match)
- **Primary means:** baseline Y approvals 2+2+2+1+3 = 10/40 = 0.250. Amnesty 3+1+2+3+3 = 12/40 = 0.300. The per-block differences (−1, 1, 0, −2, 0)/8 sum to −2/40 = −0.050.
- **DUD gate:** the mean −0.05 ≤ 0.05 and the bootstrap upper 0.05 < 0.25, so it's a DUD both ways. The HIT gate fails on the mean alone.
- **Sign flips:** the nonzero |d| values are 1, 1, 2, and the two zero blocks just multiply each outcome by 4. That gives upper 7/8 = 0.875, lower 3/8 = 0.375, two-sided 6/8 = 0.75. All match.
- **Paired t interval:** sum of squared deviations 0.08125, sd 0.1425, se 0.0637, t₄ 2.776, giving −0.05 ± 0.177 = [−0.227, 0.127]. Matches.
- **Secondary metrics:** bonus and organization loss are exact multiples of the primary (×4 and ×10), so their identical p-values are expected. Reports: −29/40 and lower p = 1/32 are consistent.
- **Bootstrap bounds:** the index arithmetic is correct: 0.025·3124 = 78.1 gives (9·o[78] + o[79])/10, and 0.975·3124 = 3045.9 gives (o[3045] + 9·o[3046])/10. Both bounds land on achievable sums (−7 and +2). **I did not enumerate the 3125 resamples myself.**

## Implementation (code read)
- **Penalty rule:** `outcome()` matches the design's formula, 3 − 3·(own report ∧ partner adverse) + 6·(partner report), applied only to adverse approvals and only in amnesty.
- **Metric agreement:** `metrics()`, `s33_independent.py` and the diagnostic all agree with `outcome()`.
- **Diagnostic identities:** its assertions (`6·qualifying/40 = extra`, `3·eligible/40 = waived`) are algebraically correct.
- **Privacy:** `observable_row` deletes `report` from trajectories. The history in prompts omits reports, but it shows charges, so an extra 6 charge reveals a partner's report. The design says this.
- **Independence caveat:** the "independent" script was written by the same agent and copies the frozen schedule logic, so it mainly guards against coding slips. It is not a second pair of eyes on the design.

## Diagnostic labelling
- **The script is properly labelled.** Its docstring and `scope` field say POST-OUTCOME and descriptive, and it never changes the frozen result.
- **REPORT.md says "post-outcome" only in the link text.** The text itself ("limits interpretation… does not isolate deterrence or establish a backfire") avoids mechanism, backfire and intent claims.
  - Small fix: put "post-outcome" in the opening words (e.g. "**S33 exposure (post-outcome):**").
  - "despite 29 flags" hints that charges were expected. "while" would be more neutral.
- **No causal-null claim:** degenerate bounds are explicitly said not to show zero risk or equivalence. OK.
- **A substantive limitation worth stating in REPORT.md:** zero charges in primary rounds means the amnesty payoffs never actually fired. The amnesty arm differs from baseline only in wording and report behaviour (29 flags vs 0), not in realised payoffs. So the DUD tests a *threat* package, not one that was ever enforced. The diagnostic implies this but doesn't say it. Also, 6 flags came from reporters who were themselves approving the partner's Y submission. That should be described, not interpreted.
- **Warmup spillover:** the one qualifying warmup report puts a public extra charge into later history for one game, so the arms' histories differ there. Minor, and it isn't mentioned.

## Bugs vs acknowledged limitations
- **Bugs:** none found.
- **Acknowledged limitations:** the bundled intervention, n = 5, a single model, unattested provider and configuration, and tool non-use not verified.
- **New but minor:** the two wording points above, plus the payoffs never firing in primary rounds being implicit rather than stated.

## Not checked
- Raw game records against the reported counts.
- The 3125-resample bootstrap enumeration.
- The replay and cached-resume claims.
- Test-suite results.
- The remote-clone reproduction.
- The figure.
- Note and reasoning contents (privacy leaks inside free text).
- The 128 stage-case tests.
