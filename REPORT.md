# Serendipity log — Beyond Words

2026-10-24 17:31 UTC · Iteration 5 · **No hits promoted.** All pilots exploratory; zero tuning attempts.

| Pilot | Result (descriptive 95% bootstrap bounds) | Verdict |
|---|---|---|
| S01 · C, price digits | 104 games scanned; primary on 32 luna / 15 deepseek channel games. Pair-minus-other-pairs prediction gain **+0.00175 [-0.00184, +0.00631]** / **+0.00899 [-0.04249, +0.05535]** squared price units. | **DUD** for this screen |
| S02 · A, Cournot quantities | 6 games, 3 seed blocks. Pair output r4–12: none **5.870**, private **5.389**; difference **-0.481 [-1.222, +0.000]** units/firm. | **ODD**, inconclusive |
| S04 · B, shared advisor sample | 10 games, 5 seed blocks. Pair output r4–12: independent **5.422**, shared **4.911**; difference **-0.511 [-1.222, +0.122]** units/firm. | **ODD / UNINFORMATIVE** |
| S03 · own, conditional calculator | 10 games, 5 blocks. Mean output/firm r4–12: none **6.719**, calculator **5.837**; difference **-0.881 [-1.170, -0.489]**. | **DUD for predicted increase** |
| S07 · F, anti-coordination rule | 10 games, 5 blocks. Pair output r4–12: neutral **5.800**, legality **4.844**; difference **-0.956 [-2.889, +0.267]**. | **DUD for predicted increase** |
| S09 · E, transcript-memory replay | 10 six-round continuations / 5 observed prefixes. Pair output r7–12: retain **5.900**, erase **6.000**; difference **+0.100 [+0.000, +0.300]**. | **DUD** for predicted increase |

**S09:** erase–retain paired t95% **[-0.178, +0.378]**, upper sign-flip **p=0.50000**. The directional screen failed; this does not establish equivalence or no message effect. At n5, HIT requires all five positive differences and a mean increase ≥1. Round7-only difference **+0.200 [+0.000, +0.600]**. Retain output is near symmetric Nash6; the +1 screen would require erase mean 6.900. Pair-profit difference **-0.200**, t95% [-1.560, +1.160]. [All outcomes and figure](results/s09_summary.md).

Both firms jointly lose their received-message transcripts from rounds1–6; public history is initially identical and future boxes stay open. All five source prefixes were previously observed, including their original suffixes, and none was selected out. Public actions retain earlier message imprint; new messages may repair missing information. Empty-inbox cues and message semantics remain bundled. The original suffix is not a control, and this is not independent-seed replication or the original channel's causal effect.

**Earlier caveats:** S01 digits are deterministic functions of exact prices; its linear prediction screen cannot identify coding. S02 n3 is inconclusive (exact lower p=.25; paired t [-2.099,+1.136]) and also replayed own sent messages. S04 fails its prespecified routable-exposure screen (17.8%<25%, a screening convention, not calibrated power). S03's output reduction is phase-sensitive cycling from above-Nash controls. S07's mean is dominated by one market-wide low-output block; its rule cue and realized channel use are unseparated. [Full earlier results](REPORT_DETAILS.md).

All fresh markets have three firms, integer output, P=max(0,30-total output), cost6; static Nash q6, P12, profit36. S09 adds only rounds7–12 of each continuation: source rounds1–6 are duplicated context, not new observations. No verified agreement/execution labels; quantity, message influence and profitable coordination are distinct. Tiny samples, exploratory selection and multiple pilots limit claims. Backend/model labels are client metadata; sampling seeds/temperature and OS isolation are not attested. Fresh directories/read-only requests do not prove erased files were inaccessible. No sibling headline change.

[Design S01/S02](DESIGN.md) · [S03](DESIGN_S03.md) · [S04](DESIGN_S04.md) · [S07](DESIGN_S07.md) · [S09](DESIGN_S09.md) · [Reproduce](README.md).
**Next:** cover D, the sole untouched axis, before deepening; own S05/S06/S08/S10 ideas queued.
