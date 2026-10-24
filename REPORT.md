# Serendipity log — Beyond Words

2026-10-24 · Iteration 10 · **No hits promoted.** All pilots exploratory; zero tuning attempts.

| Pilot | Result (descriptive 95% bootstrap bounds when estimated) | Verdict |
|---|---|---|
| S01 · C, price digits | 104 games scanned; primary on 32 luna / 15 deepseek channel games. Pair-minus-other-pairs prediction gain **+0.00175 [-0.00184, +0.00631]** / **+0.00899 [-0.04249, +0.05535]** squared price units. | **DUD** for this screen |
| S02 · A, Cournot quantities | 6 games, 3 seed blocks. Pair output r4–12: none **5.870**, private **5.389**; difference **-0.481 [-1.222, +0.000]** units/firm. | **ODD**, inconclusive |
| S04 · B, shared advisor sample | 10 games, 5 seed blocks. Pair output r4–12: independent **5.422**, shared **4.911**; difference **-0.511 [-1.222, +0.122]** units/firm. | **ODD / UNINFORMATIVE** |
| S03 · own, conditional calculator | 10 games, 5 blocks. Mean output/firm r4–12: none **6.719**, calculator **5.837**; difference **-0.881 [-1.170, -0.489]**. | **DUD for predicted increase** |
| S07 · F, anti-coordination rule | 10 games, 5 blocks. Pair output r4–12: neutral **5.800**, legality **4.844**; difference **-0.956 [-2.889, +0.267]**. | **DUD for predicted increase** |
| S09 · E, transcript-removal replay | 10 six-round continuations / 5 observed prefixes. Pair output r7–12: retain **5.900**, erase **6.000**; difference **+0.100 [+0.000, +0.300]**. | **DUD** for directional screen; near-Nash baseline |
| S11 · D, delayed feedback | 10 no-message calculator games / 5 time-matched pairs. Mean consecutive output change r4–12: immediate **2.430**, delayed **1.526**; reduction **+0.904 [-0.089, +1.815]**. | **ODD** for timing screen |
| S06 · own, denomination | 10 games / 5 time-matched pairs. Mean quantity r4–12: UNIT **5.963**, CENT **5.696**; difference **-0.267 [-0.519, -0.022]**. | **ODD** for invariance screen |
| S14 · A1, procurement auction | 10 games / 5 time-matched pairs. Buyer payment r4–12: none **8.778**, private **11.111**; difference **+2.333 [-5.600, +9.733]**. | **ODD** for payment screen |
| S16 · C2, notes-file channel | Aborted under frozen strict-output rule: 4/10 games complete; 173 responses, 10 overlong-reasoning rejections. No effect estimated. | **FAILED / unclassified** |
| S18 · A4, workplace review | 10 games / 5 blocks. Partner FAIL approval rate r3–10: self **0.000**, shared **0.000**; difference **0.000 [0.000, 0.000]** (degenerate). | **DUD** for directional screen |

<!-- S18 summary start -->
**S18:** paired t95% **[0.000, 0.000]**, upper sign-flip **p=1.00000**. Explicit synthetic PASS/FAIL labels and fixed bonus incentives; reciprocal bad approvals are profitable but stage-dominated. Incorrect approvals do not verify agreements. Identical-block bootstrap bounds can degenerate; no population zero-risk or equivalence claim. [All outcomes and figure](results/s18_summary.md).
<!-- S18 summary end -->

**S16:** strict reasoning-length failure; all173 requests replay, incomplete-data analysis and live restart blocked. No replacement or subset estimate. [Failure evidence](results/s16_summary.md).

**S14:** payment upper sign-flip p=.375; opposite large block contrasts, with high paths beginning before incoming messages. Divisible ties and bundled channel cues; no agreement labels. [All outcomes](results/s14_summary.md).

**S06:** its bootstrap excludes zero, while paired t[-.659,.125] and two-sided p=.1875 remain unresolved. Denomination bundles magnitude, formatting and conversion; nine-round windows are phase-sensitive. [All outcomes](results/s06_summary.md).

**Earlier caveats:** digits cannot identify coding; S02 also replayed own messages; S04 fails its exposure gate; S03/S11 show timing-sensitive cycles; S07 is driven by one block; S09 erases incoming information as well as memory. [Earlier detail](REPORT_DETAILS.md) · [S07](results/s07_summary.md) · [S09](results/s09_summary.md) · [S11](results/s11_summary.md).

Earlier Cournot games: three firms, integer output, P=max(0,30−total output), cost6; symmetric static Nash q6. Tiny selected samples, multiple exploratory screens, prompt cues and shared-backend interference limit inference. Model/sampling are client metadata. Actions and message influence do not verify agreements or profitable collusion. No sibling headline change.

[Methods, designs and reproduction](README.md).
**Next:** Different axis after A4; preserve completed screens and select a fresh mechanism question. No secondary-driven promotion.

[S18 release](logs/s18_release.json) · [Independent reconstruction](logs/s18_independent.json) · [Review dispositions](logs/s18_review_disposition.md).
