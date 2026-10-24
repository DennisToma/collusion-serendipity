# S06 adversarial review (static reading only: no edits, no model calls)

**Bottom line:** I found no remaining bug that would bias the CENT − UNIT estimate. The open problems all fail closed: in the worst case a valid dataset gets refused, and none can let a wrong result through. Fix #1 before the live run. #2 and #3 are cheap to fix. The rest are about reporting and scope.

## Remaining bugs

1. **A killed run can be resumed, but its data can never be analyzed (medium).** A failure marker is written only when a worker raises an `Exception`. A SIGTERM/SIGKILL (for example a wrapper timeout or an out-of-memory kill) leaves no marker, so `main` happily resumes. Ctrl-C doesn't help either: it interrupts the `as_completed` loop, but `ThreadPoolExecutor.__exit__` waits for the workers. `abort` is never set, so they keep making live calls, and their game files are never written.
   - On resume, the unfinished games replay their cached responses. Those responses carry the *original* `call_started_utc`, but `gt['started_utc']` gets a fresh `now()`.
   - `validate_game` then fails `started_utc <= call_started_utc` for good. The run completes and analysis refuses it.
   - This contradicts the "resume" claim in the design.
   - Fix: either refuse to start when `raw/` holds keys for a game with no `game_*.json`, or write a per-game start marker that blocks resume.

2. **The deadline gate and the validator check different timestamps (low).** The gate checks `now()` in `DenominationCache.call` *before* `Cache.call`. `call_started_utc` is set later, inside `Cache.call`. A request that passes the gate at 19:14:59.99 can be stamped at or after 19:15 and then fail `call_started_utc < DEADLINE`, which makes the whole dataset unanalyzable. Fix: record the gate timestamp and validate that one, or validate against the gate decision rather than the transport timestamp.

3. **Every frozen source is re-hashed from the working tree at analysis time (low, process risk).** The list includes `DESIGN_S06.md`, `test_s06.py` and `s06_independent.py`. Any post-run edit, such as adding a results note or limitation to the design file or tidying a test, breaks `analyze` (source drift). Either only append results to files outside `SOURCES`, or check non-code files against `registration_commit` via `git show` only.

4. **"Pushed manifest" and "registered before calls" aren't enforced (low).** `main` checks that sources are committed and clean. It doesn't check that the commit is pushed, or that `registration_commit` precedes the first `call_started_utc` (for example via the remote's push time). Right now the registration claim rests only on the local git history.

5. **Per-arm retry counts are missing from the output (low, but it's a mechanism gap).** Each action keeps the first valid of up to 3 attempts. If CENT produces more invalid attempts (bigger numbers, longer reasoning tripping the 40-word cap), this per-action selection is a possible pathway that never shows up in the output. `call_provenance` has the data; report invalid-attempt counts per arm, descriptively.

6. **Prompt wording (low, affects scope).**
   - UNIT says "1 accounting units equal one common currency unit", and this conversion sentence appears in *both* arms. The design text says the treatment bundles "conversion wording". Strictly, the wording is held fixed and only k changes. Fix the description, not the code.
   - In CENT, "marginal cost is 600 per unit" can be read as per *currency* unit as well as per unit of product. That ambiguity exists only in the treatment arm.

7. **Cosmetic.** `visible_rows` does nothing (it calls `scale` and returns the rows unchanged) and is imported but unused. Unused imports include `system_prompt` and `visible_rows`. The name suggests a visibility transform that doesn't exist, which could mislead a reader of the audit.

**Checked and found correct:**
- Bootstrap RNG order matches the design.
- Numerators /27 cover rounds 4–12.
- `classify` matches the spec: p ≤ .10 at n = 5 really does require five strictly same-sign, non-zero differences, because a zero or an opposite sign gives p ≥ .125.
- History and table scaling don't mutate the canonical rows.
- Stored metrics are in common currency.
- The torn-file check runs before the inherited auto-repair.
- Replay consumes every key exactly once.
- Abort propagates to the partner game, and a failed block stops all later blocks.
- The live run will currently refuse to start because the S06 files are untracked. That's correct behaviour.

## Acknowledged limitations (already in the design; not bugs)

- n = 5. The bootstrap is descriptive and the t interval is fragile. The .10 cutoff is a screen, not a significance claim.
- The sign-flip test is valid only if the two games in a block are exchangeable. Arms are not randomized within a block, and seeds don't control the API draws.
- Timing and rate-limit interference between the two concurrent games is possible.
- Model and backend labels come from the client and can't be independently verified. Temperature is uncontrolled.
- Denomination bundles magnitude and formatting. It is not about real stakes, arithmetic or collusion.
- The 19:15 deadline is operational. Any abort means no analysis.
- DUD doesn't establish equivalence. Note that the DUD rule ignores spread: differences like [+3, −3, +3, −3, 0] count as DUD, so always report the seed differences and CI next to the label.
- No pooling with earlier pilots.

## Scope of claims to enforce in the report

- **Calculator-assisted only.** Both arms get the exact best-response table from round 2. That probably removes the arithmetic route by which denomination would most plausibly matter, so a DUD means "invariant *when handed the argmax arithmetic*". It says nothing about denomination effects in general.
- **Narrow conditions.** One model (gpt-6-luna via codex), one scale ratio (100 vs 1), no messages, 12 rounds. There is no collusion content: this measures quantity level, not coordination.
- **Not comparable to S02/S03 levels.** UNIT is a different prompt from the earlier baseline, so it isn't a replication of those pilots.
