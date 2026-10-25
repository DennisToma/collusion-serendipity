# S61 review: no blocking bugs; the DUD verdict and all reported numbers reconstruct

This review uses only the supplied text. I made no edits, no calls, and did not read other critics.

## Independent reconstruction (anchor/repeat/swapped per case)

| Block | Case 1 | Case 2 | Anchor | Repeat | Swapped | Swap mismatch | Repeat mismatch | Excess |
|---|---|---|---|---|---|---|---|---|
| 24480 | B 1/1/1 | C 0/0/0 | .5 | .5 | .5 | 0 | 0 | 0 |
| 24481 | A 0/0/1 | C 1/1/1 | .5 | .5 | 1 | .5 | 0 | +.5 |
| 24482 | A 1/1/1 | B 1/1/1 | 1 | 1 | 1 | 0 | 0 | 0 |
| 24483 | B 0/0/0 | C 0/0/0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 24484 | A 0/1/0 | B 0/0/0 | 0 | .5 | 0 | 0 | .5 | −.5 |

- **Counts:** approvals are 4/5/5 and mismatches 1/1. Matches with the archived decisions are 9/8/10. All of these agree with the JSON.
- **Exact bootstrap (3,125 draws, by generating polynomials over half-units):**
  - Contrast: (x⁻¹+3+x)⁵ gives cumulative counts 1/16/111, so index 78.1 falls at S=−3 and the bounds are **[−3/10, 3/10]** ✓.
  - Anchor: (2+2x+x²)⁵ gives **[1/10, 7/10]** ✓.
  - Repeat: **[1/5, 4/5]** ✓. Swapped: **[1/10, 9/10]** ✓. Both mismatch metrics: **[0, 3/10]** ✓.
- **Paired t intervals:** the half-widths for contrast, swap, anchor and swapped are .4390, .2776, .5194 and .6208. All six intervals match ✓.
- **Sign flips (32):** contrast upper/lower/two-sided p = .75/.75/1 ✓. Anchor .125/1/.25 ✓. Repeat .0625/1/.125 ✓. Swapped .125/1/.25 ✓. Mismatch metrics .5/1/1 ✓.
- **Verdict:** the mean is 0, which is ≤.05, so the result is **DUD** ✓. Only the mean criterion triggers it; the bootstrap upper bound is .30, which is not below .25. The REPORT row and paragraph match the result file.

## Code against design

- **Selection:** `turn=max(t∈2..9, partner not passed)` uses task statuses only, and the independent script rechecks it from the RNG schedule. The case selection does not depend on outcomes ✓.
- **Swap:** `\b[ABC]\b` maps only the two active IDs. Notes such as `A\u2019s` (an escaped apostrophe) are safe because the backslash creates a word boundary, and JSON hex escapes contain no A/B/C. Swapping is an involution, preserves length and is asserted at request time. The output schema follows the swap, and `target_case` decodes the reviewed role without inversion ✓. The independent tokenizer (`\W+` split) uses the same definition of `\w`, so it is a separate implementation but not an independent definition. That is acceptable.
- **Repeat:** the recorded request is byte-identical to the anchor ✓. `fixed_model` collapses the codex fallback list to luna, and `retries=1` means there are no hidden retries ✓.
- **Guards:** failure/abort ordering, the fsync of each response before parsing, the reservation file with `open('x')`, the registration with `HEAD==remote` and the headroom checks all match the design. Registration was observed at 09:08:30, giving about 1h51m of headroom ✓.
- **Not verifiable from the supplied text:** the raw response text, `execution.jsonl` timing, the attempt and launch receipts, and whether git origin actually equalled HEAD. I am trusting `validate` and the release receipt on these points.

## Bugs
I found none that affect the numbers or the verdict. One cosmetic issue: the summary table prints raw float lists, e.g. `[-0.11942531684178381, …]`. Rounding them would read better.

## Acknowledged limits (correctly disclosed, not bugs)
- **Coupled, asymmetric anchor.** Choosing a different reference changes the descriptive picture. Repeat-vs-swapped disagreement is 2/10 (24481 A and 24484 A), compared with anchor-vs-repeat at 1/10. This shows how much the anchor choice adds variance. It is unregistered and must not be promoted.
- **Blind spot of the estimand.** The expected excess is (q−p)(1−2p), which is zero at p=.5. Most contexts look near-deterministic here, but the 24481 A and 24484 A contexts are exactly where p may be intermediate.
- **Five blocks, with mirrored contexts.** Block 24483 contains the same history twice (both TYPE-Y at turn 9), so it is not two independent observations.
- **Bundled cues.** The swap changes both the IDs and their alphabetical/serialization order. Call position is unbalanced: swapped is in the middle in 3 blocks and anchor never. Codex runs in a fresh working directory for each call, and provider identity/caching is unknown.
- **Archived matches are context only.** Swapped matched 10/10 versus anchor 9/10. That difference must not be read as the swap giving "more faithful" decisions.

## Claim scope
REPORT is suitably narrow. One recommended fix: add to the REPORT S61 paragraph itself, not only the summary file, that the bootstrap upper bound of 0.30 exceeds .25. That means **a .25 excess effect is not ruled out**, and DUD here means "below the screen's mean threshold," not invariance. The footer's general no-equivalence sentence covers this only implicitly.

## Overall
There is no blocking methodological or implementation mismatch. All 30 approvals, the 30 block cells and the 6 summaries reconstruct exactly. The DUD verdict is correct as registered, and its scope is honestly limited.
