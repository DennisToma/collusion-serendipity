S40’s estimand, intervention, and arithmetic are coherent. I found no blocking statistical bug, but two operational integrity gaps remain. No edits or model calls were made.

**Concrete remaining bugs**

- **Registration race:** [s40_replay.py:251](/home/factory/collusion/collusion-serendipity/scripts/s40_replay.py:251) checks committed/remote equality, then computes the scientific-source baseline afterward. A file changed between registration and baseline hashing can pass admission checks against that new baseline. Final validation should reject the registration mismatch, preventing publication, but calls can already have occurred against unregistered code.
- **Some terminal failures lack a failure journal:** configuration writes, the execution-start headroom assertion, and the initial journal append occur before the enclosing failure handler ([s40_replay.py:255](/home/factory/collusion/collusion-serendipity/scripts/s40_replay.py:255)). Failure there can leave a consumed launch receipt and incomplete archive without an `execution.jsonl` failure event. Resume remains blocked, but failure accounting is incomplete.

**Checks that hold**

- Selection reconstructs all ten specified source cases without filtering selected actions or explanations. All ten archived quotes happen to equal 10; they are separately reported rather than substituted for fresh controls.
- Retain preserves the source system/prompt; erase changes only the private-note array. No current archived response enters either request.
- The outcome correctly subtracts 10 from the focal quote: **normalized offer**, not realized worker payment.
- Seed-4040 scheduling provides sequential arms within cases, two workers, and barriers between source blocks. Validation checks chronology, concurrency, admission cutoff, and first-admission headroom.
- Arithmetic correctly averages two cases per seed, then five blocks; enumerates 3,125 bootstrap samples and 32 inclusive sign flips; and applies HIT precedence. At five blocks, the p gate requires every contrast strictly positive.
- Parser, intervention/selection, and classification tests passed in three read-only tests. Cache validation rejects incomplete archives; explicit routing and deduplicated fallback prevent ordinary redraw/fallback.

**Acknowledged limits and verification boundary**

This is an observed, floor-enriched challenge—not held-out discovery. Erasure bundles note availability, length, completeness, and consistency with the notepad promise. Public history preserves prior actions. One draw per arm, five source blocks, and service interference limit causal precision and transfer; descriptive intervals do not establish population equivalence. Retain must reproduce the floor before any contrast can bear on the original floor behavior.

CLI settings/model identity, effective configuration, actual tool non-use, transient drift, and shared-helper accounting loss remain explicitly unattested. Twenty-minute headroom is an admission gate, not a completion guarantee.

No live S40 archive or results were present. The S40 files were untracked, so registration, live integrity, outcomes, rendering, and clean-clone reproduction remain unverified. Earlier pilots were not reviewed.