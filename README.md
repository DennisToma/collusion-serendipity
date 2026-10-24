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

S07 (iteration 4, axis F) compares a neutral rule cue with an explicit
anti-coordination prohibition. Both arms retain the same pair-only private box;
no fines or enforcement are implemented. Ten fresh exploratory games, zero
tuning. No agreement/execution truth labels or no-channel control.
See [DESIGN_S07.md](DESIGN_S07.md) and [all S07 outcomes](results/s07_summary.md).

```bash
uv run python scripts/s07_safe_run.py       # live/resume; terminal-failure guard
uv run python scripts/s07_publish.py        # complete guarded publication, offline
uv run python scripts/s07_independent.py    # all 210 metric/window cells and intervals
uv run python scripts/s07_retry_audit.py    # rejected-output reasons by arm
uv run python scripts/s07_diagnostics.py    # explicitly post-hoc outlier interpretation
uv run python scripts/s07_present.py        # current report, tables and figure
uv run python scripts/s07_release.py        # source/input/result hashes + cached resume
uv run python -m unittest scripts.test_s07_release -v
```

The publication wrapper always verifies live data, rejects terminal-failure
records, resolves every frozen source against the full registration commit,
and checks configuration/version consistency before atomically writing the
unchanged canonical result. Recorded versions matching recomputation do not
independently attest historical backend execution. The archived original
`sim.legality` and `s07_analyze.py` CLIs retain known prospective guard gaps;
use the safe-run/publication wrappers above. Those wrappers preserve every
frozen scientific source, estimate and decision rule.

Dry run: `uv run python -m sim.legality --dry --out /var/tmp/s07_offline`, then
`uv run python scripts/s07_analyze.py --data /var/tmp/s07_offline --out
/var/tmp/s07_offline/result.json --allow-dry`. Use a fresh directory after source
changes. Synthetic permission does not authorize publishing a live dataset
through the archived CLI. Pre-run S07 validity checks are included in
`uv run python -m unittest scripts.test_s07 -v`; the three later release tests
cover terminal failure, registration/config mutations and verification bypass.

`uv run python scripts/s07_protocol_audit.py` is a synthetic protocol check:
S02 echoed own sent messages, while S07 filters by recipient. S02 therefore
bundles partner messages with own-message persistence; no memory effect has
been estimated. Its old data, estimates and frozen ODD verdict are unchanged.

The independent checker initially used Python statistics on NumPy integer
values, which truncated an aggregate mean. Its corrected implementation
reproduces all metric/window values, bootstrap and paired-t bounds and the
exact DUD rule. Original source/hash and correction history are retained.
Its supplementary freeze followed 60 responses, before completed games or
outcome inspection; only the production registration predates every live call.

`s07_present.py` wraps the frozen renderer, then adds the prespecified message
counts, explicitly post-hoc sensitivity, retry/isolation limits and checker
correction record. It changes no estimate or verdict. It updates S07 in the
existing one-page report; after regenerating older results with
`s03_present.py`, run `s07_present.py` again. Incomplete raw files are refused
before cache recovery; preserve damaged evidence before any generator resume.

### S09 counterfactual transcript-visibility replay

All five original neutral S07 prefixes are extracted deterministically by
`scripts/s09_snapshot.py`. Continue from round7 with prior received transcripts
retained or erased for both pair members, with new messages delivered normally:

```bash
TMPDIR=/var/tmp uv run python -m sim.replay --out data/s09_replay
uv run python scripts/s09_analyze.py
uv run python scripts/s09_independent.py
uv run python scripts/s09_present.py
uv run python -m unittest scripts.test_s09 -v
```

Existing caches permit complete offline resume/replay. Raw cache keys and full
requests are retained; the analyzer prohibits uncached model calls. Source and
registration hashes, original prefix identity, all attempts, exports and payoffs
are verified before writing results. `--dry` requires a separate `--out` directory;
analysis of dry data needs `--allow-dry` and a separate result destination.
A terminal failure or torn cache append stops the pilot without replacement.
See [DESIGN_S09.md](DESIGN_S09.md) for the exact prospective screen and limitations.

S09 interpretation: messages sent in round6 would first enter the round7 decision
prompt. The intervention therefore removes both previously seen transcript history
and incoming information, rather than testing pure forgetting. After the absolute
17:48 UTC cutoff, the generation command only resumes the archived cached pilot;
it cannot create a fresh replication. The published raw caches are tracked.
`uv run python scripts/s09_exact_check.py` supplies the separate post-review exact
empirical-bootstrap and raw-quantity check; it does not replace the frozen estimates.

