# Critique of the S01 and S02 pilots in DESIGN.md

I read only DESIGN.md and CLAUDE.md. I didn't look at the sibling data, llm.py or any code, so a few points below are questions to check rather than confirmed flaws.

## S01: last-digit prediction

1. **The digit feature can stand in for price level.** The last digit is a step function of price. The baseline model is linear in prices, so the digit dummies will pick up any missing nonlinearity in price level, such as kinks near a focal price or price caps. Assigned pairs in channel games probably sit in a different price range and move differently from other pairs. If so, the digit term helps them more for reasons unrelated to coding, and the decision rule still calls it a HIT. Fix: give the baseline a flexible function of price (splines or bins of the source price level and its recent change). Then the digit term only gets credit beyond that.

2. **Round-number focal points will look like a signal.** Paired agents that message each other tend to agree on prices like 70 or 75. A last digit of 0 or 5 then marks "we are at the agreed price," which predicts the next move. That is real coordination, but it is not hidden coding and it is not about digits. The current HIT criterion can't separate the two. Fix: add a "price is a multiple of 5" control, or look at the digits 1–4 and 6–9 on their own.

3. **The control arm isn't part of the primary test.** HIT only requires both datasets (llm_v1 and llm_ds_p2) to be positive in channel games. The no-channel comparison is only secondary, and it uses one deterministic pseudo-pair, which is noisy. Fix: make the primary estimate a difference-in-differences, (assigned − others | channel) − (mean over all pairs − others | no channel).

4. **The pair count is unclear.** "Assigned pair minus the five other pairs" implies six undirected pairs, which means four firms. It's also not stated whether the ridge model is fit once across all pairs (which dilutes a signal specific to one pair) or per pair role. Fix: state the firm count, and use one model shared across pairs so the pairs are compared on equal footing.

5. **Keeping only complete runs may bias the sample.** If the channel arm fails or truncates at a different rate, this filter differs by arm. Fix: report how many runs were dropped in each arm.

## S02: Cournot quantities

1. **The CI-based decision rule is unreliable with five seeds.** A bootstrap over 5 paired differences has only 126 distinct resamples, and percentile intervals under-cover badly at this size. The design admits this but still uses "CI upper < 0" to call a HIT. Fix: use an exact sign-flip permutation test (with 5 pairs the smallest one-sided p is 1/32) or a t-interval, and treat the result as descriptive only.

2. **The seed pairing does little.** There is no model seed, so pairing by seed only matches the pair assignment and schedule. The paired bootstrap then treats the two arms as more correlated than they are. Fix: also report an unpaired analysis.

3. **There may be little room for a −1 effect.** LLMs often hold back output in Cournot games even without a channel. If the no-channel arm already averages around 4.5–5, the gap to the joint optimum of 4 is too small for a −1 contrast. S02 could then come out a DUD even if a channel effect exists. Fix: report each arm against Nash (6) and the joint optimum (4), and say explicitly that a ceiling result is uninformative.

4. **Invalid outputs aren't handled.** At temperature 1 some responses will fail to parse or fall outside 0..12, and the design doesn't say what happens then. Whatever default gets filled in (0, 6, or last round's value) could create the effect on its own. Fix: decide the rule before running and report the invalid-output rate per arm.

5. **A model fallback could differ between arms.** CLAUDE.md's llm.py falls back automatically across backends, and DESIGN.md names qwen-3.6-35b "via Aqueduct", which isn't in the fallback order CLAUDE.md lists. If a rate limit forces a fallback partway through, the arms could end up on different models. Fix: pin the backend, stop instead of falling back, and confirm the model for every call from the cached logs.

6. **The channel prompt may cause the effect by itself.** Telling an agent "you may privately message firm X" changes the prompt's framing and may hint at cooperation even if no message carries a plan. "Opportunity effect" is the right label. Logging message length, and whether quantities are mentioned, would help separate framing from actual coordination.

7. **The horizon isn't specified.** If agents know the game lasts 12 rounds, defection near the end gets mixed into the round 4–12 average. Fix: state whether the horizon is disclosed and report round 12 separately.

## Process

The plan to "attempt" an Opus critic and record a failure meets CLAUDE.md as written. Even so, run one independent review before any result is promoted into HITS.md.
