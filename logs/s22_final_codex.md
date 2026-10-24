S22’s **DUD verdict is correct**. I found no material economics, arithmetic, information-flow or screening error. No files were edited and no live model calls were made.

Independent recomputation from raw game reviews confirmed:

- Partner TYPE-Y approvals, certain/lottery by seed: **1/1, 0/0, 0/1, 2/0, 0/1**. Both arms total **3/40**; paired difference **0**.
- All **3,125 ordered bootstrap samples for each of 30 summaries** reproduce the stored bounds. Primary bounds: **[-0.125, 0.100]**; paired t interval **[-0.190090, 0.190090]**.
- All **32 sign flips per metric**, including all three tails, agree. Primary upper p **0.625**, two-sided p **1**.
- The frozen rule yields **DUD** through both mean ≤0.05 and bootstrap upper <0.25. The positive expected-bonus gate, **3/20**, cannot override that verdict.

Audit draws, balanced authoritative types, every realized charge and all bonus arithmetic match independent reconstruction. In rounds 3–10, certain has **10 adverse approvals/30 charge points**; lottery has **11/12**. Mean pair/outsider realized bonuses per round are **15.150/6.850** versus **15.300/7.325**. Expected-charge bonuses are **15.150/6.850** versus **15.300/6.800**. Expected reviewer payoff is correctly **−2** in both arms.

All **300 request histories**, current statuses and **200 pair-note snapshots** preserve simultaneous information availability. Cache hashes and accepted actions agree; exhaustive cache-only replay and exports pass. All **20 source hashes** match current files and the registration commit. Environment, dispatch receipt, runtime gate, overlapping matched games and block barriers validate. REPORT.md accurately presents the directional, exploratory result without promoting secondaries or claiming equivalence.

Two low-severity issues remain:

- **Literal no-write contract mismatch:** completed resume opens `.writer.lock` with mode `w` before entering its read-only branch ([enforcement.py](/home/factory/collusion/collusion-serendipity/sim/enforcement.py:317)). This truncates the lock file; release verification explicitly excludes it. Scientific evidence is unaffected. Remedy: document the lock-file exception in a supplement, or provide a versioned truly read-only entry point.
- **Incomplete final disposition record:** [review dispositions](/home/factory/collusion/collusion-serendipity/logs/s22_review_disposition.md:41) still says final outcomes/reviews are pending. Remedy: append final review dispositions and outstanding verification status before declaring release complete.

Acknowledged limitations remain distinct from bugs: five exploratory blocks, uncontrolled sampling/service interference, sign-flip assumptions, bundled risk/wording/history, unequal realized sanctions, mechanically related bonus gate and unverified agreement or intent.

Unchecked here: failure-injection tests were inspected but not rerun; clean-clone reproduction, figure inspection and provider execution were not independently verified.