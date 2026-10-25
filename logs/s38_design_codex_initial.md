Reviewed all 12 requested files. No edits or live model calls. Read-only checks covered all 441 wage profiles, unilateral deviations, and three screening boundary cases.

**Remaining bugs**

- **Medium — interrupted calls can lose request provenance.** [horizon.py:132](/home/factory/collusion/collusion-serendipity/sim/horizon.py:132) writes the request audit only after the underlying cache returns; [resource_cache.py:72](/home/factory/collusion/collusion-serendipity/sim/resource_cache.py:72) writes the response first. Interruption during transport leaves no durable admission record; interruption between those writes leaves a response hash without its request payload. Restart correctly refuses continuation, but the promised request/attempt audit is incomplete. **Remedy:** persist and flush an admission record containing payload, key and timestamp before transport, then append completion/failure records. Validate unfinished admissions without repairing or resuming them.

- **Medium — independent verification permits dry results to be relabeled live.** [s38_independent.py:72](/home/factory/collusion/collusion-serendipity/scripts/s38_independent.py:72) uses configuration to interpret dry responses but never checks `result['dry'] == cfg['dry']`. Changing only the result’s dry flag leaves its numerical checks valid. [s38_present.py:11](/home/factory/collusion/collusion-serendipity/scripts/s38_present.py:11) trusts that flag for canonical publication protection. **Remedy:** bind result metadata to configuration in independent verification and require presentation to consume a verified result digest plus configuration identity. Add a flag-tampering regression case.

**Checks that hold**

Allocation, profits, wage/profit complementarity and equilibria `(18,18)`, `(19,19)`, `(20,20)` are correct. Current actions and notes stay hidden despite sequential API execution; known-horizon statements remain truthful through round 10.

Metric arithmetic, denominator 32, bootstrap interpolation, inclusive sign tails and HIT-first classification agree with the design. HIT indeed requires five strictly positive differences and mean ≥2. Replay reconstructs prompts and consumes every cached key once. Failed or interrupted datasets are rejected; partial-arm estimates are blocked. Registered-source and selected configuration drift checks fail closed.

**Acknowledged limitations**

Five exploratory blocks, unobserved hidden-horizon beliefs, multiple equilibria, passive workers, and no verified coordination limit interpretation. The causal target is the disclosure sentence’s effect under this protocol, without an isolated belief mechanism. Sign-flip calibration requires exchangeability/symmetry. Complete effective configuration, provider execution, actual tool non-use, and provider sampling parameters remain unattested.

No high-severity economic or screening-arithmetic defect found. No live S38 archive was present, so actual execution compliance remains unreviewed.