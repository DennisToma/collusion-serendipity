# Iteration 58 portfolio replay review

I read only the text you supplied. I did not run anything or look at the filesystem. I found two medium bugs and several overclaims, all fixable in the runner, and no high-severity bug. The REPORT.md you pasted doesn't claim the iteration-58 replay yet.

## Medium

**M1. Sibling imports can load today's code instead of the pinned revision.**
- **Where:** `run` starts each worker with `[sys.executable, ROOT/scripts/portfolio_replay.py, ...]`. Python therefore puts `ROOT/scripts` on `sys.path`. The worker adds the clone root in front of it, but never adds `clone/scripts`.
- **Effect:** imports like `import llm` or `scripts.sNN_*` come from the clone, as intended. A bare sibling import such as `from s29_analyze import ...` would instead load the current, uncommitted copy from ROOT.
- **Why it's hidden:** `imported_repo_sources` only lists files under the clone, so modules loaded from ROOT would be dropped from the record. The git-clean and evidence-unchanged checks only look at the clone, so they wouldn't catch it either.
- **Fix:** copy the runner into the temp directory, or run it with `-P`/`-I` and set `sys.path` yourself. Then fail if any loaded module's `__file__` is inside ROOT or anywhere else in the repo outside the clone.

**M2. Some checker verdicts may come from archived files, not this run.**
- **S03, S04, S07 (`function == 'main'`):** the runner calls `main()` and then reads `logs/sNN_verification.json` (or `s07_independent.json`) from the checkout. If `main()` writes somewhere else, or doesn't write, `checked` is just the committed log. And because tracked files must end up byte-identical, any passing run means the log matches the archived bytes. So "rewrote identically" and "never wrote" look the same in the receipt.
- **Fix:** send these checkers' output to a temp path, or hash the log before and after `main()` and record whether it was rewritten.
- **The pass test is too weak:** `checked.get('passed', True)` counts any dict with no `passed` key as a pass. For `verify(...)` checkers that return metrics without a verdict, the only real test is "didn't raise." Record whether each checker gave an explicit verdict.
- **The post-hoc checkers (`verify_result`) are not independent:** `verify(actual)` checks the analyzer's own output. It doesn't recompute from the data. The receipt should label S53, S56, S67 and S72 that way, not as independent checks.

## Low-to-medium overclaims in the receipt text

- **`scientific_model_calls=0` is hard-coded at the top level.** It's written even when workers failed, and for failed workers the guard count is unknown. What was measured is that `llm.chat` was called zero times, for passing workers only. Call it `llm_chat_attempts_in_passing_workers` and compute it.
- **The guard only covers `llm.chat`.** Other `llm.*` functions, direct `codex`/`opencode` subprocesses and HTTP clients get through. The docstring admits this, so the field name shouldn't say "scientific model calls."
- **"Exact" equality isn't strictly type-exact.** After a JSON round trip, Python's `==` treats `True == 1` and `1 == 1.0` as equal. That's fine for a consistency check, but "exact numeric equality, no tolerance" should say values are compared at JSON level with mixed bool/int/float allowed. NaN fails safe: it never compares equal, so it causes a failure, not a false pass.
- **`full_history_local_clone=True` needs a qualifier.** It's a `--shared` clone that borrows ROOT's object store, so it isn't independent. Its working tree also has no gitignored `data/` caches. That means the "ignored caches" part of `evidence_snapshot` does nothing inside the clone; it only matters for the ROOT snapshot. Reword so it doesn't suggest the clone's raw data was checked.
- **The runner itself isn't committed.** `runner_sha256` points at an untracked file, and `baseline_commit=a9b3c47` doesn't contain it. Commit the runner first, or record that it ran from an uncommitted working tree.
- **The receipt doesn't say which revision each pilot used at the top level.** S68 and S72 ran at `043d357` and `793a641` with today's installed dependencies. Their `revision` is in each record's spec, but the top-level `baseline_commit` reads as covering everything. List the exceptions explicitly.

## Checked and found sound (assuming the inventory is right)

- **Coverage:** the 54-row and unique-ID check is correct. The REPORT table also has 54 rows and they match: S01–S72 minus the unused numbers. S16 and S68 are the failure audits. S01's two result objects are compared as a single dict. S01, S02, S16 and S68 have no checker, and the receipt's `checker_scope` says so.
- **Archive preservation:** the clone's file hash is compared with ROOT's before each worker. Evidence is snapshotted before and after in both the clone and ROOT, `git status --porcelain` must be empty, and the runner's own hash is checked. A result file the analyzer regenerates is safe, because different bytes would fail the snapshot.
- **Guard before import:** the patch is applied before the analyzer and checker imports, each worker is a fresh process, and module-level `from llm import chat` picks up the mock. Catching the `RuntimeError` doesn't hide a call, because `call_count` still records it.

## Robustness (low)

- An analyzer subprocess writing straight to the real stdout would break `json.loads(proc.stdout)`. A missing result file at a historical revision would crash the run. Either way, `run()` aborts before any receipt is written, so it fails loudly rather than producing a false pass.
- `PYTHONHASHSEED` isn't set. Nondeterminism would show up as noisy failures, not false passes.

## REPORT.md

The supplied REPORT.md still describes iteration 57: five selected replays and no full-portfolio validation. It makes no iteration-58 claim, so there's no overclaim yet. Once the receipt lands, suggested wording: "Deterministic same-host rerun of all 54 archived result objects at pinned revisions. Results match the archive at JSON level. Existing checkers ran where available; their depth varies by pilot, and S53/S56/S67/S72 checks are self-checks of the analyzer output. `llm.chat` was guarded. This is not a scientific-validity audit, raw-provenance check, new replication, network isolation, fresh install or external attestation." Fix M1 before calling the reruns revision-pinned.
