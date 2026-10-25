# S58 adversarial review (supplied text only)

I read only the files supplied above. I didn't open the filesystem, the raw archive, live calls or any other critic's review, and I made no edits.

**Verdict:** I found no bug in the supplied code that would bias the estimate or let a wrong number publish. There are two operational risks below that could abort the pilot. Everything else is an acknowledged limitation.

## Selection (correct)
- `turn=max(t in 2..9 if partner not passed)` uses task statuses only. Archived actions, text and notes enter only as assertions, never as filters.
- I hand-checked 24480: in C's case, B is TYPE-Y at index 8 and TYPE-X at index 9, so turn 8 is right. The other nine manifest prompts match their turns and show the partner as TYPE-Y.
- `s58_independent.py` rebuilds the S29 task schedule from the RNG. That is a genuine second derivation, not a copy of the selector.
- Picking the request with the highest attempt index (`max` on `payload[8]`), plus the parse and archived-match asserts, ties each case to the accepted S29 call.
- `select_cases` re-checks every S29 `cfg['sources']` hash, including `llm.py`. So the codex message-flattening is pinned to the S29 version. Effective sampling settings are still unattested, as the design admits.

## Erasure (correct)
- The `partition` on `'Completed public rounds: '` plus `count==1` is safe. The history line ends at the first newline, and `json.dumps` escapes newlines, `\u2028`, `\x85` and similar. The `json.dumps(completed)==history` round-trip blocks non-canonical lists.
- The test confirms exactly one changed line, equal to `Round {turn+1}. Completed public rounds: []\n`. It also confirms that system, statuses, notes, schema and every non-prompt request field are identical. The independent rebuild uses a different method (splitlines/index).

## Statistics (correct; scope is honest)
- The bootstrap percentiles (position p·(n−1) over 3125 exact Fractions) match numpy's linear method. The independent script checks the float values and the exact rational strings separately.
- Sign flips are exact on the half-unit scale. Zero blocks create ties, so p = 2^k/32 with k zero blocks. HIT therefore needs all five blocks strictly positive, which forces mean ≥ .5. Bootstrap lower > 0 then holds automatically, so the gates are not independent evidence. The design says this.
- On the 0.1 lattice, DUD's mean ≤ .05 is the same as mean ≤ 0.
- The arm-level sign tests answer an irrelevant null. They are labelled that way.
- Contexts are heterogeneous. Three of the ten are both-TYPE-Y (24480_C, 24483_B, 24483_C), all with archived rejections. That gives a floor effect beyond the one noted for 24483/24484, and blocks mix own-X and own-Y reviewers. It isn't a bug, but say it alongside the floor caveat.

## Operational risks (they can abort the pilot, not bias it)
1. **No-retry parser.** `strict` rejects code fences or any extra text around the JSON. S29 retried on parse failures (it tracked attempt indices), so its failure rate tells you the risk. Before launch, count S29 requests with `payload[8]>0` and record the chance that 20 calls run clean. A single fence voids S58.
2. **Runtime fingerprint drift.** `fingerprint()` hashes `~/.codex/auth.json`, and the check runs before and after every call. If codex refreshes its token mid-run, it aborts with "Local runtime drift". It fails closed, so the loss is the run, not validity. Note it as a known abort mode.
3. **Reproduction surface.** `validate` requires the S29 raw `requests/responses.jsonl` and the logs files `s58_attempt.json` and `s58_launch.json` to exist and match their hashes in the fresh clone. Check they are committed and not gitignored as large caches; otherwise the clean-clone step fails.
   - `SOURCES` includes `CLAUDE.md`, `s58_present.py` and `s58_release.py`, so any later edit to those makes the live archive fail validation. That is a deliberate freeze, but don't touch them after launch.

## Minor issues (none affect results)
- The concurrency sweep skips zero-length intervals. When end equals start, it counts the end first.
- If the reservation file already exists, a second live call writes `failure.json` into the new directory. That's harmless, and the test doesn't assert on it.
- `fixed_model` does nothing here, since the requested model already equals `CODEX_CHEAP`.
- The mocked-live test uses identical timestamps, so its concurrency check passes trivially. The separate nonzero-timing test covers it.

## Acknowledged limitations (no fix needed; keep the wording)
- The notes still carry history.
- "Round N" with an empty history, plus the unchanged public-disclosure and "only memory" system text, is an inconsistency cue.
- Prompt length, the missing-history cue, and past reviews and rewards all change together.
- No reciprocity, reputation or field-specific mechanism is identified.
- How much information remains varies by case (the 24481 and 24483 notes recount the actions; 24484's mostly recount reasons).
- The same ten contexts were reused across S51, S55 and S58: that adds multiplicity and is not an independent S29 replication.
- Only the immediate focal choice is observed.
- Boolean actions cannot show agreement or intent.

## Before launch
Measure the S29 parse-retry rate. Confirm the three reproduction files above are committed.
