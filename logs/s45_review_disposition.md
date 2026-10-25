# S45 review disposition — before live outcomes

Initial independent Codex and Opus methodology critics both exited0. Codex read
files and ran in-memory economics,visibility,statistic and accounting-failure
checks;Opus received file text only and explicitly did not run code or inspect
raw archives. Reviews began before the final cache hardening; resolved items are
listed by their scope rather than represented as current defects.

Accepted and fixed before scientific calls:

- Independent raw reconstruction now rejects duplicate response/request rows,
  checks one-to-one key sets and recomputes both request keys and response hashes.
- Presentation independently validates the full live archive and compares the
  canonical result before writing anything. A mocked complete live run tests this
  and proves a modified result cannot change the report,figure or summary.
- Latest S41 cache records durable admissions,atomically aborts on preflight
  failure,rechecks known inputs after returned responses and tests headroom at
  first actual admission. This resolves initial Opus timing concern.
- Simulator and independent parser both handle RecursionError. Unique equilibria,
  dominance and the6/0/8/9benchmark values are asserted explicitly.
- An ambiguous memory sentence now names both public history and accessible notes.
- Temperature/token arguments are explicitly local labels,not transmitted CLI
  sampling settings. Requested low reasoning effort is distinguished from served
  settings. Route metadata report the client's request,not provider identity.
- All five archived outcomes reduce to only two independent rates. Consumer loss
  =10*unsupported rate,combined profit=9*supported+6*unsupported;profit fields are
  duplicates and the profit gate is mechanical. Verification counts are checks,
  not independent evidence.

Retained,with explicit prospective limitations:

- Auth/config/reference hashes deliberately fail closed. Token refresh may abort
  even after all calls;such a dataset is invalid,with no estimate or interrupted
  resume. Dropping auth hashing would weaken the registered local-input check;
  successful datasets must satisfy it. Provider settings remain unattested.
- Shared llm.chat writes its accounting log before returning. If that upstream
  write/transport fails,a completed upstream output can be unavailable to this
  cache. Durable admission and failure records remain,and the whole pilot aborts.
  No claim that every upstream completed output is cached. Historical llm.py is
  untouched. No silent fallback or accounting monkeypatch introduced.
- Hashing overhead is not modeled separately. The reference gate uses historical
  >=30calls/game versus20planned and a1.5multiplier;cutoff remains absolute,not a
  completion guarantee. Paired transport overlap and registration chronology are
  checked on completed archives.
- Completed resume returns through full archive validation and a call-forbidden
  replay. The inherited cache_only assignment is redundant for that path;it is
  not claimed as the sole offline safeguard.

No outcomes were available to either design critic. A second independent review
of the amended sources is requested before registration. No thresholds,prompts,
models,windows or seeds were selected from fresh outcomes.

## Amended and final patch reviews

Both amended critics exited0. Codex again checked economics/statistics in-memory;
Opus remained supplied-file-text only. Accepted further fixes before live calls:

- Independent verification requires a bijection between all200planned decision
  slots and accepted responses,contiguous preceding attempts and exact per-run
  provenance order. A hash-valid substituted response regression is rejected.
- Returned response bytes are fsynced before request binding,and the request
  append is fsynced before return. Upstream accounting loss remains separate.
- Timing language now refers only to local llm.chat intervals. The gate requires
  at least one strict positive intersection of per-call intervals across each
  paired game,not merely overlap between first/last-call envelopes. A deliberate
  alternating-call fixture fails;touching endpoints are insufficient. Provider
  execution/CLI timing remains unattested.
- All report metadata/anchor/marker validation and complete report construction
  precede summary,figure or REPORT writes. Missing/reversed/duplicate markers
  cannot cause partial publication through a validation error. Disk failure is
  not claimed as an atomic multi-file transaction.

Initial targeted Codex patch critic exited0 and found the final publication-order
and envelope-vs-call issues;both fixed. Final targeted Codex critic exited0,
found no remaining bugs in these two fixes,and explicitly performed static review
only. Twenty-one local scoped tests include full mocked-live eligibility,replay,
canonical result publication and corruption checks. Final full-suite receipt is
stored separately. No model-call outcomes,threshold/window changes or tuning.

Retained scope choices:auth refresh and conservative ancestor/config hashes may
invalidate a completed run;full hashing overhead is accepted instead of weakening
checks to stat metadata. Both repo and actual temporary-root ancestors are hashed;
this is deliberately conservative,not a complete configuration proof. Requested
route metadata are not served-model validation. The launcher stays foreground;
no commit occurs during science and raw caches remain tracked for reproduction.
No heuristic ban on repeated reasoning substrings was added:notes can legitimately
repeat reasoning voluntarily. Full canonical replay reconstructs every prompt,
while the separate verifier checks saved public histories,snapshots,payoff phrases,
readability/inverse sentence,actions,notes,reasons and exact statistics.
