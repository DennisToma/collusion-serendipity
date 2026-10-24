# Serendipity log — Beyond Words

Exploratory pilots that challenge the sibling projects' price-market findings.
Iteration 1; 2026-10-24. No confirmed hits yet. Designs and pre-outcome review
amendments: [DESIGN.md](DESIGN.md). Zero detector tuning attempts.

| Pilot | Idea → result | Verdict |
|---|---|---|
| S01 · C, price digits | Reused 104 games / 2,080 rounds. Adding source last-digit indicators to a public-history ridge predictor gives assigned-pair-minus-other-pairs mean squared error improvements of **+0.00175 [−0.00184, +0.00631]** for gpt-6-luna and **+0.00899 [−0.04249, +0.05535]** for deepseek. | **DUD** for this digit screen; no robust signal. |
| S02 · A, Cournot quantities | Registered: 5 seeds × private/no-channel, 12 rounds, qwen-3.6-35b. Live generation running; no outcome inspected. | Pending |

**S01 interpretation.** No sub-cent observations: every recorded price is an
integer. Absolute assigned-pair prediction gains are also unresolved:
+0.00076 [−0.00228, +0.00421] and +0.00903 [−0.04060, +0.05424], respectively.
Last-digit features have exactly zero residual after projection onto indicators
for the full permitted price grid. Therefore any linear-model gain could reflect
price-level nonlinearity; this pilot cannot identify intentional coding and does
not rule out signaling. No HITS.md promotion.

**Methods and limitations.** S01 snapshots contain actions/public state and
assignment metadata only, with original-file hashes. All completed source games
were included (none excluded). Five folds hold out whole games; preprocessing and
ridge coefficients fit inside each fold (alpha 10, fixed before outcomes).
Intervals are 10,000 game-score bootstrap draws, conditional on the cross-fitted
models; they omit overlapping-fit uncertainty and are descriptive. The primary
contrast uses 32 channel games for luna and 15 for deepseek. These are opportunity
assignments, not verified realized-collusion labels. No independent test-set claim.

S02 changes the economics to simultaneous output: P = max(0, 30 − total quantity),
cost 6, three firms choosing integer quantities 0..12. Symmetric static Nash is
q=6 each (P=12); symmetric joint optimum is q=4 each (P=18), verified by enumeration.
Only a randomized pair may message in the private arm; messages arrive next round.
The primary measure is pair quantity, rounds 4–12, private minus no-channel.
Five randomized within-seed execution blocks support only a discovery pilot.
No agent is instructed to coordinate. Prompt framing and delivery are bundled.

**Reproduce:** `uv run python scripts/s01_digits.py`;
`uv run python -m sim.cournot` (resumes cached/completed games);
`uv run python scripts/s02_analyze.py` once generation completes;
`uv run python -m unittest scripts.test_research -v`.
Frozen outputs: [S01](results/s01_digits.json). Independent methodology reviews:
[Codex](logs/design_codex.md), [Opus](logs/design_opus.md).

**Next:** finish S02 and choose a new axis; cover B, D, E, F and an `own` idea
before deepening any one axis. A larger follow-up requires fresh registered seeds.
