# S59 adversarial review (from the supplied text only)

I read only the text in your message. I made no edits, ran nothing, made no model calls, and read no other critic reviews.

**Verdict: I found no executable bug that would make the S59 estimate or verdict invalid.** It is fine to launch once the conditional points (4 and 5 under "Executable issues") are confirmed.

## Selection (last TYPE-Y opportunity in S29)
- `turn=max(t∈2..9 : not passed[partner])` uses only the task schedule. With 4 TYPE-Y rounds among 8 primary rounds, a case always exists. There is no filter on actions, explanations or notes. The "No note exposure" check stops the run rather than dropping a case, so it is not a hidden selection step.
- The resulting turns (24480 B9/C8, 24481 A8/C9, 24482 A6/B8, 24483 B9/C9, 24484 A7/B8) match the manifest.
- The independent checker rebuilds each turn from the `s29-tasks-{seed}-{partner}` RNG without calling `sim.notepad`. That is real separation.
- These are reused cases. The full-prompt equality check against `prompts()` proves the source prompts are faithful. It does not replicate S29.

## Lossless encoding
- Python `==` ignores dict key order and treats `True==1`, so a plain equality check would miss both problems. Both scripts also compare `json.dumps` byte-for-byte against the original history, which closes that gap.
- The rebuilt key order (round, statuses, reviews, scores, charges; agents sorted) matches how `prompts()` builds the original.
- Primitives are copied directly, so booleans, ints and negative scores survive.
- Exactly one line changes. `count(marker)==1` holds, and the system prompt, current statuses, notes, schema line and request fields are identical across arms (the test checks all of these).
- The independent checker does not import `s59_replay`. It packs the table itself, unpacks it by position, checks the reconstruction byte-for-byte, and requires the sent prompt to equal its own rebuild. Because the sent prompt must match byte-for-byte, this counts as a roundtrip, but it never parses `column_paths` generically.
- Two confounds change together with the representation: whitespace removal and roughly halved length. The design already admits both. The table also keeps the agent order fixed (sorted) rather than putting the focal employee first, exactly as the original does. That is not a confound.

## Statistics
- The percentile position 3124·p (78.1 and 3045.9) matches NumPy's linear method.
- The two scripts' exact-fraction calculations (block values as fractions vs. doubled integers ÷10) reduce to the same strings.
- The sign-flip tests are exact. Any zero block makes the upper p at least 2/32, so a HIT does require all five blocks to be positive. That makes the mean at least .5, as the design states.
- DUD at mean ≤.05 is the same as mean ≤0 on this lattice. HIT is checked first.
- The registered direction is original minus compact with the upper test, which is consistent with the question being asked.
- `t95` collapses to a zero-width interval when all block values are equal. The design already acknowledges this.

## Guards
- **Transport:** `retries=1` together with the deduplicated `[luna, luna]` model list gives exactly one subprocess attempt. `fixed_model` changes nothing in practice, since `CODEX_CHEAP` already equals `gpt-6-luna`.
- **Ordering and concurrency:** each response is written to disk before parsing. A shared abort flag plus the admission lock block any new request once a failure occurs. A thread pool of two per block keeps at most two calls in flight. The interval sweep sorts ends before starts at equal timestamps, so back-to-back calls are allowed.
- **Registration and runtime:** the one-shot reservation, registration against HEAD/remote/clean tree, and runtime fingerprint checks before and after each call all look correct. `validate` refuses archives with failures, partial runs or tampering.

## Executable issues (minor, none fatal)
1. **Spurious failure file.** If `LIVE_ATTEMPT` already exists, `run` raises FileExistsError but still writes `failure.json` into the target directory (because `new=True`). This is harmless but misleading.
2. **Independent checker can't enforce two cases per seed on its own.** It assumes two cases per seed (it divides by 2) but only checks 10 cases and 5 seeds. It relies on the primary `validate` (`cases_obj==select_cases()`) for that. It also does not re-check registration, timing or runtime, which matches its docstring.
3. **Typo in the published summary.** `s59_present.py` says "Cases and screen **originaled** without replacement", which looks like a find-and-replace slip. It is a text defect in the published summary.
4. **Clean-clone run needs files committed.** It requires `logs/s59_launch.json` and `logs/s59_attempt.json` to be committed. Also, `run()` creates `data/s59_history/.writer.lock`, which will dirty `git status --porcelain` unless that file is committed or gitignored. Please confirm this.
5. **One malformed reply ends the pilot.** The parser is strict, so a single reply wrapped in code fences aborts all 20 calls and the effect estimate. This is per the design, and S29 used the same strictness, but it is the biggest operational risk.
6. **Earlier cutoff than the repo schedule.** The 09:00 cutoff is stricter than CLAUDE.md's Phase-2 pilot deadline of 14:30. That is conservative, not a bug.

## Limitations the design already acknowledges (not bugs)
- Length, field repetition, JSON shape and reading burden all change together, so the result says nothing about mechanism.
- There is no length-matched control. A lossless decode does not mean the model understands both versions equally.
- The cases are reused and late in the game, with earlier tests counting as multiplicity. Archived rejections in 24483/24484 may set a floor on the original arm.
- Served model identity and actual sampling settings are not verified. The reported model name is the requested name, not proof of what was served.
- Persistence is process-level only (parent directories are not fsynced).
