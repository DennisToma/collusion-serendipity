# S06 — monetary denomination invariance (own axis, iteration 7)

Exploratory registration, zero tuning, no held-out test claim. Activated queued
S06 after all axes were covered; previous pilot D differs from own axis.
Ten fresh three-firm no-message Cournot games, T12, five time-matched blocks
24160..24164. IDs label blocks; they do not seed API draws or initial actions.

Underlying economics: q integer0..12, P=max(0,30-total q), cost6, individual
profit=(P-6)*q. All firms receive the same denomination within a game.
UNIT: k=1 accounting unit per common currency unit. CENT: k=100.
System displays P=max(0,30*k-k*total q), cost6*k, profit=(P-6*k)*q,
and the explicit conversion rate. Every displayed price, realized profit and
conditional-table profit is scaled by k; quantities and rounds are unchanged.
Both arms receive the same exact conditional own-profit calculator from round2,
based on the latest completed rival quantities, explicitly not a forecast.
Prompts are stateless, all completed public rounds supplied, no message box,
private reasoning never replayed. No change in real stakes or optimal actions.
Scaling bundles magnitude, formatting and numeric conversion cue; it does not
identify arithmetic errors, risk preferences or collusion. Canonical stored
prices/profits/regrets use COMMON currency, not displayed accounting units.

ONE primary: mean quantity per firm r4..12 (27 firm decisions per game),
CENT minus UNIT. No directional prediction; test invariance in either direction.
Paired bootstrap10000 from RNG2416, metrics ordered quantity/price/profit/
stage-regret/lag1-regret/distance/change/all-equal; for each: difference then
unit then cent. Descriptive percentile95% bounds; paired t95%; exact32-sign
upper/lower/two-sided absolute-sum tails using integer difference numerators/27.
HIT: absolute mean>=1, bootstrap excludes0, two-sided sign p<=.10.
DUD: absolute mean<=.25, otherwise ODD. At n5 the minimum two-sided p=.0625;
.10 is an explicit exploratory queue screen, not a .05 significance claim.
HIT requires five strictly same-sign differences and magnitude>=1; bootstrap
exclusion/sign conditions are not independent evidence. DUD does not establish
equivalence or policy invariance. No secondary may promote a HIT or change rules.

Secondary r4..12 mean price, own profit, actual stage-game regret, conditional
lag1 regret, distance from Nash6, absolute consecutive quantity change and
all-equal rate. All contrasts CENT minus UNIT in normalized common currency.
All-round/final-round metric means descriptive only. No pooling with older
pilots; fresh games all exploratory, zero tuning. Multiple pilots, n5 and
uncontrolled API sampling/interference limit inference.

Pinned codex/gpt-6-luna. Two games concurrently, sequential firms, per-block
barrier, randomized arm submission order RNG2416. 360 valid actions maximum,
max3 strict JSON attempts per action. Strict inherited parser rejects bool/
float/out-of-grid q, duplicate keys, nonstandard constants, reasoning>40 words,
nonempty message. Raw responses plus full requests cached; route labels and
attempt/timestamp provenance checked. No model fallback or replacement games.
Worker-side terminal failure sets shared abort; uncached calls observing the
flag at the logical-call guard are rejected; calls already past that guard or
in flight may finish (no atomic transport cancellation). Preserve partners, refuse partial-arm analysis.
No new uncached logical call from19:15UTC Oct24; inherited transport retries
may finish later. Absolute cutoff is operational, not a sampling guarantee.

Before calls: full dry pipeline, exhaustive scaled payoff/argmax/history checks,
strict parser, timing, provenance/tamper, deadline and worker-abort checks;
Codex and Opus methodology reviews requested (availability recorded). Freeze
scientific sources/config/tests/dependencies in committed pushed manifest.
Post-run mandatory exact-request cache-only replay, every key consumed once,
registered source hashes, exported outcomes and payoff checks, independent
raw-game metric/statistics reconstruction, byte-identical analysis/resume,
both final critics requested. No independent server-time/model attestation. Within-game attempt timestamps
must be sequential and block barriers must hold. Resumed partial games report the earliest cached call/start,
not the restart time, so completed paid actions remain reusable.
