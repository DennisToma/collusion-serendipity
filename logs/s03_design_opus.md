Exit code: 0
# S03 adversarial review: exact conditional payoff calculator

**Verdict:** I found no bug that makes the visible S03 code invalid. Before any live calls, fix three medium issues (M1–M3). M4 doesn't need code changes, but it limits how the result can be worded. Everything else is a limitation or a low-severity issue.

**What I could and couldn't check:** this session had no local file-read or shell tools. I reviewed only the four files you pasted. The imported helpers are unverified: `checked_call`, `public_history`, `Cache`, `parse`, `payoffs`, `system_prompt` and `s02_analyze.summarize`. They are listed under "To verify" below. I edited nothing and ran no models.

## Checks that pass

- **Arithmetic:** `conditional_table` gives (max(0, 30−R−q) − 6)·q. Static Nash is q=6, P=12, π=36. At R=13 there is a tie at q=5 and q=6 (π=30). At R=24, q=12 gives −72.
- **Primary window:** `metrics(start=3)` covers rounds 4..12, which is 9 rounds × 3 firms = 27 per game. That matches `exact_denominator=27` and `classify`'s `27*len`.
- **No current-round leakage:** prompts are built only from completed `rows`, and the current round's `records` are appended after all three calls. The test checks this by rebuilding each prompt.
- **Treatment delivery:** at round 1 both arms get the same prompt. After that, the test shows the control prompt equals the treatment prompt with the caption and table removed. The table is computed per firm from that firm's own two rivals.
- **Decision rules:** the order is HIT → ODD-reverse → DUD → ODD, matching the design. Fractions are used. The sign-flip numerators are integers and p = k/32 is exact as a float. The boundary tests are correct (e.g. 134/135 → ODD; all negative but mean > −1 → DUD).
- **Fail-closed behaviour:** there is a model/backend mismatch error, a cap of three invalid attempts, a 10-game requirement with no partial arms, a source-hash drift check, a schedule check, and run_id is part of the cache key so arms don't share cached responses.

## Bugs

