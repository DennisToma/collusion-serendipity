# S14 data contract

Ten fresh first-price procurement games, all exploratory; full design in
[DESIGN_S14.md](../../DESIGN_S14.md). Observable trajectories contain bids in
`agents[].price`, allocated divisible units in `quantity`, `action="bid"`, own
`profit`, and `market.payment`. Every contract quantity is1, common delivery
cost6. No private text is in observable trajectories.

`ground_truth` retains latent assigned pair, opportunity condition, unverified
agreement/execution/collusion labels (null), call provenance and private messages.
It must not be passed to an action-only detector. `reasoning_notes` are unverified
private text, not classifications. Bids for round `t` cannot read current-round
bids or messages from other firms. Agents see all prior public rounds.

Round convention: observable `round=t` is zero-based. `private_chat.round=t+1`
is the earliest zero-based decision round in which a message sent while choosing
round`t` could be read; the JSON message body key is `text`. This follows S07,
not the older S02 convention. Recipient-only inbox histories contain no own
sent messages. Sends in final observable round11 are saved with`round=12` and
cannot influence a future decision in this game. For human display round numbers
are1..12. Repeated inbox appearances are not separate sent-message events.

`raw/responses.jsonl` saves all valid and rejected responses, including client
backend/model and request start/end timestamps. `raw/requests.jsonl` binds exact
full request payloads to response hashes. The immutable successful generation
invocation journal has exactly two events in`raw/execution.jsonl`; interrupted
invocations cannot resume live or publish. Successful runs resume cache-only.
`config.json` records source hashes and registration commit; replay validates all
raw keys once, provenance, payoffs, exports, timestamp order and block barriers.
Local timestamps/remote-head observations do not independently attest provider
execution, server time, sampling randomness or enforce requested temperature.

Reproduce via [README](../../README.md), using the archived result commit if
shared scientific helpers change later. Never edit raw evidence to repair a run.
