# S45 adversarial review (static read only: no edits, no model calls)

## What checks out
- **The 16 stage profiles:** `outcome` and the tests give recipient +8, reviewer +1 for a supported post and −2 for an unsupported one. Both posting on two unsupported products pays (6,6). Staying silent while the other posts pays 8. Both posting on supported products pays 9 each. Each reviewer's own payoff doesn't depend on the other's action, so every quality pair has one dominant-strategy equilibrium. Combined profit is 9·good + 6·bad and consumer loss is 10·bad.
- **Simultaneous moves:** partner notes are held back until both have moved and stamped round t+1. The prompt history is `rows[:t]`. Reasoning is never sent back to the model. The JSON-escaped notes can't break the delimiter splits.
- **Statistics:** the bootstrap index 3124·(1/40)=78.1 gives (9·m78+m79)/10, which matches the independent formula and numpy's linear rule. The sign-flip tails count ties inclusively, so any zero difference makes p ≥ 2/32 and HIT needs all 5 blocks strictly positive. The metrics are exact eighths, so `Fraction(str(float))` is exact.
- **Replay:** it uses every cache key exactly once and checks that no raw bytes changed. Request, response and admission hashes are cross-checked.

## Bugs, with fixes
1. **`auth.json` is part of the run gate.** It is hashed in `fingerprint()` and checked before and after every call and again at completion. A routine Codex OAuth token refresh would abort this one-shot pilot for good, or invalidate a run that already finished. Fix: drop it from the gate, or hash only stable fields such as auth mode and account. Force a token refresh before you take the launch receipt.
2. **The "model/backend mismatch" abort can never fire.** `_codex` returns the model name it was asked for, not the model that actually served the call. Fix: capture `codex exec --json` session or model metadata per call, or reword the claim to "requested route recorded".
3. **The guard is expensive and blocks both workers.** Each admission hashes the node and native Codex binaries twice while holding `admission_lock`, so about 400 full hashes of large files. The S19 headroom baseline may not include this overhead. Fix: check stat (inode, size, mtime) per call and do full hashes only at dispatch and completion.
4. **The instruction-file check covers the wrong folders.** `referenced_inputs` hashes `CLAUDE.md`/`AGENTS.md` in the repo and its parent folders, but Codex runs with `-C <tmp>`. Those files don't affect the model but can still abort the run if a manager edits them. Fix: keep only `$CODEX_HOME` and the temp-folder ancestors.
5. **`s45_present.py` can damage REPORT.md.**
   - `report.replace('Iteration 30','Iteration 31')` is global and will rewrite older log text too.
   - If the `<!-- S41 summary start -->` anchor is missing, the S45 block is silently dropped.
   - If the `| S41 ·` row is missing, `next()` raises StopIteration.

   Fix: do one replacement on the header line only, assert each anchor exists, and assert the S45 block is present after writing.
6. **Gaps in the independent check:**
   - It checks system-prompt substrings, not that the other arm's readability sentence is absent or that the full template matches.
   - Nothing on live data proves reasoning never leaks into later prompts.

   Fix: rebuild the exact system string per arm, and assert no earlier reasoning text over 20 characters appears in any later user prompt.
7. **Mid-run commits.** If the wrapper's `git add -A` runs during the launch, it will commit partial raw caches. Fix: confirm `data/s45_reviewring/raw` is gitignored, or launch only when the iteration will outlive the run.
8. **Durability (minor).** Admissions are fsynced but response and request appends are not. A crash fails closed, which is correct, but the paid responses are lost. Add fsync.

## Limitations (not bugs; state them in the write-up)
- The prompts show "Round N" and T=10 is fixed. The end round isn't disclosed, but late rounds in r3–10 may still show end-game behaviour.
- Codex receives the system message flattened into user text, so it is not a true system role.
- Temperature and token settings, the served model and tool non-use are not attested.
- The DUD label lumps a reversed effect (shared < self) in with a null. Report the lower tail as a descriptive "reverse direction" note, without promoting it.
- With n=5, HIT is only possible if all five blocks agree. Power is low and a DUD is weak evidence of no effect.
- The profit gate is almost implied by the primary outcome (Δprofit = 9Δgood + 6Δbad).
- Delivery and readability are bundled together. There is no multiplicity correction across pilots.
- The design is S29-like but differs in payoffs and labels, so comparisons with it are uncontrolled.

**Verdict:** economics, statistics and the screen are correct. Fix #1 and #5 before launch, and #3, #4 and #6 if time allows. Disclose #2.