To verify committed S09 portability, run `uv run python scripts/s09_clean_check.py`.
It creates a clean local clone in /var/tmp, blocks uncached publication calls,
recomputes the archived outputs and checks exact bytes, protocol tests and links.

### S11 delayed-feedback intervention (D3)

Ten fresh no-message calculator games compare lag1 with lag2 market feedback.
The primary is consecutive output-change reduction; it is not a collusion label.

```bash
TMPDIR=/var/tmp uv run python scripts/s11_safe_run.py
uv run python scripts/s11_analyze.py
uv run python scripts/s11_independent.py
uv run python scripts/s11_present.py
uv run python -m unittest scripts.test_s11 -v
uv run python scripts/s11_release.py
# After committing all outputs, verify a clean clone:
uv run python scripts/s11_release.py --clean-clone
```

The raw request/response caches are archived with the games. After18:35UTC Oct24,
the generator can only replay the existing cache, not start a fresh replication.
Cache-only analysis verifies every request key, payoff, export, source SHA and
registration commit before writing a result. An independent implementation checks
all metric/window cells and intervals. Dry runs require a separate destination:
`uv run python -m sim.delay --dry --out /var/tmp/s11_offline`; then analyze with
`--data /var/tmp/s11_offline --out /var/tmp/s11_offline/result.json --allow-dry`.
Use a fresh dry directory after source changes. See [DESIGN_S11.md](DESIGN_S11.md).

S11 archive note: the original frozen `sim.delay` generator has a brief gap
between worker terminal failure and collector-side abort propagation; no terminal
failure occurred in the observed run. Use `scripts/s11_safe_run.py` for archive
resume: it propagates abort at the worker and forbids live model calls. It leaves
all original scientific files and cached results unchanged. The release check
uses this wrapper and independently parses every saved request history/table.
Run `uv run python -m unittest scripts.test_s11_safe_run -v` for both regressions.
The renderer is presentation code revised after outcomes, separate from the frozen
scientific manifest; its initial version was committed in703a0a8 before calls.

### S06 monetary-denomination invariance (own axis)

Ten fresh no-message, calculator-assisted Cournot games display every monetary
amount at1x or100x with an explicit conversion rate. Underlying payoffs, quantities
and optimal actions are identical. All money metrics normalize to common currency.
See [DESIGN_S06.md](DESIGN_S06.md); n5 and the two-sided .10 queue screen are
exploratory, not equivalence testing or a collusion label.

```bash
TMPDIR=/var/tmp uv run python -m sim.denomination
uv run python scripts/s06_analyze.py
uv run python scripts/s06_checked_independent.py
uv run python scripts/s06_retry_audit.py
uv run python scripts/s06_request_audit.py
uv run python scripts/s06_present.py
uv run python scripts/s06_release.py
uv run python -m unittest scripts.test_s06 -v
# After committing results, verify from a clean local clone:
uv run python scripts/s06_release.py --clean-clone
```

Source/configuration/registration hashes, every cached exact request, every key,
all exports, attempt sequences and payoffs are required before analysis. Worker
failure sets shared abort before executor cleanup; the audit checks within-game
sequential timestamps and inter-block barriers. Calls already past the guard may
finish; no atomic transport cancellation. Absolute cutoff19:15UTC Oct24 forbids
new uncached logical calls; cached replay remains possible. Raw caches are tracked.
Dry runs need a separate destination, e.g. `uv run python -m sim.denomination --dry
--out /var/tmp/s06_offline`; dry analysis requires `--allow-dry` and a separate
`--out`. Choose a fresh dry directory after source changes. No sibling checkout
or model credentials are needed for archived replay/publication.

S06 final-review note: the original frozen independent checker verifies arithmetic
but does not validate report metadata or duplicate result-game records. Use
`s06_checked_independent.py` above; its contract guard requires the registered
contrast/window/count/denominator and ten unique records before the unchanged
independent arithmetic check. The release audit also binds the complete result
to canonical reanalysis. Original scientific sources and result bytes are preserved.

### S14 procurement auction (A1)

Ten fresh repeated first-price tenders compare a pair-only private box with no
channel. Bids are6..20, cost6; ties divide one unit equally. Primary buyer payment
and pair-total profit are distinct from agreement/execution labels. See
[DESIGN_S14.md](DESIGN_S14.md). All data exploratory; zero tuning.

