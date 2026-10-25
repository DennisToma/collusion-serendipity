# S44 review (from the supplied text only; no edits, no calls)

I found no bug that invalidates the design. The causal scope, case selection, unit and intervention are all correct as written. What remains are three fragility bugs and one gap in test coverage.

## What checks out

- **Selection:** cases are picked by the rule `initial==sorted(assigned_pair)`, `initial[0]`, before anyone looks at outcomes. The case uses the round-10 request (`payload[5:9]==[run,9,agent,0]`). Every block has both arms, and archived actions only feed secondary counts.
- **Counterfactual:** the rivals come from `rows[8]`, which is round 9, and they are checked against `public[-1]['quoted_rates']`. The focal firm's own round-9 share and profit are checked against `payoff_table`. The exhaustive test runs 21 + 441 = 462 rival profiles × 21 wages against `sim.entry.outcome`. The independent formula (`all(wage>=x)`, `1/(1+ties)`) matches.
- **Isolation:** the header, prefix and tail are byte-identical between arms. Only the JSON rows are reversed. Tests check this with `replace(ap,'ROWS')` and `json.loads(ap)==reversed(bp)`. Nothing in the prompt recommends an action, and the current response is never supplied.
- **Unit:** the outcome is `rate`, the focal offer in 0–20. It is labelled "not realized worker pay".
- **Statistics:** 5⁵ = 3125 bootstrap draws with linear percentiles at index 3124·p. The independent script reproduces them exactly on doubled integers ÷ 10. The sign flip is inclusive with 2⁵ = 32 patterns. HIT needs all five differences to be nonzero and positive: a single zero gives p = 2/32 > .05. The `classify` tests cover the edge cases correctly. 15 cells = 5 blocks × 3 summaries.
- **Schedule and failure handling:** two workers per block, views run in sequence within a case, and pool exit acts as the barrier. The sweep sorts end events (−1) before start events at equal times, so the concurrency check is right. Each response is fsynced before parsing, retries=1 and `fixed_model` together mean exactly one luna attempt, the abort flag is checked before every admission, and the external receipt is opened with `'x'`, so it can only be written once.

## Remaining bugs

1. **Analysis and release only work until any frozen file changes.** `validate`/`check_inputs` hash the current working tree for `CLAUDE.md`, `llm.py`, `pyproject.toml` and `uv.lock`, and `select_cases` hashes S42's sources the same way. A later legitimate edit (the director touching `CLAUDE.md`, a `uv add` for another pilot) will make `analyze`, `s44_release.check` and the clean clone fail permanently. `clean_clone` checks out HEAD, not the registration commit. Either run the full release before any other commit, or validate against `git show <registered commit>`.
2. **The clean clone depends on an untracked receipt.** `validate` needs `logs/s44_launch.json`, which is outside `SOURCES` and only created at launch. It has to be committed before `--clean-clone`, or reproduction from origin fails.
3. **The mocked live test does not exercise the timing checks.** `utc` is patched to a constant, so every interval has zero length. The sweep skips those, so the concurrency, barrier and ordering checks pass trivially on the live path. Only the dry test covers them with real timestamps. This is a test-coverage gap, not a scientific bug.
4. **Live registration is mocked in every test.** `registration` and `subprocess.run` are stubbed, so the real HEAD == `ls-remote` check and the `git diff` path have never run. They need one manual check at registration.

## Limits already acknowledged in the design

- Selection is post hoc, reuses S43's contexts, and is not held out.
- Row order mixes position and recency, and the result cannot identify mechanism.
- Temperature and max_tokens are not sent to the Codex CLI. Provider identity, effective settings and tool non-use are unattested. Tools are restricted by instruction only, and the sandbox cannot isolate absolute paths.
- Sign-flip calibration assumes the differences are symmetric. With n = 5 the bootstrap bounds can collapse to a point and prove nothing about equivalence.
- A directional DUD (including mean > 0 with upper bound < 1) does not rule out a smaller or opposite effect.
- Shared-service interference, provider draws that seeds don't fix, and local-only UTC evidence.
- One extra limit not stated in the design: in the entry contexts the two rival offers are listed without firm IDs. This is the same in both arms, so it doesn't bias the contrast, but it may make the table hard to read.
- Strict parsing with no retries means one fenced JSON reply ends the whole pilot unclassified. This is by design.

## Schedule and arithmetic

- **Arithmetic:** 462 × 21, 3125, 32, 20 = 10 × 2 and 15 = 5 × 3 are all correct.
- **Cutoff:** the 06:00 UTC admission cutoff is stricter than the 14:30 pilot limit in `CLAUDE.md`, which is acceptable. I couldn't check whether the 20-minute headroom still holds, because the current time isn't in the supplied text.
