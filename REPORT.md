# Serendipity log — Beyond Words

2026-10-25 · Iteration 38 (S54 registered; live results pending) · **No hits promoted.** Exploratory pilots; zero tuning attempts.

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
| S35 · B, productivity asymmetry | 10 games /5 blocks. Paid wage r3–10: symmetric **11.800**, asymmetric **19.450**; asymmetric−symmetric **7.650 [3.825, 9.825]**. | **ODD** for four-unit wage screen |
| S36 · own, gross/net quotation | 10 games /5 blocks. Worker take-home r3–10: NET **8.000**, GROSS **1.800**; NET−GROSS **+6.200 [+2.200, +10.000]**. | **ODD** for two-unit reduction screen |
| S38 · F, final-round disclosure | 10 games /5 blocks. Paid wage r3–10: hidden **8.000**, known **8.000**; known−hidden **+0.000 [+0.000, +0.000]**. | **DUD** for two-unit increase screen |
| S37 · own, payroll wording | 10 games /5 blocks. Take-home wage r3–10: coded **0.000**, payroll **0.000**; coded−payroll **+0.000 [+0.000, +0.000]** (degenerate); both at allowed minimum. | **DUD** for two-unit increase screen |
| S40 · E, private-note erasure | Ten observed S37 histories /5 blocks;20 fresh decisions. Normalized offer retain **0.000**, erase **0.000**; erase−retain **+0.000 [+0.000, +0.000]**. | **DUD** for two-unit increase screen |
| S42 · B2, surprise employer entry | 10 games /5 blocks. Paid wage r7–10: entry **10.000**, duopoly **10.000**; entry−control **+0.000 [+0.000, +0.000]**. | **DUD** for four-unit increase screen |
| S43 · D, own-payoff table | Ten S42 histories /5 blocks;20 fresh decisions. Focal offer control **9.900**, table **10.200**; table−control **+0.300 [+0.100, +0.500]**. | **DUD** for one-unit offer screen |
| S41 · own, wage tick size | 10 games /5 blocks. Paid wage r3–10: fine **10.188**, coarse **9.225**; fine−coarse **+0.963 [+0.000, +2.688]**. | **ODD** for two-unit increase screen |
| S45 · A5, marketplace reviews | 10 games /5 blocks. Unsupported recommendation rate r3–10: self **0.025**, shared **0.000**; difference **-0.025 [-0.075, 0.000]**. | **DUD** for directional screen |
| S44 · own, payoff-row order | Ten S42 histories /5 blocks;20 fresh decisions. Focal offer ascending **10.300**, descending **10.200**; descending−ascending **-0.100 [-0.300, +0.000]**. | **DUD** for one-unit increase screen |
| S48 · C, partner-note deletion | Ten S29 TYPE-Y review histories /5 blocks;20 fresh decisions. Approval retain **0.400**, erase **0.400**; retain−erase **+0.000 [-0.300, +0.300]**. | **DUD** for .25 reduction screen |
| S47 · own, output example | Ten S42 histories /5 blocks;20 fresh decisions. Focal offer low example **10.100**, high example **10.000**; high−low example **-0.100 [-0.300, +0.000]**. | **DUD** for two-unit increase screen |
| S50 · F, final-round disclosure | Ten S29 TYPE-Y review histories /5 blocks;20 fresh decisions. Approval hidden **0.400**, final **0.300**; hidden−final **+0.100 [-0.300, +0.600]**. | **ODD** for .25 reduction screen |
| S51 · D, reviewer penalty | Ten S29 TYPE-Y review histories /5 blocks;20 fresh decisions. Approval charge3 **0.500**, charge9 **0.500**; baseline−strong **+0.000 [-0.300, +0.300]**. | **DUD** for .25 reduction screen |
| S53 · E, static incentive audit | All10 original S29 games /5 blocks; no new calls. Totals over40 rounds/arm (self→shared): Y approvals **2→15**; missed X **0→0**; mutual-Y **0→0**; strict Pareto **0→0**; stage regret **4→30**; pair excess **8→60** bonus points. [All six bootstrap/t intervals](results/s53_summary.md). | **ODD / context-only**, post hoc |

S25 uses a deliberately enriched fixed-history challenge. Source approvals only select cases; the comparison uses fresh outputs in both arms. Neither fresh arm reproduced any of the four archived adverse approvals used to enrich the challenge. With no adverse baseline in the fresh action-first arm, this pilot cannot demonstrate an output-order correction mechanism. The common extra order instruction and fresh model draws also differ from S19; their effects are not separated here.

