# S21 adversarial review: one design-level blocker and five concrete bugs

The plumbing is sound: the hashes, registration receipt, strict parser, replay and independent arithmetic all hold up. The main problem is in the design. I made no edits and no model calls.

## Concrete remaining bugs (fix before launch)

1. **The pilot can't produce a HIT, and the verdict can already be predicted from the frozen data.** A HIT needs the bootstrap lower bound above 0, which needs AT error to exceed A error in **every** source block. Only three cases have an explanation that contradicts the recorded action:
   - case06: approved, reasoning says "reject it too"
   - case08: approved, reasoning says "reject both"
   - case09: approved, reasoning ends "reject both"

   Those cases sit in only two blocks (24323 and 24324). Blocks 24320–24322 have explanations that agree with the actions, so an error there would have to contradict both sources.
   - Best realistic result is block values [0,0,0,.5,1]: mean .3, but the lower bound is 0 (P(resample is all zeros) = .6⁵ ≈ .078 > .025) and the sign-flip p = 8/32.
   - So in practice the outcome is binary: **DUD if AT makes zero extra errors, ODD otherwise.** One extra error gives [0,0,0,0,.5], and the upper bound is .3 ≥ .2, so ODD.
   - The design was frozen after `data/s21_cases.json` was written, and that file shows the reasoning. "Selection never reads explanations" is true of the code but not of the analyst.
   - **Fix:** state this outcome space in the design, or redefine the primary on the contradiction cases (case06, case08, case09) as a descriptive count. Don't present it as a three-way screen.

2. **The parser is brittle under a no-retry rule.** `strict()` calls `json.loads` on the raw text, so a reply wrapped in a ```json fence or with a leading newline aborts the whole pilot. Check whether `llm.chat` strips fences. If it doesn't, either accept that risk explicitly or pre-register fence stripping.

3. **`retries=1` contradicts the design.** The design says "no retries; any transport failure aborts", but the request passes `retries=1`. If `llm.chat` retries internally, a transport failure is silently retried. Check the semantics and either set 0 or document it. Also confirm whether `llm.chat` has its own disk cache: a cache hit would undercut "uncached-call", and the cutoff check doesn't see it.

4. **The one-shot guard can be bypassed by deleting the directory.** Nothing outside `data/s21_audit/` records that a launch happened, so `rm -rf` lets you relaunch. Fix: commit or push a launch receipt (or the failed archive) before analysis, and have `validate` cross-check it.

5. **The tests miss the live code paths.**
   - `test_explanation_not_selection_feature` checks that `schedule()` ignores reasoning, not that `select_cases()` does. Add a test that mutates the reasoning in the source data (or monkeypatches it) and confirms selection is unchanged.
   - No test covers the non-dry branch: a mocked `chat` returning a fenced reply, the wrong model, or malformed JSON, followed by checks that a failure event is logged and the raw row is still kept.

6. **Minor issues:**
   - When one worker raises, the other keeps calling (up to two more calls). This is archived, but say so.
   - `validate` needs full git history (`git show <commit>`), so clean-clone reproduction fails on a shallow clone.
   - `s21_present.py` and `s21_analyze.py` use cwd-relative paths. Run them from ROOT or anchor the paths.
   - Unused imports in `s21_audit.py`: `Fraction`, `itertools`, `numpy`, `student_t`.

## Information visibility

- The status vocabulary gives the original condition away: PASS/FAIL means normative, TYPE-X/Y means neutral. That conflicts with "original condition identifiers hidden". The design acknowledges that status strings are preserved, but the "hidden" claim should be softened to match.
- The T view sees the target's status plus reasoning that usually states the decision outright. So T accuracy measures whether the explanation reports the action, not guessing. Say that in the write-up.

## Checked and found correct

- **Selection:** the tie-break key `(not approved, round, id, author)` and the rows[2:10]→rounds 3–10 mapping are consistent.
- **Provenance:** source request-key and response hashes are bound to the S19 rows.
- **Timestamps:** comparing UTC isoformat strings works, including the microsecond/no-microsecond edge case.
- **Statistics:** the bootstrap interpolation in `summary` matches `np.quantile` linear. Sign-flip p, t95 and both verdict implementations agree, including the float `.2` boundary.
- **Registration:** the commit equals the remote ref, source hashes are checked at that commit, and the committed cases file is byte-identical to the one in the run directory.

## Acknowledged limitations (no action needed beyond wording)

These are all already stated in the design: post-outcome enriched selection, n=5 blocks, generation and auditing by the same model family, the strong source-priority prompt (so this tests a source-aware auditor, not a generic detector), temperature not enforced by Codex, sign-flip symmetry assumptions, and no held-out split.

**Bottom line:** fix #1 (or at least disclose it) and resolve #2 and #3 before launch. The rest is cleanup.
