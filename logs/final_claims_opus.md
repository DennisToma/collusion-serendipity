I found five problems the report should fix. Every number in REPORT.md matches the JSON (S01 means and CIs for all three contrasts in both families, 104 games and 2,080 rounds, S02 arm means, the three seed differences, paired t, unpaired bootstrap, p=0.25, prices, 216 calls, 0 retries). Both verdict labels follow the DESIGN rules: S01 is DUD because neither primary interval is positive. S02 is ODD because −0.481 is below −0.25 and the CI lower bound of −1.222 is below −1. The problems are omissions and framing.

**1. S01: the no-channel controls show a gain, and the report leaves it out.**
In `llm_ds_p2`, `control_gain` is +0.00569 [+0.00088, +0.01019] (n=15). That is the only interval in S01 that excludes zero, and it comes from games with no channel. This is direct evidence for the "price nonlinearity" explanation the report only mentions as a possibility. Add after line 16:
> "In no-channel controls the digit encoding also improves prediction: +0.00569 [+0.00088, +0.01019] (deepseek; luna −0.00065 [−0.00213, +0.00079]). This is consistent with integer-price nonlinearity, not channel-specific information."

**2. S01: the sample size is overstated.**
The table row says "104 existing games / 2,080 rounds" next to the primary contrast. The primary uses only channel games: n=32 (luna) and n=15 (deepseek). Change to:
> "104 games / 2,080 rounds scanned; primary contrast on channel games only (luna n=32, deepseek n=15)."

**3. S02: one seed carries the whole result, and with 3 seeds the bootstrap interval is just the range.**
- The seed differences are −0.222, −1.222, 0.000. A percentile bootstrap over three paired values just returns their min and max, so "[−1.222, +0.000]" is the observed range, not an interval estimate.
- In the seed that moves (24021), the outsider also cut output (5.22 vs 6.00) and total output fell by 3.22. That looks like the whole market shifted, not a pair-specific effect.
- Replace "ODD, heuristic prioritization only" and the CI wording with:
> "ODD by the frozen thresholds, driven by one of three seeds (24021: −1.222; others −0.222, 0.000). With n=3 the percentile bootstrap interval equals the range of seed differences. In seed 24021 the outsider's output also fell (−0.78), so the movement is market-wide, not pair-specific."

**4. S02: required secondary outcomes are missing, and pair profit did not rise.**
DESIGN asked for outsider quantity, total quantity, price and profits. Its amendment also asked for round-12 behaviour and arm means relative to q=6 and q=4. The report gives only the raw price means, with no interval. Add:
> "Private minus none: outsider +0.074 [−0.778, +1.000]; total −0.889 [−3.222, +0.556]; price +0.889 [−0.556, +3.222], sign-flip p=0.75; pair per-firm profit +0.056 [−4.556, +4.722]. Round-12 pair output: none 6.0/5.0/6.0, private 6.0/4.5/6.0 (seeds 24020–22)."

Pair profit is essentially unchanged, so "collusion-like" should not be read into the quantity drop.

There is also a benchmark gap, and the fix must be computed by a script before it goes in the report. The q=4/P=18 joint optimum assumes all three firms coordinate, but only the pair can talk. If the pair acts as one firm against the outsider, my own calculation (not from a repo script) gives each pair firm 4, the outsider 8, price 14, and pair profit 32 per firm. That is below the Nash 36, the classic merger paradox. So lower pair output is not obviously in the pair's interest. Add this case to the enumeration in the validity checks, then write:
> "Note: if the pair acts as one firm against the outsider, the pair-only equilibrium is unprofitable for the pair (enumerated: q_pair=4 each, q_out=8, P=14); lower pair output is therefore not by itself evidence of profitable coordination."

**5. S02: the report doesn't say the fallback broke the pre-registered "no fallback" rule.**
The 14:40 amendment says "Backend/model pinned, no fallback". The 14:49 fallback changed the model. Lines 40–48 describe the fallback but never say it went against that rule. Add:
> "This fallback deviates from the pre-registered 'no fallback' rule (14:40 amendment); it was registered before any replacement-arm outcome, but the S02 result is from an unplanned model (gpt-6-luna instead of qwen-3.6-35b)."

Also, `results/s02_cournot.json` records `"temperature": 1.0`. The report already says Codex doesn't expose temperature, but the JSON field could still mislead. Tag it `requested_not_enforced` or note this next to the reproduce command.

The causal wording is otherwise fine: "opportunity contrast, not verified collusion", the bundled channel-prompt caveat, the no-message-inference clause, and "cannot identify intentional coding" all match DESIGN. I made no edits and no LLM calls.
