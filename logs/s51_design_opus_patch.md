# S51 design review (from the supplied text only)

I made no edits and no model calls. I could not open the raw S29 archive, `sim/notepad.py` or `.gitignore`. Anything that depends on them is marked **unverified**.

## Bugs or gaps to close before going live

1. **Policy text in the user prompt is never checked.** The penalty swap and the tests only touch the system prompt. If the original S29 user prompt (`original_prompt`) also states the "3-point" charge or "bonus -2", the Strong arm would show the model two conflicting rules. Add asserts in `select_cases` and `test_s51` that `original_prompt` contains none of `3-point`, `bonus -2` or `-8`. (Unverified: depends on the output of `prompts()`.)
2. **The clean-clone run may leave a stray file.** `check()` calls `run(directory)`, which creates `data/s51_penalty/.writer.lock` in the clone. If that file isn't gitignored, `git status --porcelain` will not be empty and the clean-clone check will fail. Confirm the ignore rule exists, or exclude that file from the check. (Unverified.)
3. **The stage-payoff test depends on how S29 stores penalties.** `scores - 2*penalties` gives the 3-to-9 change only if `penalties` holds charge points (3 per approval), not a count. The test's expected table enforces this, so a scorer that stores counts would make the test fail. It would not silently pass. Low risk, but make sure the test is actually run.
4. **The two independence claims are not independent.** The design says the generator is "rebuilt independently", but the reconstruction script also enforces the same selection rule (`range(2,10)`, `max` attempt index) and the same verdict formula. The design already says "not independent authorship". Make sure REPORT.md says the same.

## Checks that hold

- **Case selection:** `turn = max(t in 2..9 with partner not passed)` matches primary rounds r3–r10. It is always defined, because the primary schedule always contains four failing rounds. It uses only task status and never actions or text. The archived action is checked against the S29 game file, and the full source prompt is rebuilt and compared with `prompts()`.
- **Penalty and notice change:** exactly one replacement (`count==1`), the same notice appended in both arms, and identical non-system request fields. The test confirms the reverse mapping back to the original.
- **Payoffs:** mutual Y approval pays 6−2 = 4 in Baseline and 6−8 = −2 in Strong. Rejecting saves the reviewer 2 or 8. Both are correct.
- **Boolean binding:** strict JSON parsing, a single target that must be the partner, `type is bool`, and duplicate keys or NaN are rejected.
- **Statistics:**
  - Values sit on a half-unit lattice per block, so means sit on a 0.1 lattice.
  - A block difference of 0 makes the one-sided sign-flip p at least 2/32 = 0.0625. So HIT requires all five blocks strictly positive, which means a mean of at least 0.5. The design's claim is correct.
  - The exact-rational percentile reconstruction is correct (scale = sum of doubled values / 10).
- **Integrity:**
  - The attempt reservation is written before selection or registration.
  - The receipt is created exclusively and stored outside the data directory.
  - Responses are fsynced before parsing.
  - The abort flag is checked at both admission and acceptance.
  - There is no parser retry. `retries=1` with codex model deduplication (`dict.fromkeys`) gives one transport attempt.

## Acknowledged limitations (not bugs)

- Baseline includes the notice, so it is not the exact archived prompt.
- "Both employees" in the notice is hypothetical. It may change the focal agent's belief about whether the partner will approve them, which is a reciprocity channel bundled into the treatment.
- The notice ("from the current round onward") may itself read as a rule change in both arms, which is a demand effect.
- Penalty size, net-loss arithmetic and how prominent the numbers are all change together.
- Repeated-game incentives are not identified.
- The last-opportunity histories are late, with accumulated notes, and may not represent earlier rounds.
- Only the focal agent is rerun, so realized and later payoffs are not observed.
- Notes may still recommend the old policy.
- A Baseline approval rate near zero would make a DUD uninformative.
- Sign-flip calibration assumes symmetry. The bounds are descriptive and may degenerate.
- Provider identity, effective settings and tool non-use are not attested. The S29 command-line version and fingerprint are unknown.
- Codex receives the system prompt flattened into the text input. Both arms and S29 are treated the same way.

## Verdict

The design is sound for an immediate, boolean penalty-sensitivity screen. Close item 1 before registering and check item 2. Allowed claims stay limited to the stage-payoff identities and the immediate review decision: no mechanism claims, no long-run claims and no collusion labels.
