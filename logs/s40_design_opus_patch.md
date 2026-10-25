# S40 adversarial review (based only on the supplied text)

I made no edits and no calls, and I did not have the raw archive.

## Concrete remaining bugs and risks

1. **Clean-clone check can fail on `.writer.lock`.** In `s40_release.check()`, `run(directory)` opens `data/s40_memory/.writer.lock` in write mode, which creates the file inside the clone. `clean_clone` then asserts that `git status --porcelain` is empty. This fails unless `.writer.lock` is gitignored. The `before`/after hashes deliberately skip that file, but the porcelain check does not. Check `.gitignore`.
2. **`logs/s40_launch.json` must be committed.** `validate()` compares the receipt to `LIVE_RECEIPT`. If that file is gitignored or never committed, `--analyze` fails in the fresh clone.
3. **The archive breaks if any of 13 shared files changes.** `validate()` requires exact current hashes for all `SOURCES`, including `CLAUDE.md`, `llm.py`, `pyproject.toml`, `uv.lock`, `s37_runtime.py` and `s16_reviews.py`. Later pilots routinely touch these. Any `uv add`, llm.py fix or CLAUDE.md edit makes S40 permanently un-analyzable at HEAD, and the release/present scripts can't be fixed after the outcome either. It would be safer to validate against `git show <registered commit>` rather than the working tree.
4. **The schedule may be too tight.** The critical path is about 10 sequential codex calls (5 blocks × 2 views, with a barrier between blocks), and each call has a 600 s timeout. At 60–120 s per call, the 20-minute headroom can run past 03:30. Admission then fails and the whole pilot ends with no estimate. A larger minimum headroom would help, or an explicit statement that a deadline abort is the expected failure mode.
5. **The concurrency limit isn't replay-validated.** "At most two concurrent calls" depends on `max_workers=2`. The chronology check covers sequential views within each case and the barriers between blocks, but not overlap across cases.
6. **The model field is a label, not evidence.** `response['model']=='gpt-6-luna'` checks the name `_codex` was asked to use, not what the provider served. Reasoning effort is also fixed at `"low"` inside `llm.py` and is not stated in the design. The design should say both.
7. **"Active" is never checked.** The design says "first active firm", but the code takes `rows[0]['agents'][0]` without checking activity. Change either the wording or the code.
8. **The independent verifier is weaker than the main parser.** It uses plain `json.loads`, so it accepts duplicate keys, and it does not check request or response hashes. That is acceptable only because its docstring disclaims independence. The report should not call it a parser check.
9. **The figure may hide the result.** Cases that all sit at the floor draw on top of each other with no jitter or counts. The table will carry the result.

## Checked and consistent

- **Unit:** offer = quote − 10, averaged per block, never a realized payment. The rival is not re-simulated.
- **Intervention:** only the notes array becomes `[]`. Marker, ending and system prompt are byte-identical, and the retain prompt equals the archived prompt.
- **Cases:** both the archived response hash and archived action are checked against the selected quote.
- **Arithmetic:** 5⁵ = 3125 bootstrap draws with linear quantiles matching numpy. The sign-flip test is inclusive at 1/32 and half-integer blocks avoid float ties. Classification order HIT > DUD > ODD is correct.
- **Failure handling:** every response is written before parsing, a shared abort flag stops new admissions, and incomplete archives are never resumed. The launch receipt is created exclusively and survives deletion of the archive directory.

## Acknowledged limits (not bugs)

- **HIT bar:** with five blocks and p ≤ .05, a HIT requires all five blocks to be strictly positive. Any zero block gives p = 2/32. This is a very strict bar and worth saying in the report.
- **Same roster position:** all cases are the same roster-position firm, which is confounded with firm identity.
- **Causal scope:** the manager saw S37 outcomes before choosing these cases. Erasure changes length, completeness and the complete-notepad promise together, and public history leaks the same action pattern. A null does not show memory is irrelevant.
- **Unenforced settings:** temperature and max_tokens are not enforced by the CLI, and provider behavior, effective config and tool non-use are unattested.
- **Abort and accounting:** a single fenced or malformed reply aborts all 20 calls with no redraw. The shared helper can lose an output if its log write fails.
- **Wording:** "take-home units" in the hypothesis sits awkwardly with "offer, not payment". Suggest "normalized offer units".

Bugs 1 and 2 would only fail at the clean-clone step. Item 3 is the most serious threat to keeping the result reproducible.
