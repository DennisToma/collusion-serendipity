# S11 — delayed market feedback (axis D3)

Registered before live calls; exploratory, zero tuning, no held-out claim.
Motivation: S03's calculator induced large output swings; feedback timing may
change those dynamics without communication. This is the first D-axis pilot.

Ten fresh three-firm Cournot games: five paired blocks24110..24114, T12.
P=max(0,30-sum q), cost6, q integer0..12, no messages or persistent reasoning.
Both arms receive exact own-profit tables conditional on latest OBSERVED rival
quantities (never a forecast). Immediate arm at round t sees completed rounds
1..t-1; delayed arm sees1..t-2. Delay applies to ALL feedback, including own
past action/profit, so no inference from fresh prices can bypass it. Separate
stateless prompts; only round number and system lag cue differ before feedback.
Delayed round2 has no table; this warmup difference is part of the treatment.
This is an information-timing package, not realistic perfect own-action recall,
not literal deletion of a persistent agent's memory, and not collusion removal.

ONE primary: reduction in mean absolute consecutive-round quantity change,
immediate minus delayed, r4..12 (27 firm transitions per game). Positive means
slower consecutive changes, NOT smaller long-run variance or convergence.
Theory: lagged best response q4/q8 could change from alternating to repeating
each value twice, reducing this metric while preserving periodicity.
Five seed-block differences; bootstrap10000 from one RNG2411 stream, metric
order quantity/price/profit/stage-regret/lag1-regret/distance/change/all-equal,
within each metric contrast then immediate then delayed. Descriptive percentile95%
bounds, paired t95%, exact32-sign upper/lower tails using integer numerators/27.
HIT if mean>=1, bootstrap lower>0 and upper p<=.05. ODD-reverse if mean<=-1 and
all five negative; DUD if mean<=.25 otherwise; remaining ODD. At n5 the HIT rule reduces to all five strictly positive differences and mean>=1;
its three conditions are not independent checks. DUD screens the directional
prediction only; it does not mean no effect. Screens only;
n5, exploratory portfolio multiplicity, uncontrolled backend sampling, API
interference and fragile CIs prevent confirmatory/equivalence interpretations.
No secondary may promote a HIT or tune the protocol.

Prespecified secondary outcomes r4..12: mean quantity, price, own profit,
actual stage-game regret, regret conditional on t-1 actions (diagnostic, including
for delayed arm), distance from symmetric Nash6, all-equal rate. All secondary
contrasts delayed minus immediate. All-round and final-round descriptive means
for all metrics. No agreement/execution truth labels, no collusion conclusion.
No pooling with S03 or any previous pilot; fresh blocks do not control API draws.

Pinned codex/gpt-6-luna; two concurrent games, sequential firms, seed barrier,
random arm submission order RNG2411. 360 valid actions; max3 strict JSON attempts
per action. Reject bool/float/out-of-grid q, duplicate keys, nonstandard constants,
reasoning>40 words or nonempty private message. Cache requests/raw responses,
log client model/backend and attempts; fail closed on route mismatch, torn
cache, source/config drift, failed/missing game or orphan key. Set a shared abort flag after terminal failure; no further uncached partner
requests, while in-flight calls may finish. Preserve completed partner on failure; no replacement or partial-arm estimation. No new uncached
logical calls from18:35UTC Oct24; inherited in-flight/internal transport may
finish later. No OS isolation or independently attested sampling/model guarantee.

Before calls: full dry pipeline, arithmetic/timing/parser/tamper tests,
independent Codex and Opus methodology critiques (availability logged), freeze
source/design/analysis/tests/verifier/dependencies in committed pushed source
manifest. After: mandatory cache-only reconstruction of every exact request,
all keys consumed once, source hashes against registration commit, exports and
payoffs verified; separate raw-game metric/statistics recomputation, byte-
identical analysis/resume, both final critics requested. Report every result.
