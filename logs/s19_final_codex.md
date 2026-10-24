S19’s frozen **DUD verdict is correct**. No result-changing arithmetic, economics, information-flow, or replay bug found.

I independently reconstructed the primary from raw game review decisions:

- Normative: **0/40**; neutral: **3/40**.
- Paired differences: **[0, 0, ⅛, ⅛, ⅛]**; mean **0.075**.
- All **3,125** ordered bootstrap samples: exact bounds **[1/40, 1/8] = [0.025, 0.125]**.
- All **32** inclusive sign flips: upper **p=0.125**.
- Paired t95%: **[-0.010011, 0.160011]**.
- Pair-bonus gate: **+7/20 points/round**.

DUD follows because bootstrap upper **0.125 < 0.25**. The positive bootstrap interval does not satisfy the frozen HIT rule.

Full offline analysis reproduced the saved result. Independent reconstruction passed all **80 metric cells, 24 bootstrap intervals, 24 t intervals, 24 sign-tail checks, 300 request histories, and 200 note snapshots**. Source hashes matched the registration commit. Complete-key replay, exports, chronology, and environment validation passed; archive bytes remained unchanged. Seven tests requiring no file writes passed, including exhaustive stage economics and information timing.

One concrete **medium-severity release gap** remains: the design requires clean-clone reproduction, but `logs/s19_clean_clone.json` is absent and S19 data/results are currently untracked. The [clean-clone procedure](/home/factory/collusion/collusion-serendipity/scripts/s19_release.py:42) clones committed HEAD, so the current archive is unavailable there. Remedy: commit the complete archive and publication artifacts, then run and retain clean-clone reproduction before declaring release complete. This does not invalidate the computed result.

Acknowledged limitations remain appropriately scoped: five selected exploratory blocks; bundled semantic framing and fixed X/Y ordering; uncontrolled draws and shared-service interference; conditional sign-flip assumptions; client-reported model/sampling metadata; cancellation races; and no identification of intent, agreement, partner-specific targeting, equivalence, or population zero risk. REPORT’s S19 claims respect these limits.

Unchecked here: clean-clone execution, figure regeneration, and filesystem-writing failure regressions. No edits or live model calls were made; earlier pilots were not reviewed.