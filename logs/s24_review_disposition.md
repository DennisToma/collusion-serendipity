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

Pending completed data and independent critics. No HIT asserted.
