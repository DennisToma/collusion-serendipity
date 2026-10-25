# Explorer handoff: observations, limits and reproduction

Iteration 54 · 54 recorded pilot entries · **No promoted hits.** This is a presentation synthesis of existing results; selection of examples is post hoc.

The explorer tested channels, incentives and interfaces outside the sibling price-market studies. Workplace review provides a useful follow-up setting: a shared notepad coincided with more adverse approvals in one small pilot, while a fresh Qwen pilot left the contrast unresolved. Incentive and payoff-accounting checks constrain interpretation. These observations do not establish an agreement, reciprocal intent or profitable collusion, and do not change either sibling headline.

In the workplace task, TYPE-Y approvals benefit the author and harm the organization. In S29 and S62, approving TYPE-Y costs the reviewer two bonus points while paying the author six. In S69, equal pooling makes the reviewer’s marginal payoff +2 at low charge and −3 at high charge; S70 keeps −3 in both arms. Each contrast below uses its own five paired blocks and ten games; r3–10 supplies forty TYPE-Y review opportunities per arm. No rows are pooled. Bounds are descriptive 95% block-bootstrap intervals; paired t intervals are shown to expose small-sample sensitivity. The t bounds are untruncated descriptive approximations and can exceed the feasible range.

| Existing pilot | Observed approvals (first → second) | Named contrast | Bootstrap95% | Paired t95% | Frozen label |
|---|---|---|---|---|---|
| [S29: Shared notepad; gpt-6-luna](s29_summary.md) | self 2/40 → shared 15/40 | shared minus self: +0.325 | [+0.100, +0.575] | [-0.049, +0.699] | ODD |
| [S62: Shared notepad; Qwen-3.6](s62_summary.md) | self 3/40 → shared 7/40 | shared minus self: +0.100 | [-0.025, +0.250] | [-0.130, +0.330] | ODD |
| [S69: Pooled reviewer charge](s69_summary.md) | high_charge 4/40 → low_charge 31/40 | low minus high charge: +0.675 | [+0.450, +0.875] | [+0.335, +1.015] | DUD |
| [S70: Fixed endowment](s70_summary.md) | baseline 2/40 → endowed 2/40 | endowed minus baseline: +0.000 | [-0.075, +0.075] | [-0.110, +0.110] | DUD |

**Why none is promoted:** S29 misses its exact sign-flip screen (one block ties; upper-tail p=0.0625 exceeds the registered 0.05 threshold), and S62 is unresolved. S69 is an expected response when the marginal incentive changes sign, so its DUD label denotes successful calibration rather than a null. S70 does not pass its directional prioritization screen; it establishes neither equivalence nor absence of an endowment effect.

**Payoff timing matters to the label:** [S72](s72_summary.md), a post hoc reuse of all S29 games, finds both employees above a same-status one-shot Nash comparator over r3–10 in **0/5 self-note games versus 2/5 shared-note games**; the difference is +0.400, bootstrap95% [+0.000, +0.800], paired t95% [-0.280, +1.080]. Both intervals include zero. Both arms have zero same-round two-sided gains. The comparator holds task statuses fixed; this is not another independent replication, a repeated-policy counterfactual or evidence of reciprocal intent.

**Whole portfolio:** 29 DUD, 23 ODD (including post hoc/context-only), 2 failed/unclassified. Entries include fresh games, reused-history decisions and reanalyses; their counts must not be read as independent samples or a calibrated discovery rate. DUD means a registered surprise screen was not met (or an expected calibration succeeded); ODD means unresolved or context-only, not a confirmed signal. The [complete original table](../REPORT.md) retains every result and frozen label; the [machine-readable inventory](iteration54_portfolio.json) binds every entry to its idea and experiment-ledger records. Axes label the questions investigated; reused data can appear under several axes.

| Portfolio axis | Pilot entries |
|---|---|
| A (6) | S02, S14, S18, S31, S45, S56 |
| B (5) | S04, S27, S35, S42, S65 |
| C (6) | S01, S16, S29, S48, S58, S62 |
| D (7) | S11, S22, S33, S43, S51, S60, S69 |
| E (6) | S09, S21, S40, S53, S67, S72 |
| F (5) | S07, S24, S38, S50, S64 |
| own (19) | S03, S06, S19, S25, S28, S32, S34, S36, S37, S41, S44, S47, S54, S55, S59, S61, S66, S68, S70 |

**Failure evidence stays visible:** [S16](s16_summary.md) failed its output contract; [S68](s68_summary.md) was interrupted with one response missing. Neither has an effect estimate. S68 must not resume. Model families, prompts, parser adaptations and execution times differ across pilots; the S29/S62 comparison does not isolate a model-family mechanism. No held-out validation or multiplicity correction is claimed.

**Suggested future confirmation, not launched:** pre-register a fresh, larger shared-versus-self notepad comparison with an unread-notepad control, counterbalanced identities, and both employees’ complete-window gains as a fixed endpoint. Keep generation and judging separate and include a matched reference. This would separate channel delivery from channel framing more directly; agreement and intent would still require separate evidence.

**Offline verification of this handoff:**

```bash
uv run --frozen python scripts/iteration54_handoff.py verify
```

This checks all baseline file hashes and original table rows, replays the four displayed workplace pilots with the shared `llm.chat` entry patched to raise, and invokes their independent checkers. S72 replays in a temporary local clone at its own pinned result revision because its protected split index predates S70. The same call guard applies in the S72 subprocess. This is a guard on the scientific call path, not a network sandbox. Verification leaves archives and documents unchanged and writes one receipt. It verifies this selected handoff, not every historical analysis or a fresh dependency installation. The canonical repository test suite is `uv run --frozen python scripts/s65_tests.py --out /var/tmp/explorer_tests.json`. Archived publication renderers rebuild the documents at their own pinned result revision; use that revision for their byte-identical full-document reproduction.
