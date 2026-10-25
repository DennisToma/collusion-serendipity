# Iteration 57 review: fresh-dependency reproduction (supplied text only)

I worked only from the text you supplied. I didn't run any commands, look at any files or make any model calls. Your listed known limits are taken as given and not raised again.

## High

**H1. No iteration-57 claim or user instructions exist, and adding them the obvious way breaks the advertised check.**
- The supplied `REPORT.md` and `README.md` are the iteration-56 versions at `e6b0c02`. Neither mentions the fresh-install receipt, `iteration57_fresh_install.py run|check`, or what it shows.
- `export_report.py --check` requires `REPORT.md == documents()`, which is built from the old `573f973` baseline. It also requires the `REPORT.md`/`README.md` hashes in `logs/iteration56_exports.json` to match.
- So any iteration-57 edit to either file makes `uv run --frozen python scripts/export_report.py --check --replay-selected` fail at HEAD. That is the command both documents tell judges to run.
- Changing `export_report.py` to accept the edit changes its source hash, which also breaks that check.
- **Fix:** put the iteration-57 claim and command in a new file that no check pins (e.g. `results/iteration57_fresh_install.md`). Or create a new presentation overlay and receipt, and point the docs at a check that matches HEAD.
- Either way, the user-facing text has to say the following, matching the receipt's `scope` string:
  - the receipt only checks consistency at a fixed target (`e6b0c02`); it doesn't attest that anything ran;
  - it doesn't verify the current checkout;
  - the export environment pins only direct dependencies (see M2).

## Medium

**M1. "Initially empty caches" doesn't prove dependencies came from a fresh public download.**
- `env = dict(os.environ, ...)` passes through any `UV_INDEX_URL`, `UV_EXTRA_INDEX_URL`, `UV_FIND_LINKS`, `UV_CONSTRAINT`, `UV_OVERRIDE`, `UV_CONFIG_FILE` or `UV_LINK_MODE`. With `HOME` unchanged, `~/.config/uv/uv.toml` and `pip.conf` still apply.
- A local find-links directory or mirror would make "fresh install" mean "installed from host-local wheels".
- **Fix:** pass `--no-config` (or set `UV_NO_CONFIG=1`), pop every `UV_*`/`PIP_*` variable, and record the effective index URL(s) in the receipt. Have `check()` require the public default index.

**M2. The export environment is only partly pinned, and `check()` doesn't verify what got installed.**
- `uv pip install` pins only the four direct packages. The transitive ones (numpy, pillow, fonttools, kiwisolver, greenlet, pyee, …) resolve to whatever is newest at run time, with no `--exclude-newer` and no hashes.
- The README's `uv run --no-project --with ...` instructions have the same gap.
- Today the byte-identical PNG/PDF pins the outcome. A later rerun can legitimately fail (or differ for reasons nobody can explain) when a transitive version changes.
- `check()` confirms each environment has packages and that they sit inside its prefix, but never compares versions. That holds for both the project environment (against `uv.lock`) and the export environment (against a frozen list).
- **Fix:** commit a constraints file built from the receipt's export inventory, plus `--exclude-newer`. Have `check()` require the export inventory to equal it and the project inventory to equal what `uv.lock` resolves to. Change the README export commands to match.

**M3. The selected replay doesn't test the path users are told to run.**
- The runner calls `project-env/bin/python scripts/export_report.py ...` directly. Users are told to run `uv run --frozen python ...`, which goes through uv's project discovery and environment selection (and, without `UV_PROJECT_ENVIRONMENT`, uses `.venv`).
- The receipt therefore shows "a fresh environment reproduces". It doesn't show that the documented command works in a fresh clone.
- **Fix:** run the replay and canonical-test stages through `uv run --frozen` with the same env, or say plainly that the interpreter was called directly.

**M4. Credentials and live endpoints are inherited during the replay and test stages.**
- The full host environment, including any API keys and `CODEX_HOME`/`HOME`, is visible while the 926 tests and 5 replays run.
- You state that network isolation isn't claimed, but the only guard against model calls is the in-code call guard.
- **Fix:** remove model and provider credentials from `env` and point `HOME`/`CODEX_HOME` at the scratch directory. That's cheap, and it makes "no scientific calls" depend on more than one patch.

## Low

- **L1. Byte identity could be made structural.** A zero exit from `--build` implies `render()` rewrote the artifacts, but nothing structural proves it. Deleting the eight `ARTIFACTS` in the clone before `export-build` would make "rebuilt identically" impossible to confuse with "left untouched".
- **L2. JSON parsing of stage output is fragile.** stdout and stderr are merged before `json.loads`. Any warning (matplotlib, Playwright, uv) makes the run fail. That fails safely, but for the wrong reason. Capture stderr separately.
- **L3. The PDF re-extraction isn't independent.** The `--check-pdf` re-extraction in the same `--build` process compares against a receipt that process just wrote. It's only meaningful because `logs/iteration56_exports.json` is in the byte-identity set, so don't describe it as an independent check.
- **L4. Source binding could record more.** The receipt stores `clone_source: 'origin'` but not the remote URL (minus credentials) or `git -C clone rev-parse HEAD`. `check()` also ignores `record['host']`. Recording all three costs little.
- **L5. `initial_empty_paths` proves nothing by itself.** It's a constant list name-matched in `check()`, so the emptiness rests only on the runner's code, which is bound by `runner_sha256`. Acceptable, but describe it that way.
- **L6. `TARGET` is a 7-character short hash.** It fails safely if it ever becomes ambiguous, but storing the full SHA in the script is cleaner.

## Looks sound

- The target revision, runner hash, lock hash and artifact hashes are all bound to Git.
- The receipt requires the stage list in order and a zero exit for every stage.
- Clone cleanliness is checked after both the tests and the build.
- The replay result is compared to the saved replay log.
- `check()` requires the 926-test count with zero failures and zero errors.
- A failed run overwrites the receipt with `passed: false` and the error. That's honest, but the wrapper's auto-commit will then commit a failing receipt, which is correct behaviour.
- The scope string accurately lists what is reused from the host.
