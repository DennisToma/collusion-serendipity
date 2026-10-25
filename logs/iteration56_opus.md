I reviewed only the text you supplied. I did not run `--check`, look at the filesystem or raw caches, or inspect the PDFs visually.

## Medium

**1. The figure can go missing without any check failing (`page()` and `render()`).**
- The figure is inserted with `markup.replace('<p><strong>Why none is promoted:', …, 1)`, and nothing confirms the replace actually happened. If the marker changes, the figure is silently left out.
- The image guard can't catch this: `xs.every(...)` returns true when the page has no `<img>` at all.
- The PDF coverage check can't catch it either. It only looks for source Markdown fragments, and the caption and alt text are added afterwards, so they are never checked.
- **Fix:** require that the marker appears exactly once, and require at least one image in BRIEF (for example `img.count() == 1`).

**2. The README overstates what `--check` does.** It says "The current `--check` checks … saved text-coverage receipts." In `main()`, plain `--check` only compares file hashes against `logs/iteration56_exports.json`. It then prints `record['pdf_text_coverage']` next to `passed=True`, which looks like coverage was verified when it wasn't. Only `--check-pdf` checks coverage. **Fix:** reword the README, or leave `exports` out of the output when `--check-pdf` wasn't given.

**3. The PDF coverage check doesn't show the original table survived.** `pdf_checks` checks that each fragment appears somewhere in the extracted PDF text, with all whitespace removed. It ignores order and which row or column a value sits in. Short cells (`ODD`, `DUD`, `+0.000`, the S-IDs) almost always match by chance, so the check passes even if cells are dropped or shuffled. "Re-extracts every paragraph and table cell" is literally true but suggests row-level checking. **Fix:** say "text presence", or check rows in order, e.g. join each row's cells and search for the row as one sequence.

**4. The brief's numbers may not be re-checked by the current command.** The new verification text says it "checks all original report rows and saved numerical bindings". The brief's own numbers (its table, S72's +0.400 and intervals, the 29/23/2 counts) were tied to result files by `iteration54_handoff.py verify`, and `export_report.py` doesn't run that. Two partial protections exist:
- The brief file is hash-protected through `preservation()`, so it can't have changed.
- The chart reads the result JSONs directly, but its values are never compared with the brief's text. `chart_rows` is stored in the receipt and never re-checked.

Unless `iteration55_claims.run()` also covers the brief, which I can't tell from the supplied text, either narrow the claim to report rows or add a check that the brief's table matches the chart's values.

**5. Most links in the exports point to GitHub, not to local files.** Every link that isn't one of the four exports goes to `github.com/.../blob/<BASELINE>/...`. That includes "complete original table", which opens the iteration-55 REPORT.md on GitHub rather than the local `REPORT.pdf`/`REPORT.html`.
- If the repo is private or `573f973` isn't pushed, a judge's copy has dead links everywhere. The disclaimer ("requires repository access") exists, but this is still the main way judges would follow the evidence.
- The only check is a local `is_file()`. It doesn't confirm the file exists at BASELINE, so a link to a file created after the baseline would pass the build and 404 on GitHub.
- **Fix:** check paths with `git cat-file -e BASELINE:path`, and consider pointing "complete original table" at `REPORT.pdf`.

## Low

- **PDF byte reproducibility:** the code comment says rerenders "can reproduce exact bytes". Chromium's PDF output usually includes a document `/ID` (a UUID), and fixing the timestamps doesn't remove it. No user-facing text claims byte-identical PDFs, so just don't make that claim. `--check` only shows the files haven't changed since the build.
- **Overflow check:** the horizontal-overflow check runs at the default screen width, not the A4 print width. Clipping in print is only caught indirectly, through the text-coverage check.
- **Saved corruption probes:** `verify_sources` takes `rejected_corruption_probes` from the saved receipt instead of re-running them. That's fine as long as nothing claims the probes were re-run.
- **Build order:** `--build` overwrites REPORT.md/README.md and renders the exports before `verify_sources()` runs, so a failed audit leaves half-updated files. `preservation()` runs first, which limits the damage.
- **"Complete log" size:** REPORT is 3 pages with 176 fragments. Fifty-four rows of 3 or more cells already account for about 162 inline tokens, which leaves very little room for prose. That could be fine, but it's worth confirming "complete log" (as opposed to a summary) is the right label.
- **Page titles:** the HTML/PDF titles are just "BRIEF" and "REPORT". This is cosmetic.

## Checked and consistent

- **Chart values:** all four rows (mean, bootstrap, paired t) match the brief's table exactly.
- **Labels:** the direction labels (shared − self, low − high charge, endowed − baseline) and "five paired blocks each" are consistent.
- **x-axis:** the limits (−0.2 to 1.08) show S69's untruncated paired-t upper bound of 1.015.
- **Wording:** the caption and NOTICE stay within the known limits: post hoc selection, no pooling, no collusion/agreement/equivalence claim, S69 described as calibration.
- **Counts:** 54 entries = 6+5+6+7+6+5+19 = 29+23+2. "Five selected replays" = S29, S62, S69, S70, S72.
- **Commands:** `COMMAND` runs as written. The README notes that full Git history and a separate pinned render environment are needed. The archived commands are correctly marked as revision-bound.
