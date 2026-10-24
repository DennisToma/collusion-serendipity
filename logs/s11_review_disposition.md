# S11 independent review dispositions

## Methodology, before live outcomes

Both critics requested before any live S11 calls. Codex reads current source;
Opus receives a fixed stdin snapshot. Later guards are recorded below.

Codex design review exit0: found one medium provenance-resume bug. The cache
could backfill a missing request entry after a pre-existing response. Fixed
before live calls: constructor rejects any pre-existing key-set mismatch and
verifies every request hash, response hash and dry flag. Two new regressions
cover missing and corrupted provenance; no repair occurs. Accepted all listed
scope limitations: full feedback/own recall/warmup/lag wording bundle; n5,
backend interference and uncontrolled sampling; consecutive smoothness is not
convergence, long-run variance reduction or collusion removal. The critic
found no remaining timing/arithmetic/screen error. Its snapshot predated the
new constructor guards; the final review will inspect frozen sources.

Opus design review: completed below; both design reviews preceded live calls.

Opus design review exit0: no blocking implementation defect in pasted snapshot.
- Retained the common directional screening rule used by preceding pilots, including
  five-negative ODD-reverse screen. Every DUD reports the actual mean and intervals;
  DUD never means "nothing here" or equivalence. A strong mixed reverse would be
  shown explicitly. No outcome has been inspected.
- Accepted explicit caveats: naive delayed best response predicts smoother
  consecutive changes, so this alone is not surprising evidence of learning,
  stabilization or collusion removal. Any HITS handoff must say so itself.
- Explained n5 HIT equivalence (five positive differences, mean>=1); bootstrap
  and p conditions are not independent evidential checks.
- Clarified shared RNG2411 draw order in DESIGN before outcomes. No numerical
  estimator change; independent exact3125 bootstrap remains supplementary.
- Source registration/remote ancestry and first-call chronology will be checked
  operationally after push and before generation. No server-time attestation is
  claimed. Historical transport observations S03/S07 are 15-18 minutes for~370
  calls; the critic's two-hour estimate is not supported by those observations.
- Several cited test gaps/tautological test were fixed while the fixed Opus
  snapshot ran. Current tests include no same-round leakage, full dry export/
  source/version/game/failure/cache tampering and missing/corrupt provenance.
- Switched config temperature constant to TEMPERATURE. Fixed own locking resource
  cleanup below; no live scientific request or outcome yet.

Supplementary checks after launch, before any S11 treatment-effect inspection:
- `s11_transport_audit.py` uses only synthetic responses and mocked transport.
  Wrong-model refusal, valid-but-orphan cache key refusal and byte-identical
  cached replay after cutoff all PASS; zero live model calls. It does not edit
  any frozen source or inspect partial treatment outcomes.
- `s11_reference.py` implements the prespecified deterministic q4/q8 toy example.
  Both lags have full-window mean6 and population variance4; consecutive-change
  reduction is20/9 over the primary window. This is analytical protocol
  verification, not an LLM result, new pilot or mechanism label.
- `s11_chronology.json` checks all13 source hashes against703a0a8 and config.
  Remote reference was observed17:55:52.546725, first client call17:55:52.825256.
  All ordering is based on local observation/client timestamps; no independent
  server-time attestation. No partial treatment estimates inspected.

## Final independent critics (both exit0)

Codex (`s11_final_codex.md`) independently recomputed raw240 cells,24 bootstrap
and8 t intervals, exact primary[11,-25,57,27,52]/27, both sign tails and unchanged
ODD. It checked all366 keys,13 registered hashes, release hashes and chronology.
Its only remaining bug is low-severity worker-to-collector abort propagation:
a partner can enter a call between terminal checked_call failure and collector
handling. No terminal failure occurred in this dataset, so no estimate/exclusion
changes. Accepted prospective fix without thawing scientific sources:
`s11_safe_run.py` sets abort inside the worker call guard and forbids live model
calls. Both invalid-output and route-failure regressions PASS. Release uses the
archive guard and still reproduces result/data bytes exactly. The original
runner remains archived; README directs archive resume through the wrapper.

Opus (`s11_final_opus.md`) analytically checks all primary arithmetic/sign tails/
t interval, secondary means/differences and quantity t interval, all-round/final
means and analytical reference. It had no raw-file/tool access and did not
recompute bootstrap quantiles; do not attribute those checks to Opus. Those are
covered separately by Codex and the independent raw-game checker.
- The uncommitted-artifact blocker was a snapshot of review launch: every
  scientific artifact/script was committed and pushed as1a8c435 during review.
  Clean clone of1a8c435 PASS:17-artifact release audit,15 tests,4 output artifacts
  byte-identical. Final revised-wrapper clone follows; critics remain intact.
- Recorded both final dispositions here after their completion.
- Renderer is outside the13-file frozen scientific manifest. Its original was
  committed in703a0a8 before calls; later presentation-only revisions are
  explicitly identified in `s11_renderer_provenance.json` and retained patch.
  No claim that the revised renderer predates outcomes or that clean cloning
  independently attests execution chronology. Frozen result SHA remainsd136e501.
- Added separate post-review `s11_request_audit.py`, with no production prompt
  helper imports: all366 raw histories/lag cues and317 actual calculator tables/
  rival summaries match exact allowed completed rows. No new estimator/window.
- Clarified time-matched pairs: IDs do not seed actions, initial state or API
  draws. Marked lag1 regret as a diagnostic against hidden feedback in the
  delayed arm; it is not a treatment success or equal-information optimization
  comparison. A received-feedback-regret metric would be a new posthoc outcome,
  so it is deferred rather than promoted.
- Restricted the theoretical prediction to symmetric toy cycles initialized
  away from Nash; both lags can remain fixed at Nash6.
- Retained all five variable blocks including the reverse block. No posthoc
  block exclusions, unpaired/Wilcoxon tests, changed screen or secondary HIT.
  Per-block outcomes and plot already expose heterogeneity. Descriptive final
  round stays out of HITS. Contrary to one sentence in the critique, final/all-
  round summaries WERE prespecified in DESIGN_S11; they remain descriptive.

All numerical results and the original frozen sources/config remain unchanged.
There is no active scientific generation and no additional live model call.

Final revised clean clone of1477204 PASS: archive-only worker guard,17 protocol
checks,47 local links and4 output artifacts byte-identical (frozen result,
summary,figure,independent raw-metric audit). All69 discovered tests PASS.
All13 scientific source hashes and original result SHA remain unchanged.
