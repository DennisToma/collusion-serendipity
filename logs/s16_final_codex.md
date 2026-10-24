S16’s **failed-pilot conclusion is supported**. No scientific effect estimate is admissible. ODD is an operational queue label; the registered scientific decision rule was never evaluated.

Two remaining low-severity audit bugs were reproduced using **in-memory mutations only**:

- **Complete-game timestamps escape validation.** The failure auditor removes `started_utc` and `ended_utc` before metadata comparison, without independently checking their bounds. An impossible start in 2099 and end in 1900 still passed. “All rows/metadata” therefore overstates verification. [Code](/home/factory/collusion/collusion-serendipity/scripts/s16_failure_audit.py:182)
- **Post-abort call starts escape validation.** Calls completing after failure are collected without asserting they started beforehand. Moving the retained self/B call’s start to `19:48:05`, after the `19:48:04.723876` failure record, and updating its response hash still passed. [Code](/home/factory/collusion/collusion-serendipity/scripts/s16_failure_audit.py:99)

These are validator gaps. **The actual saved timestamps satisfy both properties**; I found no corresponding execution violation.

Independent recalculation confirmed:

- **10 planned, 6 started, 4 complete, 2 failed/partner-aborted, 4 unstarted.**
- **173 responses = 163 accepted + 10 rejected.** Every rejection had valid bid/note fields and reasoning over 40 words; fatal attempts were **47/44/46 words**.
- **173 public histories, 116 note snapshots**, and exact consumption of every cached key once. Four complete games and both failed prefixes reproduced.
- All **16 scientific sources** match registration `73fe09d`; latest failure JSON and release hashes agree.
- Static economics: **3,375 profiles, 44 pure Nash equilibria, payments {6,7}**.

Treatment timing is correct: visibility wording differs from round 1; partner content arrives from round 2; current-round bids/notes remain hidden. Analysis and live continuation fail closed. I calculated no treatment-effect statistics.

Acknowledged limitations remain separate: bundled wording/content/context/endogenous writing, shared-service interference, client-only provenance attestation, tiny exploratory scope, logical snapshots rather than filesystem-tool capability, and no verified agreement labels. The failure cannot establish an access effect or an arm-specific failure propensity. Clean-clone reproduction remains explicitly pending until artifacts are committed.

No files edited or live model calls made.