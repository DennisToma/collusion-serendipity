# S16 adversarial review (failure archive only)

**Verdict:** I found no remaining integrity bug in the failure finding itself. The claims that 4 of 10 games completed, that the fatal decision was three over-long reasoning outputs, that every cached key replays exactly through the frozen simulator, and that no effect is estimated all hold up against the supplied code and JSON. Four narrower problems remain, about how claims are worded and how the release is evidenced.

**How I checked:** I had no file-reading or shell tool in this session, so I couldn't open the raw games or `responses.jsonl`. Every recalculation below uses only what you supplied: the `results/s16_failure.json` counts, the code, and the git status snapshot. I made no edits and no model calls.

## Recalculated numbers

| Claim | My calculation | Result |
|---|---|---|
| 173 responses | 38+37+36+36+14+12 | ✓ |
| 163 accepted | 4×36 + 11 + 8 | ✓ |
| 10 rejected | 2+1+0+0+3+4, which matches the 10 rejection details row by row | ✓ |
| Partial prefix, 24242_self (11/3/14) | Rounds 0–2 give 9, plus A and B in round 3; 11 + 3 rejections = 14 | ✓ |
| Partial prefix, 24242_shared (8/4/12) | Rounds 0–1 give 6, plus A and B in round 2; 8 + (A's round-1 rejection + C ×3) = 12 | ✓ |
| Fatal decision | C, round 2 counted from zero (3 counted from one), reasoning of 47, 44 and 46 words; the error string `…/2/C` matches | ✓ |
| Call in flight at abort | Started 19:48:02.895, before the shared arm's last completion at 19:48:04.722965 and so before `abort.set()`. Recorded at 04.723876 and completed at 07.345. Next call (C, round 3) raised `Terminal failure`, matching the marker | ✓ |
| Seed barriers | 43:48.550651 ≤ 43:48.551690; 46:56.093797 ≤ 46:56.094803 | ✓ |
| Arm starts within 60 s, intervals overlap | Arm start gaps are about 2 ms, 0.4 ms and 0.4 ms; intervals overlap in every block | ✓ |
| Launch order and deadline | Commit 19:40:10 ≤ preflight 19:40:17.224 ≤ first call 19:40:17.377; last call 19:48:07, before 20:15 | ✓ |
| 6 started / 4 unstarted | Consistent with the barrier and the abort | ✓ |
| 13 tests | 10 in `test_s16` + 3 in `test_s16_failure` | ✓ |
| 116 note-snapshot requests | Equals 96 + 20, which needs pair-member retries in 24240 plus pair requests in 24242 to total 20. That works only for pairs ({B,C}, {A,C} or {B,C}) or ({A,B}, {A,B}). I couldn't evaluate `Random(seed).sample` to confirm which | Consistent, not verified |

**Replay logic:** A cache miss raises `PrefixEnd`. Combined with the global checks that all 173 keys are used, none twice and every request covered, an early miss in the partial prefix would leave keys unused and fail the audit. The abort that `PrefixEnd` sets during replay only blocks uncached keys, so later cached replays are unaffected. The sequence check in the mutation test catches a rehashed fatal response. Analysis fails on the journal check and live resume fails on the failure marker, both before any metric runs.

## Remaining issues

1. **The rejection cause is the first check that failed, not every check.** `strict_response` returns the first failure in a fixed order: fields, then bid, then reasoning, then note, then the outsider's forbidden note. So the summary's "not invalid bids" is supported (bid is checked before reasoning). "Not oversized notes" is not: any of the 10 responses could also have had a note over 60 words or a forbidden outsider note, and it would still be labelled only "overlong reasoning". Either report every violated check per response, or narrow the wording to "first violated check: reasoning length (all 10); bids were valid".

2. **The clean-clone reproduction isn't evidenced and the archive isn't committed.** In the git snapshot, `data/s16_tender/`, `results/s16_failure.json`, `scripts/s16_failure_*`, `scripts/test_s16_failure.py`, `figures/s16_failure.png` and `logs/s16_launch_preflight.json` are all untracked. A clean clone of HEAD (73fe09d) contains none of them, so `s16_failure_release.py --clean-clone` can't have passed at a committed state. `logs/s16_release.json` has no clean-clone field either. The design requires this step. Commit, run it, and record the commit it passed at.

3. **"ODD" for a failed run falls outside the registered decision rules.** HIT, DUD and ODD are defined only on the primary estimate, and no rule maps a terminal failure to a verdict. Calling it ODD (whose registered meaning is "between DUD and HIT") lets the run be read as a scientific ODD. The REPORT table makes this worse: the S16 row sits under the column header "Result (descriptive 95% bootstrap bounds)". Use "FAILED / unclassified", or say plainly that ODD is a placeholder assigned after the outcome.

4. **The failing firm's role isn't reported.** C may be the outsider for seed 24242 (if the pair is {A,B}) or a pair member. An outsider's prompt has no notes channel at all, which matters when deciding whether the failure has anything to do with notes. Report C's role (pair or outsider) and the rejections by arm and role, which the design lists as a descriptive. Don't attach any rate claim.

**Still pending, not a bug:** the disposition says the final critic reviews of the failure report have been requested; none have come back yet. I couldn't review the figure or `s16_failure_present.py` because they weren't supplied.

## Acknowledged limitations (not bugs)

- **Preflight log:** `logs/s16_launch_preflight.json` is client-side evidence. It isn't hashed into the config or the registration commit and could be edited later. `server_time_attested: false` already says this; "pushed registration" in the summary should read "client-observed remote HEAD".
- **Inherited race:** the gap between the deadline/abort guard and the timestamp is a known, fail-closed race. It didn't come into play here; the margins were seconds against the abort and about 27 minutes against the cutoff.
- **Supplementary audit code:** the post-failure audit, presentation and release scripts were written after the abort, are outside the frozen manifest, and are labelled as supplementary.
- **Rejection split by arm:** rejections are equal (5 self, 5 shared). The summary correctly makes no claim about arm-specific failure rates.
- **Scope:** n=5, one model on a shared backend, bundled visibility cues, unverified agreements and divisible ties limit scope. None of these is exercised, since no effect was estimated.

## Scope of claims

No effect, interval, sign test, profit contrast or note-use comparison appears anywhere, and I'm not asking for any from the four complete games. The "operational lesson" is correctly framed as needing a new registration on fresh seeds. Apart from issues 1, 3 and 4, the wording in the summary and REPORT stays within what the evidence supports.
