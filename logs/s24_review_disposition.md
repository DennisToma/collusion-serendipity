# S24 review dispositions

## Methodology, before live outcomes

Both independent critics completed with exit0. Codex inspected repository files
and ran selected in-memory checks. Opus reviewed supplied source text only and
explicitly did not execute checks or inspect omitted files. Its supplied snapshot
preceded fixes to the stale lottery assertion and deterministic-score equality.
Neither review is represented as independent full raw-data reproduction.

- Codex medium cutoff crossing: accepted. Added a second cutoff check immediately
  after preflight and before the base cache call, local request admitted_utc, and
  analyzer ordering/cutoff checks. A synthetic preflight crossing the cutoff
  refuses dispatch with zero model calls. Provider execution is not attested;
  late base-cache logical starts still fail publication.
- Codex medium export byte integrity: accepted. Analyzer reconstructs canonical
  JSONL bytes; a key-order-only mutation is rejected without rewriting exports.
- Opus high stale stochastic-wording test: fixed during dry readiness, before the
  review returned; no live calls. Both arms now require deterministic3 and no
  lottery language. Single-phrase identity invariance is tested separately.
- Opus score equality: accepted before review return, enforced for every game in
  analyzer and independent raw reconstruction. Expected/realized metrics remain
  duplicated inherited fields; no separate scientific finding is attached.
- Opus expected-versus-deterministic wording: retained identical across arms and
  disclosed in design; deterministic charge3 is explicit immediately beforehand.
- Opus launcher lock gap: documented. The simulator writer lock, exclusive
  one-shot receipt and refusal of preexisting raw/config fail closed. Keeping
  the initial probe lock while main independently locks would deadlock without
  a larger lifecycle rewrite; no rewrite needed for this bounded pilot.
- Informational duplicated guards/unused import/hard-coded note total: no causal
  or numerical bug. Exactly20 archived notes/game and ten games enforced; derived
  nonempty counts retained. All timestamps originate in normalized local UTC.

Final readiness:18 protocol tests PASS; final300-key synthetic replay and
independent100 metric cells/30 bootstrap+t summaries/30 sign tails/300 histories/
200 snapshots PASS. No scientific live calls or outcome inspection before freeze.

## Final claims

Both final critics exit0; accepted with scope distinctions. Codex independently
reconstructs primary counts from raw decisions, all3125 bootstrap samples/32 sign
flips/t interval/score gate, the exact phrase contrast at300 archived histories,
all request keys/source/configuration/export bytes and independent full-statistic
replay. Opus has supplied-text access only: it hand-checks primary arithmetic,
bootstrap multiplicities/t/sign values, score arithmetic and the unchanged DUD;
it explicitly does not inspect raw files. It is not a second raw-data replay.

- Codex low abort/admission race: accepted and documented in README. Admission
  lock is released before local admission timestamp/base transport; another
  worker can set abort in that gap and one previously checked call can proceed.
  A synthetic mock demonstrates it. This archive has zero transport/parse/route
  failures or terminal aborts, so the race does not alter its data. Every failed
  or interrupted dataset is rejected at publication. Preserve frozen source;
  future reuse must define already-admitted requests and serialize abort and
  admission transitions. Do not claim fully atomic cancellation.
- Opus pending disposition/commit/clean-clone: ordinary remaining publication
  steps at review time, tracked in STATUS and dedicated release/clean-clone
  receipts. Independent
  full186-test suite and inspected figure are manager checks, not critic claims.
- Opus dead archive flag/count rounding: acknowledged prospective cleanup. Exact
  independent raw arithmetic verifies every current8/24-denominator count and
  every statistic; no current result defect or post-outcome source change.
- Opus suggested secondary directional-opposition sentence: not adopted. Partner
  selectivity is zero, so it has no opposing sign. All registered secondary
  outcomes and their uncertainty remain in the linked summary, unpromoted.

Scientific verdict unchanged DUD:1/40 partner Y approvals each arm;AI-human0,
bootstrap[-.075,.075],paired t[-.109749,.109749],upper p.75. Low observed rates,
selected n5 and identity/persona bundling remain explicit. No equivalence, real
human comparison, mechanism, agreement, secondary promotion or sibling claim.
Source20-file manifest and result SHA236d34b8 unchanged. No new scientific calls.