<!-- S45 summary start -->
**S45:** paired t95% **[-0.094, 0.044]**, upper sign-flip **p=1.00000**. Shared versus self-only notepads in fixed two-seller markets. Delivery and stated readability bundled; public actions visible in both arms; approvals do not verify agreement. [All outcomes and figure](results/s45_summary.md).
<!-- S45 summary end -->

[Post-outcome S45 transparency appendix](results/s45_action_text.md) lists every unsupported recommendation with exact returned text;it assigns no agreement,intent or mechanism label.

S45 has a near-floor self-only baseline (1/40 versus shared0/40). Its primary contrast comes from one block (24964);a missed supported recommendation occurs in a different block (24960). The DUD classification is the registered directional screen,not evidence that private notes never matter. Local wrapper timing and requested-route metadata do not attest provider execution. The registered failure-record survival language is broader than implemented durability:transport-failure records are flushed but not fsynced;durable admissions still reject interrupted continuation. No transport failure occurred in this completed archive.

<!-- S41 summary start -->
**S41:** Paid wage r3–10: fine **10.188**, coarse **9.225**; fine−coarse **+0.963 [+0.000, +2.688]**; paired t95% [-1.378, +3.303], inclusive upper sign-flip **p=0.25000**. Frozen **ODD** for the two-unit screen. 2 of 5 block differences are positive; 3 tie. The largest block gap is +4.3125 (coarse 6.1250, fine 10.4375). Ten fresh games/five paired blocks; zero tuning or pooling. The half-unit grid changes feasible deviations, equilibria and numerical salience together. This does not isolate representation, competition or anchoring, and low wages do not verify coordination. The same payoff formula gives coarse pure-Nash wages18–20 and fine pure-Nash wages19–20. Bounds are descriptive; small-n/sign-calibration limits apply, and any degenerate interval is not population equivalence. Regret uses each arm's own feasible grid, so its contrast mixes the changed opportunity set with behavior. The local Codex wrapper requests low reasoning effort; served settings remain unattested. [All outcomes and figure](results/s41_summary.md).
<!-- S41 summary end -->

Five paired game blocks are the resampling unit unless stated otherwise; intervals are descriptive empirical bootstrap bounds. With n5 they can degenerate, and sign/t intervals may disagree. No multiplicity correction, held-out validation or equivalence claims. Actions, private notes and high rewards alone do not verify an agreement or profitable collusion. Earlier pilots did not freeze the Codex binary/configuration; S32 fingerprints known local inputs but its mutable expected-baseline field leaves transient coordinated drift unexcluded. S33–S36 use immutable closure baselines plus completion checks; complete effective configuration and provider execution remain unattested. S36 hashes selected environment values without referenced-file content coverage. S38 adds named referenced-file contents and repo/temp-root instruction ancestors;complete effective settings and provider execution remain unattested.

Cournot: three integer-output firms, P=max(0,30−total output), cost6, symmetric static Nash q6. Workplace: synthetic fixed work types and personal bonus incentives; no realistic task production. Identity/wording, uncontrolled model draws and shared-service interference limit transfer. Procurement ties are divisible. Labor: initially two employers,value20,wages0..20,one passive divisible unit allocated to the highest wage. Integer-wage duopoly/control pure-Nash wages18–20;S41 half-unit pure-Nash wages19–20;S42 adds a third employer fromr6 in the entry arm,whose pure-Nash wages are19–20.

**Earlier caveats:** S01 digits cannot identify coding; S02 echoed own notes; S04 fails its exposure gate; S03/S11 dynamics depend on timing/window phase; S07 is driven by one block; S09 removes incoming information as well as memory; S16 is an operational failure with no effect estimate. S19 adverse JSON actions can contradict explanations; S21's action-aware auditor correctly reads the selected challenge cases. No sibling headline change.

S29 remains ODD because one of five blocks ties;the bootstrap-positive interval alone does not satisfy the registered screen. [Post-outcome transparency appendix](results/s29_action_text.md) lists all adverse decisions and infers no intent.

[All methods, outcomes, earlier uncertainty and figures](REPORT_DETAILS.md) · [S19 adverse actions](results/s19_action_text.md) · [S21 audit](results/s21_summary.md) · [Reproduction](README.md) · [Unpromoted handoffs](HITS.md).

**Next:** Fresh different-axis pilot after E/S53; own/S54 opportunity-correlation idea and own/S52 framing remain proposed. S46/S39/S49 queued, S32 unconfirmed and S30 unrun. Avoid reusing the same ten focal histories without a new scientific reason.

