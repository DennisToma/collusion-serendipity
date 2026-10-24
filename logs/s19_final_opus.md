# S19 adversarial review

**Verdict: DUD is correct and reproduces from the published numbers. I found no blocking bug.** I worked only from the material you pasted. I made no edits or live calls and read nothing else in the repo.

## Recomputed by hand (all match `results/s19_labels.json`)

- **Primary:** the per-block differences are [0, 0, 1, 1, 1] approvals out of 8. The mean is **3/40 (0.075)**, from 0 of 40 normative versus 3 of 40 neutral approvals.
- **All 3125 bootstrap resamples:** the resampled mean depends only on how many of the five draws hit a positive block. That count runs from 0 to 5 with 32, 240, 720, 1080, 810 and 243 resamples (total 3125). Sorted positions 78–79 fall in the "1 positive draw" group, giving a lower bound of **1/40**. Positions 3045–3046 fall in the "5 positive draws" group, giving an upper bound of **1/8**. Both match.
- **Paired t interval:** the standard deviation is 0.068465 and the standard error is 0.030619. With t₀.₉₇₅,₄ = 2.77645 the interval is **[−0.0100, 0.1600]**. Matches.
- **All 32 sign flips:** the two zero blocks don't change the sum. An upper result needs all three ones positive, which is 4 of 32 = **0.125**. The two-sided count is 8 of 32 = 0.25 and the lower p is 1.0. Matches.
- **Screening rule:** HIT fails because 3/40 < 1/4. DUD is triggered because the bootstrap upper bound 1/8 < 1/4. **DUD is correct.** The pair-bonus gate is 7/20 (differences 0, 0, 0.5, 0.5, 0.75 per block).
- **Secondary outcomes spot-checked:**
  - Selectivity: bootstrap [1/40, 7/40], sign-flip p = 1/8.
  - Organization loss: bootstrap [0, 1], p = 1/4.
  - Normative pair bonus: lower bound 277/20.
  - Economics: if every positive submission is approved, total bonus is 21 per round, split 14 to the pair and 7 to the outsider. One negative approval moves the pair by ±0.5 or the outsider by +0.75, and costs the organization 1.25 per round. All consistent.
- **Truth and simultaneity:** the code builds each round's prompts from completed rounds only. Notes written in a round are held back until the next round, and the round-numbering filter is correct. The deadline and timestamp string comparisons sort correctly, including when microseconds are omitted. The launch receipt passes: 2608 s remaining against 1207 s required, and the registration commit equals HEAD (f64d98d).

## Remaining issues

1. **Medium (operational): the release isn't committed yet.** `data/s19_labels/`, `results/`, `figures/` and `logs/s19_*` are all uncommitted. The clean-clone reproduction the design requires can't be shown until they are. *Fix:* commit and push, then run the clean-clone replay and save its receipt.
2. **Low: the independent check doesn't independently check the prompts.** `s19_independent.py` rebuilds histories, statuses and notes, but not the system-prompt wording for each arm. That wording is only checked by a replay that reuses the same `prompts()` function. *Fix:* scan all 300 saved requests and assert that PASS/FAIL/defective/incorrect never appear in the neutral arm, that TYPE-X/TYPE-Y never appear in the normative arm, and that the payoff sentences match.
3. **Low (wording): "positive bootstrap excludes zero" in `REPORT.md`.** With n=5 and 3 of 5 blocks positive, a percentile bootstrap lower bound above zero is nearly automatic. *Fix:* call it a descriptive resampling property, not evidence.
4. **Cosmetic:** the `REPORT.md` footer links only S18 artifacts. There is also dead code (`cache_only=resuming`, a duplicated abort check), which was already noted in the review dispositions.

## Acknowledged limitations (not bugs)

- Once two blocks show zero difference, HIT is impossible: the sign-flip p can't go below 1/8.
- The framing change is bundled: label meaning, explanatory wording, and TYPE-X/TYPE-Y order and valence all change together. The neutral arm also still uses the word "charge".
- Notes are endogenous and may carry the effect.
- No agreement or intent is verified.
- n=5, one model, no correction for multiple tests.
- Sign-flip assumes the block differences are exchangeable; API draws and the shared service are uncontrolled.
- Model and backend are client-side metadata only.

## Not checked

- The raw game files and the 300 request/response records, so the raw review decisions themselves weren't recounted beyond the per-game metrics. The figure was not checked either.
- `s19_release.py`, `s19_checked_independent.py`, `test_s19_publication.py`, `legality.py`, `s19_present.py`.
- The final reviewer logs, the EXPERIMENTS/HITS/STATUS diffs, whether the source hashes match the files on disk, and whether the tests pass.
