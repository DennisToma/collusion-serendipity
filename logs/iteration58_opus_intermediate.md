# Adversarial review of the iteration 58 portfolio replay

**Verdict:** I found no high-severity bugs. From the supplied text, the core claims hold: all 54 entries are covered, each result is compared exactly against its saved JSON, the `llm.chat` guard goes in before the scientific imports, and results are bound to their pinned revisions. The problems are medium or low. Some wording promises more than the code does, and a few checks have gaps.

I worked only from the text you supplied. I didn't look at the filesystem, and the receipt's checker details and import maps were left out, so I couldn't check those parts.

## What I confirmed

- **Coverage.** The receipt has exactly 54 records, in the same order as the REPORT table. There are 50 checkers, with none for S01, S02, S16 and S68, which matches the "Fifty" claim. `check()` requires the receipt's specs to equal `specs(ROOT)` exactly. `protected_baseline_files` is 3112, which is 3120 tracked files minus the 8 mutable ones, so the numbers agree.
- **Result equality.** `canonical()` compares the whole saved object. It keeps bool/int/float distinctions, rejects NaN and applies no tolerance. If an analyzer rewrites its own result file, the "self-compare" is still meaningful: the evidence snapshot plus the clone-vs-ROOT hash check force the file to match the committed bytes.
- **Guard before import.** `patch('llm.chat')` imports `llm` from the clone before any analyzer import. `call_count` is checked after the block, so a retry wrapper that catches the error still causes a failure.
- **Revision binding.** Each result's hash is bound to both the pinned revision and the current checkout. Every imported repository `.py` is bound to `git show` at that revision and to the current file. As a side effect, S67, S68 and S72 must use the same source code as HEAD, so only their data differs.
- **Inputs.** Baseline records show `evidence_files_unchanged` = 3120, the same as the tracked count. So no ignored data existed in the clone, and the replays ran from committed data only. That is a strong point and could go in the write-up.

## Medium issues

1. **"Disposable clones" (plural) is inaccurate.** `run()` makes one clone and checks out each revision in turn for all 54 workers. `git status --porcelain` doesn't show ignored files, and `evidence_snapshot` only covers tracked files plus `data/`. So ignored files that one worker writes under `results/`, `logs/` or caches would carry into later workers, and to other revisions, without being detected.
   - Fix: run `git status --porcelain --ignored` after each worker, or use a fresh worktree per pilot.
   - Or change the wording to "one disposable clone, sequential checkouts."
2. **The `data` field in the spec is a label the runner builds, not a verified input.**
   - It is derived from the result filename. For the post-hoc entries (S53, S56, S67, S72), `analyze()` takes no arguments, so `data/s53_payoffs` and the like are never used. They may not exist, and the real inputs are the S29, S14 and S65 games.
   - The same applies to `main` checkers and S01.
   - So "It lists each pilot's data" overclaims. Assert `Path(spec['data']).exists()` and mark it unused where it is, or drop the claim.
3. **Nothing stops reads from the source checkout itself.** The module guard only covers imports. A hardcoded absolute path, such as `~/collusion/collusion-serendipity/data/...` or a cache directory in `llm.py`, would read ROOT's data, including ignored caches, instead of the pinned clone. The baseline file counts suggest this didn't happen through `data/`, but the code doesn't prove it.
   - Fix: run the probes with ROOT hidden, or grep the analyzers for absolute paths.
   - Separately, the module check runs after the code has executed. It detects, it doesn't prevent.
4. **Six checkers pass just by not raising an exception.** These are S03, S04, S07, S06, S11 and S14. With `checked.get('passed', True)`, a receipt like `{"all_match": false}` would count as a pass. The receipt does record this basis, and `require(__debug__)` suggests the checkers use asserts. But nobody has confirmed that each of these six actually raises on a mismatch.
5. **The headline doesn't say that three entries can't replay at HEAD.** S67, S68 and S72 only pass at historical revisions, because their validators reject data appended later. The headline "every saved pilot result" should say "51 at the baseline, 3 at their pinned historical revisions."
   - "Genuine historical result revisions" and "legitimate later appends" are judgments. `check()` only shows that the result bytes are the same at those revisions, not that those revisions produced them or are ancestors of the baseline.
6. **Some claims can't be checked from this material.** Examples: that the S53/S56/S67/S72 checkers "read original raw responses … independently reconstruct", and the corruption-probe claims. `iteration58_verify.py` and the checker sources weren't supplied. Cite the code that shows these, or soften the wording.

## Low issues

- **`check()` hardcodes `completed_analyses=52, failure_audits=2`.** It should count them from `category == 'FAILED'`.
- **`check()` ignores several receipt fields.** It never validates `evidence_files_unchanged`, `evidence_manifest_sha256`, or whether `checker_success_basis` matches the checker output. The manifest hash could be recomputed from `git ls-tree` at the revision.
- **The parent process imports without the guard.** It imports `scripts.iteration55_claims` from ROOT in both `run` and `check`. Confirm that this import has no side effects and doesn't pull in `llm`.
- **Credentials aren't stripped from the worker environment.** Calls through `codex exec`, subprocesses or internal `llm` helpers that bypass `chat` aren't guarded either. This is disclosed, but removing API keys from `env` would be cheap extra protection.
- **Some failures crash the whole run instead of being recorded.**
  - A worker `TimeoutExpired`, or anything `llm.py` prints at import time, would break `json.loads(proc.stdout)` and kill the run, so no receipt gets written. `llm.py` is imported when the patch starts, which is outside the stdout redirect.
  - This is robustness, not a correctness problem.
- **Fixed run settings narrow the claim.** `PYTHONHASHSEED=0` and single-threaded BLAS mean this shows consistency under those settings only.
- **"Immutable worker copy" isn't enforced.** The worker is a normal writable file in a temp directory.
- **Duplicate stdout hash.** S56's captured stdout hash is the same as S14's (`bf3b6a…`). That's probably fine (shared S14 code printing), but it's worth a quick look.
- **REPORT.md hasn't been updated yet.** It still says iteration 57 and "selected replays cover five pilots." When you update it, add the per-revision caveat from issue 5. `preserved()` only allows changes outside the `| S` rows and the historical STATUS log.

## Wording on scope

The scope disclaimers are already appropriate: deterministic rerun consistency, not scientific validity, network isolation, fresh installation or external attestation. I wouldn't add more caveats. The changes needed are "one clone," the 51+3 split, and the data-field wording.
