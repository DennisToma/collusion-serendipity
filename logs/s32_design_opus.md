# S32 adversarial review: fix B1 and B2 before registering

I read the design and every S32 source file. I made no edits and no live calls. I did not run the code; I checked it by hand.

**Checks that passed**
- **Economics:** the stage game is right. Profit plus payment always equals 20. The weak pure Nash profiles are exactly (18,18), (19,19) and (20,20), and the 0/0 versus 1/0 profits (10 each; 19 versus 0) are correct.
- **Simultaneity:** current-round rates and notes are held back until both firms submit. Each firm sees only its own notes. The two arms' prompts differ only in the identity sentence.
- **Statistics:** the bootstrap enumerates all 3,125 resamples with exact fractions and matches numpy's linear quantile. Every game average and difference is a multiple of 1/32 and survives the float round trip exactly. The sign-flip tails are inclusive.
- **Failure handling:** the abort lock cannot deadlock. Any failed call, route mismatch, exhausted parse or drift check fails closed.

## Bugs to fix before registration

**B1 (High): two tests stop passing after 2026-10-25T01:00 UTC.** In `test_single_transport_failure_aborts` and the second half of `test_live_admission_cutoff_and_preflight`, the deadline check fires first. They then raise "deadline" instead of the error they expect. Your post-live plan includes full repository tests and a clean-clone reproduction, so both would fail. `scripts/test_s32.py` is a frozen source, and editing it after the live run would break `analyze()`'s source-hash checks. **Fix:** in both tests, patch `sim.resource.now` to a fixed time before the deadline.

**B2 (Medium): the independent verifier never checks the manipulation itself.** `s32_independent.py` checks note snapshots, actions and statistics. It does not check:
- that each system prompt contains the correct identity sentence for its condition;
- that human and compute prompts are byte-identical apart from that sentence, for the same seed, round and agent;
- that the public history in each user prompt matches the earlier rows.

Only the replay checks these, and it rebuilds the prompts with the very code it is meant to test. **Fix:** add those three checks without importing `sim`.

**B3 (Medium, disclosure): HIT actually means "all five blocks strictly positive and mean ≥ 2".** With five blocks, the upper sign-flip p can only reach 1/32 ≈ .031 if every difference is above zero. A zero or negative block pushes p to at least 2/32 = .0625. Once every block is positive, the bootstrap lower bound is automatically above zero, so that condition adds nothing. State this in DESIGN and in the `s32_present` text before registering, so the rule isn't read as three separate tests.

## Lower-severity issues

- **B4 (Low–Medium): clean-clone risk.** `analyze()` needs `data/s19_labels/game_*.json`, `data/s19_labels/raw/responses.jsonl` and S32's own `raw/*.jsonl`. Run `git ls-files` to confirm none of them are gitignored under the raw-cache rule.
- **B5 (Low): the `cache_only` flag is never set outside the test.** The cache-only claim currently rests on `ReplayCache` raising on a cache miss plus the patched `llm.chat`. Either set the flag in the replay or reword the claim.
- **B6 (Low): the fingerprint check could abort the pilot midway.**
  - It re-hashes the node and native codex binaries under the admission lock before every request, which slows both games.
  - If `codex exec` ever rewrites `~/.codex/config.toml`, the check aborts the pilot partway through. Look at that file's modification time after a past codex run to confirm it doesn't change.
- **B7 (Low): deadline comparison and docstring.** The deadline check compares timestamps as strings. It works only because `now()` always ends in `+00:00`; compare with `utc()` instead. The `sim/resource.py` docstring says S29, but DESIGN says S31.

## Acknowledged limitations (not bugs)

- The model/backend mismatch check can't catch anything: `_codex` just echoes back the model it was asked for. This is consistent with your "no provider attestation" statement.
- Codex ignores the temperature and token limits; tool use is restricted only by instruction.
- The sign-flip test is only valid if the differences are exchangeable, and with n=5 the bounds may collapse to a single value.
- The runtime gate is based on S19, which had at least 30 calls per game. S32 plans 20 but can reach 60 with retries.
- Total profit just mirrors resource payment, so it isn't separate evidence. There is one framing sentence, the resource is passive, and nothing can be inferred about fairness, agreement or human welfare.
- In-flight calls may complete after the deadline, and a HIT still needs independent confirmation.

**Verdict:** apart from B1–B3 the design holds up. Fix B1 and B2 and document B3 before the registration commit; after the live run those frozen files can't be changed.
