# S62 adversarial review (static only: no edits, no model calls)

**Verdict:** The economics, simultaneity, statistics and replay logic look correct to me. Don't launch yet, though: one high-severity failure-mode problem and one operational problem are each likely to abort the whole pilot before it produces an estimate.

## What I checked and found correct
- **Economics:** Approving X gives the reviewer +1 and approving Y gives −2, so approve-X/reject-Y is strictly dominant and the unique stage equilibrium. `outcome`, `metrics` (7 per X approval, 4 per Y approval) and the independent reimplementation agree. Pair total bonus equals pair internal bonus with two players, as the design already says.
- **Simultaneity and visibility:** Both reviews in a round are built from earlier rows and notes only. New notes are added only after both submit, and private reasoning is never replayed.
- **Statistics:** All 3,125 bootstrap means with (N−1)·p interpolation match `np.quantile` linear. The sign flip is inclusive, so one zero contrast gives p = 2/32. A HIT therefore needs all five contrasts strictly positive, which matches the design. The Fraction recovery from k/8 is exact.
- **Cache and replay:** Torn or duplicate rows fail closed, request/response hashes are cross-bound, replay must consume every key exactly once, and raw bytes must be unchanged afterwards. Exports are checked to be canonical.

## Remaining bugs

**1. HIGH: game-output fences will predictably abort the run.** The only readiness probe came back wrapped in a ```json Markdown fence. `parse_action` rejects fences, and the tests confirm it. Retries resend the same prompt with no error feedback, and three bad attempts abort the entire pilot. If the model fences half the time, the pilot survives 200 decisions with probability 0.875²⁰⁰ ≈ 10⁻¹². **Fix:** before registration, pre-specify that the game parser accepts exactly one ```json fence (the same rule as readiness), applied the same way in both arms. Report the fence rate descriptively, and update `test_readiness_fence_does_not_relax_game_parser` and `s62_independent.py` to match.

**2. MEDIUM: 20 minutes of launch headroom is too little.** Blocks run one after another and each game's 20 calls are sequential, so about 100 calls sit on the critical path. That is roughly 8–25 minutes at 5–15 s per call, before any 429 waits under the shared 45/min lock. `common_qwen` also removes the old cold-start retries, so a single timeout or 5xx ends the pilot (the design acknowledges this). **Fix:** require ≥ 60 minutes in `runtime_precheck`, or skip the launch.

**3. LOW: the runtime and the analysis disagree on the deadline field.** At runtime, `TenderCache` checks the deadline against `logical_started`. `analyze` instead asserts `call['call_started_utc'] < DEADLINE`, and that timestamp is taken a few milliseconds later. A call admitted right at 09:59:59.99x could complete normally and still leave a dataset that can't be published. **Fix:** have the analysis check `admitted_utc`, which it already validates.

**4. LOW: the model/backend check in `checked_call` can never fail.** `llm._aqueduct` returns the *requested* model name, not the served one. **Fix:** label it as a routing echo, not a check of what was served.

**5. LOW: one canary in `s62_independent.py` never fires.** It tests for `'private work notepad'`, but the prompt says `'work notepad'`. The non-pair branch never runs anyway. **Fix:** align the string or delete the branch.

**6. LOW: an error message names the wrong backend.** `main()` says "pins qwen-3.6-35b/codex"; it should say aqueduct.

**7. LOW: a brief lock gap.** `launch()` releases the writer lock before `main()` takes it again. The outer `logs/.s62-launch.lock` covers this, so no action is needed beyond noting it.

## Acknowledged limitations (not bugs)
- This is not a controlled cross-family comparison: the API differs from the CLI, and the serving stack and date differ.
- The served model, its settings and its sampling draws can't be verified, and nothing is fsynced.
- Note delivery, stated readability, note content and later history all change together between arms.
- With n = 5 the sign flip has p ≥ 1/32, there is no multiplicity correction, and a DUD does not show equivalence.
- The pair-internal-bonus gate is mechanically tied to approvals, so it isn't independent evidence.
- Tool use is restricted only by instruction.

## Before launch
1. Decide and pre-register the fence rule (bug 1).
2. Raise the required headroom (bug 2).
3. Switch the analysis deadline check to `admitted_utc` (bug 3).

Then rerun the offline suite and register. If bug 1 stays unfixed, I expect the run to abort and spend calls without producing an estimate.
