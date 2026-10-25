# S53 review: static checks only, from the supplied text (no raw archive, no edits, no model calls)

## Concrete bugs and design defects

1. **Strict Pareto rounds are the same metric as mutual-Y rounds.** An agent's excess over Nash is 6×(incoming approval minus Nash incoming) plus the cost of its own deviation.
   - **Both X:** Nash is full approval, worth 7 each, which is already the maximum. Excess can't be positive.
   - **Mixed status:** the X author already gets the 6 at Nash, so approving Y can only cost them 2. Excess can't be positive.
   - **Both Y:** each agent's excess is 6×incoming − 2×outgoing. That is positive only when both approve, giving +4 each.

   So `strict_pareto_rounds == mutual_y_rounds` in every profile, and the regret and pair-excess identities make two more metrics linear in Y approvals and missed X. The "six equal metrics" carry only three independent quantities. Neither the design nor the summary says so, and readers will think they are seeing six findings. Add an exhaustive test asserting the equality, and state it in the design and summary.

2. **The hash freeze leaves out the replay code.** `freeze()` hashes the S53 scripts but not `scripts/s29_analyze.py`, `scripts/s29_independent.py` or `llm.py`. Yet the S29 replay and its independent check depend on all three. If they drift, the release still passes.

3. **The model-call guard is weak.** `patch('llm.chat')` only replaces the attribute on the `llm` module. If `s29_analyze` was already imported and did `from llm import chat`, it keeps the real function. Also, inside `analyze()` the import runs before that function's own patch, so the guard only holds through `release()`'s outer patch. Nothing blocks subprocess/codex or network calls. "Model-call-forbidden" is therefore a narrower claim than it sounds.

4. **The registration timing isn't enforced.**
   - `freeze()` doesn't refuse to run if `results/s53_payoffs.json` already exists.
   - `checked_manifest()` checks the manifest against HEAD, not against a pushed commit.
   - Paths are relative to the working directory, and `ROOT` is never used.

5. **Release is not atomic.** `release()` writes the JSON and figure before the independent check runs. A failed check leaves new artifacts on disk with no receipt. On the first run `byte_identical=False`, so the claim needs a second run to mean anything.

6. **The denominator of 8 is asserted only indirectly.** That each game has exactly 8 Y and 8 X opportunities is inferred from equality with `pair_bad`. Assert the per-game Y-submission count directly. Main also selects primary rounds by list position (`rows[2:10]`) without checking `row['round']`. The checker's keyed lookup catches a mismatch, but only by crashing.

7. **The independent checker shares assumptions with the main script.** Both read the action as `next(iter(reviews.values()))`. The checker also assumes the highest attempt number is the accepted response, and unpacks the request payload by position (`payload[5:9]`), which breaks silently if the format changes.

8. **Organization loss is in the design but never computed.** The design specifies −10 per Y approval, but nothing exports it. Either compute it or drop it from the design.

## Verified correct

- Payoffs: approve X gives reviewer +1 / author +6; approve Y gives reviewer −2 / author +6; reject gives 0/0.
- The one-shot Nash is unique (dominant strategies): approve X, reject Y.
- Full approval maximizes the pair's one-round bonus in all four status pairs.
- Regret = 2×Y approvals + missed X; pair excess = 4×Y approvals − 7×missed X.
- The mutual-Y definition is simultaneous, needing both submissions Y and both approvals.
- Bootstrap: exact `Fraction` arithmetic over all 3125 ordered draws, with linear interpolation at index 78.1, matching numpy's default quantile. The paired t interval uses df 4 and ddof=1.

## Acknowledged limitations (not bugs)

- Post-hoc choice of the strongest result means selection and regression to the mean.
- With five blocks, the bootstrap is anticonservative and intervals can collapse to a point.
- The analysis is static only: no repeated-game equilibrium, intent, mechanism or causal mediation.
- Note delivery and readability are bundled; there is one model and synthetic work; source runtime is unattested.
- The checker has the same author as the main script.
- Mutual-Y counts per round are not conditional on both-Y rounds; that rate appears only in the counts table.
- The scope wording is appropriately careful: ODD/context-only, no HIT, no new replication or collusion label.

## Priority fixes

Fix item 1 (state and test the identity) and item 2 (hash the S29 analyzer, its checker and `llm.py`) before release. The others are hardening.
