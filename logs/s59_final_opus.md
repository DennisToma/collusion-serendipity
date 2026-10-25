# S59 adversarial review

I reviewed only the supplied text. I made no edits, ran no live scientific calls, and did not read the raw archive. I could not see `scripts/s59_action_text.py`, `scripts/s59_reviews.py`, or the raw `responses.jsonl`, so the 20 approvals below are taken from `results/s59_history.json` and are not re-derived from the returned text.

## Numbers I recomputed by hand

All of them match the reported values.

- **Approvals (20 raw values):**
  - Original arm: 0,0 | 1,1 | 1,1 | 0,0 | 0,0, so **4/10**.
  - Compact arm: 0,0 | 0,0 | 0,1 | 0,0 | 0,0, so **1/10**.
  - Agreement with archived actions: 9/10 (original) and 6/10 (compact). ✓
- **Block cells (15):**
  - Original: 0,1,1,0,0, mean .4.
  - Compact: 0,0,.5,0,0, mean .1.
  - Contrast: 0,1,.5,0,0, mean .3. ✓
- **Bootstrap (all 3125 draws):** I used generating functions on a half-unit scale.
  - Contrast (3+x+x²)⁵: 243 draws give a mean of 0, which puts index 78.1 at 0. Draws with sum ≥8 number 31 and sum =7 number 70, so indices 3045–3046 both give .7. Interval **[0, .7]** ✓.
  - Original: (3+2x²)⁵ gives **[0, .8]** ✓.
  - Compact: (4+x)⁵ gives **[0, .3]** ✓.
- **Paired t intervals:** standard errors are .2, .2449 and .1, multiplied by 2.7764. This gives [-.255, .855], [-.280, 1.080] and [-.178, .378] ✓.
- **Sign flips (32):**
  - Contrast and original arm: two nonzero blocks, so upper p = 8/32 = .25, lower p = 1, two-sided p = .5 ✓.
  - Compact arm: .5 / 1 / 1 ✓.
- **Verdict:** mean ≥ .25 but the lower bound is 0, so it is not a HIT. The mean is above .05 and the upper bound is above .25, so it is not a DUD. **ODD** is correct.
- **Byte counts:** I derived 24480_B by hand. The original history is 9×168 + 80 boolean characters + 16 separator characters + 2 = **1610**. The compact table is a 138-byte header + (9×31 + 80 + 8 commas) + 2 = **507**. Both match. This also confirms that key order and spacing match the default `json.dumps` serialization.

## Design compliance

- **Case selection:** cases are chosen using the task-status schedule only (`range(2,10)`, partner not passed). The independent checker rebuilds that schedule from the RNG on its own ✓.
- **What the compact view changes:** only the history value. The tests confirm exactly one line differs and that the system prompt and request fields are identical. The independent checker rebuilds the entire expected prompt and compares it byte for byte ✓.
- **Lossless round trip:** booleans and negative numbers survive, and the check compares canonical `json.dumps` strings, not just Python dict equality, so key order is verified too ✓.
- **Independent checker:** it does not import `pack_history`, but it hard-codes the same nine-column layout. It is a separate implementation, not separately designed.

## Executable bugs and gaps (none affect the reported numbers)

1. **The checker does not fully confirm the selected source request.** `s59_independent.py` checks the run, turn and agent, but not that the case uses the highest attempt index, or that the archived response parses to the archived action. `select_cases` does check both, and `validate` compares cases against `select_cases()`, so the gap is only in the checker's independence.
2. **The clean-clone check will fail until the live files are committed.** `validate()` needs `logs/s59_launch.json`, `logs/s59_attempt.json` and `data/s59_history/`. All three are still untracked in the current git status. Commit them before running `--clean-clone`.
3. **An early reservation failure leaves a stray marker.** If `LIVE_ATTEMPT` already exists, a second destination directory still gets a `failure.json`. This is harmless.
4. **`fixed_model()` has no effect.** It sets a module global to the value it already has (`CODEX_CHEAP` is already `gpt-6-luna`). That is harmless here, but the patch would not be thread-safe if the value ever differed.

## Limitations the design already acknowledges (not bugs)

- Length, repeated field names, JSON structure and reading burden all change together, so no mechanism can be inferred.
- Temperature and token limits are not actually passed to the codex CLI.
- The provider, model settings and tool non-use are unverified.
- Persistence is process-level only; parent directories are not fsynced.
- The same S29 games are reused across many pilots, so this is not an independent replication.

## Main concern about the interpretation

The +.3 difference comes from three reviewers who are TYPE-X themselves (in games 24481 and 24482), and every one of them approved in the archived game. The other 7 cases are 0/0, and S59's original-arm rate (.4) sits within the .4–.6 range other pilots on the same ten histories report for their reference arms (S48 retain .4, S50 hidden .4, S51 charge3 .5, S55 visible .6, S58 retain .6). If those arms used byte-identical prompts, identical inputs give rates spread over about .2, which is close to the .3 effect. I could not confirm the prompts were identical from the supplied text. A HIT is impossible with this layout unless all five blocks are positive. The ODD verdict and the report's restrained wording are appropriate. I would add one sentence pointing out that the identical-prompt reference arms vary.

## Claims in REPORT.md

- Headline 4/10 vs 1/10, +.300 [0, .700], t interval, p = .25: correct.
- "All nine fields survive exact roundtrip": correct.
- No mechanism or replication claim, and "No hits promoted": consistent with the evidence.
