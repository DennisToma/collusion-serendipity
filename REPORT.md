# Serendipity log — Beyond Words

2026-10-24 · Iteration 8 · **No hits promoted.** All pilots exploratory; zero tuning attempts.

| Pilot | Result (descriptive 95% bootstrap bounds) | Verdict |
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

**S14:** payment t95% **[-10.574, +15.240]**, upper sign-flip **p=0.37500**. Pair-profit **+0.800**, outsider-profit **+1.533** (secondary, unresolved). Opposite large block contrasts; high paths begin before incoming messages in either arm. Third bidder is uninformed about the box. Static pure-Nash payments {6,7}; divisible ties, bundled role/prompt cues, unverified agreements. [All outcomes and figure](results/s14_summary.md).

**S06:** all displayed prices/profits and conditional tables scale100x, with explicit conversion and identical real incentives. CENT−UNIT quantity: paired t95% **[-0.659, 0.125]**, two-sided sign-flip **p=0.1875**. The registered .10 queue threshold allows the n5 minimum p=.0625; this is exploratory. The bootstrap excludes zero while the t interval and sign screen do not resolve a mean shift; ODD is retained. The odd nine-round window is phase-sensitive, with all-round arm means near Nash. Denomination bundles magnitude, formatting and numeric conversion cue in calculator-assisted games. No equivalence or collusion claim. [All outcomes and figure](results/s06_summary.md).

**Earlier caveats:** S11 compares delayed feedback including own recall/warmup; slower consecutive changes do not establish convergence or reduced collusion. [S11 details](results/s11_summary.md). S01 digits are deterministic functions of exact prices; its linear screen cannot identify coding. S02 n3 is inconclusive and also replayed own sent messages. S04 fails its routable-exposure gate (17.8%<25%, a screening convention, not calibrated power). S03 is phase-sensitive cycling from above-Nash controls. S07 is dominated by one low-output block, and rule wording and channel use remain bundled. S09 removes incoming round6 information as well as older message history; public imprint and future renegotiation remain, with previously observed prefixes. [Earlier detail](REPORT_DETAILS.md) · [S07](results/s07_summary.md) · [S09](results/s09_summary.md).

Earlier Cournot markets have three firms, integer output, P=max(0,30-total output), cost6; symmetric static Nash q6, P12, profit36. S09 has only six new rounds per continuation; source prefix is context. No verified agreement/execution labels; quantity, message influence and profitable coordination are distinct. Tiny samples, exploratory selection, multiple pilots and shared-backend interference limit inference. Model labels are client metadata; sampling/temperature and OS isolation are not independently attested. No sibling headline change.

[Design S01/S02](DESIGN.md) · [S03](DESIGN_S03.md) · [S04](DESIGN_S04.md) · [S07](DESIGN_S07.md) · [S09](DESIGN_S09.md) · [S11](DESIGN_S11.md) · [S06](DESIGN_S06.md) · [Reproduce](README.md).
**Next:** Choose a different axis after S14; keep checkpoint artifacts current. No secondary-driven promotion.

[S14 release](logs/s14_release.json) · [Independent reconstruction](logs/s14_independent.json) · [Review dispositions](logs/s14_review_disposition.md) · [S06 verification](logs/s06_release.json).
