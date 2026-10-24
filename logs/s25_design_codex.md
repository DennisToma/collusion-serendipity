One concrete guard gap remains. The assigned-order contrast otherwise matches the stated fixed-history scope.

- **P2 — Dispatch provenance checks omit cases and source data.** In [s25_replay.py:201](/home/factory/collusion/collusion-serendipity/scripts/s25_replay.py:201), dispatch checks hash only `SOURCES`, which excludes `data/s25_cases.json` and every S19 data file. The completion check has the same omission and writes `complete` before the later `validate()` checks source data. This contradicts DESIGN_S25’s promise to check code, cases, and source-data hashes at every dispatch and completion. Persistent drift eventually prevents analysis, but additional calls can occur meanwhile; temporary drift restored before validation goes undetected. **Action:** check the frozen case-file digest and `cases_obj['source_sha256']` at admission and before recording completion.

The substantive controls check out:

- Reconstructed cases exactly match the frozen JSON and S21 selection: ten negative-type targets, four archived approvals, six rejections. Selection uses actions/statuses rather than explanation semantics.
- Paired requests preserve the original system, history, statuses, accessible notes, schema values, and remaining instructions. Only the two requested fields swap. Visibility checks found complete prior public rounds, matching current statuses, and only prior notes from accessible authors. The archived current response is absent.
- The parser rejects duplicate keys, wrong fields/types, incomplete review maps, and notes without notepad access. Noncompliant field order remains valid; analysis reconstructs actual order from raw response text.
- Directory locking, exclusive external launch receipts, incomplete-archive rejection, and deduplicated single-attempt routing support the one-shot policy. The independent checker correctly limits itself to numerical reconstruction; production validation supplies provenance/publication checks.
- Contrast direction, block averaging, bootstrap percentiles, inclusive sign flips, and frozen classification agree with the design and independent calculations.

Explicitly acknowledged limitations are appropriately distinguished from bugs: selected histories, five blocks, uncontrolled stochastic draws, service interference, unenforced temperature/token limits, local chronology, and requested serialization rather than internal reasoning order. The screen cannot establish confirmatory significance, collusion, or why S19 explanations contradicted actions.

Six targeted tests passed, with transport setup mocked to avoid filesystem writes. I also checked source visibility and representative uncertainty calculations. Full archive-writing tests were not run. No edits or live model calls were made.