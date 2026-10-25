The live publication path closes both issues in `logs/s38_design_codex.md`. I found no remaining publication blocker in these patches.

- **Archive eligibility:** [s38_present.py:14](/home/factory/collusion/collusion-serendipity/scripts/s38_present.py:14) requires full `analyze()`, compares the entire reconstructed result with supplied JSON, then invokes independent verification before writing output. This restores completion, failure-marker, cutoff, overlap, freeze, and registration checks.
- **Displayed audit claims:** [s38_independent.py:92](/home/factory/collusion/collusion-serendipity/scripts/s38_independent.py:92) checks response counts, retry counts, and note metadata. Subsequent reconstruction binds archived notes to raw responses. Full-result equality also binds displayed limitations to the analyzer’s fixed text.

One residual distinction: standalone `verify()` still accepts altered or missing `limitations`, because it never examines that field. This does **not** bypass live rendering’s full-result comparison, but its `passed=True` should not be interpreted as independently validating limitation text.

The presentation regressions cover corrupted response counts, failure markers, interrupted execution, late admissions, and source drift. Retry, note, and limitation mutations lack explicit regression cases.

Static review only; no edits, model calls, external searches, or test execution.