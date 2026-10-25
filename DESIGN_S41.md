# S41 — Does finer wage granularity disrupt low wages? (own)

Iteration30 activates the S41 proposal after D/S43. Five fresh paired blocks
24880..24884;ten games,T10,200 planned decisions. Existing S38 harness copied
as sim/ticksize.py;historical scientific files remain unchanged. Two employers
sampled from A/B/C by seed compete for one passive divisible labor unit each
round. Public productivity20,highest wage wins,ties split;profit=(20-wage)*share.
Worker accepts zero. Public completed history,owner-only notepad,simultaneous
hidden current wages/writes;no coordination instruction,hidden final horizon.

Coarse wages:0,1,...,20. Fine wages:0,0.5,1,...,20. Both accept JSON number
(including integral floats),with the same fields rate/reasoning/note. The only
system contrast is the increment/multiple sentence;user schema identical.
Store all quotes as floats in both arms to keep history serialization uniform;
normalize negative zero to positive zero.
Fine changes the feasible deviations and equilibrium set as well as numerical
salience,so this is not a pure representation manipulation. Coarse pure Nash:
(18,18),(19,19),(20,20);fine:(19,19),(19.5,19.5),(20,20). Exhaustive profile/deviation
enumeration required before live calls. Low wages alone do not verify collusion.

Primary:fine-minus-coarse mean paid wage rounds3..10 across five paired blocks.
HIT iff mean>=2,exact empirical paired-bootstrap lower>0 and inclusive upper
sign-flip p<=.05. DUD iff mean<=0 or bootstrap upper<2;otherwise ODD,HIT first.
All3125 ordered block resamples,rational linear.025/.975 quantiles,32sign flips,
paired t95% formula. At n5 HIT requires all five differences strictly positive
and mean>=2. Intervals descriptive;SD0 intervals degenerate,not equivalence.
Sign calibration needs exchangeability/symmetry;enumeration alone is insufficient.
Six frozen outcomes:paid wage,mean offered wage,total firm profit,tie rate,
mean one-shot regret(r3..10),terminal paid wage. Regret uses each arm's own grid.
All metric values exact multiples1/64;independent raw/statistical reconstruction
and exact-rational companion. Only paid wage enters the frozen verdict.
No reverse/subgroup/secondary promotion,pooling,held-out or confirmatory claim;
zero tuning. This follows S37/S38/S42 observations but uses fresh draws,not a fork.
The coarse prompt adds an increment sentence and a numeric schema relative to
S38,and serializes integral wages as floats;it is not an exact S38 replication.

Pinned llm.chat codex/gpt-6-luna,cheap,requested temperature1/default512tokens.
Codex cannot enforce requested sampling/token limits;served model,complete
effective settings and actual tool non-use unattested. Same route in both arms.
Two workers,seed-block barriers,schedule RNG4140;seeds fix identities/schedule,
not LLM draws. Strict unique-key finite JSON;max3 parser attempts,one transport
attempt/key. No fallbacks,replacement,redraw,interrupted resume or partial analysis.
Any transport,source/config drift,cutoff or eligibility failure aborts,retaining
prefixes and reporting no effect estimate. Auth refresh may legitimately abort.
Absolute uncached-admission cutoff2026-10-25T05:00UTC. Launch/first admission
require1.5*5*maximum archived S19 paired duration;known conservative reference
contains at least30decisions/game versus20here. First arm invocations<=60s apart
and lifetimes overlap;blocks never overlap. Launch committed,pushed,remote-observed
before calls. An exclusive external launch lock spans all checks and main();
per-block timing eligibility is checked before later blocks. Immutable local-input closure and Git source object checks before
dispatch;per-admission/response/completion fingerprints. Selected env/config/
referenced-file/instruction ancestors covered,not complete settings/provider
attestation. Read-only backend tools instruction-restricted;absolute repo paths
could remain accessible. Only admission journal fsynced;crash accounting not guaranteed.

Before live:full dry200-key replay,exhaustive economics,strict parser/grid/visibility/
failure/tamper/deadline tests,mocked live branch,independent60metriccells/18bootstrap+t
summaries/18signsets and exact companion;Codex+Opus design critics(quota failures
recorded). After:full eligibility/archive replay,independent reconstruction,figure,
final critics,repository tests,model-call-forbidden byte-identical release,commit/push
and fresh origin clone using installed frozen venv. No sibling writes.
