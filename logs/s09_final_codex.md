S09’s **DUD verdict and numerical claims check out**. No remaining implementation or statistical bug was confirmed.

One minor **claim-scope issue** remains: “memory erasure” includes withholding previously unread messages. Source-round-6 messages first enter decision prompts in round 7, but `erase` removes them alongside the previously seen rounds1–5 transcript. Thus even the round7 contrast bundles forgetting with loss of incoming information. This follows the registered intervention; descriptions of a “causal-memory” effect should make that distinction explicit. See [erasure filter](/home/factory/collusion/collusion-serendipity/sim/replay.py:116), [delivery timing](/home/factory/collusion/collusion-serendipity/sim/replay.py:145), and [claim wording](/home/factory/collusion/collusion-serendipity/DESIGN_S09.md:49).

Independent recalculation from the raw games reproduced:

- Primary block differences: `[0, 0.5, 0, 0, 0]`; mean **+0.100**, bootstrap95% **[0, 0.300]**, t95% **[-0.177645, 0.377645]**, exact upper p **0.5**.
- Round7 difference **+0.200 [0, 0.600]**; outsider round7 differences all zero.
- Pair-profit difference **−0.200** and message-word difference **−6.166667**.
- All **210 metric cells, 22 bootstrap intervals, and seven t intervals** matched. The exact decision rules correctly return DUD.

Treatment and provenance checks passed: stored prompts preserve identical initial public histories, exclude current-round information, and deliver continuation messages from round8. Source, registration, and release hashes match; all 183 cached requests map uniquely to 180 accepted decisions plus three retain retries. Recorded calls follow registration push and finish before cutoff. Earlier guarded issues are not remaining findings.

**Acknowledged limitations:** five previously observed prefixes; fragile intervals and conditional sign-flip assumptions; uncontrolled sampling and unattested isolation; bundled inbox cues and semantics; retained public-history effects and later message repair. These prevent equivalence, original-channel-effect, mechanism, or collusion conclusions. Current reporting generally respects those limits.

No edits or live model calls were made.