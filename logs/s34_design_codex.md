Found two **medium-severity validation gaps** in S34.

1. **Paired execution checks can accept serial transport activity.** [s34_analyze.py:193](/home/factory/collusion/collusion-serendipity/scripts/s34_analyze.py:193) checks game-wrapper start/end times. Those starts are recorded before admission checks and transport calls. Consequently, two games can satisfy the ≤60-second start and overlap gates even when their actual model-call intervals do not overlap. This weakens the intended temporal pairing.

   **Remedy:** additionally check the difference between each arm’s first actual transport start and require overlap between their first-start/last-completion intervals. Add a canary with overlapping wrappers but disjoint transport intervals.

2. **Dispatch preflight chronology and headroom are incompletely verified.** [s34_analyze.py:165](/home/factory/collusion/collusion-serendipity/scripts/s34_analyze.py:165) allows the dispatch receipt to occur after requests have begun, provided it precedes the earliest game completion. The recorded `remaining_seconds` is bounded against execution start, rather than recomputed from a timestamp identifying the runtime check. Thus internally inconsistent preflight evidence can pass publication checks and exact cache replay.

   **Remedy:** record the runtime check’s timestamp, recompute headroom from that timestamp, and enforce runtime-check → dispatch receipt → first admission → transport-start ordering. Check the registered headroom requirement again at first admission. Add timestamp-mutation canaries.

The economics and statistical arithmetic checked out. Approval yields author +6 and reviewer +1 for X or −2 for Y; reports do not affect payoffs. Balanced schedules provide eight primary opportunities per type per game. Sequential calls preserve simultaneous information because current actions and notes are withheld. Bootstrap interpolation, inclusive sign-flip tails, contrast direction, and HIT-first classification match the design. In-memory checks passed 64 payoff cases and screening boundary examples.

**Acknowledged limitations:** five exploratory blocks; bundled wording/schema/attention effects; adverse approvals do not establish agreement; structural plain-arm report zeros are not comparable reporting propensities; provider execution, complete effective configuration, tool non-use, and sampling controls remain unattested.

Read all nine requested files. No edits or live model calls. The full suite was not run because it writes temporary artifacts; no completed S34 live archive was available to validate.