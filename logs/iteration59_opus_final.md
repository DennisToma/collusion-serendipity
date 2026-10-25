# Iteration 59 review: final REPORT claims and presentation method

I found **no blockers**. I found four medium issues and several low-priority recommendations. I worked only from the text you supplied: I ran no commands, opened no files, called no models and made no edits. Anything that depends on the repository contents or Git history is marked unverified.

## Checks I carried out (by hand, on the supplied text)

**S29 lead**
- The per-seed counts give self 0+0+0+1+1 = **2/40** and shared 2+4+6+2+1 = **15/40**. The per-block differences (+.250, +.500, +.750, +.125, 0) average **+0.325**. This matches the summary table and the lead.
- The bootstrap interval [0.100, 0.575] and the t interval [−0.049, 0.699] match the summary table, the lead, the export receipt's chart_rows and the brief.
- One block ties (seed 24484). Counting all 32 sign flips with the tie included gives 2/32 = **0.0625**, which is above the registered threshold of ≤ 0.05. S29 meets every other HIT condition: mean ≥ .25, bootstrap lower bound > 0, and internal-bonus contrast +1.3 > 0. So "ODD, not HIT" is correct.
- The payoff description matches DESIGN_S29: approving TYPE-Y gives the author +6, the reviewer −2 net and the organization −10.
- The denominator is right: 4 TYPE-Y tasks × 2 employees per game in rounds 3–10 is 8 per game, and 5 games makes 40 per arm. Uncertainty is computed over 5 paired blocks, and 3125 = 5⁵ bootstrap resamples.

**S62 lead**
- The counts give self 1+1+1+0+0 = **3/40** and shared 4+0+2+1+0 = **7/40**. The differences sum to 0.5, so the mean is **+0.100**. The bootstrap interval [−0.025, 0.250] matches.
- The ODD label is correct, but only just. The rule calls a result DUD when the bootstrap upper bound is **< .25**, and S62's upper bound is exactly .250.

**Other cross-checks**
- **S53:** the regret and excess figures are fixed rescalings of the approval counts (4/30 = 2× and 8/60 = 4× of 2/15). The report's "rescalings" wording is accurate.
- **Chart (S69, S70):** S69's 31/40 − 4/40 = 27/40 = +.675 matches. The chart's x-axis range (−.2 to 1.08) contains every interval, including S69's t upper bound of 1.015.
- **Portfolio counts:** I counted the REPORT table directly: **54 rows, 29 DUD, 23 ODD, 2 FAILED**. The brief's axis counts also total 54 (6+5+6+7+6+5+19).
- **PDF row checks:** the receipt's row counts fit the tables. The REPORT count of 55 is one header plus 54 rows. The BRIEF count of 13 is the two tables (5 + 8 rows including headers).
- **Post-hoc selection:** it is stated in the lead ("Examples above were selected post hoc"), in the brief, and in the figure caption. The future controls (self/shared/unread notepad, counterbalanced identities, both employees' complete-window gains) match the brief and are clearly marked "not launched".
- **How reproduction is described:** REPORT and README keep the two things separate. One sentence covers the saved iteration-58 receipt for all 54 primary results; another says the current command reruns five selected analyses and "does not rerun all 54".

## Medium issues (not blockers)

1. **The REPORT.md wording points the wrong way.** `verification_note()` is inserted *after* the table, but it says "All 54 original pilot rows **below** are preserved". The rows are above it. README already replaces this with "rows in REPORT.md". REPORT should say "above" or "in the table above". This needs a rebuild and new receipt hashes.

2. **Some export links show older content than readers will expect.** Links other than the two reproduction notes are pinned to the baseline commit `573f973`, and the script only checks that the file exists there.
   - For files that `preservation()` hash-protects, that is fine.
   - It is not fine for README, which `preservation()` exempts (as it does REPORT.md and STATUS.md). The "[Reproduction](README.md)" link in REPORT.html and REPORT.pdf therefore opens the **baseline README**, which still has the old `iteration55_claims.py` command, not the current verification command.
   - The README sentence "Source links … point to the frozen evidence revision" is also inaccurate: three different revisions are used.

3. **The BRIEF export blurs saved results and fresh reruns.** BRIEF's added verification text, followed by `PORTFOLIO_NOTICE` ("All 54 primary result objects reproduce … 50 existing checkers also run"), is written in the present tense. It never says the current command only checks the saved iteration-58 receipt. The "iteration 58" heading helps, but a reader could still take it as a fresh 54-result rerun. I'd add: "recorded in iteration 58; the current command checks that saved receipt and reruns only five selected analyses."

4. **Two archived receipts may not be protected (unverified).** The `--build` allow-list and the separate link pinning suggest the baseline predates iterations 57 and 58. If so, `logs/iteration57_fresh_install.json` and `logs/iteration58_portfolio_replay.json` are not covered by `preservation()`. They are bound only through `source_hashes` in the iteration-59 receipt, which `--build` rewrites. Only the two `*_reproduction.md` files are compared byte-for-byte against their original revisions. That means "archived receipts remain unchanged" is not independently enforced for those JSON files unless `iteration57_fresh_install.check()` or `portfolio_replay.check()` compare them against Git. Please confirm, or add the same Git-show equality check the .md files get.

## Recommendations (low priority)

- **Units:** in the lead, call +0.325 an "approval-rate difference (≈32.5 percentage points of 40 opportunities per arm)".
- **S62 boundary:** in the lead or the details, say that S62's upper bound sits exactly at the 0.25 cut-off.
- **Sign test:** note that with five blocks the sign screen is only met if all five differences are strictly positive. The design says this; the lead doesn't.
- **Lead links:** in the HTML/PDF exports, the lead's brief link goes to the archived iteration-54 brief on GitHub, not the local BRIEF.pdf. Consider pointing readers to the local file.
- **Model name:** use the exact name "qwen-3.6-35b".
- **Blank lines:** `FRESH_NOTICE` followed by `'\n\nRender…'` leaves extra blank lines in README. This is cosmetic only.
- **Dropped pre-table text:** `--build` keeps only the original REPORT from the table onward, so the original text before the table is dropped. It is still in Git, but nothing confirms that no caveat appeared only there.
- **Write order:** `--build` writes REPORT.md and README.md before `verify_sources()` runs. The output is deterministic and recoverable from Git, so the risk is small.
- **Uncommitted work:** the working tree has the edits and the untracked iteration-59 logs uncommitted. The receipt hashes depend on committing them together, and the pinned revisions `f5fd3df`, `cd3505c` and `573f973` must be on the remote for the links to resolve.

## What holds up

- The S29/S62 numbers, denominators, ODD labels and payoff description match the saved summary fields you supplied and the registered screen.
- All 54 rows are present, with the labels and counts consistent.
- The post-hoc and no-multiplicity caveats are present.
- The known limits are stated: no independent scientific validation, no held-out discovery claim, no network isolation and no cross-platform claim.

Fixing issues 1–3 needs only a rebuild of the exports and receipt. Issue 4 needs a check in the repository.
