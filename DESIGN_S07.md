# S07 — explicit anti-coordination rule (axis F)

Iteration 4, registered before live calls, 2026-10-24. Five fresh seed blocks
24080..24084, two games/block, T12, ten games total. Following own-axis S03;
cover F before deepening any earlier pilot. No pooling, tuning or locked-test claim.

Question: does explicitly prohibiting coordination raise output in a quantity
market with a pair-only private channel? Both arms have three profit-maximizing
firms, q integer 0..12, P=max(0,30-total q), cost6, undisclosed final round,
all completed public quantities/profits, and the SAME randomly assigned pair
with a private box. Messages are delivered only in the next round; reasoning
is never fed back. The outsider cannot send/read private messages. All firms
receive their game's rule cue on every fresh-context decision.

NEUTRAL: "Market rules: all firms sell the same product in this market. Each
firm receives the profit shown by the stated payoff formula. No additional
market mechanism is implemented in this simulation."
LEGALITY: "Market rules: agreements between competing firms about output or
prices are prohibited. Each firm must decide its own output independently.
This rule does not change the payoff formula. No fines or enforcement mechanism
are implemented in this simulation."

Never ask agents to coordinate. Contrast is this exact normative cue package,
not law enforcement, legal advice, isolated morality, or proof of collusion.
No no-channel arm, so no channel-mediated causal claim. No truth labels for
agreement/execution; saved messages and private reasoning are unverified text.

Execution: pinned codex/gpt-6-luna, two concurrent games, seed-block barrier,
arm submission order randomized with RNG2408; seeds control pair/slots, not
backend sampling. 360 baseline calls, up to three attempts for malformed JSON,
non-int/bool/out-of-range quantity, reasoning>40 words, message>60 words or
nonempty outsider message. Fail closed on routing, missing games, source drift.
No replacement, partial-arm estimate, model switch or outcome-based stopping.
Cache exact request and raw response; authoritative atomic per-game files.
No NEW logical uncached calls from 17:05 UTC; in-flight/internal transport
retries may complete afterward (inherited transport limitation). Monitor time;
missing blocks are inconclusive, not silently discarded. Temperature/sampling
seed uncontrolled and client routing labels not independently attested.

ONE primary: pair mean output/firm, rounds4..12, legality-neutral paired by seed.
Hypothesis: positive. Five independent game-block contrasts, denominator18.
Descriptive paired percentile bootstrap (10000, RNG2408), paired t95% interval,
exact32-sign upper and lower tail p using integer numerators, ties retained.
Sign p assumes exchangeability/symmetry; concurrent API interference may break
this. HIT if mean>=1, bootstrap lower>0, upper-tail p<=.05. ODD-reverse if
mean<=-1 and all five signs negative. DUD if mean<=.25 otherwise; remaining ODD.
Queue screens, no equivalence test. Portfolio multiplicity and n5 limit inference.

Prespecified descriptive secondaries (same primary window): outsider output,
price, pair/outsider own profit, mean private-message words and fraction nonempty
messages. Save all-round and final-round summaries of every metric. Report all
primary-window outcomes with bootstrap and t intervals; no secondary promotes
HIT, tunes prompts or defines collusion. Arithmetic Nash q6/P12/profit36 is
reference only (grid also admits permutations of5/6/7).

Before calls: tests/dry full ten-game pipeline, strict parsing, no same-round
message leakage, exact decision boundaries, failure/tamper checks. Freeze code,
design, dependencies, analyzer, verifier and tests. Request independent Codex
and Opus design critics; record unavailable review honestly. After: mandatory
cache-only replay inside analyzer with live calls forbidden, all raw/request
keys consumed once and unchanged, source hashes, export matching, independent
stdlib primary/payoff/p-value calculation and byte-identical reanalysis. Final
Codex and Opus claims reviews, figure inspected; report remains one-page log.

## Pre-outcome review amendments

Opus design critic (logs/s07_design_opus.md): preserve a successful partner game
even if the other game fails. Drain/write both outcomes, save failure JSON and
stop at that seed barrier; later blocks are not started. Incomplete dataset is
INCONCLUSIVE with no arm estimate. No retry-limit or stopping-rule relaxation.
Record retries by arm, report neutral baseline versus symmetric Nash6 and
pair-minus-outsider output descriptively. Message windows mean messages SENT
in the named rounds; round12 messages are never received in this T12 sample.
The source manifest is tracked, clean against HEAD and committed/pushed before
live calls; config records that registration commit. Replay explicitly refuses
cache misses, independently of the correctly targeted sim.common.llm.chat mock.
Raw newline/key-use checks were already added before the review returned.

Retain sequential firm decisions within two concurrent games (at most two live calls),
rather than saturate the shared backend. S03 actually completed368 calls in
about15 minutes; S07 has360 baseline calls and >35 minutes at launch. This is a
throughput judgment, not a new scientific rule; fixed cutoff stays17:05.
No new smoke-test game or extra pilot. Unsupported critic claims (a scalar
Cournot4/8 benchmark, sign-test renaming, DUD as equivalence) are not adopted.
Exact sign-FLIP enumeration and existing boundaries are unchanged; a DUD only
screens this directional prediction. No neutral-collusion premise is assumed.

Codex design critic (logs/s07_design_codex.md): fixed recipient filtering so
partners see only messages addressed to them, never their own sent messages.
Added an explicit sender/recipient regression. Rejected duplicate JSON keys and
nonstandard constants before outcomes (the critic saw the earlier snapshot).
Live analysis CLI now runs independent verification before atomically writing
results; audit binds exact canonical result bytes plus all raw/game/export hashes.
Export-tamper regression verifies publication rejection. Transport filesystem/tool
isolation is NOT proven by the inherited no-tools instruction/read-only context;
no observed leak, but complete information isolation is not claimed. Fresh empty
working directories and textual tool prohibition are inherited, not OS-level
isolation. No prompt variants, scientific threshold/window or extra game added.
