# S43 review (I only read the text you supplied; no files opened, no calls made)

## Concrete remaining bugs

1. **Wrong limitations text in `s43_present.py`.** The last prose paragraph seems to be carried over from S40/S37. It says the manager picked S43 "after observing S37 floor behavior," but the design gives the reason as S42 marginal-cost explanations. It also says "note availability … complete-notepad promise change together," but S43 keeps the notes identical in both arms. What the table actually bundles is arithmetic, fixed-rival salience, length and ordering, as the design says. "Controled" is also misspelled. This paragraph would publish false scope claims and should be rewritten.
2. **The table's game rules aren't checked against S42.** `payoff_table` hard-codes value 20, one unit of labor, highest bid wins and an equal split on ties. `select_cases` hashes `config.json` but never asserts those values from it. `s43_independent.py` and `test_s43.py` repeat the same formula, so they can't catch a wrong rule. Add asserts that read the S42 config.
3. **The entry arm's rival set is never checked.** `rival_rates` comes from `rows[8]` (round 9), minus the focal firm. Nothing asserts that the round-10 roster has the same rivals. If the entrant joined at round 10, or the roster changed, the table would leave out a firm that is really bidding. Add an assert that the rival IDs in round 9 and round 10 match.
4. **"Initial ordered roster" isn't confirmed.** The code uses `rows[0]['agents'][0]`. If the `agents` list is sorted or reshuffled each round, this isn't the simulator's roster order. Assert against the roster in the config.
5. **The count "441" is off.** The test checks 21 one-rival profiles plus 441 two-rival profiles, which is 462 profiles × 21 actions = 9,702 rows. The design text says 441.
6. **The one-shot receipt is spent before the last pre-call checks.** `LIVE_RECEIPT` is written before the `cases_sha256`/`check_inputs` asserts. A mismatch with zero calls made still permanently blocks a rerun. If that's intended, document it. Otherwise move the receipt write after those checks.
7. **The clean-clone run may fail on the lock file.** `run()` creates `data/s43_payoff/.writer.lock` inside the clone. Unless that file is committed or gitignored, `git status --porcelain` won't be empty and the check fails. I can't tell from the supplied text which it is.
8. **The independent verifier never reads `config.json`.** It doesn't check each row's response backend/model or the `failure.json`/`transport_failures.jsonl` files. It relies on `analyze`/`validate` for those. That's acceptable, but don't call it an independent integrity check.

## Checked and correct

- **Unit:** the primary outcome is the focal offer, and every output labels it "not realized wage."
- **Control prompt:** it is byte-exact to the source prompt. The table is spliced in only before `Return strict JSON only`, and no archived current response is supplied.
- **Table content:** it lists all 21 own wages as exact fractions, with ties split equally. It says the rival offers are hypothetical and not a forecast, and it has no recommendation, joint-payoff row or collusion wording.
- **Statistics:** 3,125 = 5⁵ bootstrap draws and 32 = 2⁵ sign flips. The percentile positions (78.1 and 3045.9) stay in range. At n = 5, p ≤ .05 needs all five block differences strictly positive (a zero gives p = 2/32). That makes the bootstrap gate redundant, as the design says. The test cases for HIT, ODD and DUD in `test_s43.py` classify correctly. Doubling to integers in the independent sign test is exact because block differences are half-units. 15 block cells = 3 summaries × 5.
- **Schedule:** two workers run per seed block, each case's two views run in sequence, and there's a barrier between blocks. The concurrency ≤ 2 sweep and the barrier checks match what `run` does.
- **Failure handling:** every response is saved before parsing, there are no parser retries, any failure aborts the run, partial archives are refused, and nothing resumes.

## Acknowledged limits (not bugs)

- The source histories were picked after the fact, and S42 outcomes aren't the control.
- The table bundles several things at once, so it can't isolate arithmetic, beliefs or a mechanism.
- Rivals aren't rerun, so there's no realized-pay claim.
- n = 5 blocks, no held-out set, zero tuning, and no equivalence claim from degenerate bounds.
- Codex doesn't enforce temperature or max_tokens, the model name is the requested one rather than verified served identity, and actual tool non-use is unattested.
- Read-only tools could still read absolute paths, and accounting after a power loss is unattested.
- The 04:30 UTC deadline and the 20-minute headroom are set by the local clock and aren't checked against server time.
- A HIT would not change the sibling headline.
