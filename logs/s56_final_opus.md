# S56 adversarial review (based only on the supplied text)

**Scope:** I couldn't access the raw S14 archive, so I didn't rebuild anything from raw requests or responses. That means I haven't confirmed the 360 raw bindings, the 376 requests, the replay of the original S14 analysis, or the file hashes. What I did check: I recomputed the numbers from the published round records and worked out the 3375-profile census by hand. I made no edits, made no model calls and read no other reviews.

## Verified

- **Payoffs:** `profits`, `payoff` and `sim/tender.outcome` give the same results. I recomputed every regret and profit for these rounds and all match: (20,19,19), (19,19,19), (18,19,19), (19,19,18), (19,19,17), (14,16,14), (20,20,20), (20,19,20), (6,7,7) and (7,7,6).
- **The 80 game cells:** 24200-private, 24202-private and 24203-none match exactly for pair regret (105/2, 193/6, 88/3), outsider regret (69/2, 401/6, 236/3) and pair profit (77/2, 455/6, 263/3). Arm totals per 45 rounds also match: above-Nash 9→18, stable 29→19, strict-both-gain 14→19, payment 395→500.
- **Census:**
  - 44 static pure-Nash profiles: 43 where at least two bids are 6, plus (7,7,7).
  - 30 fixed-pair/singleton stable profiles: (a,6,6) and (6,b,6), plus (7,7,7).
  - 2141 strict-both-gain profiles: I derived this analytically by summing over outsider bids 7 to 20 (198, 174, 151, 158, 140, 148, 134, 144, 134, 146, 140, 154, 152, 168). It matches exactly.
- **Sacrifice vs. Pareto gain:** The code handles these separately and correctly. Because there are no transfers, both pair members can only gain at once through a tie, and both implementations get this right. Example: (18,19,19) has zero pair regret and no strict gain.
- **Summaries:** The means for payment (79/9, 100/9, 7/3), stable fraction (29/45, −2/9) and above-Nash (1/5) are correct. I recomputed the above-Nash t95% interval and got [−0.839, 1.239], which matches. The 3125-draw bootstrap result for payment, [−5.6, 10.0], agrees with `source_validation` from the original S14 independent checker, a third implementation. There are 24 summaries (48 intervals) and 80 cells.
- **REPORT claims:** Every S56 number in REPORT.md matches the JSON. The claim that all contrast intervals span zero holds for all 16 intervals (bootstrap and t).

## Concrete issues (reporting, not computation)

1. **A gap that isn't disclosed: the stable set is strictly smaller than the Nash set.** The 14 Nash profiles (6,6,c) with the outsider bidding 7 or more count as "unstable" and as "strict-both-gain." This matters for the results:
   - 10 of the 42 unstable rounds are pure-Nash rounds at (6,6,7): 5 in none, 5 in private.
   - The same 10 rounds make up 10 of the 33 strict-gain rounds.
   - The stable-fraction contrast in block 24201 (−2/9) comes entirely from such Nash rounds.

   Calling stability "a competitive static benchmark" hides this. The summary and REPORT should state it.
2. **The design question is answered by construction for high-payment rounds.** A stable round must have a payment of 7 or less, so no high-payment round can be stable. Metric 7 only carries information about rounds with payments of 6 or 7. The summary states the inequality but not what follows from it.
3. **REPORT uses the wrong word.** It says "stable *profiles* 29→19" and "profiles permitting…", but these are counts of rounds, with repeated profiles counted more than once. Meanwhile the census counts distinct profiles. The two are easy to confuse.
4. **The REPORT block isn't checked by any script.** The untracked `scripts/s56_documents.py` (going by its name, it probably writes the REPORT block) isn't in the frozen manifest. Neither checker compares REPORT.md to the JSON, and `verify()` doesn't check `registration`, `registration_receipt` or `source_validation`. I checked the numbers by hand and they match, but there is no automated guard.
5. **Fresh-clone reproduction isn't shown.** In the git status snapshot, the results, receipt and logs are still uncommitted. Nothing supplied shows a fresh-clone or byte-identical regeneration run. Don't claim these until they're logged against the pushed commit.

## Acknowledged limitations (not bugs)

- The raw binding check only looks at the final attempt of each call. Whether earlier attempts were correctly retried is left to the S14 replay, as disclosed.
- The "independent" checker was written by the same author. It is backed up by the hard-coded stable set and my derivation.
- The analysis is post hoc on reused outcomes; n=5 with uncorrected small-sample intervals; the 3125-draw bootstrap differs from S14's 10000-draw one; the counterfactuals are static; the pair/outsider partition is fixed rather than a strong equilibrium; transfers are benchmarked but never implemented; and provider identity and tool non-use aren't attested.

**Bottom line:** I found no computational bugs in what I could check. The ODD/context-only verdict holds up. Items 1–3 should be disclosed, and items 4–5 need to be done or logged before any claim of verified release.
