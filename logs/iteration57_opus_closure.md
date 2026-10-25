# Iteration 57 adversarial review: fresh-install reproduction and report claims

**Verdict:** I found no high-severity issues. The receipt binding, artifact byte checks, failure path and scope language mostly hold up. Four medium issues remain, and one of them (M1) must be fixed before the claims can be checked from the repository.

This review is based only on the supplied text. I had no filesystem access, so I could not see the omitted stage stdout.

## Medium issues

**M1. Uncommitted dependencies would break both `check` commands.**
- Git status shows `requirements-export.lock`, the runner, the receipt, `iteration57_release.py` and `results/iteration57_reproduction.md` as untracked (`??`).
- `check()` binds `export_lock_sha256` and `runner_sha256` to working-tree files.
- `logs/iteration57_exports.json` `source_hashes` covers all of them.
- If any of these is missing from the commit, both `iteration57_fresh_install.py check` and `export_report.py --check` fail on a clean clone.
- **Fix:** commit them atomically, then run a clean-origin `check` and `--check --replay-selected` after pushing, as earlier iterations did.

**M2. The README render block implies byte identity across hosts.**
- The block ends with `git diff --exit-code -- BRIEF.pdf REPORT.pdf …`.
- PDF and PNG bytes depend on host fonts, system libraries and the Chromium build. The claim scope is explicitly same-host.
- **Fix:** add one sentence right at the command, for example: "Byte identity is expected only on the recording host; elsewhere use `--check-pdf` content checks."

**M3. Index and configuration fields are stated, not observed, and the wording overreaches.**
- `uv_config_disabled` and `default_index` are hard-coded constants that `check()` merely compares against themselves.
- `uv sync --frozen` installs from the source URLs and hashes recorded in `uv.lock`, not from `UV_DEFAULT_INDEX`. So "uses the public PyPI default index" in `iteration57_reproduction.md` only accurately describes the export install.
- The doc's own caveat ("describe settings… rather than independently observed") partly covers this.
- **Fix:** reword to "project packages come from `uv.lock`'s hash-pinned sources; export packages from the hash-locked requirements against PyPI".

**M4. The environment scrub is narrower than "configuration isolation" suggests.**
- Only `UV_*`, `PIP_*` and a few `PYTHON*`/`VIRTUAL_ENV` variables are removed.
- Still inherited: `GIT_*` (for example `GIT_DIR`, url rewrites), `PLAYWRIGHT_DOWNLOAD_HOST` and other `PLAYWRIGHT_*` variables, proxy and CA variables, and `HOME`/`XDG` caches such as fontconfig.
- The Chromium download is not hash-pinned by any lock. Its integrity rests on Playwright's CDN plus the byte-identical outputs, which indirectly pin it via the Chromium version in `iteration56_exports.json`.
- The existing caveat ("Git configuration and host networking remain available") is close.
- **Fix:** either pop `GIT_*`/`PLAYWRIGHT_*` except `BROWSERS_PATH` and record that, or name these inherited variables in the scope paragraph.

## Low issues and observations

- **Probe gaps in `iteration57_release.py`.** There are no rejection probes for:
  - `runner_sha256`
  - `project_lock_sha256`
  - `actual_clone_revision`
  - `initial_empty_paths`
  - a mismatched scratch path or prefix
  - a mismatch between `canonical_tests` and its stdout

  The code checks all of these. Only the tests are missing.
- **Fields not checked by `check()`.** The selected replay names (S29, S62, S69, S70, S72) are claimed but only the count of 5 is checked. Python 3.12.15 and the uv version are recorded but not required.
- **Timeout handling.** On `TimeoutExpired`, the failing stage is never appended to `commands`, so its partial stdout and stderr are lost. Only `error` survives. An exception while writing in `finally` could also mask the original error.
- **Origin URL.** `origin_url` is a host-local SSH alias (`gh-csr:…`), not `REPO_URL`. Source binding correctly rests on the full commit SHA plus `actual_clone_revision`. Just don't describe the receipt as attesting the public GitHub remote.
- **Headline wording.** "926 canonical checks" in the headline omits the scoped historical synthetic-clock fixtures. The reproduction doc carries that caveat; consider a two-word "(incl. synthetic fixtures)".
- **Selected replay is self-consistency.** It compares against saved JSON in the same repository. This is consistent with the stated scope, but it is not an independent validation.
- **Stale "Next" line.** "before14:30UTC" in the preserved REPORT text may be stale by presentation time. It comes from baseline text, so editing it is optional.

## Consistency checks that pass

- The REPORT PDF fragment count is 176 in the fresh-install receipt and 177 in the current exports receipt. The extra fragment is the added notice paragraph, so the counts are consistent.
- The figure hash is identical across both receipts, and `iteration57_release.py` treats the figure as immutable.
- The runner hash in the receipt matches `source_hashes` in `iteration57_exports.json`.
- The receipt contains all 11 stages with exit code 0.
- The project and export inventories are complete, with no external site paths.
- The `--out` requirement protects the committed receipt.
- Archived and current scope are clearly separated in REPORT, README and the reproduction doc.
- The run took 4 minutes 3 seconds, including the Chromium download and 926 tests. That is plausible but tight, and I cannot verify it from the supplied text.
