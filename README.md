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
