No high-severity issues found. I reviewed only the text you supplied. I didn't run `--check`, didn't open the repo, the raw caches or the PDFs, and couldn't see `iteration55_claims.py` or `iteration54_handoff.py`. Anything that depends on those files is marked unverified below.

## Medium

**M1. The supplied receipts aren't tied to the final script, and the main command has no receipt.**
- `iteration56_repeat_build.json`, `iteration56_relocation.json` and `iteration56_negative_checks.json` record no script hash, no commit and no exact command line. Nothing shows they ran against the `export_report.py` with hash `b314…`. They could predate the closure fixes.
- Both executed outputs include `pdf_coverage_reextracted: true` but no `selected_replays` key. So they ran `--check-pdf` without `--replay-selected`. None of the supplied text shows the advertised command (`--check --replay-selected`) actually running. The README/report wording "Repeat/relocation receipts are actual executed checks" is only as strong as that.
- The negative probes cover only the figure marker, row order and `file:` links. Four closure fixes have no probe:
  - PDF link targets checked against pinned HTML
  - the `replace_once` guards
  - source verification running before the render receipt
  - the probe-list deletion in `verify_sources`
- **Fix:** add `sha(scripts/export_report.py)`, `git rev-parse HEAD` and `argv` to each receipt. Add one receipt from running the exact advertised command, and probes for the closure fixes.

**M2. Plain `--check` hash verification is only checked against itself.**
- `record['files']` and `record['source_hashes']` come from `logs/iteration56_exports.json`. That file is new, so `preservation()` doesn't protect it, and nothing else hashes it.
- Someone could edit an export and its receipt hash together and plain `--check` would still pass. The `scripts/export_report.py` entry has the same problem: the script compares itself to a value it reads from a file it doesn't protect.
- The only real anchor is the Git commit. The README sentence "Plain `--check` verifies source/export hashes" should say "consistency with the committed receipt", or the receipt hash should be pinned somewhere that is protected.

**M3. The `--check-pdf` instructions are unclear about which environment to use.**
- The README says "use the pinned export command with `--check-pdf`" but never gives the full command. The pinned command uses `--no-project`.
- `--check-pdf` always runs `verify_sources()`, which calls `audit.run()`, `products()` and preservation over 3,060 files with full Git history. Adding `--replay-selected` there needs the project's dependencies, which `--no-project` won't install.
- A successful build under `--no-project` suggests `verify_sources` doesn't need them, but that's unverified. Replay under `--no-project` very likely fails.
- **Fix:** print the literal `--check-pdf` command and state that it must not be combined with `--replay-selected`, or give a `--with`-on-project variant.

## Low / scope notes

- **Replay count:** "five selected scientific analyses" in `sources()` is hard-coded. `checked['selected_replays']` is computed but never checked against 5, so add `require(len(replay['replays']) == 5)`.
- **Link count label:** `portable_relative_links` counts PDF annotations, not links. A link that wraps onto two lines counts twice, and the 1 and 4 figures depend on layout.
- **Link targets:** they are checked with `git cat-file -e` in local Git only. Nothing checks that commit `BASELINE` (`573f973…`) is on GitHub or publicly readable. The text does admit that "requires repository access".
- **PDF text coverage:** the fragment check is a substring search over text with all whitespace removed. Short fragments ("ODD", "DUD") are trivially present, so the row-order check is the real safeguard. The HTML-only figure caption, which carries the "Post hoc selection; no pooling" caveat, is never checked in the PDF.
- **Chart labels:** the model names ("gpt-6-luna", "Qwen-3.6") and contrast labels are hard-coded. Only `primary_contrast` is checked against the source JSON.
- **Intervals and claims:** the labels match across the table, legend and receipt (bootstrap vs paired t, both descriptive). The S69 t upper bound of 1.015 is shown and explained as untruncated. Wording for S29 ("coincided"), S69 (calibration), S70 (no equivalence) and S72 (both intervals include zero) stays within the stated limits. Values in `chart_rows` match the brief table after rounding.
- **Preservation:** it compares Git blob hashes of working-tree bytes. Line-ending or filter attributes, or a submodule, would cause a false failure or a crash, but it fails safe. The STATUS check assumes new log entries are appended at the end.

Running `uv run --frozen python scripts/export_report.py --check --replay-selected` on the final commit would settle most of M1.
