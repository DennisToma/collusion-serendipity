# S31 independent review: wage-setting employers (A2)

**Bottom line:** I found no bug that changes the S31 result. The DUD verdict is arithmetically correct under the frozen rule. The one change I'd make is a wording fix in REPORT.md. I made no edits and no model calls.

## What I recomputed
- **Equilibria.** I worked through all 441 wage profiles by hand. If one firm offers less than the other, it does better by matching, so no uneven profile is an equilibrium. With equal wages w, a firm gets (20−w)/2; raising its wage by one gets it 19−w. Holding equal wages pays only when w≥18, so the pure equilibria are exactly (18,18), (19,19) and (20,20). Total employer profit there is 2, 1 and 0. At (0,0) each firm gets 10, and one firm raising to 1 gets 19. Worker earnings plus employer profit always equal 20. All of this matches the design.
- **Primary result.** All five block differences are 0. All 3,125 bootstrap means are 0, so both bounds are 0. All 32 sign-flip sums equal the observed 0, so the upper p is 1. The t interval is [0,0]. With a mean of 0 (≤0.5) the verdict is DUD, and the profit gate (shared minus self = 0) is consistent.
- **Secondary results.** I reproduced every reported number for offered wage, tie rate and regret: the bounds 3/80, 3/40, −3/80, 199/20, 159/16 and 799/80; the t intervals [−0.0222, 0.0472] and [9.9325, 10.0175]; and the sign-flip p-values of 0.5. Every metric fits the stated denominator of 32. Games with tie rate 0.875 fit a single (10,9) round; the regret of 65/16 checks out.
- **Simultaneity and visibility.** Round-t notes are added only after both employers submit. Each prompt is built from history up to the previous round. Self-only employers see only their own notes; the independent verifier rebuilds every note snapshot from the raw caches and checks it. With empty history, the two arms' prompts differ only in the one sentence about who can read the notepads.
- **Failure handling.** The transport layer makes one attempt per call, a single failure stops all new requests, and an interrupted run cannot be resumed. All of these fail safe.

## Bugs that remain
1. **Medium, REPORT.md wording.** "this low wage level verifies no agreement" can be read as saying it proves there was no agreement. Replace it with "a wage of 10 does not show that any agreement occurred". Also say that a wage of 10 matches neither equilibrium wages (18–20) nor the joint-profit wage (0). Each employer gives up about 4 profit per round compared with its best reply, which is consistent with an even-split habit rather than strategy.
2. **Low, replay check.** It blocks live calls by patching `sim.common.llm.chat`. That works only because `sim.common` and `sim.labor_cache` load the same `llm` module. The source is frozen, so document this rather than change it.
3. **Low, deadline check.** It compares timestamps as text. That is correct for this exact timestamp format but would break if the format changed. Document it.
4. **Low, notes count.** "written=100" is hard-coded, not counted. The game checks make it true, but the count isn't independently measured.

## Limitations already acknowledged
These are already stated in the write-up:
- Readable notes and the readability sentence are bundled; public wages are visible in both arms.
- The profit gate follows mechanically from wages.
- With five blocks, any zero difference rules out p≤0.05.
- The model, its sampling and backend tool use are not verified by the provider.
- The setup has no real labor-market features.

There is no claim of equivalence and no claim about the population. A DUD here says nothing about whether shared notes would matter from a different starting wage level.

## Not checked
I had no access to the raw responses, so I could not:
- recompute the primary from individual wage choices, or read the 200 notes and reasons;
- run the cache replay, the tests or the source-hash checks;
- verify the remote git state, the timing records or the figure.

The game summaries alone do not pin down the raw wages: they are consistent with some mixes of tied wages around 10, not just a constant 10. I did not read any other final critic reviews.
