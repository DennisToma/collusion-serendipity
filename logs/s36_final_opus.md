# S36 independent adversarial review

I couldn't execute anything in this session. I had no shell, made no edits and made no model calls. Everything below comes from reading the code and the reported values.

## Arithmetic, recomputed by hand from the game-level primaries in `results/s36_grossnet.json`
I didn't have the raw rate choices; see "Not checked" at the end.

- **Block differences (net − gross):** 10, 1, 10, 0, 10. Mean is 31/5 = **6.2**. Net arm mean is 8, gross arm mean is 9/5 = 1.8. All match.
- **All 3125 bootstrap samples:** the 2.5% and 97.5% bounds sit at sorted positions 78.1 and 3045.9.
  - Difference: the 32 samples with no 10 come first (means up to 1.0). Next are 15 samples with mean 2.0 (positions 32–46), then 60 with mean 2.2 (positions 47–106). That gives a lower bound of **11/5**. The 243 samples with mean 10 fill positions 2882–3124, so the upper bound is **10**.
  - Gross arm: cumulative counts are 1024, 2304, 2944, 3104, 3124, 3125, giving bounds **[0, 27/5]**.
  - Net arm: the bounds are **[4, 10]**.
  - All match.
- **32 sign flips** (numerators 320, 32, 320, 0, 320; observed sum 992): any flip of a nonzero block takes the sum below 992. Only the two choices for the zero block reach it, so p(upper) = **2/32 = .0625**, p(lower) = 1, and two-sided p = 4/32. All match.
- **Paired t:** standard deviation √27.2 = 5.215, standard error 2.332, t(4) = 2.7764, giving **[−0.276, 12.676]**. Matches.
- **Verdict:** the mean is at least 2 and the lower bound is above 0, but p = .0625 > .05, so it isn't a HIT. The mean is above 0 and the upper bound (10) is at least 2, so it isn't a DUD. **ODD is correct**, with no promotion.
- **Secondary metrics:** firm profit is exactly 20 minus take-home. The offered-rate numerators, tie rates and regret (9 at take-home 0, 4 at take-home 10) all check out.

## Code review
- **Economics:** `outcome` subtracts the offset before it computes the maximum, shares and profits, so gross g maps to net g−10 for every profile and every unilateral deviation. The test covers this exhaustively. The Nash set {18, 19, 20} is correct (all weak equilibria). Net-minus-gross is the direction in the code, the result file and the report.
- **Parsers:** both are condition-specific (offset to offset+20), reject duplicate keys and non-finite numbers, and catch `RecursionError`. A JSON list containing the three key names fails safely with `TypeError`.
- **Visibility:** each firm sees only its own notes, in both arms. Notes from the current round are added only after both firms have submitted, so the moves are truly simultaneous.
- **Failure handling:** a failure at admission sets the abort flag while holding the admission lock. A transport, parse or model/route failure aborts the pilot and leaves failure markers. An interrupted journal blocks both resume and analysis.
- **Command-line fingerprint guards:** the baseline is deep-copied, so it can't follow a changed config file. The fingerprint is checked at launch, at every admission, after every response and at completion.
- **Runtime headroom:** 1.5 × 5 × 156.728 = 1175.46 s required; 3102.47 s remained. Both match.

## Remaining bugs (none block the verdict)
1. **Low:** `s36_launch.launch()` releases the writer lock before `main()` takes it again, which leaves a small race window. Fix: hold one lock across both, or pass the lock handle through.
2. **Low:** the "independent" verifier's `expected_prompts` is a copy-paste of the production prompt. It proves the two match, not that the wording is right. Fix: say so in the verifier description.
3. **Low:** `validate_call_overlap` and the "actual transport" check in `verify_transport_and_preflight` test the same timestamps twice. The second adds nothing, so its label overstates it. Fix: relabel it or drop one.
4. **Low/medium (interpretation):** in 3–4 blocks both arms seem to settle on a quoted value of about 10. In the gross arm that is the lowest allowed quote, take-home 0, profit 20. In the net arm it is take-home 10. So the gap may come from the number 10 standing out (the tax/subsidy amount) or from gravitating to the bottom of the grid, not from anchoring as hypothesised. The report should add one descriptive sentence about raw quotes, derived as offered rate + offset. It shouldn't treat the hypothesised anchoring as supported or call the gross arm's monopsony outcome collusion. The current report already says neither.

## Limitations already acknowledged (not bugs)
- Several changes are bundled together: wording, grid labels and arithmetic.
- n = 5, and the sign-flip test assumes the paired differences are exchangeable or symmetric.
- The fingerprint covers only known local inputs. Ancestor `AGENTS.md` files, other files under `~/.codex` and node dependencies are not covered.
- Temperature and token limits aren't enforced by Codex, and whether the model actually avoided tools isn't verified.
- A legitimate auth-token refresh during the run would have aborted it.
- No agreement between the firms is verified.

## Not checked
- I couldn't recompute from raw rates. The `responses.jsonl`, `requests.jsonl` and game files weren't available, so I relied on the game-level primaries and on `logs/s36_independent.json` reporting a pass.
- I didn't run the tests, the cached replay or `s36_exact_check`.
- I didn't look at `s36_exact_check`, `s36_reviews` or `s36_release`, the `cournot`/`legality` modules, the figure, or the state of origin.
