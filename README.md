# Collusion Serendipity Explorer

**Research takeaway:** The explorer tested channels, incentives and interfaces beyond the sibling price-market studies. No hit was promoted. Workplace review supplies an unresolved lead: shared notes coincided with more organization-harming approvals in one small pilot, while the fresh Qwen follow-up left the contrast unresolved. Neither sibling headline changes.

**The lead and its uncertainty:** Employees review each other; in S29/S62, approving TYPE-Y benefits the author, costs the reviewer and harms the organization. In S29 (gpt-6-luna), TYPE-Y approvals were **2/40 with self notes versus 15/40 with shared notes**: shared-minus-self approval-rate difference **+0.325**, descriptive block bootstrap 95% CI **[+0.100, +0.575]**, paired t 95% CI **[-0.049, +0.699]**. Each arm has five games and forty TYPE-Y opportunities over rounds 3–10; uncertainty uses five paired blocks. One block ties; the registered upper-tail sign-flip p=0.0625 misses the 0.05 screen. S62 (qwen-3.6-35b), ten fresh games in five blocks, gives **3/40 versus 7/40**, contrast **+0.100 [-0.025, +0.250]** (bootstrap 95% CI). Both pilots remain ODD. [Current evidence brief, payoff accounting and all intervals](BRIEF.pdf).

The frozen portfolio contains 54 entries: 29 DUD, 23 ODD/context-only and two failed. Entries reuse data and are not independent replications. These exploratory screens have no multiplicity correction or held-out validation. Adverse approvals do not establish agreement, intent or profitable collusion.

| Read | Contents |
|---|---|
| [Brief PDF](BRIEF.pdf) / [HTML](BRIEF.html) | Selected evidence, payoffs and uncertainty |
| [Report](REPORT.md) / [PDF](REPORT.pdf) / [HTML](REPORT.html) | All 54 pilot rows and current interpretation |
| [Methods and limitations](REPORT_DETAILS.md) | Per-pilot setup, caveats and figures |
| [Experiment ledger](EXPERIMENTS.tsv) / [ideas](IDEAS.tsv) / [splits](data/SPLITS.md) | Registration/result chronology and exploratory status |
| [Current state](STATUS.md) / [handoffs](HITS.md) | Append-only research history; no promoted hit |

**Check the current release.** Start from a clean full-history clone (no `--depth`), [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.12.15, the recorded Python version. Run from the repository root. The first two commands may download Python or dependencies; the check reads saved evidence and guards the selected replays.

```bash
uv python install 3.12.15
uv sync --frozen --python 3.12.15
uv run --frozen python scripts/export_report.py --check --replay-selected
```

This checks all 54 table rows, 307 numerical bindings, 144 sample/window fields and saved reproduction receipts, then reruns five selected analyses and separate checkers (S29, S62, S69, S70 and S72). S72 uses its genuine historical revision. It verifies export hashes and reports saved PDF coverage; it does not re-extract PDF text or rerun all 54 analyses. No API credentials are needed for these replays. The selected replays guard `llm.chat`; this is not network isolation or independent scientific validation.

**Recompute every primary result.** With the project environment installed:

```bash
uv run --frozen python scripts/portfolio_replay.py run --out /var/tmp/explorer-portfolio.json
uv run --frozen python scripts/portfolio_replay.py check --out /var/tmp/explorer-portfolio.json
```

The first command reruns 52 completed analyses, two failure audits and 50 existing checkers in disposable pinned checkouts; checker depth varies. The second checks the resulting receipt. This reproduces archived primary result objects, not every supplementary artifact or a new independent dataset. [Coverage, revisions and limits](results/iteration58_reproduction.md). S68 remains interrupted, with no effect estimate or restart.

**Canonical checks.** `uv run --frozen python scripts/release_tests.py --out /var/tmp/explorer-tests.json` runs the existing suite with its historical synthetic fixtures. Three named legacy S60 document tests additionally read the archived README; the actual current presentation is checked separately. Frozen tests and scientific validators are unchanged.

**Rebuild and inspect the reader exports.** Run in a clean released clone: the build regenerates tracked reader documents, exports, figure and receipt. The export environment is separate from the project environment and uses a hash-locked dependency file:

```bash
uv venv --python 3.12.15 /var/tmp/explorer-export61
uv pip install --python /var/tmp/explorer-export61/bin/python --require-hashes -r requirements-export.lock
/var/tmp/explorer-export61/bin/python -m playwright install chromium
/var/tmp/explorer-export61/bin/python scripts/export_report.py --build --check-pdf
git diff --exit-code HEAD -- README.md REPORT.md BRIEF.html BRIEF.pdf REPORT.html REPORT.pdf figures/explorer_handoff.png logs/iteration61_exports.json
```

Dependency/browser installation needs network access; Linux may also need Chromium system libraries. Rendering blocks browser network requests. `--check-pdf` re-extracts text, checks complete table rows in order and validates link targets. The final command tests byte identity on the recording host. Other hosts may change PDF, PNG, embedded HTML and receipt bytes; report those differences alongside the content checks. Keep the brief/report exports together for local links. Pinned GitHub evidence links require repository access.

**Historical reproduction.** [Fresh-install evidence](results/iteration57_reproduction.md) targets the archived handoff `e6b0c02`, reusing host Python, uv, OS libraries and fonts. Its receipt-only check does not reproduce the current checkout. [The complete iteration-60 runbook](https://github.com/DennisToma/collusion-serendipity/blob/73492a929c2245a033f1b1598a03703c3f6f6ee6/README.md) retains all per-pilot commands, including historical generation and publication commands; use their recorded revisions. Archived files linking to per-pilot README instructions refer to that runbook. Read it offline with `git show 73492a929c2245a033f1b1598a03703c3f6f6ee6:README.md`. The current replay commands above reproduce saved evidence without starting simulated agents. Future work is an unfinished, unregistered proposal in the [report](REPORT.md).
