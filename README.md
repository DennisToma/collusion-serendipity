# Collusion Serendipity Explorer

Discovery pilots for the Apart AI Collusion Sprint. Read [REPORT.md](REPORT.md)
for results, [DESIGN.md](DESIGN.md) for frozen choices and amendments, and
[STATUS.md](STATUS.md) for the handoff. The sibling repos are read-only inputs.

Install/run with `uv` (Python >=3.12). The pinned dependency resolution is in
`uv.lock`; no sibling checkout is needed to reproduce snapshotted analyses.

```bash
uv run python scripts/s01_digits.py
uv run python -m unittest scripts.test_research -v
uv run python -m sim.cournot --out data/s02_cournot_luna --backend codex --model gpt-6-luna --n 3
uv run python scripts/s02_analyze.py --data data/s02_cournot_luna
```

The registered fallback above uses the local Codex subscription, pinned to
gpt-6-luna. The original Aqueduct attempt is incomplete and retained separately;
that backend uses credentials from `~/collusion/compute.env` and the shared rate
limiter in `llm.py`. No scientific result pools models. Completed per-game files
are authoritative; JSONL exports are rebuilt after all planned games finish.
`data/s02_cournot_luna/raw/responses.jsonl` caches every response so incomplete runs
can resume without re-spending successful calls. Configuration mismatches and
concurrent writers to the same dataset fail closed. Never mix dry and real data.

Offline harness smoke test (writes only scratch data):

```bash
uv run python -m sim.cournot --out /var/tmp/serendipity_smoke --dry
uv run python scripts/s02_analyze.py --data /var/tmp/serendipity_smoke \
  --out /var/tmp/serendipity_smoke/analysis.json --allow-dry
```

Analysis refuses dry data unless explicitly requested, and does not draw a
publication figure from it. Both pilots are exploratory, with no model or prompt
tuning. Pilot verdicts prioritize follow-up; they are not findings of misconduct.

S04 (iteration 2) isolates a common sampled public-information advisor response
from independent same-model responses. Read [DESIGN_S04.md](DESIGN_S04.md) for
the exact intervention and exposure-gated screen. Ten fresh games, no pooling
with S02. Both arms sample two advice vectors per round; only scalar own advice
is delivered, with no shared-identity cue or seller message channel.

```bash
uv run python -m sim.advisor
uv run python scripts/s04_analyze.py
uv run python scripts/s04_verify.py
uv run python scripts/render_report.py
uv run python -m unittest scripts.test_research scripts.test_s04 -v
```

The live generator refuses code/configuration drift by source hash and uses a
single writer lock. Completed per-game files are authoritative. It waits for
both games in each seed block before starting the next, with at most two games
running. All responses (including unused advisor samples) are cached with
separate run/role/slot/attempt keys; every response's model/backend label is
checked. The verifier reconstructs all prompts with live calls forbidden,
compares all outcomes/advice/provenance, checks exports, and independently
recomputes the primary contrast. The analyzer refuses incomplete or dry data.
No outcome-dependent early stopping or replacement seed is allowed.

A separate synthetic-state instrument check, `uv run python
scripts/s04_precheck.py`, has eight cached advice calls and no seller games; it
was run once before live games, with no model or prompt selection. Offline
smoke test (choose a fresh scratch directory if the source/config changed):

```bash
uv run python -m sim.advisor --out /var/tmp/s04_offline --dry
uv run python scripts/s04_analyze.py --data /var/tmp/s04_offline \
  --out /var/tmp/s04_offline/analysis.json --allow-dry
```

No model credentials or sibling checkout are needed for cached analysis and
verification. `scripts/render_report.py` builds the one-page log plus details
for all completed pilots; it does not estimate incomplete S04 outcomes.

S03 (iteration 3, axis own) tests an exact conditional own-profit table without
messages. All firms in a game see the same interface; the table uses only the
last completed rival quantities and explicitly is not a forecast. The hypothesis
concerns mean output, and the effect bundles arithmetic, salience and framing.
See [DESIGN_S03.md](DESIGN_S03.md); every seed is exploratory (zero tuning).

```bash
uv run python -m sim.calculator                # live/resume; cached completed calls
uv run python scripts/s03_analyze.py           # offline, all 10 games required
uv run python scripts/s03_verify.py            # complete replay, live calls forbidden
uv run python scripts/s03_report.py            # figure from frozen results
uv run python scripts/render_report.py         # current one-page log + all details
uv run python -m unittest scripts.test_research scripts.test_s04 scripts.test_s03 -v
```

For a dry run, use `uv run python -m sim.calculator --dry --out
/var/tmp/s03_offline` and `uv run python scripts/s03_analyze.py --data
/var/tmp/s03_offline --out /var/tmp/s03_offline/results.json --allow-dry`.
Choose a fresh scratch directory after any source/design change. The generation
config freezes all simulation/design/analysis helpers and the dependency lock.
`logs/s03_analysis_freeze.json` also records reporting/verification source hashes
before live outcomes. Reproduce from this iteration's commit if future shared
source files change. Exported trajectories have `quantity` actions, no text;
metadata has `assigned_pair=null`, unverified labels, tables and reasoning notes.
A small sample DUD is a queue screen and cannot establish equivalence, lack of
cycles or lack of a policy effect. Raw caches are retained for paid-call reuse.
