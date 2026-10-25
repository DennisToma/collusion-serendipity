# S55 adversarial review (supplied text only)

**Verdict: no blocking executable bug found.** The design is sound as a narrow screen of one visibility change. I checked everything below by reading the code and did not run anything. I did not read the S51 source, so the claim "exactly S51's selection" is unverified.

## Selection (outcome-independent)
- `turn=max(t in 2..9 : not passed[partner])` uses only task status. It is cross-checked against `task_status(seed,t)`, and the independent script re-derives it from the `s29-tasks-{seed}-{partner}` RNG. Every primary schedule has four TYPE-Y rounds, so the max always exists.
- Taking the max attempt is fine. The strict parse and the archived-approval match confirm it is the accepted response.
- Approvals, notes and text never enter selection. The "no note exposure" assert could in principle exclude a case, but it does not here: all ten cases are present.

## Deletion is exact
- `request()` requires exactly one marker line and canonical `json.dumps` (`==statuses`). It deletes only `case['agent']`, and `json.dumps` keeps insertion order.
- The test checks that exactly one line changed, that after = `{partner:'TYPE-Y'}`, and that system and all non-prompt request fields are identical. The independent rebuild uses `splitlines` rather than `partition`, but the same `json.dumps`, so it shares the serialization assumption.
- History, notes, horizon and schema stay byte-identical. The system text still says "each employee is assigned one work submission", so the missing entry is a visible completeness cue, as the design acknowledges.

## Economics
- The payoff test asserts A's score = 6·incoming − 2·outgoing for both own types. That is correct.
- The test fixes the partner's type at TYPE-Y (`passed B=False`), so it covers only this case. That is acceptable.
- The design rightly declines any role-confusion or irrelevant-information reading. History shows own type matters strategically: both-Y rounds are mutual rejections in every game, and approvals of a TYPE-Y partner happen when the reviewer is TYPE-X (reciprocity). Reviewers can also infer their own type from the alternating pattern and from notes such as "A=X, C=Y". A null result therefore cannot mean the model ignores its own type.

## Composition (acknowledged)
- Own status is X in 7 cases and Y in 3, and block 24483 is Y/Y.
- Pooling cases where deletion removes "X" with cases where it removes "Y" can cancel opposite effects. The no-subgroup rule is correct, but the report should say a DUD does not rule out type-specific effects in opposite directions.

## Statistics
- The bootstrap enumerates all 3125 ordered draws with linear interpolation at 78.1 and 3045.9 (correct indexing), which matches `np.quantile(method='linear')`. The exact rational reconstruction on the doubled (/10) scale is right.
- Sign flips: an exact tie with a zero block gives p ≥ 2/32, so HIT ⇔ 5/5 positive blocks with p = 1/32 and mean ≥ .5. This matches the design's statement.
- `mean<=1/20` is the same as `mean<=0` on the 0.1 lattice. The t interval collapses when all blocks are equal. Both are acknowledged.
- The arm-level sign tests are labelled non-primary, which is correct.
- n = 5 percentile bootstrap is anti-conservative. Calling it "descriptive" is correct.

## Guards
- Failure handling holds up:
  - One transport attempt: with `retries=1` and backend `codex`, `dict.fromkeys` collapses to the single model.
  - Responses are fsynced before parsing.
  - Abort is serialized with admission.
  - `pool.map` inside a `with` block gives real block barriers.
  - Attempt reservation happens before selection, runtime or registration.
  - `.writer.lock`, failure-only refusal, and no resume of incomplete archives are all in place.
- Validate checks the schedule, the ≤ 2 concurrency sweep, the barrier and order, hashes, timing headroom, and registration ancestry plus per-file `git show` hashes.
- `fixed_model` is redundant but harmless.

## Operational risks (not bugs)
1. **auth.json drift kills the run.** `s37_runtime` hashes `~/.codex/auth.json` before and after every call. If codex refreshes its token mid-pilot, the pilot fails closed and the single attempt is used up. Worth checking the token's age before registering.
2. **Clean clone needs two log files committed.** Live `validate` reads `logs/s55_launch.json` and `logs/s55_attempt.json` through ROOT. If they are not committed and pushed, the fresh-clone reproduction fails. It fails loudly, so this is not a silent hazard.
3. **Environment pin.** Validate requires the current interpreter's python/numpy/scipy versions to match. That is consistent with the frozen-venv clone step, but it fails on any other machine.
4. **Returned model is unverified.** `response['model']` is the requested model name echoed back by `llm.py`, not the served one. The design acknowledges this.

## Scope
The claims are appropriately limited:
- the immediate focal decision only, with no partner adaptation;
- late histories;
- no replication;
- any HIT needs fresh confirmation.

No overclaiming found in `s55_present.py`.
