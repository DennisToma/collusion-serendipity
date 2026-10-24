Exit code: 0
# Adversarial methodology review of S04 (shared public-information advisor)

**Bottom line:** the design is careful about provenance and call matching. Its main weakness is that the primary outcome sits on a weak causal path. Several implementation details could make the two arms identical, or make games non-independent, without anyone noticing. Fix the items in section 5 before any live output exists.

---

## 1. Material flaws

**F1. A naive response cache can silently erase the treatment.** The two advisor calls use the same prompt, and every game's round 1 has the same empty history. If the cache key is a hash of the prompt, model and parameters, several things break:
- The second advisor sample is served from the cache and equals the first, so "shared" and "independent" become the same arm.
- Round-1 advice and seller actions are identical across all 10 games, and possibly later rounds too wherever histories coincide. The games stop being independent units.
- Retries after invalid JSON may return the same cached invalid output.

Fix: key every live call on `(run_id, seed, arm, game_id, round, role, slot, attempt)`, and assert that the two slots are distinct cache entries. Dry-run keys are already separate, which is good, but live-to-live collisions are the real risk.

**F2. Codex exec context contamination.** Codex exec is an agent, not a bare sampler. Run from the repo, it loads AGENTS.md or CLAUDE.md-style context, can read files (including DESIGN_S04.md, the hypothesis and other games' caches), and may use tools. A seller that reads the design or another game's log breaks blinding and independence. Fix: run every call with `-C` set to an empty per-call scratch directory under `/var/tmp`, in a read-only sandbox, with no repo instructions loaded. Log the exact command, and verify on a dry run that the model cannot see repo files.

**F3. The primary outcome has a weak mechanism, so a DUD is nearly guaranteed and tells you little.**
- Routing changes only the *correlation* between the two pair members' advice. Each firm's marginal advice distribution is identical in both arms because the slot is randomized.
- So round-level expected output differs only through (a) a nonlinear response to correlated advice, or (b) path dependence: correlated advice produces correlated actions, which produce a history the advisor and sellers then react to.
- The advisor is told to justify each recommendation "by each firm's own profit". That pushes it toward best response (about 6) and removes the main lever for restraint.

A difference of at least 1 unit is half the distance from Nash (6) to the joint-monopoly output (4), which is large for a second-order channel. Expect a DUD from the prior alone. The report should say this up front and not present a DUD as evidence that shared advisors are harmless.

**F4. The most likely real effect is mechanical correlation, and the design relegates it to a secondary.** Pair advice equality, pair action equality and the signed-change product will rise in the shared arm by construction whenever a single response recommends a symmetric vector. Two things follow:
- These secondaries must be labelled as **mechanically induced by routing**, not as evidence of coordination.
- This is the most interesting serendipity angle: a common advisor produces collusion-looking correlation with no messages and no intent, which is a candidate false-positive generator for the Q1.4 and Q2.2 detectors.

Saying nothing about detectors is fine for this iteration. But pre-register action-correlation as a co-primary with its own decision rule, or explicitly accept that the pilot's main informational value is being left out of the primary.

**F5. The degeneracy guard has no threshold and measures the wrong quantity.** "Count per-round sample vector disagreement" counts differences in unused components, such as the outsider's or the first member's. What matters is the **delivered contrast**: in how many rounds the second pair member's advice differs between the shared and independent routing, i.e. slot A's component for that firm versus slot B's.

Pre-specify:
- an UNINFORMATIVE label, overriding DUD, if the delivered-contrast rate is below some value (e.g. 25% of rounds 4–12, pooled; pick the number now);
- the delivered-contrast rate is reported per game.

Better still, measure advisor sample diversity *before* the live run (see section 5).

## 2. Decision-rule weaknesses

**D1. HIT is effectively one condition plus a magnitude check.** At n=5, exact p≤.05 requires all five differences to be strictly negative, and then a percentile bootstrap upper bound below 0 is automatic. The bootstrap clause adds nothing. That is acceptable, but say so instead of presenting it as a separate safeguard.

**D2. The DUD rule is anti-conservative and can misclassify consistent effects.**
- A percentile bootstrap on 5 points has fewer than about 126 distinct resamples and badly under-covers. Its lower bound is roughly the sample minimum.
- Example: five differences all near −0.8 meet "bootstrap lower > −1" and are labelled DUD, even though that is a perfectly consistent restraint effect that would be scientifically interesting.

Fix: base DUD on the point estimate plus the sign pattern, or on the t interval. Alternatively, define DUD only as "point estimate ≥ −0.25", and treat everything between that and HIT as ODD.

**D3. Effects in the opposite direction are folded into DUD.** For an explorer, shared advice *raising* output (more aggressive, synchronized best-responding) is a surprise worth flagging. Label a point estimate ≥ +1 with a consistent sign as ODD (reverse), not DUD.

**D4. Power is not stated.** Rejecting with the sign-flip test needs P(all 5 differences < 0) of about 0.8, so Φ(δ/σ_d) ≥ 0.956, so δ ≳ 1.7·σ_d. Estimate σ_d (between-game SD of pair mean output, rounds 4–12) from S02 now and write down the minimum detectable effect. If it is much larger than 1, HIT is near-unreachable, and the design should say so before outcomes exist.

**D5. Ties and missing games are unspecified.**
- Ties: a difference of exactly 0 is plausible with integer actions and modal advice. Pre-specify how the sign-flip handles it (e.g. it counts as non-negative, or the conventional drop-zero rule). Dropping a zero leaves n=4, which makes HIT impossible.
- Missing games: if a game fails after 3 retries, n drops to 4 and the minimum p becomes .0625. Pre-specify one of: (a) rerun the whole game with a new attempt ID, at most k times, logged, with the arm-execution slot kept; or (b) drop the block and report that HIT is unreachable. Also report failure counts by arm, since differential failure is a selection channel.

**D6. The profit screen can pass for the wrong reason.** Pair profit can rise because the *outsider* cuts output, not because of pair restraint. Report the profit decomposition (price effect versus own-quantity effect) alongside the screen.

## 3. Causal and interpretive confounds

- **C1. Pairing gives little variance reduction.** Without API seeds, seed-block pairing matches only the pair assignment and slot schedule. It mainly controls for **time drift**, such as Codex model or server changes and rate-limit periods. That is still worth keeping, but don't claim more for it. Log the model label and timestamps per call so drift can be checked.
- **C2. Within-round simultaneity must be guaranteed.** State and enforce that the three sellers in a round are sampled with no access to one another's current choices or cache entries. Concurrency across games must also never mix histories.
- **C3. Same model for advisor and sellers.** Advice adoption is confounded by the fact that the advisor recommends what the seller model would have chosen anyway. The adoption metric needs a baseline: the outsider's agreement with the advice the advisor *would* have given it, which you already have in the vector. This is cheap and very informative.
- **C4. Advice framing.** Pin the exact wording ("An advisor recommends you produce X"?). Whether sellers treat it as authoritative changes adoption a lot. It is held constant across arms, so it is not a confound for the contrast, but it limits external validity.
- **C5. Pair membership is identified in prompts?** If firm indices appear in the history (Firm 1/2/3), advised firms may infer something from the outsider's behaviour. That is fine, but confirm that nothing in the seller prompt reveals who else is advised.
- **C6. Interpretation scope.** This tests "correlated sampling from one call versus two calls of the same model". It is not common-advisor collusion, hub-and-spoke, or algorithmic-pricing advisor effects. The design already says this; make sure REPORT.md and HITS.md repeat it verbatim.

## 4. Minor points

- Over 10 secondary contrasts at n=5 with no multiplicity control: report them as descriptive only, without p-values, or with a stated "no correction, exploratory" note.
- Rounds 4–12 is a reasonable burn-in. All-round and final-round metrics are already prespecified, which is good, but name the primary window as the only one eligible for HIT.
- Who counts as the "first pair member" in the independent arm should be randomized per seed, not fixed by firm index, to avoid confounding with listing order.
- RNG 2404 is used for the bootstrap, arm-slot randomization and (implicitly) the slot schedule. Use separate named streams so that changing one doesn't shift the others.

## 5. Required pre-outcome fixes, in priority order

1. **Cache key**: include game, arm, round, role, slot and attempt. Assert that the two advisor slots never share an entry. (F1)
2. **Codex isolation**: empty working directory, read-only sandbox, no repo instruction files. Verify with a dry run that the model cannot see repo files. (F2)
3. **Advisor diversity pre-check**: on synthetic or dry histories (separate cache keys), sample the advisor twice per state for about 20 states and measure the delivered-contrast rate. If it is near 0, redesign before spending the live budget. This tests the instrument, not the outcome, so it is not peeking. (F5)
4. **Write down the minimum detectable effect** using σ_d from S02. (D4)
5. **Revise labels**: DUD = point estimate ≥ −0.25. Add UNINFORMATIVE (delivered contrast below threshold) and ODD-reverse (≥ +1). Drop the bootstrap clause from DUD. (D2, D3, F5)
6. **Pre-specify tie handling and the failed-game replacement rule.** (D5)
7. **Promote pair action correlation to co-primary**, labelled as mechanical, or explicitly record why it isn't. (F4)
8. **Add the outsider-baseline adoption metric and the pair profit decomposition.** (C3, D6)
9. **Separate RNG streams; randomize the first pair member per seed.**

Once these are in, the pilot is a clean, cheap test. The likely outcome is a null on output restraint and a strong mechanical correlation effect. The second is probably the more useful result to hand off.
