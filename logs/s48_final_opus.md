# S48 review (from the supplied text only)

**Verdict:** I found no bug that changes the DUD outcome. The only discrepancy is wording in REPORT.md about which part of the rule produced the DUD.

## Reconstruction
I could not re-parse the 20 raw response texts because the archive wasn't supplied. Instead I worked from the 20 booleans recorded per case in `results/s48_notes.json`.

- **Approval counts:** retain is 4/10 (24480B, 24481C, 24482B, 24484A). Erase is 4/10 (24481C, 24482A, 24482B, 24484A).
- **15 block cells:**
  - Retain: [.5, .5, .5, 0, .5], mean 2/5.
  - Erase: [0, .5, 1, 0, .5], mean 2/5.
  - Retain−erase: [.5, 0, −.5, 0, 0], mean 0.
- **3125 bootstrap draws, counted by hand in half-units:**
  - Contrast: the sum −3 covers sorted indices 16–110, so both quantile indices 78.1 and 3045.9 give **[−3/10, +3/10]**.
  - Retain: **[1/5, 1/2]**.
  - Erase: the counts expand as (2+2x+x²)⁵ = 32, 160, 400, 640, 720, 592, 360, 160, 50, 10, 1, which gives **[1/10, 7/10]**.
  - All three match.
- **t95 intervals:** ±.4390, [.1224, .6776] and [−.1194, .9194]. All match.
- **32 sign flips:** contrast upper .75, lower .75, two-sided 1.0. Retain .0625/1/.125 and erase .125/1/.25. All match.
- **Verdict and match counts:** mean ≤ .05 gives DUD. The archived-match counts of 7/7 also check out.

## Integrity checks: no bugs found
- **Case selection:** the code picks the last round where `passed[partner]` is false in rounds r3–r10 and asserts `statuses[partner]=='TYPE-Y'`. It uses exogenous task status only. The independent script rebuilds the partner task schedule from the RNG string, which is a real cross-check. Each partner has 4 TYPE-Y primary rounds, so a case always exists.
- **Retain vs. erase prompts:** retain is the exact archived prompt. Erase keeps the bytes outside the notes snapshot unchanged: the code checks the markers are unique, checks the snapshot serialisation is canonical, and keeps the author-filtered order. Own notes and public history are preserved, and the unit test checks the head and tail are identical.
- **Boolean outcome:** the parser requires a strict unique-key schema, the partner as the only key and a real boolean. NaN is rejected. Notes and reasoning are never replayed.
- **Source and registration:** registration commit e6ddcde equals remote main, observed at 05:02 UTC, before the 06:15 deadline. There are no partial runs, retries or fallbacks; with `retries=1`, the backend is pinned to a single model name.

## Weaknesses and acknowledged limitations
1. **DUD came from the mean rule, not precision.** The bootstrap upper bound (.30) is above the .25 threshold, so the data do not rule out a reduction of the registered size. REPORT should say outright that this DUD is not evidence of no effect. The present wording ("a degenerate interval is not equivalence") doesn't fit, because this interval isn't degenerate.
2. **Run-to-run noise is about as large as any effect.** Fresh retain draws on byte-identical prompts disagreed with the archived action in 3 of 10 cases. There is one draw per cell and only 2 of 10 pairs are discordant, one in each direction.
3. **The HIT bar is effectively .5, not .25.** Any zero block forces p ≥ 2/32, and blocks move in steps of .5. So a HIT needed every block ≥ .5, meaning a mean of at least .5. The design notes that all five must be positive but doesn't spell out what that does to the bar.
4. **The model check is circular.** `response['model']` echoes the requested name, so it can't confirm which model actually served the call. This is already listed as unattested.
5. **The independent script isn't fully independent.** It reuses the case manifest and doesn't re-check request/response hashes or `accepted.jsonl`; `validate` covers those. I couldn't inspect `s48_reviews.py` or `s16_reviews.py`.
6. **Erasing partner records while saying both notepads are readable** may come across to the model as the partner having gone silent. This is acknowledged.
7. **The fresh retain baseline didn't disappear** (4/10 fresh vs. 5/10 archived). So that caveat in the design doesn't apply, although block 24483 is 0 in both arms.

No mediation or long-run claims were found; the report language stays within scope.
