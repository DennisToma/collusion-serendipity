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

While S03 is running, `uv run python scripts/s03_progress.py` logs only
completion/routing/retry/latency metadata to `logs/s03_runtime_checkpoints.jsonl`;
it does not expose actions or treatment-effect estimates. Required cache-only
reconstruction runs inside the analyzer as well as the independent verifier.

`uv run python scripts/s03_economics.py` independently enumerates the static
integer-game equilibria and verifies the q4/q8 lag-best-response cycle used in
the S03 interpretation notes. It reads no LLM outcomes and writes
`logs/s03_economics.json`.

The final S03 interpretation is rendered with `uv run python scripts/s03_present.py`.
It first runs the original frozen renderer, then adds the observed cycling
interpretation from prespecified metrics and clarifies that DUD concerns the
registered directional prediction. It changes no estimates, windows, thresholds
or frozen source hashes. Run this after a base `render_report.py` refresh.

Before replaying S03, run `uv run python scripts/s03_audit.py`. This read-only
preflight checks newline-complete raw files, use of every cache entry exactly
once, actual UTC start times against the cutoff, and invalid-retry reasons by arm.
It protects the committed evidence from the shared cache's recovery behavior on
a damaged final line. The audit is also a post-run verification, with output in
`logs/s03_execution_audit.json`; it changes no scientific estimate or verdict.

Final verification also binds the entire result JSON to canonical byte-identical
reanalysis and independently checks the queue verdict (`logs/s03_execution_audit.json`).
`uv run python -m unittest scripts.test_s03_publication -v` checks rejection of
altered verdicts/intervals and unused cache entries. Pre-run validation comprised
8 S03 tests within the 21-test suite; these are 2 additional publication checks.
The frozen transport wrapper's deadline is checked per logical call, while
internal transport retries are not separately bounded/logged. This run finished
before 16:08 UTC; a future experiment near a strict cutoff needs per-transport
attempt enforcement. See final critic dispositions for the precise limitation.

S07 (iteration4, axis F) compares a neutral market-rule cue with an explicit
anti-coordination prohibition; both arms have the same pair-only private box.
No fines or enforcement are implemented, so this tests the exact normative cue
package. See [DESIGN_S07.md](DESIGN_S07.md); ten fresh exploratory games, zero
tuning, no agreement/execution truth labels and no no-channel control.

```bash
uv run python -m sim.legality             # pinned live/resume, source drift rejected
uv run python scripts/s07_analyze.py      # complete arms + mandatory offline replay
uv run python scripts/s07_verify.py       # independent arithmetic, exports, all keys
uv run python scripts/s07_report.py       # current report + detailed tables + figure
uv run python -m unittest scripts.test_s07 -v
```

Dry run: `uv run python -m sim.legality --dry --out /var/tmp/s07_offline`, then
`uv run python scripts/s07_analyze.py --data /var/tmp/s07_offline --out
/var/tmp/s07_offline/result.json --allow-dry`. Use a fresh directory after source
changes. `s07_report.py` updates S07 in the existing report; after regenerating
older pilots with `s03_present.py`, run `s07_report.py` again. The analysis and
verifier refuse incomplete raw files before the inherited cache can recover
them; preserve damaged evidence and inspect it before any generator resume.