```bash
TMPDIR=/var/tmp uv run python scripts/s14_launch.py # first live launch, after freeze/push
TMPDIR=/var/tmp uv run python -m sim.tender       # completed archive, cache-only
uv run python scripts/s14_analyze.py
uv run python scripts/s14_independent.py
uv run python scripts/s14_request_audit.py
uv run python scripts/s14_economics.py
uv run python scripts/s14_present.py
uv run python scripts/s14_release.py
uv run python scripts/s14_release.py --clean-clone # after committing all artifacts
uv run python -m unittest scripts.test_s14 -v
```

The raw exact requests/responses are archived. Analysis refuses missing/extra
keys, partial games, code/registration drift and failed blocks. All calls are
replayed offline before estimation. Two games run concurrently with a block
barrier; no uncached logical call begins at/after19:45UTC Oct24. Cached resume
stays available. For offline smoke checks, use a separate directory with
`uv run python -m sim.tender --dry --out /var/tmp/s14_offline`, then
`uv run python scripts/s14_analyze.py --data /var/tmp/s14_offline --allow-dry --out /var/tmp/s14_offline/result.json`.

### S16 delayed notes-file access (C2), failed protocol

Ten planned procurement games compare author-only with shared notes, naming the
same pair and retaining own notes in both arms. The harness uses logical JSON
appends/snapshots; no external filesystem tool. The registered strict parser
aborted at three consecutive overlong-reasoning responses. Four games complete,
two started/aborted, four unstarted; no market effect is estimated and no games
are replaced. [Design](DESIGN_S16.md) · [Failure evidence](results/s16_summary.md).

```bash
uv run python scripts/s16_failure_audit.py  # exact cache-only full/prefix replay
uv run python scripts/s16_present.py        # failure summary + protocol figure
uv run python scripts/s16_release.py        # verifies failed archive, no effects
uv run python -m unittest scripts.test_s16 scripts.test_s16_failure -v
uv run python scripts/s16_release.py --clean-clone # after committing all artifacts
```

The archived generator and complete-dataset analyzer intentionally refuse this
failed invocation. All173 requests/responses and four completed games are retained;
there is no complete scientific result/export. Frozen source hashes and registration
are unchanged. The postfailure auditor independently reconstructs response validity,
completed public histories and accessible notes from cached prefixes, without
estimating any treatment contrast or making new model calls.

Synthetic successful-protocol reproduction still works with a fresh scratch path:
`uv run python -m sim.notes --dry --out /var/tmp/s16_offline`, then
`uv run python scripts/s16_analyze.py --data /var/tmp/s16_offline --allow-dry
--out /var/tmp/s16_offline/result.json`. It cannot overwrite the failed live archive.
Any new live pilot needs a new registered output contract and fresh seeds.

### S18 workplace review incentives (A4)

Ten fresh repeated review games compare self versus shared notepads. Immutable
submissions have authoritative PASS/FAIL labels. An approval rewards its author6;
reviewer receives+1 for PASS or-2 for FAIL. Incorrect approvals cost the organization10.
The primary is partner approval rate on FAIL tasks in rounds3..10 (8 opportunities/game).
Incorrect approvals are observable; agreements and reciprocal intent remain unverified.
[Registered design](DESIGN_S18.md). Auxiliary reasoning/note word counts are style
requests rather than action-validity gates on this fresh dataset; S16 is unchanged.

```bash
TMPDIR=/var/tmp uv run python scripts/s18_launch.py # one live invocation after source freeze/push
TMPDIR=/var/tmp uv run python -m sim.workplace      # completed archive only, cache-only
uv run python scripts/s18_analyze.py
uv run python scripts/s18_checked_independent.py
uv run python scripts/s18_present.py
uv run python scripts/s18_release.py
uv run python -m unittest scripts.test_s18 scripts.test_s18_publication -v
uv run python scripts/s18_release.py --clean-clone # after committing complete artifacts
```

The release command forbids model calls, verifies complete exact-request replay,
registration/source/configuration/chronology/exports/payoffs, independently rebuilds
all seven outcomes and all3125 empirical bootstrap samples, and checks byte-identical
canonical result and cached resume. Dry runs use a fresh separate directory:
`uv run python -m sim.workplace --dry --out /var/tmp/s18_offline`, then
`uv run python scripts/s18_analyze.py --data /var/tmp/s18_offline --allow-dry --out /var/tmp/s18_offline/result.json`.
No partial-dataset estimate or automatic failed-invocation resume is permitted.

