# S21 independent adversarial review

**I could not check the raw responses.** This session has no shell or file-read tool, only Docs and Drive connectors. So I never opened `data/s21_audit/responses.jsonl`, `requests.jsonl`, `execution.jsonl` or `logs/s21_release.json`. Everything below is recomputed from the pasted `data/s21_cases.json` and the case-level outputs in `results/s21_audit.json`. That does not meet your raw-response requirement. Before release, run `scripts/s21_independent.py` again and spot-read the 30 raw texts.

## Recomputation (from case-level outputs)
- **Truth:** case04, 06, 08 and 09 are true, the other six false. That makes 4 approvals, and every source block has 2 cases.
- **Actions only (A):** 10 correct, 0 errors, 0 abstentions.
- **Both (AT):** 10 correct, 0 errors, 0 abstentions.
- **Explanation only (T):** 0 correct, 0 errors, 10 abstentions.
- **Block values:** error contrasts are 0 in all five blocks. Correct (A, AT) and abstain (T) are 1 in all five blocks.
- **Primary (AT−A error):** mean 0. The 5^5 bootstrap gives [0, 0]. Paired t gives [0, 0] because the standard deviation is 0. Upper sign-flip p = 32/32 = 1.
- **Fields that are all 1:** sign-flip p = 1/32 = 0.03125, which matches the reported value.
- **Verdict:** mean ≤ .05, so **DUD**. This matches. All three contrasts and all 15 summaries are consistent.

## Concrete remaining issues
1. **The release isn't committed yet.** `REPORT.md` is modified and `data/s21_audit/`, `results/`, `logs/` and `figures/` are untracked. The clean-clone reproduction the design promises can't have happened against these files yet.
2. **The "all four previously observed adverse approvals" claim is never checked by the code.** `assert sum(truth)==4` only shows that four games each have at least one negative-type approval. Selection takes one case per game, so a second approval in the same game would be dropped silently. S19 reports 3/40 *partner* approvals, so the fourth must be a non-partner review. Either add a check that each game has at most one such approval and that the total is 4, or reword the claim.
3. **`s21_independent.py` is not independent on ground truth.** It takes `truth` from the production-generated `cases.json`. It should rebuild truth directly from `data/s19_labels/game_*.json` (`rows[r].agents[i].reviews[author]`).
4. **The independent check parses raw text loosely.** It uses `json.loads`, not a strict parser, and doesn't confirm backend/model on each raw row. That's minor because `validate` covers both, but it weakens the "independent" label.
5. **The most informative result isn't reported.** case06, case08 and case09 have explanations that explicitly contradict the recorded action ("reject it too" / "reject both" while the review shows `true`). AT went with the recorded action in all three. A descriptive sentence saying so, with no test and no promotion, is allowed under the design and is the actual answer to "do explanations override actions?"

## Acknowledged limitations (not bugs)
- **A is a lookup.** The target key sits in the reviews map, so A was always going to hit the ceiling. The primary contrast could only go positive through AT errors, so DUD was close to certain.
- **T's 10/10 abstentions are driven by the prompt.** The system prompt defines `reviews` as the only action source. The model abstained even on case04, whose reasoning plainly says "approve B". So T−A tests compliance with instructions, not how persuasive explanations are. The design discloses this.
- **Interval bounds are degenerate.** [0, 0] bootstrap and t intervals with zero standard deviation are not an equivalence or zero-risk claim. The summary already says so.
- Other disclosed limitations:
  - The status vocabulary reveals the semantic condition.
  - The analyst had already seen the explanations.
  - Cases were selected after outcomes were known.
  - n = 5 blocks.
  - Generation and auditing use the same model family.
  - Codex ignores the temperature and max-token settings.
  - The primary metric excludes abstentions (the error-or-abstain secondary covers this).

## Points checked and found sound
- **Strict parser:** rejects duplicate keys, NaN, non-boolean values, extra fields and JSON fences.
- **Visibility:** the three views differ only in the response fields shown.
- **Selection:** never reads explanations (there's a test for this).
- **One-shot guards:** an exclusive receipt file, a replay mode that makes zero calls, and partial runs blocked from resuming. The fallback model name is scoped and restored, and a test confirms exactly one subprocess call.
- **Timing:** registration was observed at 21:13Z, before the 22:00Z cutoff. ISO string comparison is valid here because every timestamp has the same format.
- **Analysis:** the bootstrap uses the same linear percentile method in both scripts.

**Bottom line:** the DUD verdict holds on the case-level data, and the statistics are right. Before release: commit the files (issue 1), fix or reword the "all four" claim (2), make the truth check independent (3), and confirm the raw-response check locally.
