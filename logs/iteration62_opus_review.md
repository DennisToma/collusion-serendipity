# Review of the `--full-validation` path in `check_release_clone.py` and the fixture scope in `release_tests.py`

**Verdict:** The command ordering and the check against the recorded revision are sound. Before you state the narrow claim, fix H1 and either fix or weaken the wording for M1 and M2. Nothing below questions the frozen scientific results.

## High

**H1. The receipt can't show which runner produced it.** Git status shows `scripts/check_release_clone.py` as modified and uncommitted. The runner always runs from `ROOT`, not from the clone. `acceptance_runner_sha256` and `exporter_sha256` both hash `ROOT` working-tree files. If you run it before committing and pushing the runner, the receipt says `result_revision=X`, but the code that ran is not X's version of the runner. Nothing in the code catches this.
- **Fix:** Fail unless the runner's bytes equal its bytes at the recorded revision (`git show <rev>:scripts/check_release_clone.py`), or unless `git status --porcelain` in `ROOT` is empty. Also hash the exporter from `clone/`, not `ROOT/`.
- **Sequence:** commit and push the runner, then run, then commit the receipt in a later revision.

## Medium

**M1. The three archived-README fixtures may not be doing anything.** `archived_readme_fixture` only patches `Path.read_bytes`. In Python 3.12, `Path.read_text` and `open()` don't go through `read_bytes`, so if a named test reads the README another way it reads the current README. Tests that check "drift is rejected" or "a false claim is rejected" could still pass that way. Nothing records that the archived bytes were actually served.
- **Fix:** count interceptions for each named test and assert at least one each. Until then, only say the three tests ran under a fixture that redirects `read_bytes`.

**M2. "All 926 pass" doesn't rule out skips.** The check is `tests == 926 and failures == errors == 0`. Skipped tests and expected failures still count toward `tests`.
- **Fix:** assert `skipped == 0` (and that unexpected successes are zero) if `repository_tests.run` records those fields, or report the counts in the claim.

**M3. A failure can leave an old PASS receipt in place.** `--out` is only written on a non-zero return code. These failures exit without rewriting it:
- the coverage assertion;
- a byte mismatch;
- the clone becoming dirty;
- a `TimeoutExpired` (1200 s per command — check the portfolio run fits);
- a `json.loads` error.

If you reuse a path that already holds an earlier PASS, it stays there.
- **Fix:** delete or pre-write `passed: false` at startup, and write the failure record in a `try/finally`.

**M4. Environment isolation is partial.** Only `UV_PROJECT_ENVIRONMENT` and `VIRTUAL_ENV` are removed. The child processes still inherit `PYTHONPATH`, `PYTHONHOME` and `UV_*` settings such as `UV_PYTHON`, `UV_NO_SYNC`, `UV_OFFLINE` and index URLs. A `PYTHONPATH` pointing at `ROOT` would load modules from the working repo instead of the clone.
- **Fix:** remove `PYTHONPATH`/`PYTHONHOME` and `UV_*` except the cache directory, or fail if they're set.
- **Also:** have the receipt record the interpreter that ran (`uv run python -c 'import sys; print(sys.executable, sys.version)'`). "New project environment" currently rests only on `.venv` being absent beforehand.

**M5. The export environment isn't checked against its lockfile.** The claim says it reuses the export environment, but the receipt doesn't show that `/var/tmp/explorer-export61` still matches `requirements-export.lock`.
- **Fix:** record a `pip freeze` or a hash of it, or soften "rebuilds PDFs" to "rebuilds with the pre-existing export environment".

## Nits
- `records[5]` only works because of where the commands are inserted. Look the record up by its argv instead.
- `json.loads(records[5]['stdout'])` breaks if `portfolio_replay.py check` prints anything besides JSON. Parse the `--out` file or the last line.
- Saving full stdout/stderr from the 52-analysis run inside the receipt could make it large; the repo has to stay under 100 MB.
- "Remains clean" means `git status --porcelain` shows nothing; ignored files aren't checked. Word the claim that way.
- `ls-remote ... .split()[0]` throws an `IndexError` if the branch isn't on the remote. That's harmless but the message is unclear.
- The `release_tests` docstring says "only three legacy tests read the pre-compression README". That holds only for reads through `read_bytes` (see M1).

## REPORT/README claims (consistency only)
- S29 matches its table row: 2/40 = 0.050, 15/40 = 0.375, difference +0.325.
- S62 matches its table row: 3/40 = 0.075, 7/40 = 0.175, difference +0.100.
- The verdict column has 54 rows: 29 DUD, 23 ODD/context-only and 2 FAILED, matching the stated totals.
- REPORT doesn't claim the full-clone acceptance yet, so leave it that way unless the run passes.
- The export header still says iteration 61; that's fine if iteration 62 only adds a receipt.
- The eight files compared match the README's `git diff` list, assuming `EXPORT_FILES` has five entries (I couldn't see it).

## Claim wording, if the run succeeds and H1 is fixed
Change "passes all 926 canonical tests" to "926 tests, 0 failures/errors (skips: N)". Change "three named archived-README fixtures" to "three named tests under a `read_bytes` archived-README redirect", unless M1 is fixed. Otherwise the claim is supported, and it already rules out cross-host, empty-cache and independent-replication claims.

## What I reviewed
I read only the supplied text of `check_release_clone.py`, `release_tests.py`, `README.md` and `REPORT.md`. I didn't read `export_report.py` (including `EXPORT_FILES`), `portfolio_replay.py`, `repository_tests.py`, `s65_tests.py`, the legacy S60 test bodies, or any receipt. Nothing was run or edited.