| # | Sev | Issue | Remedy |
|---|---|---|---|
| M1 | Medium | **Analysis dependency not hashed.** `s03_analyze` imports `summarize` from `scripts/s02_analyze.py`, which produces the bootstrap CI used by the HIT rule. That file isn't in `SOURCES`, so a later edit could change `ci95` without any drift error. `pyproject.toml`/`uv.lock` (numpy/scipy versions) aren't recorded either. | Add `scripts/s02_analyze.py` (and ideally `uv.lock`) to `SOURCES` before the live run, or vendor `summarize` into s03. |
| M2 | Medium | **Treatment table isn't checked against the real payoff engine.** The "exhaustive" test compares `conditional_table` to a hand-written copy of the same formula, not to `sim.cournot.payoffs`. If `payoffs` differs in any detail (floor, cost, intercept, rounding), treated firms get wrong profit numbers and the 'exact' label in the design would not hold. `validate_game` checks rows against `payoffs` but never checks the table. | Test: for all r1, r2, q in 0..12, `conditional_table(r1+r2)[q]['own_profit'] == payoffs([q, r1, r2])[0]`. |
| M3 | Medium | **Treatment-only objective reminder.** Only the calculator arm sees "Your goal remains to maximize your own total profit over many rounds". If `system_prompt` doesn't already say "many rounds / total profit", this is new horizon information. A reminder like that plausibly pushes toward restraint, i.e. against the hypothesis, and would shrink a real effect toward DUD. The design's claim that the objective is unchanged is unverified. | Check `system_prompt`. If the wording isn't there, put the sentence in both arms before freezing, or say explicitly that the bundle includes a horizon reminder. |
| M4 | Medium (interpretation) | **Economics: best-responding to last round's rivals with 3 firms produces cycles, not convergence.** The best response is BR(R) = (24−R)/2, so a symmetric deviation e becomes −e: all firms at 4 give R=8, BR=8, then R=16, BR=4. The average of that cycle is 6. A table that strongly changes behaviour can therefore leave mean output unchanged and land in DUD. | Don't call a DUD "no effect". Report the per-round quantity path and the oscillation diagnostics (`absolute_change`, `lag_conditional_regret`, `distance_nash`) next to the verdict. Treat `lag_conditional_regret` as a manipulation check only: it is zero by construction for anyone following the table. |
| L1 | Low | **The execution-slot randomization does nothing.** With `workers=2` and exactly two games per seed block, both games start at once; the shuffled order only decides which one is submitted microseconds earlier. The seed doesn't control API draws, so "pairing" brings no common random numbers. The sign-flip test is effectively a test of two i.i.d. arms with an arbitrary pairing. | Describe it that way. An unpaired 10-game permutation test (minimum p = 1/252) would be more powerful, but changing it now would deviate from the frozen design, so leave it as a limitation. |
| L2 | Low | **HIT effectively requires all five contrasts to be strictly positive.** With n=5, p ≤ .05 means only the all-positive configuration can reach the observed sum. A single zero or negative contrast gives p ≥ 2/32. The bootstrap condition (lower bound > 0) is then automatically met, so it adds nothing. | State this in REPORT so readers understand the rule. |
| L3 | Low | **Labelling hazard.** A large reverse effect that isn't negative in all five seeds (e.g. mean −3 with 4/5 negative) is labelled DUD. The mean-exactly-¼ boundary can never occur, because 135/4 isn't an integer. Both follow the frozen design. | Always print the signed mean next to the label. |
| L4 | Low | **`analyze` doesn't link recorded quantities back to the raw cache.** It counts cache lines but never checks that each final attempt parses to the stored `quantity`, that earlier attempts were actually invalid, or that `trajectories.jsonl`/`ground_truth.jsonl` match the game files. The design assigns this to the replay step. | Make sure the replay script checks all of this, and log it. |
| L5 | Low | **`temperature_requested=1` is written to config but never passed to the model call.** It's a provenance field that isn't enforced. | Remove it or rename it `temperature: uncontrolled`. |
| L6 | Low | **Reanalysis is fragile.** `DESIGN_S03.md` and the shared `llm.py` are hashed, so any later edit (for example, writing results into the design file) breaks byte-identical reanalysis. Hashes are also resolved relative to the working directory. | Record the git commit in config and reanalyze from a checkout of that commit. |
| L7 | Low | **Promised tests are missing.** There's no unit test of the exact sign-flip computation (zeros/ties, one-sided counts). There's no end-to-end `analyze(allow_dry=True)` test, though the dry run may cover it. | Add a small sign-flip test, e.g. [1,1,1,1,0] → p_upper = 2/32. |

## To verify (outside the pasted files)
1. **`parse`:** it must reject floats, bools and out-of-range values rather than clamping them. Clamping that kicks in more often in one arm would bias the primary.
2. **`Cache`:** it must be thread-safe when two games append at the same time (append lock, keyed lookup), and its key must include the prompt text, system prompt, attempt and model.
3. **`public_history`:** it should contain only quantities, prices and profits from completed rounds.
4. **`summarize`:** check what keys it returns. `ci95` must be the percentile bootstrap. For secondaries, if it emits its own `exact_signflip_p_*` computed on floats, label that clearly.
5. **`system_prompt(agent, None)`:** check it for the horizon/objective wording (see M3).

## Limitations, not bugs (the design already discloses these)
n=5 with descriptive CIs; the treatment is a package of information, salience, prompt length and myopia cues; no identified effect of correcting arithmetic; results can't establish or rule out collusion; model labels aren't attested; temperature isn't controlled; many secondaries without multiplicity control; "apparent restraint" just means output below 6 in the NONE arm, which could also be miscalculation. The hypothesis also only has room to show up if NONE output is below about 6. If the baseline already produces around or above Nash, a DUD mostly reflects that ceiling.

**Scope of claims:** the design's own wording is fine as long as REPORT says "total effect of the table package on mean output, rounds 4..12, gpt-6-luna, n=5", and gives the M4 cycling caveat whenever the result is a DUD.
