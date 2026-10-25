# S43 adversarial review (supplied text only)

**Basis.** I used only the text you supplied. I made no edits or paid calls, ran nothing and did not read other reviews. The raw archive wasn't available, so I rebuilt everything from the 20 per-case quotes in `results/s43_payoff.json`, not from the raw `responses.jsonl`.

## Independent reconstruction: all match
- **15 block cells:**
  - Control: 9.5, 10, 10, 10, 10, mean 9.9.
  - Table: 10, 10.5, 10.5, 10, 10, mean 10.2.
  - Contrast: 0.5, 0.5, 0.5, 0, 0, mean 0.3.
- **Bootstrap (3125 draws, counted exactly from binomial composition counts):**
  - Contrast: k-ones counts 32/240/720/1080/810/243. The interpolation positions 78.1 and 3045.9 give **[0.1, 0.5]**.
  - Control: **[9.7, 10.0]**. Table: **[10.0, 10.4]**.
- **Sign flips (32):** the contrast exceeds the observed sum only when all three nonzero blocks keep a plus sign, so p = 4/32 = **0.125**. Both arms give 1/32.
- **Paired t95:** SD = √0.075, half-width 2.7764 × 0.12247 = 0.3400, giving **[−0.040, 0.640]**. The arm intervals [9.622, 10.178] and [9.860, 10.540] also match.
- **Descriptive counts:** floor counts are 0/0. Archived-quote matches are 9 (control) and 8 (table).
- **Verdict:** mean 0.3 < 1 and upper bound 0.5 < 1, so **DUD** is correct. No HIT was possible: with two zero blocks the smallest attainable p is 0.125.
- **Payoff table logic:** both implementations give share 0 below the top rival offer and 1/(1 + number of tied rivals) otherwise. Against rivals at [10] or [10, 10], 11 gives profit 9 versus 5 or 10/3 at 10. This is consistent with the 4→1-unit amendment.

## Remaining bugs (minor; none changes the verdict)
1. **"Empirical bootstrap" label.** `summary()` computes percentile bounds. If "empirical" means the basic method (2·mean − quantile), the control arm would be [9.8, 10.1], not [9.7, 10.0]. The contrast and table arms happen to be identical either way. Rename the label or define it.
2. **`fixed_model()` does nothing.** It sets `CODEX_CHEAP` to the value it already has. The model is pinned only because `_codex` dedupes to one name. The comment overstates what this guards against.
3. **The independent verifier shares assumptions with the main code.** It takes rival rates from `rows[8]` exactly as `select_cases` does. It also gets its verdict from the result's float `ci95` rather than its own exact bounds (these were cross-checked first, so it's harmless). It's a separate reconstruction, not an independent derivation, which the docstring already says.
4. **Ambiguous table wording.** "own_profit is your profit for this one round" could be read as real rather than hypothetical. The preceding sentence partly fixes this.

## Acknowledged limits (correctly stated)
- **Case selection:** cases were chosen after reading S42 explanations, but not by action. All ten archived quotes were 10.
- **The table is a bundle:** it changes arithmetic, fixed-rival salience, length and row order together. It isolates no mechanism.
- **Outcome is the focal offer:** rivals weren't rerun, and the report, summary and figure all say these are offers, not worker pay.
- **Unattested runtime:** the model identity is the requested label, sampling and token settings weren't enforced, tool non-use is unattested, and `source_fingerprint_matches = false`. The fresh control arm, not the archived source, is the comparator, so this mainly limits transfer.
- **Small sample:** n = 5 blocks gives a coarse sign test, and there's no equivalence claim. A null doesn't show that payoff information is irrelevant.

## Not verifiable from the supplied text
- The per-response strings, request bindings, timestamps and concurrency.
- The RNG 4343 schedule.
- Round-9 rival offers (presumably 10, but not shown).
- S42 source hashes, the registration commit on origin, and the release and clone receipts.

The registration time (03:32:24) leaves about 58 minutes before the 04:30 cutoff, which meets the 20-minute requirement. Launch and first-admission headroom need checking in `execution.jsonl`.

**Bottom line:** The DUD verdict, the numbers and the choice of unit hold up. No blocking bugs; only the labeling and comment fixes above.
