# S16 — Delivered partner notes versus self-only notes (axis C2)

Prospective iteration9 exploration, zero tuning. The S14 auction and all its
scientific files remain unchanged. Fresh ten games, five time-matched seed
blocks24240..24244, T12. Same seed fixes pair identity, not API sampling.

Question: does enabling partner access to a market-notes file raise procurement
payments relative to author-only notes, holding designated pair and writing cues
in both arms? No instruction to coordinate. Pair members in BOTH arms know the
same partner identity, may append one note<=60 words after each bid, and replay
all their own earlier notes. In self, only the author sees its entries; in shared,
both members see both files. Outsider has no file and is uninformed about access.
One visibility sentence differs in the system prompt; shared names the partner
explicitly as reader and writer. This bundles access wording,
partner-content availability, context length and endogenous writing. It does not
isolate semantic persuasion or identify an actual agreement.

The harness implements a logical append-and-snapshot tool with JSON note writes
and next-round prompt snapshots; this is not a filesystem tool-use capability
evaluation. Entries have round, author, text. All current bids and note writes
remain hidden until all three have submitted. No same-round note reads, reasoning
replay, public text or transfers. Final-round writes cannot affect later bids.
Three suppliers, common unit cost6, integer bids6..20. Buyer must purchase one
divisible unit at the lowest bid; equal lowest bids split quantity/revenue/cost.
All completed bids, allocations, profits and buyer payments are public. Own total
profit objective, horizon undisclosed. Static pure-Nash payments are {6,7},
verified exhaustively before calls. No verified agreement/execution truth labels.

Primary: mean buyer payment rounds4..12, shared minus self. Per-game mean then
five paired differences. Ten-thousand block percentile bootstrap RNG2424 with
exact integer sum/rational quantile primary; paired t95%; inclusive exact32-sign
upper-tail test. Sign test assumes exchangeable execution slots/symmetric block
differences; randomized arm submission order is not an API seed experiment.
HIT iff mean>=1, bootstrap lower>0, upper p<=.05 and mean pair-total profit
contrast>0 (supporting gate, not significant co-primary). DUD iff mean<=.25 or
bootstrap upper<1, otherwise ODD; evaluate HIT first. No secondary promotion,
block exclusions, window changes or updated rule after outcomes. DUD is not
equivalence. At n5 minimum upper p=.03125 requires all positive block differences.
Same thresholds as S14 but independent data, no pooling or confirmatory claim.

Prespecified secondary r4..12: pair-total profit, outsider profit, pair mean bid,
outsider bid, pair allocation share, lowest-tie frequency, winner-set change rate
(including r3 for r4), mean unilateral stage-deviation regret across firms.
All-round/final means descriptive; note sent/nonempty/available counts and retries
by arm/role descriptive. Private reasoning is saved but never replayed. Both pair
arms have identical output allowance; outsider must return empty note.

Pinned codex/gpt-6-luna, two games concurrently, sequential A/B/C within each,
barrier between seed blocks, randomized submission order RNG2424.360 valid actions,
max3 strict-JSON attempts per decision, all attempts cached. No fallback, redraw,
replacement or pooling. Interrupted invocation cannot resume live; terminal worker
failure sets shared abort and blocks analysis. Completed partner retained. Arm
starts within60s and execution intervals overlap. Absolute logical-call cutoff
2026-10-24T20:15UTC; transport retries can finish later, no atomic cancellation.
A guard/record timestamp race near cutoff fails closed rather than admitting
a possibly late call. One immutable start/complete journal; completed replay cache-only. Sampling,
temperature and backend identity remain client records, not provider attestation.

Before calls: strict parser, full economics and both-arm visibility canaries,
deadline/abort/corruption/interrupted-invocation checks, complete dry replay,
independent270 metric cells/27 bootstrap/9 t/all32 signs. Request independent
Codex+Opus methodology reviews, preserve quota failures. Freeze full scientific
manifest and push before calls. After: mandatory all-key exact-request replay,
source/registration/export/payoff/attempt/time/barrier validation; independent
statistics, saved-snapshot audit, byte-identical rerun, figure, both final critics
requested, clean-clone reproduction. Presentation scripts outside scientific
manifest. No sibling writes. Multiple selected pilots, n5, one model, bounded
homogeneous-cost tender, divisible ties and shared-service interference limit scope.
