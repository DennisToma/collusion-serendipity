# Iteration 58 independent review dispositions

Design critics: Codex read the repository and checked entry-point coverage/source bindings without running the full sweep; Opus saw supplied text only, with no filesystem or raw inspection. Their original reviews and process exits are retained separately. Neither is described as an external raw-data audit.

Accepted changes:

- Both critics: JSON object equality accepted bool/int and int/float substitutions. The runner now compares finite canonical JSON serialization with sorted keys, preserving those type distinctions and all fields. Integration probes exercise a real archived result's integer-to-float change.
- Opus M1: a worker launched from the live repository's scripts directory could expose bare sibling imports. The runner now copies its own bytes to external scratch before workers launch, places clone root/scripts first, and rejects modules imported from the source checkout outside the explicitly reused installed environment. The first version of this exclusion incorrectly rejected NumPy from that environment; its complete failed receipt is retained, and the dependency exception fixes the runner without editing frozen code.
- Opus M2: committed main-checker logs could conceal a missing fresh write. S03/S04/S07 now must actually write their expected output once in the current call, observed without modifying their source, and that written object must match the file read afterward. The receipt distinguishes an explicit success flag from successful completion without exception.
- Opus scope: replace the hard-coded broad model-call count with the sum of observed `llm.chat` attempts in passing workers; keep the narrower call-path guard and no-sandbox qualification. Describe shared object-store clones and reused dependencies explicitly, list all historical revision exceptions, and bind the new runner by its hash pending its atomic result commit.
- Codex/implementation compatibility: S67 requires its genuine historical result revision because its split-index protection correctly rejects later additions. S68/S72 already use their genuine historical result revisions. No scientific validation patches are used. Restrict repository output to iteration-58 logs.

Declined factual interpretation:

- Opus described the S53/S56/S67/S72 `verify(actual)` calls as only self-checks that do not recompute from original data. Source inspection contradicts that claim. Each separate checker opens the original response cache/request ledger and game files, reconstructs accepted actions and independently computes its specified metrics/intervals against the supplied target. See `scripts/s53_independent.py:12`, `scripts/s56_independent.py:75`, `scripts/s67_independent.py:59`, and `scripts/s72_independent.py:108`. The documentation nevertheless calls these existing same-author checks with pilot-specific depth; neither statistical independence nor new data is claimed.

Limits retained:

- Exact deterministic recomputation is consistency evidence, not scientific validity or uniform raw-provenance coverage. S01/S02 have no additional checker here. Failures stay failures with no effect estimate.
- Source/output hash bindings become durable only when committed together; receipts alone are not external execution attestations. Fresh-origin execution is a separate closure check, never claimed before it runs.
- Reused Python/packages/host libraries, local shared object-store clones, no network/process sandbox, and no cross-platform or fresh-current-install claim.

Final-review changes and dispositions (before the first result commit):

- Codex's unrestricted probe output and optimized-Python findings are fixed: output destination validation occurs before verification; `__debug__` is required before any probe; actual subprocess probes reject both unsafe destinations and `-O`. The probe receipt now reports 25 cases. No portfolio-runner source changed for these fixes, so the final 54-result receipt remains bound to the same frozen runner.
- Opus's raw-response probe concern is fixed: the probe now requires the analyzer's `KeyError: 'text'`, and the retained error shows the failure originates inside S29 analysis before the final Git-clean check. The type mutation and import-call probes already required their specific errors.
- Scope is explicitly 54 inventory-mapped **primary** result objects. Supplementary analyses, per-pilot summaries and figures are outside this runner. The documentation reports 43 explicit success flags and seven completion/assertion-based checker receipts, all compared to archived outputs.
- Preservation manifests and all 50 checker receipts are now checked against their actual frozen Git trees/logs. The main/source data roots and input conventions are accurate, historical exceptions are ledger-bound ancestors, and ignored clone outputs outside writer locks reject. A copied runner is described without claiming filesystem immutability or read isolation.
- Opus H1 is declined as a frozen-release scope requirement, not a current execution defect. No new scientific experiment occurs, so CLAUDE's per-experiment ledger requirement does not request a row here. The deliberate preservation rule prevents silent future ledger/direction changes; the instructions now say to use the released revision on a later branch. Existing scientific validators already use this archive discipline. STATUS entries append, preserving the complete historical prefix.
- The critics' atomic-commit concerns remain pending until the source/receipt/docs milestone commit. Reader exports and fresh-origin closure are subsequent work; neither was claimed by the reviewed draft.
