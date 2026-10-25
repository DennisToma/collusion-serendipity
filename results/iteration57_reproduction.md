# Reproduction from freshly installed dependencies

Iteration 57 checks the archived reader handoff at full revision
`e6b0c02bb189923b3fd039fe67db153826ee3aff`. It is a reproducibility audit, with no
new simulated-agent calls, estimates, tuning or pilot classifications.

The runner clones **origin with full history** into `/var/tmp`, creates new
project and export virtual environments, and starts with absent uv and browser
cache paths. It disables uv configuration and inherited `UV_*`/`PIP_*` settings,
configures the public PyPI default index, installs project packages from the
hash-pinned sources in the original `uv.lock`, installs all export dependencies from the new hash-locked
`requirements-export.lock`, and downloads Chromium into the new browser path.
Both environments' complete installed package versions and package locations
are recorded and checked against their respective locks. The export lock was
made from the first fresh run's inventory; it changes no scientific dependency
file or analysis configuration.

The final [execution receipt](../logs/iteration57_fresh_install.json) records
commands, separate stdout/stderr, exit codes, environment inventories, runner
and lock hashes, and direct Git-byte comparisons. It contains:

- Five selected scientific replays and separate checkers: S29, S62, S69, S70
  and S72. S72 uses its genuine historical result revision. Their existing
  scientific call guards and scientific validators remain unchanged.
- The canonical 926 checks with zero failures/errors and terminal exit zero.
  The repository's documented narrow historical synthetic fixtures remain in
  use; these are not 926 independent scientific replications.
- Fresh export building and PDF text extraction, followed by byte comparison
  of all eight archived artifacts: four reader documents, the interval PNG,
  original export receipt, REPORT.md and README.md. The clone finishes clean.

This reproduces the fixed archived handoff, **not later checkout edits**. Current
iteration-57 export consistency and selected evidence use the separate current
`scripts/export_report.py` command. The original iteration-56 receipt remains
unchanged; current reader exports have their own `logs/iteration57_exports.json`.

To check the committed receipt's consistency without downloading or rerunning:

```bash
uv run --frozen python scripts/iteration57_fresh_install.py check
```

To execute a new fresh installation without replacing the committed receipt:

```bash
uv run --frozen python scripts/iteration57_fresh_install.py run \
  --out /var/tmp/explorer-fresh-receipt.json
```

Run from a full-history checkout with `origin` access. Prerequisites are uv,
the registered base Python 3.12.15 environment, working
network access for Git/PyPI/Chromium, sufficient `/var/tmp` space, and the host
libraries needed by Chromium. The runner uses the current interpreter's base
Python. Scientific analyses may reject a different Python version; the
registered requirements are deliberately retained. No sibling checkout or new
scientific API credentials are required. Normal completion and caught Python
failures remove scratch environments/downloads. Caught failures write
`passed: false` to the specified receipt, including preflight failures.
Abrupt process loss can prevent receipt writing and cleanup, leaving an older
receipt or scratch files. Choose an unused output path for each run and require
the actual process to finish with exit zero before interpreting its receipt.
Timeouts are recorded as failures; their partial stage streams are not retained.
The `run` subcommand requires an explicit `--out`; omitting it stops before
installation and leaves the committed receipt untouched.

The host Python installation, uv executable, OS libraries and system fonts are
reused. This is selected same-host reproduction, not a new machine, container,
cross-platform result, fresh OS installation or full-portfolio raw audit.
Downloads require network access. The scientific call guard is not network
isolation; the host environment remains available to subprocesses. A committed
receipt documents the executed run and checks its consistency with code and
Git artifacts; it is not independent external execution attestation. Re-running
`check` does not execute the recorded commands. Original small-sample,
post-selection, model-serving and interpretation limits still apply.
The configuration and cache-absence fields describe settings and checks
enforced by the source-bound runner, rather than independently observed network
configuration. Git configuration and host networking remain available.
Inherited Git and Playwright download settings, proxy/CA settings and system
font configuration are outside the scrubbed uv/Python environment. Chromium's
download is selected by pinned Playwright; no independent browser-binary hash
lock or public-remote attestation is claimed.

The first fresh run and initial critiques are retained as superseded records.
Their feedback prompted complete export locking, configuration isolation,
preflight failure handling, separate stderr, exact installed-version checks,
the documented uv invocation, and the explicit archived-versus-current scope.
