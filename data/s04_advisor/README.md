# S04 — blinded common-sampling advisor intervention

Registered in DESIGN_S04.md and EXPERIMENTS.tsv, iteration 2. Ten exploratory
Cournot games; five fresh seed blocks 24040..24044; two arms (`shared`,
`independent`), T12. No pooling with S02 and no detector tuning. Source hashes
are recorded in config.json; registration commit 3f75341, analysis freeze
9574c06. All configured sources were unchanged at live start. See STATUS.md
for current completion and review state; never estimate a partial arm.

`game_<seed>_<condition>.json` is authoritative and contains rows plus metadata.
`trajectories.jsonl` and `ground_truth.jsonl` rebuild only after all games finish.
Observable rows follow SCHEMA.md's quantity-action extension; agents have
quantity/action/profit and empty public messages, market has realized price,
cost and demand intercept. No private advice/reasoning is exported in observable
rows. **Ground-truth metadata must never be detector input**: it contains pair
assignment, sampled advice, routing slots, private reasoning, call model/backend
labels and timestamps. Collusion/agreement/execution/hard-negative labels are
null, not inferred from arm assignment or absence of seller messages.

Raw responses in raw/responses.jsonl are keyed by run/arm, round, role/slot,
attempt, model, prompt and requested sampling parameters. Advisor0 and advisor1
are separately sampled, even with byte-identical prompts. Both arms make both
advisor calls; shared routing withholds one vector, independent routing selects
a different vector per member. Only the firm's own scalar recommendation is
delivered. The outsider is not told any advice. Sellers have identical framing
across arms and do not see whether the source was shared. Advisers and sellers
see only completed public rounds, with no current-choice leakage.

The two game slots in each block are randomized and run concurrently; both
finish before the next block. Pair/slot seeds control assignment and schedule,
not model randomness. Backend/model pinned to codex/gpt-6-luna; a provenance
mismatch fails closed. Codex sampling temperature/API seed is uncontrolled and
model labels are client reports. No persistent advisor state, private data
aggregation, common branding, or instruction to coordinate is tested.

Analysis: `uv run python scripts/s04_analyze.py` (refuses incomplete/dry data).
Verification: `uv run python scripts/s04_verify.py` replays with all live calls
forbidden, checks exports and independently recomputes the primary contrast.
Generator/resume: `uv run python -m sim.advisor`; exact unchanged code/config
required. Writer lock prevents concurrent generation to this dataset.
Synthetic precheck lives in ../s04_precheck and is never pooled as game data.
