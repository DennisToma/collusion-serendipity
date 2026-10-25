# S48 adversarial review (supplied text only, no edits, no calls)

## Bugs or likely bugs (fix before launch)

1. **Erase re-serializes your own notes, so "all other bytes" isn't guaranteed.** `request()` rebuilds the snapshot with `json.dumps(own)`, which uses default separators and `ensure_ascii=True`. If S29 used different formatting, or notes contain non-ASCII text (dashes, "−"), the erase arm also changes how your own notes are written. That is a confound on top of the deletion. The test, `s48_independent.py` and the design check only the parsed equality, and the independent script copies the same construction, so it shares the blind spot. **Fix:** in `select_cases`, add `assert json.dumps(json.loads(notes))==notes`, or slice the partner entries out of the original string.

2. **Any failure before the first model call permanently blocks `data/s48_notes`.** This includes an unpushed HEAD, a dirty source file, `NODE_OPTIONS` being set, or `codex --version` failing. `new` is true and the directory already exists, so `failure.json` gets written and the folder can't be reused. A failed `registration()` writes `failure.json` but no receipt; failures after registration also leave `logs/s48_launch.json`. The tests show this is deliberate, but it spends the one-shot on operational mistakes. **Fix:** run `registration()` and `launch_observation()` as a preflight that writes nothing.

3. **The "exogenous task status" claim isn't checked.** Selection uses `rows[t]['market']['passed'][partner]`. S44 talks about "labor histories", so if passing depends on the partner's earlier effort, choosing the last TYPE-Y round depends on behaviour. Confirm in the S29 game code before calling the selection exogenous.

4. **Unexplained changes in the working tree.** `logs/s29_release.json` and `data/SPLITS.md` are modified but not committed. Neither is in `SOURCES`. Check why before registering.

5. **Unreviewed source.** `scripts/s48_reviews.py` (and `s16_reviews.py`) are hashed as scientific sources but weren't supplied. I can't vouch for them.

6. **Release dependency.** `validate` needs `logs/s48_launch.json`, so it must be committed or the clean-clone reproduction fails.

## Checks that pass on this code

- **Selection:** zero-based indices 2..9 map to rounds 3..10. Each case is cross-checked against the prompt's `statuses[partner]=='TYPE-Y'`, the public-history length, notes matching `gt['notes_file']`, and the archived boolean.
- **Action binding:** the `max(payload[8])` request choice is protected because `strict` plus the archived-match assert would catch a wrong-phase pick. `strict` requires exactly the partner key with a real boolean value and rejects duplicate keys and NaN.
- **Transport:** `chat(..., retries=1)` with `backend='codex'` makes one logical attempt. `fixed_model` is redundant but harmless.
- **Statistics:** quantile position `p*(N−1)` matches NumPy's linear method. The inclusive sign flip gives p=1/32 only when all five blocks are strictly positive; one zero block gives p=2/32, which correctly blocks a HIT. The exact-rational and doubled-integer reconstructions agree. Classification order (HIT, then DUD, then ODD) matches the design.

## Acknowledged limitations (not bugs)

- n=5 blocks, so a HIT needs all five blocks at ≥+0.5. Power is very low, and ODD or DUD is the likely outcome.
- Content, length and position change together, and choosing the last round makes the length difference as large as possible. Partner information echoed in your own notes or the public history survives deletion.
- If the fresh retain approval rate is near zero, the result is an uninformative DUD.
- Temperature and max_tokens are not passed to the CLI. Provider identity and tool non-use can't be verified, and the CLI fingerprint can't be compared with S29's.
- One malformed output (for example a fenced JSON block) aborts all 20 calls, with no retry.
- The sign-flip test assumes symmetry. The histories were chosen after seeing S29, so this is exploratory, not a mediation or long-run estimate.
- `s48_independent.py` doesn't re-check schedule or timing; its docstring says as much.

## Verdict

Item 1 is the only defect that could quietly change what the experiment measures. Items 2–6 are things to check or tidy before launch. No mediation or long-run claims are supported by this design, which matches its own scope.
