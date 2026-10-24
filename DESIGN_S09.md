# S09 — erase private-message memory at a fixed public history

Registered iteration 5, 2026-10-24 before continuation calls. Axis E; no tuning.

Question: do prior private messages cause lower subsequent Cournot output,
conditional on the public history those messages have already helped produce?
All five S07 neutral games (seeds 24080..24084) supply rounds1–6. None selected
by message content, action, or effect. All S07 outcomes, including original suffixes, were observed before choosing S09; this is an
exploratory follow-up, not independent replication or locked-test evidence.
Local snapshots include original source SHA256; original S07 files remain intact.

Ten continuations, two per prefix, run rounds7–12 only (180 valid decisions total),
using pinned codex/gpt-6-luna, at most two games concurrently, seed-block barrier.
`retain` sees original received messages; `erase` sees none of rounds1–6.
Both retain identical public history initially, identical neutral rules, private
boxes and future-message delivery. From round8 new messages may restore information.
No erasure announcement or other prompt change; joint removal of both members' received-message transcripts from prompts;
no persistent agent state exists. No prior private reasoning or own
sent messages are replayed. Agent choices are simultaneous; no current-round leaks.
The outsider sees identical prompts at the fork, a useful negative-control exposure
check, but later actions may respond to the pair. Empty inbox is an unavoidable
format/content intervention and cannot separate missing-message cues from semantics.
The continuation control is regenerated; original S07 suffix is not a control arm.

Source prefixes fixed before calls. Schedule RNG2409 randomizes slot submission order
within each block; actual process completion is uncontrolled. API sampling seeds and
temperature are uncontrolled, so five prefix blocks, not 180 decisions, are units.
Inherited transport uses a fresh empty temporary directory per call, read-only
sandbox request, and explicit no-commands instruction. A mocked invocation test
checks these properties; no parent AGENTS.md exists in the observed temporary
path. Live generation sets TMPDIR=/var/tmp and records transport settings. These
are not OS isolation: an agent could potentially read erased files elsewhere;
actual absence of file/tool access is not independently attested.
Inherited transport may retry internally; logical-call deadline17:48 UTC does not bound
an already-running transport retry. Stop on any terminal game failure; keep cached
responses and any completed partner, no replacement/no selective restart. After
an observed terminal failure, prohibit new uncached requests from the partner;
already in-flight requests may finish. Reject torn raw appends without auto-recovery. Three strict
JSON parse attempts per action, all logged. Freeze source/config/registration commit,
full request and response cache; mandatory cache-only full replay before publication.

One primary: mean pair quantity per firm over all six continuation rounds, difference
erase minus retain. Per-block integer numerator over12 pair decisions; n=5. Fixed
10,000 block percentile bootstrap draws (RNG2409), paired-t95% interval (df4), and
upper one-sided exact sign-flip p over32 signs, conditional on slot exchangeability/
symmetric differences (not a guaranteed randomized test of an independently sampled
population). Descriptive intervals are fragile at n5; no multiplicity correction.
HIT iff exact mean >=1, bootstrap lower>0 and upper p<=.05. This defines a
causal-memory HIT, explicitly not a profitable-collusion HIT. Pair-profit direction
is reported separately: output increases could help or harm profit depending on rivals.
ODD-reverse iff exact mean<=-1 with all five differences negative; mean<=-1
otherwise is ODD; DUD iff -1<mean<=.25; otherwise ODD. At n5 the HIT
p rule requires all five positive differences (minimum p=1/32); this is a
stringent screening rule, not a calibrated test for a meaningful null effect. No secondary promotion or outcome-driven cutoffs.

Prespecified descriptive secondaries on rounds7–12: pair profit, outsider output/profit,
market price, sent-message words/nonempty slots (including final-round messages never received).
Also outsider round7 output difference as a descriptive negative-control outcome. Also round7-only pair output difference
(immediate fork before any new messages received); mean absolute arm output differences
at the fork; number of source nonempty messages (exposure, not proof of coordination).
Every result includes all five prefixes. No agreement/execution ground truth; reduced
output, message influence and profitable coordination are distinct claims. If HIT,
hand off narrow causal-memory claim; a fresh-prefix replication with semantic placebos
would be needed. No original S07 arm pooling, independent-seed or legal-policy claim.

Reproduce: `TMPDIR=/var/tmp uv run python -m sim.replay --out data/s09_replay`, then
`uv run python scripts/s09_analyze.py`. Dry mode uses a separate output directory.
