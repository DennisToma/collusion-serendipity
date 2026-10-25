# Serendipity log — Beyond Words

2026-10-25 · Iteration 23 (in progress) · **No hits promoted.** Exploratory pilots; zero tuning attempts.

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
| S19 · own, neutral labels | 10 games / 5 blocks. Partner negative-type approval rate r3–10: normative **0.000**, neutral **0.075**; difference **0.075 [0.025, 0.125]**. | **DUD** for directional screen |
| S21 · E, action/explanation audit | 10 selected S19 cases / 5 source blocks; 30 gpt-6.1-sol calls. Confident errors actions **0/10**, both **0/10**; difference **+0.000 [+0.000, +0.000]**. | **DUD** for factual-audit screen |
| S22 · D, stochastic enforcement | 10 games / 5 blocks. Partner TYPE-Y approval rate r3–10: certain **0.075**, lottery **0.075**; difference **0.000 [-0.125, 0.100]**. | **DUD** for directional screen |
| S24 · F, team identity | 10 games / 5 blocks. Partner TYPE-Y approval rate r3–10: human **0.025**, AI **0.025**; difference **0.000 [-0.075, 0.075]**. | **DUD** for directional screen |
| S25 · own, output field order | 10 selected S19 histories / 5 blocks; 20 fresh decisions. Adverse target approvals action-first **0/10**, reason-first **0/10**; difference **+0.000 [+0.000, +0.000]**. | **DUD** for one-sided format screen |
| S27 · B, team concentration | 10 games /5 blocks. Partner Y approval rate r3–10: three **0.075**, two **0.250**; difference **0.175 [0.075, 0.300]**. | **ODD** for directional screen |
| S29 · C, partner notepad | 10 games /5 blocks. Partner Y approval rate r3–10: self **0.050**, shared **0.375**; difference **0.325 [0.100, 0.575]**. | **ODD** for directional screen |
| S28 · own, role payoff table | 10 games /5 blocks. Partner Y approval rate r3–10: prose **0.175**, table **0.075**; prose−table **0.100 [-0.050, 0.275]**. | **ODD** for reduction screen |
| S31 · A2, labor duopsony | 10 games /5 blocks. Worker earnings r3–10: self **10.000**, shared **10.000**; self−shared **0.000 [0.000, 0.000]** (degenerate). | **DUD** for wage-reduction screen |
| S32 · own, resource identity | 10 games /5 blocks. Paid rate r3–10: human **17.525**, compute **13.725**; human−compute **+3.800 [-0.250, 7.875]**. | **ODD** for directional framing screen |
| S33 · D, reporting/amnesty | 10 games /5 blocks. Partner Y approval rate r3–10: baseline **0.250**, amnesty **0.300**; reduction **-0.050 [-0.175, 0.050]**. | **DUD** for reduction screen |
| S34 · own, inert report field | 10 games /5 blocks. Partner Y approval rate r3–10: plain **0.200**, flag **0.175**; reduction **0.025 [-0.100, 0.150]**. | **DUD** for reduction screen |
| S35 · B, productivity asymmetry | Registered: ten fresh labor games, productivity20/30 versus20/20; self-only notes. No live outcomes yet. | **PENDING** |

S25 uses a deliberately enriched fixed-history challenge. Source approvals only select cases; the comparison uses fresh outputs in both arms. Neither fresh arm reproduced any of the four archived adverse approvals used to enrich the challenge. With no adverse baseline in the fresh action-first arm, this pilot cannot demonstrate an output-order correction mechanism. The common extra order instruction and fresh model draws also differ from S19; their effects are not separated here.

<!-- S34 summary start -->
**S34:** paired t95% **[-0.177, 0.227]**, upper sign-flip **p=0.50000**. Stage payoffs identical; added wording plus output field,shared notes both arms. No isolated schema,attention or collusion claim. [All outcomes and figure](results/s34_summary.md).
<!-- S34 summary end -->

With S34 plain baseline20%,the largest possible observed reduction is20 percentage points,below the25-point HIT screen. Both DUD clauses apply;all80 primary flag decisions set report=false. The contrast concerns adding the offered option;no equivalence or isolated reporting-mechanism result.

<!-- S33 summary start -->
**S33:** the reporting/amnesty package remained DUD;29 primary request flags triggered no extra charges or waivers,while one warmup report qualified. [Exposure diagnostic](results/s33_reporting_diagnostic.json) is post-outcome;no isolated deterrence or backfire claim.
<!-- S33 summary end -->

Five paired game blocks are the resampling unit unless stated otherwise; intervals are descriptive empirical bootstrap bounds. With n5 they can degenerate, and sign/t intervals may disagree. No multiplicity correction, held-out validation or equivalence claims. Actions, private notes and high rewards alone do not verify an agreement or profitable collusion. Earlier pilots did not freeze the Codex binary/configuration; S32 fingerprints known local inputs but its mutable expected-baseline field leaves transient coordinated drift unexcluded. S33/S34 use immutable closure baselines plus completion checks; complete effective configuration and provider execution remain unattested.

Cournot: three integer-output firms, P=max(0,30−total output), cost6, symmetric static Nash q6. Workplace: synthetic fixed work types and personal bonus incentives; no realistic task production. Identity/wording, uncontrolled model draws and shared-service interference limit transfer. Procurement ties are divisible.

**Earlier caveats:** S01 digits cannot identify coding; S02 echoed own notes; S04 fails its exposure gate; S03/S11 dynamics depend on timing/window phase; S07 is driven by one block; S09 removes incoming information as well as memory; S16 is an operational failure with no effect estimate. S19 adverse JSON actions can contradict explanations; S21's action-aware auditor correctly reads the selected challenge cases. No sibling headline change.

S29 remains ODD because one of five blocks ties;the bootstrap-positive interval alone does not satisfy the registered screen. [Post-outcome transparency appendix](results/s29_action_text.md) lists all adverse decisions and infers no intent.

[All methods, outcomes, earlier uncertainty and figures](REPORT_DETAILS.md) · [S19 adverse actions](results/s19_action_text.md) · [S21 audit](results/s21_summary.md) · [Reproduction](README.md) · [Unpromoted handoffs](HITS.md).

**Next:** Complete S35 productivity-asymmetry pilot with frozen four-unit wage screen; S32 remains unconfirmed and S30 unrun.
