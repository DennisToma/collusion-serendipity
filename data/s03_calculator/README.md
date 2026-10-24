# S03 conditional own-profit table: exploratory no-message games

Registered at 424c351; reviewed/frozen implementation at 29a4b3f. Design:
[DESIGN_S03.md](../../DESIGN_S03.md). Five planned fresh blocks 24060..24064,
two arms `none`/`calculator`, T12, three firms per game, pinned codex gpt-6-luna.
The seed identifies a temporal execution block and randomizes arm submission
slots. It does not set API sampling or a stochastic market (economics deterministic).
No model/prompt selection, no tuning, no locked-test headline or source pooling.

Both arms see completed public actions/profits and the last rival quantity sum.
From round 2 only, the calculator lists exact own hypothetical profits for q0..12
conditional on unchanged lagged rival quantities; it is explicitly not a forecast.
Every firm in a game gets the same arm; no assigned pair, no messages/advisor.
Complete request payloads include all text delivered to each firm. Cached
responses retain model/backend/timestamps; Codex does not enforce temperature
or independent server sampling seeds. Client model labels are not attestation.

`game_<seed>_<arm>.json` is authoritative, with observable rows and metadata.
`trajectories.jsonl` and `ground_truth.jsonl` are deterministic atomic exports
created only after all ten games finish. Ground truth includes unverified/null
agreement/execution labels, per-firm tables, private reasoning snippets and call
provenance; it is never a source of collusion truth. The shared schema's action
extension is `quantity`; `assigned_pair=null` because all firms are symmetric.

`raw/responses.jsonl` has the inherited request key and untouched model response.
`raw/requests.jsonl` stores the complete keyed payload and response SHA256. Keys
include dry flag, system/user prompts, tier/backend/requested temperature,
run_id, zero-based round, agent, attempt and model. No cross-arm response reuse.
`config.json` freezes source/design/analysis/dependency hashes, client routing,
workers, deadline and Python/NumPy/SciPy versions; drift fails on resume.
`schedule.json` holds randomized within-block arm execution order. Absolute
cutoff is no new uncached calls from Sat 16:35 UTC; in-flight responses retained.

Reproduce from the frozen commit if shared code changes later:
`uv run python scripts/s03_analyze.py`, then
`uv run python scripts/s03_verify.py` (all live calls forbidden).
Analysis itself also requires exact cached reconstruction before estimating.
The separate verifier checks exports and independent primary/regret arithmetic.
Live/resume `uv run python -m sim.calculator` pays only for uncached requests;
completed games are not regenerated. Dry runs require a separate scratch directory.

The primary is mean quantity per firm r4..12, calculator minus none, game/seed
block the unit. A tiny-sample DUD is a queue label, not equivalence or absence of
cycles; this intervention bundles arithmetic, salience, context length and myopia.
Full reporting will be in `results/s03_calculator.json` and REPORT_DETAILS.md.
