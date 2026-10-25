## Narrow final adversarial review (iteration 55)

**What I reviewed:** only the text you supplied: `scripts/iteration55_claims.py`, the disposition JSON, and the REPORT and README excerpts. I didn't read the repo, run `--check` or `--replay-selected`, hash anything, or look at the source JSONs or raw caches. Any statement below about whether a check passes describes what the code would do, not something I observed.

### The fixes you listed
| Fix | Verdict |
|---|---|
| One explicit 54-entry source map | Fixed. `SOURCES` holds 54 named paths, `run` requires `set(SOURCES)` to equal the inventory IDs, and no glob is left. |
| Baseline REPORT rows checked directly | Fixed. `git show BASELINE:REPORT.md` rows must equal the `report_row` values, and the current rows must equal those too. |
| Full REPORT/README baseline-plus-overlay check | Fixed. Each document is rebuilt exactly from the baseline plus three REPORT replacements and one README paragraph swap. If an anchor were missing, `replace` would do nothing and the check would then fail, so it can't pass silently. |
| 13 corruption probes, labelled by layer | Fixed: 4 preservation, 4 binding, 3 semantic, 2 editorial. Each probe raises if its mutation is accepted, and an edit that changes nothing would be accepted, so a missing target string can't produce a vacuous pass. The semantic probes call `check_row` directly, so they test the bindings rather than the equality guard. |
| Scaling assumptions written down | Fixed. The ×40 and ×5 factors are spelled out in `limits`. For S60–S70 the code checks `n_games==10`, 5 blocks, `3..10`, 5 games per arm, integer counts from 0 to 8, and that the count sum equals the mean × 40. |
| S72 game and round counts | Fixed. Per arm it checks 5 games and 40 rounds, and that the sums of `both_gain` equal the scaled means. |
| Mutable documents preserved during replay | Fixed. STATUS, REPORT and README are compared byte-for-byte before and after, and `preserved(BASELINE)` runs again. |

### Concrete issues (no highs)
**M1. The README overstates the clone requirement as S72-only.** Every mode depends on the baseline commit (`git rev-parse BASELINE`, `ls-tree`, `git show`), so a shallow clone fails even for `--check` without the replay. Suggested wording: "Use a full-history clone; the audit and the S72 replay both need historical commits." The REPORT's command line has no clone caveat at all.

**M2. "Offline" is broader than what the code enforces.** The `llm.chat` patch only applies inside the replay's child Python process. If the S72 "pinned historical clone" step starts its own interpreter or imports from another checkout, that code isn't covered by the patch. The receipt scope is honest about this ("llm.chat guard, not network isolation"), but the README and REPORT just say "offline". Either show that S72 runs in-process under the patch, or say "no-LLM-call guard" instead of "offline".

**M3. A fresh-clone reproduction hasn't been recorded yet.** The disposition says it "will be recorded separately". Until a log exists, nothing should state or imply that it has been reproduced from a clean origin. The current wording is a "Verify … with" instruction, which is fine as long as it stays an instruction.

**M4. Possible risk that I can't verify: the replay receipt is compared byte-for-byte.** `--check --replay-selected` requires `logs/iteration55_selected_replay.json` to be identical. If any replay record contains a temp path, timing or clone directory, the check fails on someone else's machine. Confirm that the records contain only deterministic fields.

### Low (noted, no action needed)
- No probe mutates README directly; it is only covered by the reconstruction check.
- Denominators come from `n_games×4` and `n_blocks×8`, not from fields that literally mean "per arm". Your extra checks make this safe, but it reads oddly.
- `NUM` only treats an ASCII `-` as a minus sign, so a Unicode `−` in a future edit would fail the check rather than slip through.

### Final claims
"54 rows", "307 highlighted values and failure counts", "144 metadata checks", "reporting fidelity, not scientific validity", "five selected replays" and "No hits promoted" are all consistent with the code's logic. Whether they actually pass is still unconfirmed by this review.
