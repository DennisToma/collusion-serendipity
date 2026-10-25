# S37 adversarial review (DESIGN_S37.md and the code you pasted)

I reviewed only the files you pasted. I edited nothing, ran no tests and made no model calls. So the test outcomes below are what the code as pasted should do; nobody has run them.

**Verdict: not ready to register.** The economics, simultaneity and screening rule are correct. But the independent verifier has two bugs that should make the claimed passing tests fail. Fix them and get a full green test run before you commit the registration.

## Remaining bugs

**HIGH — the independent verifier crashes on the fifth metric** (`scripts/s37_independent.py`, inside `verify`). `cases[s,c]` is built with `enumerate(KEYS[:-1])`, so `stage_regret` is left out. The later `for k in KEYS:` loop then hits `cases[...]['stage_regret']` and raises `KeyError`. As a result:
- `verify()` cannot return `passed`, so `test_mocked_live_end_to_end` and the live run's "independent check" should fail.
- Even without the crash, only 40 cells would be checked, not the 50 the design claims.
- **Remedy:** use `enumerate(KEYS)`. The regret value already in `vectors` (sum ÷ 2, then ÷ 8) matches the analyzer's ÷ 16. Then assert that `metric_cells == 50`.

**MEDIUM — the dry-mode verifier adds the offset twice.** `TenderCache` maps a dry response to `rate = quantity + 10`. The verifier uses `quantity + 10 + offset`, which is quantity + 20. The `obj['rate']==a['price']` check therefore fails on any dry archive, so `test_raw_quote_and_normalization_tamper_rejected` can't pass, and neither can the planned "full dry 200-key replay" through the verifier.
- **Remedy:** use `quantity + 10`.
- **Related gap:** dry rates only reach 10–22. The dry replay never tests the Nash quotes (28–30) or the top of the grid. Map the dry grid onto the full 10–30 range.

**Consequence of both:** the "exhaustive tests" and "independent check" can't currently have passed. Rerun the whole suite and record the log before the registration commit.

**MEDIUM — the 60-second start-separation and overlap rules are only checked after the money is spent.** The first dispatch guard holds the admission lock while it does slow work: 22 `git show` calls, hashing the S19 data and fingerprinting the node/codex binaries. Meanwhile the partner game waits. If the gap goes over 60 s, `analyze` rejects the whole pilot after all calls are made.
- **Remedy:** run the one-time heavy preflight before the worker pool starts, or check the gap when the partner's first call is admitted and abort before any transport call.

**LOW — the model-identity check can't catch anything.** `llm._codex` reports back the model name it was asked for, not the model that actually answered. So the model/backend mismatch check in `checked_call` can never fail on `codex`. REPORT.md should say the served model is unattested, not "pinned".

**LOW — the "independent" prompt check isn't independent.** `expected_prompts` is a word-for-word copy of `prompts()`. It catches tampering with stored payloads, but a wording or economics error would be copied into both. Describe it as a byte-equality check.

## Checked and correct
- **Economics:** effective cost = quote − 10, in 0..20. The pure Nash quotes are only (28,28), (29,29) and (30,30). At 27/27 each firm earns 1.5, but moving to 28 earns 2, so it isn't an equilibrium. Profit plus take-home pay is 20 every round.
- **Simultaneity:** both prompts come from the same `rows`/`chat` before either firm's note is added, and each firm sees only its own notepad.
- **Statistics:** every metric is an exact integer over 32. The bootstrap uses the same linear quantiles as numpy. With n = 5, the sign-flip p ≤ .05 requires all five differences strictly positive, and a zero difference gives p = 2/32. That makes the bootstrap gate redundant, which the summary already says.
- **Screening code:** `classify` matches the registered rule.
- **Failure handling:** torn, duplicate or unfinished journals are rejected. Any single failure stops the pilot with no estimates and no resume.

## Already-acknowledged limitations (not bugs)
- The two arms bundle labels, wording and sentence length together.
- Temperature, token limit and reasoning effort aren't enforced by the provider.
- Actual tool non-use is unverified.
- An auth refresh triggers an abort.
- Five exploratory blocks, with no multiplicity correction.
- The sign-flip test assumes exchangeability.
- No subtraction of S36 effects.
- A negative effect is classed as DUD.

**One limitation to add:** if both arms end up at the competitive wage (18–20), a +2 difference is structurally almost impossible. A DUD there would show no power, not evidence that wording has no effect.
