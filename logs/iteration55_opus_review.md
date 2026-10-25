I found no high-severity defect that the supplied code proves. I found five medium issues where the wording claims more than the code checks, plus four smaller ones. I worked only from the text you supplied: I didn't open any files or run `--check` or the replay, so I haven't reproduced 307/144/3042 or anything else.

**What I reviewed:** `scripts/iteration55_claims.py` as pasted; the REPORT and README excerpts; and the digest. I checked how displayed values are bound to fields, the sample/window checks, how unchanged files are compared to the Git baseline, the corruption probes and the selected-replay wrapper.

**What the audit already acknowledges:** it doesn't revalidate the science, doesn't replay raw caches, and doesn't check unbolded wording. S02/S04 window labels are kept as written but not checked. S01's category comes from its frozen report. The `llm.chat` guard is not network isolation.

## Medium

1. **The four table-row probes only show that the row text is frozen.** `check_row` first checks `row == pilot['report_row']`. So `displayed_value`, `wrong_direction` and `failure_gains_estimate` fail at that string comparison, and `missing_row` fails the row-count check. None of them reaches `check_token`. Only the four probes that edit the JSON artifacts (S70, S29, S68, S62) exercise the field bindings.
   - Fix: say so, or add a probe that skips the equality check and changes a bound value. An example is S01 `+0.00175` shown as `+0.00176`.

2. **"Explicit saved-JSON fields" is overstated for the count pilots.** For S60–S70 and S72, about 40 of the 307 values are a stored field multiplied by a constant written into the script: `mean×40`, `n_games×4`, `mean×5`, `n_blocks×8`.
   - The `40 = n_games×4` binding only works because 10 games × 4 equals 5 per arm × 8 opportunities.
   - The "8 Y opportunities per game" figure is only checked indirectly (`primary_rounds=='3..10'`, `pair_bad×8` is a whole number). No saved count of Y opportunities is read.
   - S72's ×5 and ×8 have no consistency check at all.
   - Fix: reword the claim as "fields or documented fixed scalings", and list them in `limits`.

3. **REPORT text outside the table can change without being caught.** `REPORT.md` is excluded from the unchanged-file check. Only lines starting with `| S` are compared, and they're compared to the index, not to the baseline `REPORT.md`.
   - The excerpt shows empty `<!-- S59 summary -->` and `<!-- S62 summary -->` blocks. If those had content at baseline, it was removed and nothing would flag it.
   - The new headline numbers (54/307/144/"five") and "zero game-outcome tuning attempts" aren't tied to the receipt either.
   - Fix: compare non-table REPORT sections to the baseline, or say they aren't covered.

4. **The rows are compared to the index, not to the baseline report.** "All 54 rows retain their original text" assumes that every `report_row` in `iteration54_portfolio.json` matched the baseline `REPORT.md`. Comparing directly against `git show BASELINE:REPORT.md` would remove that assumption.

5. **Each pilot's source file is picked by filename.** The script globs for `sNN_*.json` and excludes names containing `action_text`, `context`, `diagnostic` or `all_y`. It doesn't use a path recorded in the index, so a file renamed or added before the baseline could change which artifact gets checked.
   - `probes()` excludes only `action_text`, so the two selection rules disagree. (Ambiguity there would crash, not fail silently.)

## Low

- **Category mapping:** `UNINFORMATIVE` and `UNRESOLVED` are counted as ODD. The 23 ODD total therefore depends on a mapping choice, which should be disclosed. S01 is hardcoded as DUD (acknowledged).
- **Sample/window checks are opportunistic:**
  - The window and fresh-decision checks only run if their regex matches, so a missing display is skipped rather than failed. "144 checks" is a count, not proof of full coverage.
  - The block-count regex takes the first match in the cell.
  - Some expected values come from `n_*` fields rather than the underlying arrays; S53 and S56 are the exception.
- **S68 failure tokens:** they're paired with fields by position (`zip`), so the check is only correct if the `143` from `exit143` is the last number in the cell. Passing implies that today, but it breaks easily.
- **Replay guard:**
  - It patches only `llm.chat`; any `codex exec` subprocess or other transport isn't blocked.
  - The `preserved(BASELINE)` check afterwards wouldn't catch the replay creating new files or editing STATUS/REPORT/README.
  - "S72 uses its pinned historical clone" may not exist in a clean checkout, so the README's offline command may not be reproducible there.

## Supported as worded

If the script runs as written:
- Highlighted values are matched by field path, not by searching for a matching value.
- Display precision and sign are checked exactly, with no tolerance.
- Baseline files are compared by Git blob hash, and the STATUS log is append-only.
- Categories add up: 29 + 23 + 2 = 54.
- The S60–S70 counts match the per-game summaries.
- README and REPORT correctly say there is no full-portfolio raw reproduction.
