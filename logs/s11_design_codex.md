Read all nine files. One concrete remaining bug; no additional treatment-timing, arithmetic, or decision-rule error found.

**Remaining bug — medium: resume can silently repair missing provenance.** [DelayCache](/home/factory/collusion/collusion-serendipity/sim/delay.py:36) checks torn lines and duplicates but permits an existing response without its request-audit entry. A subsequent cache hit [backfills that entry](/home/factory/collusion/collusion-serendipity/sim/delay.py:65). Thus, a crash between response and audit appends can be silently repaired on resume; the analyzer’s correspondence check then passes. This weakens the promised fail-closed provenance policy. Reject pre-existing response/request mismatches before resuming. Confirmed using in-memory file doubles, with no filesystem writes or model calls.

**Acknowledged limitations, not remaining bugs:**

- Treatment bundles feedback age, suppressed own-action recall, lag wording, and round-two calculator availability. It supports claims about that package.
- Five blocks, portfolio multiplicity, uncontrolled backend sampling, and possible interference limit inference. Sign-flip validity remains conditional on exchangeability/symmetry; intervals are descriptive.
- Reduced consecutive quantity change does not establish convergence, reduced long-run variance, or collusion removal. The design correctly restricts those claims.

Current guards address exact request replay, unused keys, route mismatch, source hashes, torn caches, deadlines, and terminal-failure aborts. The 27-transition indexing, contrast directions, integer sign-flip tails, and verdict precedence match the design.

No edits or live model calls were made; this was a code/design review, not certification of a completed dataset.