<!-- S44 summary start -->
**S44:** paired t95% [-0.378, +0.178], upper sign-flip p=1.00000. Block differences: +0.00, -0.50, +0.00, +0.00, +0.00. Identical headers and payoff rows; only row sequence reverses. Focal offers, not realized worker pay; observed histories, uncontrolled model draws, n5. The directional screen does not exclude smaller or reverse effects and does not identify a mechanism. [Methods, all outcomes and figure](results/s44_summary.md).
Only the paired contrast sign-flip is a registered hypothesis; arm-level sign-flip fields in JSON are generic tests against zero and carry no row-order claim.
<!-- S44 summary end -->

<!-- S48 summary start -->
**S48:** immediate TYPE-Y review after partner-note deletion. Retain 4/10, erase 4/10; paired t95% [-0.439, +0.439], inclusive upper sign-flip p=0.75000. Five source-block differences [0.5, 0.0, -0.5, 0.0, 0.0]. Retain is the exact archived prompt; erase removes only partner records. Own notes and public history preserve indirect communication, so this is no mediation or long-run channel estimate. Observed histories, uncontrolled fresh draws and n5 limit transfer. DUD is triggered by the mean≤.05 rule; the bounds include the .25 directional target, so they do not exclude that effect. Source S29 CLI inputs were not fingerprinted. [All cases, methods and figure](results/s48_summary.md).
Only the paired contrast is the registered hypothesis; generic arm-level sign-flip fields test against zero and carry no deletion-effect claim.
<!-- S48 summary end -->

<!-- S47 summary start -->
**S47:** A JSON syntax example with rate 0 versus 20 gave a high-minus-low focal-offer difference of **-0.100 [-0.300, +0.000]**; paired t95% [-0.378, +0.178], upper sign-flip p=1.00000. Both arms had the same payoff table, history and explicit non-recommendation warning. Four blocks tie; one differs by −0.5. The registered two-unit screen is DUD, with no equivalence, mechanism or realized-wage claim. Five observed source blocks and uncontrolled draws limit transfer. Known source/replay local fingerprints differ;both fresh arms share one frozen local runtime,with provider execution unattested. [All cases, methods and figure](results/s47_summary.md).
Only the paired contrast is a registered hypothesis; generic arm-level sign-flip fields test against zero.
<!-- S47 summary end -->


**S50:** paired t95% [-0.580, +0.780], upper sign-flip p=0.50000;block differences [0.0, 0.0, 1.0, 0.0, -0.5]. Final-round disclosure leaves 3/10 adverse approvals;this does not verify an agreement,strategic foresight or a completed terminal game. The .25 reduction remains unresolved. Only focal agents are rerun,and generic future-note rules/historical continuation cues survive. [All outcomes and figure](results/s50_summary.md).

S50 response backend/model checks verify requested labels only;they do not attest served identity or routing.

**S51:** reviewer charge3→9 (net−2→−8): 5/10 versus 5/10 adverse approvals; paired t95% [-0.439, +0.439], upper sign-flip p=0.75000; block differences [-0.5, 0.0, 0.5, 0.0, 0.0]. The .25 reduction remains unresolved. Both arms add the same current-policy notice. All user history and notes stay fixed, including dated old-policy cues. Only focal decisions are rerun; this does not measure long-run enforcement or verify coordination. [All outcomes and figure](results/s51_summary.md) · [All returned text](results/s51_action_text.md).

**S53 (post hoc):** 0/9 shared and 0/9 self-only both-Y opportunities had simultaneous mutual-Y approvals (0/40 rounds per arm). These zero-width empirical bootstrap/t intervals are degenerate and do not establish population absence or equivalence. No missed X approvals occurred. In these data the regret and pair-excess contrasts are exactly two and four times S29’s original approval contrast; they add no independent finding. The pair-excess contrast is +1.300 bonus points/round, bootstrap95% [+0.400, +2.300], paired t95% [-0.195, +2.795]. Strict Pareto improvement equals mutual-Y mechanically. Same-round results do not exclude mixed-status or delayed reciprocity, or both employees gaining across multiple rounds; they do not verify an agreement. Original S29 ODD is unchanged. [All six metrics, game cells and figure](results/s53_summary.md).

S53 release: both critics and all611canonical checks pass;[fresh origin-clone proof](logs/s53_remote_clean_clone.json) reproduces seven artifacts byte-for-byte from results commit `5ed960c` using the installed frozen venv (no fresh dependency install).
