# S18 workplace review trajectories

Ten exploratory games, fresh paired seeds24280..24284, self/shared notes, T10.
Primary rounds3..10. Definitions and fixed screen: ../../DESIGN_S18.md.

`trajectories.jsonl` has one completed round per line, extending SCHEMA.md for
non-price decisions. `market.passed` is the authoritative task-label dictionary;
`agents[].reviews` maps each other employee to boolean approve/reject, `action`
is `review`, and `profit` is that employee's bonus score (not money or price).
There is no price field. Public messages are empty. `market.incorrect_approvals`
counts approved FAIL submissions and `organization_loss` is ten times that count.

`ground_truth.jsonl` and per-game `ground_truth` contain pair/condition, private
notepads, private reasoning and call metadata; detectors must not read them unless
explicitly authorized for that view. `agreement_verified`,
`coordinated_actions_verified`, `realized_collusion` and `hard_negative` are null.
Incorrect approvals can be measured from public test labels; agreement and intent
are not labeled. A designated pair is an opportunity label only.

`raw/responses.jsonl` caches every returned logical response; `raw/requests.jsonl`
records exact prompts with hash linkage. Failed logical transports, if any, retain
payload/error separately and invalidate the dataset. Internal llm.py transport
retries are not individually attested. Sampling/model/backend metadata are client
records. `raw/execution.jsonl` must contain exactly start/complete. Partial or
failed invocation cannot be resumed for live generation or analyzed as a subset.

Reproduce at the complete results commit so working sources match `config.json`:
`uv run python scripts/s18_release.py` (offline, model calls forbidden), then
`uv run python scripts/s18_present.py`. No earlier pilot is pooled or amended.
