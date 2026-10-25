# S43 adversarial review (supplied text only)

I made no edits and no model calls. Everything below comes from the supplied text; I didn't read the raw archive. Overall I found no blocking bug. Causal scope, unit, isolation, the table and the arithmetic hold up. The bugs below are about how strong some checks are, not about the logic.

**What checks out**
- **Causal scope:** the control is a fresh redraw from the exact source prompt, and neither arm sees the archived round-10 answer. Source outcomes aren't used as the control, and the archived matches are reported only as descriptive counts.
- **Selection:** all ten S42 games are used, round 10, with `sorted(assigned_pair)[0]`. The roster and productivity are checked for rounds 9 and 10. The case is chosen by roster position, not by what the agent did.
- **Isolation:** the only change is a supplement inserted before the single `\nReturn strict JSON only` marker. The system prompt, public history and notes are untouched. The table has no recommended action, best-response flag or joint-payoff column, and says the rival offers are hypothetical.
- **Table:** the share rule is right: 0 below the highest rival, 1/(1+ties) otherwise, profit (20−w)·share. There are 21+441 = 462 rival profiles × 21 wages = 9,702 rows, all checked. Against rival offers [10] or [10,10], the best response is wage 11 with profit 9, versus 5 or 10/3 at wage 10. That supports the amended one-unit threshold.
- **Unit:** the outcome is the focal agent's integer offer, averaged per seed, giving five blocks. It is labelled as an offer, not a worker's pay.
- **Statistics:** 5⁵ = 3,125 bootstrap draws; linear percentiles at positions p·3124 match numpy's linear method. There are 2⁵ = 32 inclusive sign flips, computed exactly with Fractions (the verifier uses doubled integers). HIT needs all five block differences strictly positive: a zero or negative block gives p ≥ 2/32 = .0625. The unit tests for [1]×5 → HIT, [0,2,2,2,2] → ODD and [.5]×5 → DUD are correct. The design's counts are all correct (20 calls, 15 block cells, 3 summaries).
- **Failure and cache handling:** responses are saved before parsing, and there is one call per request with no fallback to another model (`fixed_model` stops it). Admission is guarded by a lock and an abort flag, and a failure-only archive can't be restarted. The receipt is written with exclusive create (`'x'`), and there's a check that no more than two calls overlap.
- **Schedule:** five blocks, each with two cases running at once and their two views run one after the other. In the worst case that is about 10 sequential slots × 605 s ≈ 100 min after the last admission. That's acknowledged.

**Remaining bugs**
1. **The table is checked against the S42 simulator at only one of 21 wages per case.** `select_cases` compares just the agent's round-9 wage with its archived share and profit. The independent verifier rebuilds the table from the same prompt-rule text, so the other 20 rows are never compared with the simulator's real allocation code. Any extra rule in the simulator (a reservation wage, an outside option) would go unnoticed, and the design doesn't list this as a limit.
2. **The release check's REPORT.md byte-identity test is vacuous.** `render()` never writes REPORT.md, and nothing checks REPORT.md's numbers against `results/s43_payoff.json`.
3. **The mocked live tests freeze `utc`.** Every call interval then has zero length, so the concurrency sweep, block barriers and ordering checks pass without testing anything in live mode. Only the dry run actually exercises them.
4. **Edits to some tracked files abort a live run.** `CLAUDE.md`, `llm.py` and `DESIGN_S43.md` are in `SOURCES`, and `check_inputs` runs on every admission. Any edit to one of them during the run (for example by the wrapper or the director) aborts it, leaving an unclassified pilot. This fails safe, but it isn't listed as a risk. Separately, `DESIGN_S43.md` can never be annotated afterwards without breaking validation.
5. **Unverified:** whether `data/s42_entry/raw/*.jsonl` is tracked in Git. The clean-clone reproduction needs it.

**Acknowledged limits (not bugs)**
- The challenge was chosen post hoc, after reading S42.
- The treatment bundles arithmetic, scenario salience, length and row order.
- Results are offers, not realized pay.
- At n = 5, the bootstrap gate adds nothing beyond the sign test.
- The sign test assumes exchangeability; the SD = 0 bounds degenerate and support no equivalence claim.
- The 4→1 amendment was made with source outcomes already known.
- Temperature and token limits aren't enforced by Codex.
- The served model, tool non-use and full configuration are unattested; read-only tools could still read absolute paths.
- A token refresh rewriting `auth.json` can abort the run.
- The 20-minute margin is a convention, not a runtime guarantee.
- A response still in flight when another worker fails is saved but not accepted.
- The one-shot receipt is spent even if setup fails.
- Re-validation needs a frozen checkout and the same environment.
- There is no held-out validation and no change to the sibling headline.
