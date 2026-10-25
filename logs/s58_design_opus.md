# S58 adversarial review (supplied text only, no edits)

**Verdict: do not register yet.** There is one executable bug, and it breaks both the independent verifier and the unit test suite. Both files are in the frozen `SOURCES` set, so they must be fixed before you register. The live request constructor itself is correct.

## Executable bugs

**B1 (blocker): `scripts/s58_independent.py` cannot pass.** It finds the history line with `line.startswith('Completed public rounds: ')`. But every source prompt's first line is `Round N. Completed public rounds: [...]` (see `prompts()` in `sim/notepad.py` and all ten prompts in `data/s58_cases.json`). No line matches, so `next(...)` raises `StopIteration` on the first row. The replacement line is also wrong: it rewrites the whole line as `'Completed public rounds: []\n'`, which would drop `Round N. ` and reset the current round, the exact thing the design forbids. If someone "fixes" the lookup alone, the verifier would then reject every correct erase request. Fix: find the single line that *contains* the marker, check the marker appears exactly once, and rebuild it as `prefix + marker + '[]\n'`.

**B2 (blocker): `test_selection_and_exact_public_history_erasure` fails for the same reason.** Its `assertTrue(original[i].startswith(...))` check is false for every case. That means `test_full_dry_and_mutations` (which calls `verify`) also fails, and the canonical-suite preflight cannot honestly pass. If `logs/s58_preflight_*.log` shows a pass, check which code it ran.

**B3 (cosmetic):** the docstring in `scripts/s58_replay.py` still says "Own-current-status history sensitivity", left over from S55.

## Checks that pass

- **Selection:** uses only `market.passed`, takes the maximum index in 2..9 where the partner is TYPE-Y, and the independent verifier rebuilds the S29 task RNG. It is outcome-independent. It picks the highest-attempt request and confirms the archived review matches.
- **Erasure in `request()`:** the marker must appear exactly once, `json.dumps(history)` round-trips, only the list is replaced, and `Round N.`, the statuses, the notes and the schema are kept. Default ASCII-escaped JSON means the history can't contain raw newlines.
- **Transport:** codex only, `retries=1`, and `fixed_model` collapses the fallback list to luna, so each request is one logical attempt. On failure, any in-flight partner response is still saved to `responses.jsonl` but not accepted, because `abort` is set.
- **Statistics:** exact `Fraction` arithmetic. Interpolation indices stay in range (3045.9 is below 3124). The sign-flip test is inclusive, and blocks equal to zero create ties that push p to at least 0.0625, so HIT really does require 5/5 strictly positive blocks. The verifier's doubled-integer reconstruction is right.
- **Scheduling:** the barrier and two-call concurrency sweep are correct, and first-view orders are opposite within each block.

## Operational risks (not bugs)

- `auth.json` is in the runtime fingerprint. If codex refreshes its token during the run, the post-call drift check aborts the pilot. The one-shot reservation then forbids a rerun, so the effect estimate is lost.
- `CLAUDE.md`, `llm.py` and `uv.lock` are in `SOURCES`, and `validate` compares them to the *current* working tree. Any later change to them makes the archive impossible to analyse or release. Comparing to the registered commit would avoid this.
- There is no parser retry, but selecting the max attempt implies S29 sometimes needed retries. One fenced or malformed reply out of 20 ends the pilot.
- `clean_clone` requires an empty `git status --porcelain`. `run()` creates `data/s58_history/.writer.lock`; unless that file is gitignored, the check fails.

## Scope and statistics (limitations, mostly already acknowledged)

- **HIT is close to unreachable.** Archived retain approvals are 0/2 in blocks 24483 and 24484. Unless fresh retain draws differ from the archive, those blocks give a contrast of zero or less, and HIT needs all five positive with mean ≥ 0.5. The pilot works mainly as a DUD/ODD screen with very low power; say so explicitly.
- **How much erasure removes varies by block.** The 24481 and 24482 notes list nearly every past action ("A approved C"), so erasing the list removes little there. In 24483 and 24484 the notes carry less. The contrast mixes blocks with different amounts of leftover information.
- In three of the ten cases (24480_C, 24483_B, 24483_C) the reviewer is TYPE-Y in the current round as well as the partner, which is a different incentive situation from the other seven. Turns range from index 6 to 9, so erasure removes between 6 and 9 rounds.
- Erasure also contradicts the system prompt ("All statuses… become public", "Your only memory is the provided history"). The inconsistency cue therefore can't be separated from the information that was removed. You acknowledge this; keep it prominent.
- The source blocks have been reused across S51, S55 and S58. These results are not independent replications, and no reciprocity mechanism has been identified.

**Before registering:** fix B1 and B2 (and B3 if you like), rerun the full suite and the 20-call dry run, then register.
