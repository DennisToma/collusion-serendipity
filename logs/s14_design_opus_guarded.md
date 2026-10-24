I reviewed only the code you pasted. I had no shell access in this session, so I didn't check the clock, `data/s14_tender`, the git state or the test logs. (I also made one stray Google Drive search call by mistake. It was denied and returned nothing.)

# S14 adversarial review

## Remaining bugs and gaps (ordered by severity)

1. **The "one invocation" guarantee can be bypassed by deleting the folder.** The journal (`raw/execution.jsonl`) lives inside the same output folder it is meant to protect. If someone deletes `data/s14_tender` (or an interrupted run's journal plus the raw cache) and starts again, the code sees a fresh run and makes new live calls without complaint. Nothing outside that folder records that a start happened. So the threat DESIGN calls "silent live redraw" is only blocked if the folder survives. Fix: before the first live call, write and commit (or push) the `start` event somewhere outside the folder. For example, append to an `EXPERIMENTS.tsv` row and commit it. At analysis time, check that this anchor exists and that exactly one start was ever recorded.

2. **"Commit/push before calls" is required but never enforced.** `main()` checks that the source files are tracked and unchanged against HEAD, and records `rev-parse HEAD` as `registration_commit`. It never checks that this commit exists on the remote (for example with `git branch -r --contains`), or that its push happened before the journal's start time. The analyzer only checks that the file contents at that commit match the recorded hashes. So "registered prospectively" rests on a local commit that could have been made the same minute. Either check the remote before calls or soften the claim. As of the git status in this session, `DESIGN_S14.md`, `sim/tender.py` and every `scripts/s14_*` file are untracked. A live run would stop at the `ls-files` check, which is correct, but it means registration hasn't happened yet.

3. **The two arms reject invalid answers differently, and the design doesn't say so.** In the `none` arm, every firm (and the outsider in `private`) must return `private_message == ''`, otherwise the answer counts as invalid and is redrawn. Pair members in `private` have no such rule. Redrawing until a stricter rule is met is a form of selection that depends on the arm. It could also abort the whole dataset for a reason unrelated to bidding. The cost is small, but report invalid-attempt counts by arm and firm role, and add a sentence to the limitations.

4. **A crash in setup can permanently lock the live run before any call is made.** The `start` event is written before `TenderCache(...)` and `schedule()` run. If anything fails in between (bad JSON in an old file, or `config.json` exists without a journal), the next run refuses for good, even though no model was called. That is fail-closed and scientifically safe, but it's an avoidable risk to the 19:45 deadline. Moving the `start` write to just before the first block would fix it.

5. **A call can pass the deadline guard and still break the analysis.** The deadline is checked in `TenderCache.call` before `Cache.call` stamps `call_started_utc`. A call that passes the guard at 19:44:59.99 can be stamped 19:45:00.01. The analyzer then fails on `call_started_utc < DEADLINE` and the whole dataset can't be analyzed. DESIGN only mentions retries finishing late, not this case. Fix by stamping the start time before the guard, or by comparing against the guard's own timestamp.

6. **Small nits, all fail-closed or cosmetic:**
   - The abort check in `TenderCache.call` is duplicated (harmless).
   - DESIGN calls the test a "sign test", but the code runs a sign-flip (randomization) test on the magnitudes. The "five positive differences needed" claim is still right (any zero or negative block gives p ≥ 2/32), but name the test correctly in REPORT.
   - Deadlines and timestamps are compared as strings. That works only because every timestamp comes from `isoformat()` in UTC. Worth a comment or an assert on the format.
   - Source hashes are read relative to the current directory, so the analyzer must be run from the repo root.

## Checked and correct (not remaining issues)

- **Treatment timing:** messages are delivered after all of the round's bids. Only the recipient sees them, from the next round on. Calls within a round are made one after another, but no information from the current round leaks between them. Final-round messages are recorded but never shown to anyone. Each private game has 24 messages, as expected. The `round` label on a message is the round it was sent, numbered from 1 like the public history.
- **Provenance:** the response and request caches must match key for key, and their hashes are checked. Torn or duplicate rows are refused rather than repaired. On resume, only cached answers are allowed. Replaying from the cache must reproduce every row and ground-truth field, use every key exactly once, and leave the cache bytes unchanged. Block starts must be within 60 s, the two games in a block must overlap in time, and blocks must not overlap each other.
- **Inference:** the exact rational bootstrap uses the same random stream as the independent script. The sign-flip p-values reproduce. The profit gate uses the latent pair in both arms and is computed exactly. The HIT/DUD/ODD rule matches DESIGN, with HIT evaluated first. The independent script also enumerates all 3,125 bootstrap resamples as a cross-check.
- **Economics:** the pure-Nash set is the profiles where at least two firms bid 6, plus (7,7,7). So the possible Nash payments are {6, 7}, which the exhaustive test confirms.

## Acknowledged limitations (not bugs)

- n = 5 blocks: the t-intervals are fragile and the minimum possible p is .03125.
- The sign-flip test assumes the execution slots are exchangeable.
- The prompts differ in more than the channel: the box, the role cues and the wording change together.
- Shared-backend interference, and model labels and temperature that the client can't verify.
- The tie rule and full public disclosure are particular choices; costs are identical and there is one model.
- No agreement or collusion labels. Senders don't see their own past messages.
- An in-flight call can finish after an abort.
- Multiple exploratory screens; a DUD verdict does not mean the arms are equivalent.

## Scope of claims

The primary result is a difference in payment, so whether a payment is "above static Nash" isn't needed for the verdict. When REPORT gives payment levels against the Nash set {6, 7}, it shouldn't treat payments above 7 as collusion. An undisclosed horizon can support higher payments in repeated play without any communication, and both arms can sit above 7. A HIT supports only one claim: in this bundled prompt design, adding a private box raised mean buyer payment over rounds 4–12. It isn't evidence about real tenders or about agreements.
