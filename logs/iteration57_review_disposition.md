# Iteration 57 review scope and dispositions

This is an engineering reproduction audit, not a scientific pilot. All
scientific sources, results, ledgers, split records and original pilot rows
remain unchanged. Independent critics were requested under CLAUDE.md.

## Design review

Codex performed a read-only repository review; no installation or tests were
executed by that critic. It found three medium issues: preflight failure could
retain a stale passing receipt, export transitive dependencies were not fully
locked, and reader instructions had not yet been updated. Preflight operations
now occur inside the receipt-writing failure handler. Both environments have
complete exact-version checks; exports consume a complete hash lock. A supported
editorial overlay updates REPORT/README and creates a separate current export
receipt. The original iteration-56 receipt is preserved.

Opus reviewed supplied text only. Its integration concern was addressed by that
overlay. uv configuration is disabled, inherited UV/PIP settings are cleared,
the public default index is configured, and stdout/stderr are separated. The
runner now invokes the documented uv command. The full target SHA and actual
clone revision are recorded. Host credentials, Git configuration, Python, OS
and fonts are not isolated; neither a network sandbox nor independent execution
attestation is claimed. The existing scientific call guards remain unchanged.

## Intermediate final review

Opus's supplied-text review supported the principal reproduction claim but
identified receipt-overwrite, current-export interpretation and render-command
pitfalls. `run` now requires an explicit `--out`. Reader notices explicitly say
current iteration-57 exports were built separately. The README render sequence
includes a Git diff check against committed exports. Documentation explains
that configuration/cache fields describe checks enforced by source-bound code,
rather than independent observation of network behavior. More rejection probes
cover counts, versions, environment leakage, clone cleanliness and locks.

Codex independently checked recorded artifact/source hashes and raised two
medium consistency gaps. The runner now requires complete command records,
matches exact argument templates and compares captured JSON (or the canonical
suite's final JSON suffix) with the stored summaries. Current export checking
requires exact complete sets of artifact/source keys. In-memory regression
probes reject omitted coverage, altered checkout arguments, contradictory stdout
and missing captured streams. No archived scientific validator was changed.

## Retained operational records

The initial successful fresh run is superseded by the complete-lock refinement
run, whose receipt and exact runner bytes are retained. A subsequent run began
before the last consistency fixes. Its source-digest guard correctly rejected
publication with `Runner changed` after those fixes; that failed receipt and
the launched runner bytes are retained. It produced no final passing receipt,
scientific estimate or exclusion. The final strict run must finish before any
release claim or current export build. No intermediate record substitutes for
the final `logs/iteration57_fresh_install.json`.

Closure review results and exact scopes are recorded separately. Supplied-text
Opus feedback is not a raw-cache, filesystem, PDF visual or independent runtime
audit. A successful receipt check establishes Git-committed consistency, not
external attestation.

## Closure review

Both critics exited zero and found no high-severity issue. Codex checked receipt
consistency and all current export/source hashes, and executed a mocked
preflight failure; it did not rerun scientific analyses or installation. Its
remaining abrupt-process/timeout issue is retained as an explicit limitation:
the instructions now promise receipt writing/cleanup only for normal completion
and caught Python failures, require the actual terminal exit, recommend a new
output path per run, and disclose lost partial timeout streams. No SIGTERM or
process-loss guarantee is claimed. Every released run has an observed terminal
exit zero. This wording fix does not alter the successful runner or its digest.

Opus's remaining supplied-text concerns prompted same-host qualification beside
the README's Git diff command, precise project-lock versus export-index source
wording, and explicit inherited Git/Playwright/proxy/CA/font scope. Neither critic
independently observed package downloads or verified all raw trajectories.
Both critics' Git-binding concerns are resolved only by the atomic result
commit/push and the subsequent actual full-history clean-origin check; the
closure receipt must be read for its actual outcome. The critic snapshots
preceded these final wording edits and the commit. No unanimous raw-audit or
independent runtime-attestation claim is made.
