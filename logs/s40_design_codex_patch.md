S40’s intervention and estimator match the registered design. I read all eight requested files and performed read-only, in-memory checks; no edits or paid calls. No live S40 archive exists yet, so execution and release integrity remain unverified.

**Concrete remaining bug**

- **Headroom check has a timing gap.** [s40_replay.py:211](/home/factory/collusion/collusion-serendipity/scripts/s40_replay.py:211) checks one `utc()` value, then obtains another for the registration receipt. Mocking those instants across the boundary produced an accepted receipt with **1,199 seconds** remaining. Retrospective validation rejects that receipt, but only after calls could have occurred. Further setup can also reduce headroom before execution starts. Use one checked receipt timestamp and enforce launch headroom immediately before starting execution.

**Checks passed**

- Selection reconstructs the ten specified source cases without filtering actions or explanations. Each contains nine owner-only notes; all ten archived selected quotes are 10. This verifies source selection, without reviewing earlier pilots’ scientific conclusions.
- Retain preserves the archived system and user prompt. Erase replaces only the notes array with `[]`; no current archived answer enters either request.
- The outcome is correctly **normalized focal offer: quote minus 10**, not worker payment. Each seed averages its coded/payroll cases; the primary averages five seed differences. Bootstrap enumeration and linear quantiles, paired-t bounds, inclusive sign flips, and HIT/DUD/ODD precedence match the design. Numerical spot checks passed.
- Scheduling implements two case workers, sequential randomized arms, and seed-block barriers. Replay checks arm chronology and barriers.
- Strict parsing, fixed-model deduplication, admission/output journals, failure rejection, incomplete-cache rejection, source hashes, committed registration binding, and the external one-shot receipt are present. Release combines full reconstruction with separate raw-rate arithmetic verification and blocks model calls during regeneration. Previously flagged missing-case and retrospective registration-headroom checks are present.

**Acknowledged limits**

This remains an observed, floor-enriched challenge with five source blocks and uncontrolled sampling. Erasure jointly changes note availability, length, factual completeness, and consistency with the complete-notepad promise. Public history retains earlier behavior. A null cannot establish memory irrelevance; without fresh retain-floor reproduction, a difference cannot explain the original floor.

Uncertainty bounds are descriptive. Requested temperature/token limits are unenforced. Effective configuration, provider behavior, tool non-use, and transient reverted drift remain unattested. Accounting-log failure can lose backend output before `llm.chat` returns; the design acknowledges terminal failure without an estimate. No inference establishes hidden reasoning, coordination, collusion, or downstream worker-payment effects.