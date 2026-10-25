# Adversarial review: iteration 58 portfolio replay

**Verdict:** the core claim holds within its stated scope. The supplied code supports deterministic recomputation of 54 inventory-mapped result JSONs, with exact canonical equality. One bug will likely break the published commands, one probe proves less than it claims, and two scope statements need tightening. I reviewed only the supplied text and ran nothing. Where a finding depends on repository contents I couldn't see, I say so.

## High

**H1. `preserved()` will reject the next ordinary repository update, including the experiment-ledger row this iteration should add.**
- `preserved()` requires every tracked file at baseline to stay byte-identical, apart from eight exempt files (`STATUS.md`, `REPORT.md`, `README.md`, the export script and the four reader exports). Both `run` and `check` call it, and `check` also requires `protected_baseline_files == preserved()`.
- CLAUDE.md requires a new `EXPERIMENTS.tsv` row for every experiment, and the director rewrites `DIRECTION.md` about every two hours. If either file is tracked at `a9b3c47`, which is almost certain, the committed receipt and both documented commands fail as soon as that happens. That may include this iteration's own ledger row.
- The check conflates "scientific evidence preserved" with "no tracked file changed".
- **Fix:** before committing, make it an append-only check for `EXPERIMENTS.tsv`, exempt the coordination files (`DIRECTION.md`, `PLAN.md`, `HITS.md`, …), and rerun. Also confirm the `STATUS.md` log is appended at the end; the prefix check fails if new log entries are inserted at the top.

## Medium

**M1. The `raw_response_corruption` probe passes no matter what the analyzer does.**
- The probe edits a tracked file in the clone and then runs the worker. The worker ends with `require(git status --porcelain == b'')`, so it always fails with "Replay changed checkout", whether or not the analysis detected the corruption.
- This probe has `error=None`, so the failure reason is never checked.
- The other two probes are sound, because they assert specific error messages that are raised before the cleanliness check.
- **Fix:** assert an expected analysis error such as `KeyError`, `Archived result differs` or the checker's message, and/or check the recorded stderr in `logs/iteration58_verification.json`. Until then, drop "raw responses" from the probe claims in `iteration58_reproduction.md`.

**M2. "Fifty existing checker entry points also run" hides that 7 of the 50 have no explicit pass flag.**
- S03, S04, S06, S07, S09, S11 and S14 are recorded as "completed without exception". The runner uses `.get('passed', True)`, so their success means only "returned a nonempty dict equal to the archived log".
- If the archived log itself records a mismatch in another field (for example `ok: false` or a non-empty `mismatches` list), it would be replayed faithfully and still count as passing.
- **Fix:** state the split (43 explicit / 7 implicit) and say that those 7 count as passing because their output equals the archive, not because their contents were inspected.

**M3. "Every saved pilot result" / "the complete archived portfolio" is broader than what was replayed.**
- Coverage is exactly the 54 primary JSONs mapped by `SOURCES` from the iteration-54 inventory, which the code enforces correctly.
- Supplementary result artifacts are not replayed, even where REPORT.md cites numbers from them. Example: the S67 opportunity context (`results/s67_opportunity_context.md`: 9/40 both-Y rounds, 0/9 strict improvement). The per-pilot summaries are also outside coverage.
- **Fix:** say "54 primary pilot result objects" instead.

## Low

- **L1. Unguarded imports.** The parent process imports `scripts.iteration55_claims` (in `specs()`, for both `run` and `check`) with no guard in place. Also, `patch('llm.chat')` runs `llm.py`'s own top-level code before the guard exists. "Guard before scientific imports" is true only for the workers. Check whether `iteration55_claims` imports any analyzers.
- **L2. Undisclosed normalisation in `canonical()`.** It turns non-string dict keys into strings (`{1: x}` equals `{"1": x}`), and it raises an error on mixed key types or NaN. Equality is slightly looser than "exact" in that one respect.
- **L3. Data directory checked at the wrong revision.** `specs()` checks that the data directory exists in the current checkout, not at the pinned revision. This is harmless here because the replay itself would fail.
- **L4. Redundant comparison for S03/S04/S07.** For these checkers, the second "differs from archive" comparison reads back the file just written, so it always passes. Real protection comes from the before/after evidence snapshot. That works, but the error message is misleading.
- **L5. Runner hash binding.** Any fix from H1 or M1 that touches `portfolio_replay.py` invalidates `runner_sha256`, so the whole replay has to be rerun. Don't patch the receipt.
- **L6. REPORT.md isn't updated.** Its header still says "Iteration 57" and it doesn't link the iteration-58 reproduction. It's presentable, but the new evidence isn't visible to judges.

## Checked and consistent

- **Coverage counts:** there are 54 unique records whose order matches the inventory. 54 − 3 = 51 baseline entries, 54 − 4 = 50 checkers, and `check()` derives the two failure audits from categories. 3112 protected = 3120 − 8 exempt files.
- **Revision binding:** S67, S68 and S72 are tied to their ledger commits and must be ancestors of the baseline. Result bytes are hashed against the pinned Git revision and the current checkout. Imported sources must match both the revision and the current checkout. Each evidence manifest is re-derived from a fresh checkout (record counts: 2707, 2923, 2956 and 3120).
- **Failure audits:** S16 and S68 rerun only their audits, have no checker, and no effect estimate is added.
- **Model-call guard:** the guard is installed before analyzer import; the `llm.chat`-at-import probe asserts its error string. Calls caught inside analysis code are still detected through `call_count`.
- **Type-exact equality:** bool, int and float are kept distinct, and this is tested both by unit cases and by the real S29 integer-to-float probe.
- **Fresh writes for `main` checkers:** S03/S04/S07 must write their output once in the current call. Writing to tracked logs is safe because the evidence snapshot catches any byte change.
- **Scope language:** the scope statements correctly disclaim scientific validity, network or filesystem sandboxing, fresh installation, cross-platform reproduction and external attestation, and keep "same-author" on the post-hoc checkers. I couldn't verify the claim that those checkers recompute independently, because the import maps and checker sources weren't supplied.