S18 final-review guard: the original frozen independent checker accepts a missing
aggregate metric, so use `s18_checked_independent.py` above. It requires the complete
seven-outcome contract, denominators, summary fields and unique per-game records
before the original arithmetic. Both original sources and scientific result stay
unchanged; publication regressions exercise the omission found by the critic.

### S19 normative versus neutral labels (own)

Ten fresh workplace games hold incentives and shared-note access fixed. The
normative arm uses PASS/FAIL quality language; neutral uses TYPE-X/TYPE-Y and
organization-charge language. Primary: negative-type approvals between partners,
neutral minus normative, rounds3..10. Descriptive selectivity compares approvals
of the partner versus outsider; neither outcome verifies an agreement or intent.
All eight outcomes and the directional screen are registered in [DESIGN_S19.md](DESIGN_S19.md).
DUD includes reverse effects; no secondary promotion, tuning or pooling.

```bash
TMPDIR=/var/tmp uv run python scripts/s19_launch.py # one invocation after source freeze/push
uv run python scripts/s19_analyze.py
uv run python scripts/s19_checked_independent.py
uv run python scripts/s19_present.py
uv run python scripts/s19_release.py
uv run python -m unittest scripts.test_s19 scripts.test_s19_publication -v
uv run python scripts/s19_release.py --clean-clone # after committing all artifacts
```

Completed `uv run python -m sim.labels` invocations validate the full archive
without rewriting exports or making model calls. Analysis requires the recorded
Python/NumPy/SciPy versions. Fresh dry runs use a separate destination:
`uv run python -m sim.labels --dry --out /var/tmp/s19_offline`, then
`uv run python scripts/s19_analyze.py --data /var/tmp/s19_offline --allow-dry --out /var/tmp/s19_offline/result.json`.

S19 post-outcome supplements preserve all original scientific sources and results:
`uv run python scripts/s19_request_contract.py` independently checks every saved
exogenous system/payoff/status/access clause; endogenous note vocabulary is not
forbidden. `uv run python scripts/s19_action_text.py` lists every negative-type
approval in the registered window with its accepted raw explanation. These are
descriptive audits, with no new causal, agreement or intention labels.


S21 (iteration12, axis E) reuses one selected S19 response/game to test factual
reading of structured actions when explanations disagree. Ten cases, five source
seed blocks, three independent views, pinned gpt-6.1-sol/codex. This is an enriched
post-outcome challenge, not a held-out or prevalence estimate. See
[DESIGN_S21.md](DESIGN_S21.md). Run commands from the repo root with full git
history back to registration; no sibling checkout is required.

```bash
uv run python scripts/s21_audit.py            # one-shot live OR completed read-only validation
uv run python scripts/s21_analyze.py          # complete offline request/source/hash validation
uv run python scripts/s21_independent.py      # independent raw counts and 15 summaries
uv run python scripts/s21_present.py          # summary, figure and current REPORT row
uv run python -m unittest scripts.test_s21 -v
```

All thirty request/response pairs and selected case source hashes are retained.
Internal cheap-model fallback is disabled only within this runner's invocation;
shared llm.py remains unchanged. A failure aborts the full pilot without retries
or subset estimates. The exclusive external launch receipt also blocks relaunch
after accidental dataset-directory deletion. Raw responses remain immutable;
accepted parsing is a separate source-bound file. Dry run in a fresh scratch
folder: `uv run python scripts/s21_audit.py --dry --data /var/tmp/s21_smoke`, then
analyze with `--data /var/tmp/s21_smoke --out /var/tmp/s21_smoke/result.json
--allow-dry`. Dry data cannot replace canonical results or the live dataset.


S21 publication adds `uv run python scripts/s21_release.py` (deterministic result
comparison and immutable cached replay) and `uv run python
scripts/s21_source_audit.py` (separate post-outcome independent original-game
truth reconstruction, all-four-event completeness, strict texts and view/route
checks). The frozen `s21_independent.py` is the arithmetic checker and must be
used with protocol validation. Explanations retain embedded payoff amounts and
reciprocity claims; only separate payout/history fields are omitted. The term
confident error means a wrong non-null answer, without elicited probability.
