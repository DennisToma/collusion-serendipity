# Replaying all primary pilot results

Iteration 58 adds one command for deterministic recomputation of every primary pilot result in the frozen inventory. The scope is **54 primary result objects: 52 completed analyses and two failure audits**. Fifty existing separate checker entry points also run. These counts describe archived entries and checks; reused games appear in several entries. Supplementary analyses, per-pilot summaries and reader figures are outside this runner's recomputation scope.

From a full-history clone, with the existing project dependencies installed:

```bash
uv run --frozen python scripts/portfolio_replay.py run --out /var/tmp/explorer-portfolio.json
uv run --frozen python scripts/portfolio_replay.py check --out /var/tmp/explorer-portfolio.json
```

The first command actually reruns the analyses. The second checks receipt consistency against the runner, frozen Git objects and current scientific sources; it does not attest to a fresh execution. The committed execution receipt is [iteration58_portfolio_replay.json](../logs/iteration58_portfolio_replay.json). It lists each pilot's main/source data root, analyzer, input convention, result path, checker, revision, imported repository source hashes and returned checker details. The data root is not a complete list of all files read. To check that saved receipt use `uv run --frozen python scripts/portfolio_replay.py check`.

The execution uses one disposable local `--shared` clone with sequential checkouts, borrowing this repository's Git object store. Receipt checking uses separate disposable checkouts to bind preservation manifests. Every result is compared with the complete saved JSON object, ignoring object-key order and tuple/list representation. It retains boolean/integer/float distinctions, rejects nonfinite numbers and applies no numerical tolerance or field exclusions. The original saved artifact bytes are also hash-bound to the corresponding Git revision and current checkout. Tracked clone files and retained data files must remain byte-identical after each replay (regenerable writer locks are excluded), each checkout must finish clean, and ignored outputs outside those locks are rejected. Current preexisting scientific evidence is checked against the baseline; original report rows and the historical STATUS log are preserved. Preservation manifests and fresh checker receipts are also bound to their actual Git trees/logs.

Fifty-one entries use evidence revision `a9b3c47654c1f694b253a4b8ab70477a2731aa5d`. Three entries use their historical result revisions because their validators protect the precise split index before later appends. Those revisions are checked against the original result-ledger entries and must be ancestors of the baseline:

| Pilot | Result revision |
|---|---|
| S67 | `15b318959aa08eccd2b7d0b19768f6dde539352f` |
| S68 | `043d3577e614e7858c9a97843fa1d05143315510` |
| S72 | `793a6411f6d7b646b1897d964b531cbaa7116cc0` |

No archived validator is patched to accommodate later files. S16 reruns its registered failure/prefix audit, and S68 reruns only its interruption/binding audit. Neither gains a behavioral effect estimate, resumes generation, or becomes a successful scientific pilot.

`llm.chat` is patched to raise **before** scientific imports in each fresh worker. Passing workers must record zero attempts. A copied runner runs outside the source repository, with its bytes checked after execution; scientific imports come from the pinned checkout, with the existing installed dependency environment explicitly reused. Module files imported from the source checkout outside that dependency environment are rejected after execution. This guard covers the established scientific call path; it does not isolate filesystem reads, network access or subprocesses. No scientific model generation is part of this command. Reruns use `PYTHONHASHSEED=0` and single-threaded BLAS settings.

The existing checker depth varies. S01 and S02 have no additional checker in this runner; the two failure audits also have no additional checker. S03/S04/S07 checker receipts must be freshly written by the current invocation. Other checkers must return a nonempty receipt or write one to a newly created temporary path. The receipt distinguishes an explicit `passed=true` from a successful return without exception. The S53/S56/S67/S72 separate checkers read original raw responses and game records and independently reconstruct their specified counts, payoffs or intervals; passing the analyzer result as their comparison target does not make them new independent data. These are existing same-author checks, not an external scientific review.

Forty-three checker receipts explicitly report `passed=true`; seven (S03/S04/S06/S07/S09/S11/S14) signal success by completing without an exception and matching their archived output. Those seven use assertions to reject mismatches; receipt equality alone is not a new evaluation of every status field. Both the runner and probe command reject optimized Python, and repository output paths are restricted before verification starts.

This extends the earlier five-pilot rerun to every inventory-mapped primary result. It establishes consistency under the archived code and reused same-host dependencies. It does **not** establish uniform raw-provenance coverage, scientific validity, a new independent replication, cross-platform byte equality, or absence of collusion. The original screens, estimates, labels, failures and no-promoted-hit conclusion remain unchanged. The separate [iteration-57 fresh-install receipt](iteration57_reproduction.md) still targets its earlier fixed handoff; no fresh installation of this iteration is claimed.

This is a verifier for the frozen release. Later changes to protected evidence, ledgers or coordination files deliberately fail preservation; use the released checkout when working from a newer research branch. This iteration recomputes existing estimates and runs no new scientific experiment, so it adds no experiment-ledger row. Historical STATUS entries remain an exact prefix; new entries append at the end.

Corruption probes are reproducible with:

```bash
uv run --frozen python scripts/iteration58_verify.py --out /var/tmp/explorer-portfolio-probes.json
```

They test receipt omissions/substitutions and actual disposable-clone S29 changes to result types, raw responses and an attempted `llm.chat` call during import. No frozen source or archive in this checkout is changed. Git-committed receipts record local consistency; they are not external execution attestations.

Implementation failures remain available: [initial sweep log](../logs/iteration58_initial_sweep.txt), [S67 split-index rejection](../logs/iteration58_s67_initial_failure.txt), and [overbroad dependency-import guard failure](../logs/iteration58_initial_import_guard_failure.json). The initial sweep used an incorrect S28 path and was rejected after a runner edit; it is not a release proof. The corrected import guard explicitly permits the reused project environment. No scientific rule or evidence was changed to fix these runner issues.
