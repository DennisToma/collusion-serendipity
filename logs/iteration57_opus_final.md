# Iteration 57 adversarial review: fresh install, receipts, report claims

**Scope:** supplied text only. No filesystem access, reruns, edits or model calls.

**Verdict:** I found no high-severity issues. There are four medium issues and several low ones. All of them are about what the receipts actually prove, or about traps in the user commands. None of them contradicts a scientific number. Within the stated known limits, the main reproduction claim is supported by the code as written. That claim is: e6b0c02 was reproduced in new environments, with five selected replays, 926 canonical tests and eight byte-identical artifacts.

## What holds up

- **Revision and source binding.** The run checks out the full SHA detached from a fresh `origin` clone. It records `actual_clone_revision` and checks it equals `TARGET`. `check()` ties the runner to its own sha256 and the project lock to `TARGET:uv.lock`, so any later edit to the runner invalidates the receipt. That is correct.
- **Artifact byte checks.** Rebuilt bytes are compared directly with `git show <rev>:<name>` inside `run()`, before hashing, and the clone must end clean. `check()` checks the eight hashes against Git and checks that the set of artifacts is exactly those eight. This is strong evidence, and it is not circular.
- **Dependency isolation.** Each run gets a new `TemporaryDirectory`. `UV_*`/`PIP_*`, `VIRTUAL_ENV`, `PYTHONPATH` and `PYTHONHOME` are stripped, and the uv cache and browser path are pinned to scratch. Exact version sets are compared against both locks in both directions, with no external site paths and every package inside the prefix. Python, OS and fonts are reused, as disclosed.
- **Failure handling.** `finally` always writes the receipt. Errors set `passed: false` and re-raise. A `check()` failure after `passed=True` is caught and the receipt is downgraded. A timeout leaves the stage list incomplete, which `check()` rejects.
- **Scope wording.** REPORT, README and `results/iteration57_reproduction.md` all say "selected same-host" and "not cross-platform or full-portfolio". They also say the receipt is consistency evidence, not attestation, and that the 926 checks include scoped synthetic fixtures.

## Medium issues

**M1. A plain `run` can clobber the committed receipt and break the current `--check`.**
`--out` defaults to `logs/iteration57_fresh_install.json`.
- On failure, it overwrites the committed passing receipt with `passed: false`.
- On success, it still rewrites the receipt, because timestamps and stdout change. `logs/iteration57_exports.json.source_hashes` pins that receipt's hash, so `export_report.py --check` would then fail with "Export/source hash differs".

The docs recommend `--out /var/tmp/...`, but the default command is the trap. Suggested fix: make `--out` required, or default it to `/var/tmp`, and put the committed path behind an explicit flag.

**M2. `export_report.py --build` passes its own hash check trivially and silently overwrites committed exports.**
In `main()`, `render()` writes a new `logs/iteration57_exports.json`. The hash comparison then reads that freshly written receipt, so it cannot fail. The README's render steps run `--build` in the user's working checkout. That gives no byte-identity check against the committed BRIEF/REPORT PDFs, HTML and receipt, and it overwrites them. Only the fresh-install runner, which compares against Git, actually proves byte identity.

Suggested fixes:
- Add "then `git status --porcelain` / `git diff --exit-code` must be empty" to the README render block, or
- Have `--build` compare the new bytes against `HEAD` before reporting success.

**M3. The reader-facing exports are not the artifacts that were fresh-reproduced. REPORT and README don't say so.**
The fresh run reproduced the e6b0c02 (iteration 56) exports. The current iteration-57 BRIEF/REPORT PDFs and HTML have different hashes (`f11dcf…` vs `9365e7…` and so on) and were built outside the fresh runner. `results/iteration57_reproduction.md` states this ("not later checkout edits"). However, `FRESH_NOTICE` in REPORT.md and README.md does not. A judge reading the iteration-57 PDF could reasonably think that PDF was the one reproduced.

Suggested fix: add one clause to `FRESH_NOTICE`, for example: "The current iteration-57 exports were built separately and are checked by `export_report.py`, not by this run."

**M4. Two receipt fields are self-asserted, so `check()` tests constants.**
- `uv_config_disabled = True` and `default_index = 'https://pypi.org/simple'` are hard-coded in `run()`, not observed. The "Index/config drift" check in `check()` is therefore tautological.
- `initial_empty_paths` is just `list(paths)`, the path names. Emptiness is enforced at run time by `require` on a brand-new temp dir, but the receipt cannot show it.

The supporting evidence is real: the env construction is visible in the runner, and its sha is bound. The wording should still match. Either describe these as "configured, runner-bound" fields, or record observed evidence, such as `uv` output naming the cache dir or the resolved index URLs taken from `uv.lock`.

## Low issues

- **Remote identity is not bound.** `clone_source: 'origin'` resolves to a host SSH alias (`gh-csr:…`). `check()` does not verify the remote URL or that it is the public `REPO_URL`. Since the SHA is verified this is acceptable, but the receipt cannot show the clone came from the public GitHub repo.
- **Untracked required files.** `requirements-export.lock` and `logs/iteration57_*.json` are untracked in the snapshot. Both the current `--check` and `iteration57_fresh_install.py check` hard-require them. Confirm they land in the commit; the wrapper's `git add -A` should cover this.
- **The export lock sits outside the target revision.** It is read from the current `ROOT`, not the clone, and it was derived from the first fresh run's inventory. The "fixed target" therefore depends on a post-hoc current-tree file. This is disclosed, and byte identity supports it, but it does not show that the original iteration-56 renderer environment matched.
- **Probe coverage in `iteration57_release.py` is thin.** It has six probes. None cover `canonical_tests` counts, environment leakage or `inside_prefix`, `clone_clean`, lock hashes, or the `selected_replays` count. Cheap to add.
- **Some download and config variables are inherited.** `PLAYWRIGHT_DOWNLOAD_HOST` and similar variables, plus `~/.gitconfig`, are not stripped. Isolation is described as dependency-level, so this is only worth a word in the scope string.
- **The receipt embeds full stdout/stderr.** Watch repo size if the canonical-test output is large.
- **Fragment counts differ between receipts.** REPORT has 177 source fragments in the current export receipt and 176 in the fresh receipt's saved coverage. This is expected because REPORT changed, but a judge comparing the two receipts may ask, and a one-line note would pre-empt that.

## Report claims

The claims I checked are consistent with the code and the receipt:
- "five selected scientific replays": `selected_replays == 5`, passed.
- "926 canonical checks": 926 tests, 0 failures, 0 errors.
- "eight byte-identical artifacts": eight hashes checked against Git.
- "new project/export environments, initially empty uv/browser caches": consistent with the runner.

Calling REPORT.md, README.md and `iteration56_exports.json` "artifacts" is acceptable. Apart from M3, I found no overclaim.
