# Clean-origin acceptance — iteration 62

At 2026-10-25T15:59:54.500618+00:00, a full-history origin clone of `3d2a9fdad1edce5e2466c5cfd37b1a1b57dcc70a` completed the documented setup, canonical tests, full archived primary replay and reader rebuild. The acceptance runner was committed in that same revision; its recorded SHA256 is `4de619ad98963d18a4effe3a264bc1b5ec598089b359fe82dd2e1f298e21eba8`.

| Check | Observed result |
|---|---|
| Project environment | Initially absent; created from the frozen project lock; actual clone interpreter recorded |
| Current presentation | 54 original rows, 307 numerical bindings, 144 metadata checks; five selected replays/checkers |
| Canonical suite | 926 executed tests; zero recorded failures/errors |
| Full archived primary replay | 52 completed analyses and two failure audits; all 54 primary result objects match |
| Existing additional checkers | 50 executed; their scientific coverage varies by pilot |
| Full replay receipt | Consistency check passes against pinned historical Git objects |
| Scientific model calls in replay workers | Zero attempted through guarded llm.chat |
| Reader rebuild | Fresh PDF text, row and link extraction passes; eight target-revision files byte-identical |
| Clone status | git status --porcelain empty after all commands |

The canonical suite uses its existing scoped historical synthetic fixtures. Three named S60 tests receive archived README bytes through their existing read_bytes fixture; actual current presentation is checked separately without that fixture. Frozen tests and scientific validators were not edited. This record does not assert new independent scientific validation, a new dataset, agreement or collusion, or a change to any exploratory verdict.

The outer checkout is an origin clone. Its historical replay workers use local disposable checkouts at the already registered revisions. A new project environment was created using warm caches; the pre-existing export environment, Chromium, host Python/uv, OS libraries and fonts were reused. Inherited Python path/home/optimization and uv overrides were removed except the cache directory; uv configuration was disabled and the public default package index selected. This is same-host acceptance, not an empty-cache install, cross-host replication or network sandbox.

The tested revision retains iteration-61 reader exports. Later iteration-62 reader exports add a pointer to this acceptance record and are checked separately; the eight-file identity claim applies to the tested revision.

[Complete command output, canonical receipt, all 54 replay records and file hashes](../logs/iteration62_remote_full_acceptance_final.json). The preliminary working-tree-harness run is retained separately in logs/iteration62_remote_full_acceptance.json; it is not the final acceptance evidence. Both initial reviews and their dispositions are retained.

To repeat, use a full-history checkout with a branch whose origin ref matches HEAD, install the separate export environment documented in README, commit/push the runner, then run:

```bash
uv run --frozen python scripts/check_release_clone.py --full-validation --export-python /var/tmp/explorer-export61/bin/python --out /var/tmp/explorer-final-acceptance.json
```

The command needs origin access and may download Python/project dependencies. Its output is initially marked non-passing; only completed success replaces that state. No new experiment was run, so the experiment ledger remains unchanged. S68 remains interrupted without an estimate or restart.
