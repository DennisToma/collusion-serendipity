# S67 final-review addendum (based only on the supplied text)

I ran nothing and enumerated no files. Every judgement below comes from the code and logs you supplied.

**Earlier medium findings:**

1. **HITS entry: resolved.** I withdraw my earlier request to confirm that HITS does not add S67. `check()` requires exactly one `## S67 — Unpromoted settlement-aware accounting` heading. The text calls it post hoc bookkeeping, makes no confirmation request and leaves S65 at UNRESOLVED/ODD. That matches the older unpromoted entries.
2. **Earlier pilot rows: resolved, with one caveat.** `check()` requires each of the 48 manifest rows to appear exactly once and the table to have exactly 49 `| S` rows. The log confirms 48 and 49. The caveat: it matches rows as substrings, not whole lines. If text were appended to the end of an old row, the check would still pass. So "byte-identical" overstates it slightly. Comparing whole lines (`set(old) <= set(rows)`) would close this.
3. **Mutation coverage: resolved.** `s67_postreview_check.py` runs the real `verify` against seven in-memory changes: round, game, exact bound, aggregate, missing metric, stage profile and opportunity count. Its log shows all seven rejected and the result file unchanged. The script only catches `AssertionError`, so a `KeyError` would crash it rather than pass, which is the safe direction. Under `-O` the explicit `raise AssertionError` still runs, so the check fails loudly rather than silently passing.
4. **Opportunity display: resolved.** `s67_context.py` re-checks the manifest, runs `verify` and only displays counts that were already exported (9/40 both-Y rounds per arm). It adds no metric or estimate, and its wording ("not forced by absent opportunities"; zero events ≠ absence) is appropriately limited. Two low gaps:
   - Of its two counts, only `both_y` has a mutation test; `strict_pareto_rounds` has none.
   - `--check` doesn't check the line it adds to README.

**Accepted as described, not verified from the supplied code:**
- The S65 replay patches `llm.chat` through the module, and the guard explicitly excludes OS isolation.
- The separate implementation verifies the prespecified quantile convention; it is not claimed to validate the choice of convention.

The S65 replay code wasn't included, so I can't confirm either point. The README wording does match what you describe.

**Verdict:** All earlier medium findings are resolved. What remains is low severity: whole-line row matching, a mutation test for `strict_pareto_rounds`, and including the README line in `--check`. I see no statistical change, no new experiment and no problem with how S67 is promoted.
