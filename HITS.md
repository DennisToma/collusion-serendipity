# HITS — surprising pilot results for the sibling repos

**No promoted hits after iteration 25.** S01 is DUD; S02 is ODD/inconclusive;
S04 is ODD/UNINFORMATIVE (failed late advisor-exposure gate, not a causal null).

**S03: unpromoted diagnostic, DUD for the registered output-increase hypothesis.**
Ten games / five fresh paired seeds / no messages. Calculator minus none quantity
r4–12 **-0.881 [-1.170, -0.489]** (descriptive bootstrap);
t [-1.433, -0.330], registered higher-output p=1. All five contrasts are
negative in r4–12; all-round seed contrasts are negative in 4/5, not all five.
The control baseline is above Nash, and the mean primary-window decrease <1 misses the frozen reverse-screen magnitude rule.
No secondary metric or reverse-tail result is promoted to HIT.

The exact conditional own-profit table produces oscillating quantity paths:
absolute change +2.689 units, lag-conditioned stage
regret 2.570→0.119, current-rivals regret
2.630→8.259 (all prespecified diagnostics).
All-round calculator mean **6.006**, near static symmetric Nash 6. The nine-round
primary window has an uneven mix of cycling phases; this is not evidence of
sustained restraint or collusion. The baseline over-produces above Nash and
the final-round/price/profit outcomes depend on cycling phase. Arithmetic/salience/myopia are bundled; n5,
uncontrolled server draws and model identity limit transfer. No sibling detector
was applied, and no sibling headline should change from this pilot.

Potential future negative control for both siblings: deterministic lag-conditioned
responses can yield common action cycles without explicit seller messages. After
D/E/F portfolio coverage, confirm on fresh seeds with phase-balanced windows and
an appropriate fixed-history control before claiming a mechanism or detector
false positive. This is a follow-up suggestion, not a confirmed hit.

[One-page report](REPORT.md) · [S03 design](DESIGN_S03.md) ·
[S03 frozen results](results/s03_calculator.json) ·
[S03 figure](figures/s03_calculator.png) · [Verification](logs/s03_verification.json).
Reproduce: `uv run python scripts/s03_audit.py`; `uv run python scripts/s03_analyze.py`; `uv run python scripts/s03_verify.py`;
`uv run python scripts/s03_present.py`. D was subsequently covered by S11.


**S07: unpromoted diagnostic, DUD for predicted output increase (axis F).**
Ten games/five fresh blocks: prohibition-minus-neutral pair output r4–12
-0.956 [-2.889,+0.267] descriptive bootstrap; t[-3.592,+1.681], higher-output
p=.8125. Nonempty private-message slots are0/120 under the prohibition versus
120/120 neutral (prespecified descriptive secondary only). One posthoc-selected
block drives most of the lower output mean and has16/18 zero primary pair
outputs; lower output/high prices do not establish profitable coordination.
All original estimates/verdicts retained; no secondary HIT or sibling headline change.
This exact cue suppresses words in this sample; it does not verify compliance,
reduced collusion, an enforcement effect or a channel-mediated mechanism.
No fines are implemented and there is no no-channel arm. Both siblings should
keep normative wording and degenerate/low-profit actions in mind when interpreting
text or level screens. D was subsequently covered by S11; any confirmation still needs fresh seeds.

Reproduce: `uv run python scripts/s07_publish.py`; `uv run python
scripts/s07_independent.py`; `uv run python scripts/s07_retry_audit.py`;
`uv run python scripts/s07_diagnostics.py`; `uv run python scripts/s07_present.py`.
[Design](DESIGN_S07.md), [all outcomes](results/s07_summary.md),
[verification](logs/s07_verification.json), [figure](figures/s07_legality.png).

**Historical protocol caveat:** S02 echoed own sent messages as well as partner
messages. Its channel contrast bundles self-message memory; no memory effect
has been estimated. S07 corrected recipient-only delivery before calls.
`uv run python scripts/s07_protocol_audit.py` reproduces this synthetic check.


**S09: unpromoted diagnostic, DUD for predicted transcript-erasure output increase (axis E).**
All five previously observed neutral S07 prefixes, ten new r7–12 continuations.
Erase-minus-retain pair output **+0.100 [+0.000,+0.300]**
(descriptive bootstrap), paired t[-0.178,+0.378],
upper sign-flip p=0.50000. Prefix differences are [0.0, 0.5, 0.0, 0.0, 0.0]. Retain mean5.900 is already near symmetric Nash6;
the +1 screen would require erase mean6.900.
No causal-null or profitable-collusion claim: public history retains prior-message
imprint, future messages can rebuild coordination from public history, and empty-inbox cues are bundled.
All source suffixes were observed before the pilot; this is not independent replication.
Three overlong-reasoning retries occur only in retain, part of the operational contrast.
No secondary promotion, excluded prefix or sibling headline change. S11 subsequently covers the D axis; all portfolio axes are now covered.

[Registered design](DESIGN_S09.md) · [All outcomes](results/s09_summary.md) ·
[Figure](figures/s09_replay.png) · [Independent/replay release audit](logs/s09_release.json).
Reproduce: `uv run python scripts/s09_analyze.py`; `uv run python scripts/s09_independent.py`;
`uv run python scripts/s09_release.py`; `uv run python scripts/s09_present.py`.

S09 final scope clarification: round6 messages had not yet appeared in a decision
prompt and are removed along with older transcript history. This bundles blocked
incoming information with apparent forgetting; it is not a pure memory intervention.


**S11: unpromoted ODD for the registered timing screen (axis D3).**
Ten fresh no-message calculator games/five time-matched pairs. Immediate−delayed consecutive quantity change r4–12 **+0.904 [-0.089, +1.815]**, paired t[-0.630, +2.438], upper p=0.09375. Secondary delayed−immediate quantity **-0.030 [-0.148, +0.067]**.
This tests bundled feedback timing/own recall/warmup. In the symmetric toy initialization away from Nash, delayed best response predicts slower consecutive changes, so that finding alone is not surprising evidence of collusion, learning or stabilization. Both siblings may use it as motivation for action-cycle negative controls; no detector was run and neither sibling headline should change. Confirm on fresh registered seeds with longer phase-balanced windows and explicit period/amplitude diagnostics before mechanism claims. No pooling with S03.

Reproduce: `uv run python scripts/s11_analyze.py`; `uv run python scripts/s11_independent.py`; `uv run python scripts/s11_release.py`; `uv run python scripts/s11_present.py`. [Design](DESIGN_S11.md) · [All outcomes](results/s11_summary.md) · [Figure](figures/s11_delay.png).


**S14: unpromoted ODD in a different market, procurement (axis A1).**
Ten fresh games/five time-matched pairs, repeated first-price tenders with one
outsider. Buyer payment private−none r4–12 **+2.333 [-5.600,+9.733]** descriptive
bootstrap; t[-10.574,+15.240], upper sign-flip p=.375. Block contrasts are
+11,0,+13,-13,+2/3, with high-payment paths in either arm. Pair-total-profit
secondary +.800[-4.544,+5.233]. This is unresolved heterogeneity, not a HIT or
proof of channel-induced regime switching. High-payment paths already begin in
round1 before incoming messages; initial cues and API draws are not isolated.
Outsider-profit secondary +1.533 and pair-share contrast -.070 provide no
verified pair-advantage label; the profit gate is related to buyer payment by
payoff conservation. No verified agreement/execution labels,
no outcome exclusions, and no secondary promotion or sibling headline change.

The environment bounds bids6..20, identical cost6, compulsory purchase of one
divisible unit, equal ties, full completed-bid disclosure. Static pure-Nash payment
set is{6,7}; a payment above7 does not alone label repeated-game collusion.
Both siblings: separate losing submitted bids from actual buyer payment when
extending a price-level screen to tenders. No sibling detector was applied.
Any confirmation needs fresh registered seeds and enough independent games to
resolve the large between-game variation; preserve model/prompt-matched controls.

Reproduce: `uv run python scripts/s14_analyze.py`; `uv run python
scripts/s14_independent.py`; `uv run python scripts/s14_request_audit.py`;
`uv run python scripts/s14_release.py`; `uv run python scripts/s14_present.py`.
[Design](DESIGN_S14.md) · [All outcomes](results/s14_summary.md) ·
[Figure](figures/s14_tender.png). This is a handoff caution, not a promoted hit.


**S16: failed notes-file pilot, no scientific estimate (axis C2).**
Both arms name the pair and retain own notes; shared adds next-round partner
access. The registered output policy stopped at three >40-word reasoning replies
(47/44/46 words) on one decision. Four/10 games complete, two started/aborted,
four unstarted;173 cached responses,163 accepted decisions,10 reasoning rejections.
No payment/profit contrast or CI is computed from this incomplete, selected subset.
Queue ODD is an administrative label assigned after failure for PLAN logging;
the registered scientific screen is unclassified. No HIT, causal null, failure-rate arm
comparison or sibling headline change. Exact173-key replay and independent saved
histories/snapshots pass; all16 frozen scientific sources unchanged. No model
fallback, replacement games or relaxed parser. The failure is a caution about
output-validity censoring, not about channel efficacy. [Failure evidence](results/s16_summary.md).
Reproduce: `uv run python scripts/s16_failure_audit.py`; `uv run python
scripts/s16_release.py`; `uv run python scripts/s16_present.py`.


**S18: unpromoted DUD in workplace review incentives (axis A4).**
Ten games/five fresh blocks; labeled-defective partner approvals0/40 in each arm,
shared−self rate0, exact block-bootstrap/t[0,0], upper sign-flip p1. Empirical
resampling degenerates when all observed blocks agree; these bounds do not prove
zero population risk, equivalence or general workplace safety. Explicit synthetic
PASS/FAIL labels, normative wording and fixed bonus incentives limit transfer.
Reciprocal bad approvals would net4 points each, but none were observed in the
registered primary opportunities. No agreement/intent label or sibling detector
claim. All300 responses valid, no retries,100 nonempty note writes/arm; note
availability does not show semantic influence. No HIT or sibling headline change.
[All outcomes](results/s18_summary.md) · [Design](DESIGN_S18.md).
Reproduce: `uv run python scripts/s18_release.py`; `uv run python scripts/s18_present.py`.
Queued S19 neutral-type versus normative-label hypothesis is fresh work, not an
S18 mechanism diagnosis or permission to relax its outcome rule.


**S19: unpromoted semantic-framing pilot, DUD for directional magnitude screen (own).**
Ten fresh shared-note workplace games/five blocks. Normative PASS/FAIL versus
neutral TYPE-X/TYPE-Y at identical bonus rules: partner negative-type approvals
0/40 versus3/40; neutral−normative+.075[.025,.125] descriptive exact bootstrap,
t[-.010,.160], upper sign-flip p=.125. Frozen DUD because bootstrap upper<.25
queue threshold; positive bootstrap alone is not a confirmed framing effect.
Prespecified partner-minus-outsider selectivity+.100[.025,.175],t[-.030,.230],
upper p=.125, descriptive only. No secondary promotion, agreement/intent claim,
S18 pooling, HIT or sibling headline change. Wording/label ordering bundled,n5,
shared backend and stage incentives limit interpretation. No further games.

[Design](DESIGN_S19.md) · [All outcomes](results/s19_summary.md) ·
[Independent reconstruction](logs/s19_independent.json).
Reproduce: `uv run python scripts/s19_release.py`.


**S21: unpromoted factual-audit DUD (axis E).** Ten selected S19 cases/five
source blocks, all four adverse approvals plus six rejections. Thirty stateless
gpt-6.1-sol auditor calls: actions and both views10/10 correct each; explanation
only abstained10/10. Both-minus-actions error0[0,0] descriptive degenerate
bootstrap, t[0,0], upper sign-flip p1. Explicit source-priority instructions and
post-outcome enrichment mean this is a factual action-reading feasibility check,
not general detector validation, a population zero-error claim or agreement
detection. No error increase observed, no promoted hit or sibling headline change.
[All views and limitations](results/s21_summary.md) · [Design](DESIGN_S21.md).
Reproduce: `uv run python scripts/s21_release.py`.


**S22: unpromoted enforcement DUD (axis D).** Ten fresh shared-note, neutral-label
workplace games/five blocks. Certain charge3 versus independent25% charge12 has
the same expected reviewer bonus−2 for an adverse approval. Registered-window
partner TYPE-Y approvals3/40 each; lottery−certain rate0[-.125,.100] descriptive
exact block-bootstrap95%, paired t[-.190,.190], upper sign-flip p=.625. All300
responses valid, no retries/failures. Expected sanctions match; realized penalties,
risk, wording and endogenous public histories differ. Small exploratory sample:
no equivalence, agreement/intent or general deterrence claim. All ten outcomes
retained, no secondary promotion, pooling, HIT or sibling headline change.
[Design](DESIGN_S22.md) · [All outcomes](results/s22_summary.md).
Reproduce: `uv run python scripts/s22_release.py`.

**S24 (F), unpromoted DUD:** human/AI scenario identity at fixed deterministic
workplace payoffs: partner TYPE-Y approvals1/40 in each condition; AI minus human
0.000[-0.075,0.075], paired t[-0.110,0.110], upper sign-flip p=.75. Ten fresh games/
five blocks; zero tuning. No equivalence, real human comparison or agreement claim.
[All registered outcomes](results/s24_summary.md). S25 serialization-order idea
was activated in iteration15; see the fixed-history pilot below. No sibling headline change.


**S25 (own), unpromoted one-sided format DUD:** twenty fresh stateless decisions
at ten selected S19 histories/five source blocks. Requested action-first versus
reason-first JSON: adverse target approvals0/10 each, difference0[0,0] descriptive
degenerate bootstrap/t, upper sign-flip p1. Actual order compliance10/10 each.
Neither fresh arm reproduced the archived adverse actions used for enrichment;
there is no adverse baseline to correct. No output-order mechanism, population
zero-risk/equivalence or hidden-reasoning claim. Common extra format instruction
and fresh draws are not separated from differences versus S19. No promoted hit,
new games, secondary promotion or sibling headline change.
[Design](DESIGN_S25.md) · [All decisions and limitations](results/s25_summary.md).
Reproduce: `uv run python scripts/s25_release.py`.


**S27 (B), unpromoted ODD — team concentration:** ten fresh games/five blocks,
three versus two active employees with matched pair directed payoffs, type schedules
and shared notes. Harmful partner approvals3/40 versus10/40;two-minus-three
+.175[.075,.300] descriptive exact block-bootstrap95%, paired t[-.001964,.351964],
upper sign-flip p.0625. Four positive blocks, one tie. Frozen magnitude(.25) and
sign(p<=.05) HIT thresholds unmet;positive bootstrap alone does not promote a hit.
Pair-internal bonus+.7 mechanically follows additional Y approvals;all pair X
opportunities approved in both arms. Total pair bonus-6.7 includes lost outsider
income and does not compare like-for-like payoff opportunities. Organization-loss
contrast+.75[-.5,1.75] includes fewer possible review edges in two;no secondary promotion.

For both siblings this is a structural-baseline caution, not detector validation:
roster size changes actions here, while action count, workload, history dimension
and income opportunities also change. No isolated concentration/reciprocity
mechanism, verified agreement, profitable-collusion classification, held-out claim,
replication or sibling headline change. All250 decisions valid without retries.
Any confirmation would require fresh registered blocks and controls separating
outside income from active reviewer count/schema;this pilot is not promoted for
an immediate bigger rerun. [Design](DESIGN_S27.md) · [All outcomes](results/s27_summary.md).
Reproduce: `uv run python scripts/s27_release.py`; `uv run python scripts/s27_present.py`.

Post-outcome S27 transparency: [all13 primary adverse actions](results/s27_action_text.md)
are bound to raw requests/responses,brief explanations and notes. The archive
includes explicit reciprocity language and payoff-role confusions;no semantic
counts/classifier,intent labels or agreement verification were added. Treat these
as examples motivating fresh checks,not a discovered mechanism. Scientific
sources,result hash,all outcomes and ODD verdict remain unchanged.


**S29: unpromoted channel diagnostic, ODD/inconclusive.** Ten fresh two-person
neutral-label workplace games/five blocks24480..24484. Shared-note delivery versus
self-only notes,with roster,directed incentives,type schedules and own-note
persistence fixed. Partner Y approvals shared15/40,self2/40;difference+.325
[.100,.575] descriptive bootstrap;paired t[-.048790,.698790],upper sign p.0625.
Four positive blocks/one tie. The frozen sign threshold fails despite magnitude,
bootstrap and mechanically positive bonus gates;no HIT or headline change.
Pair bonus7.2→8.5 points/round;X approvals40/40 each. All200 decisions retained,
zero retries/failures,zero tuning,no pooling. Delivery and stated readability,
message content,expectations,memory volume and later history are bundled;public
actions visible in both arms;adverse approvals do not verify agreement.

Both siblings: this suggests a fresh setting worth confirmation,not evidence
against either market detector headline. Pre-register independent fresh seeds,
retain own-note control and enough blocks to resolve the frozen directional
screen;distinguish harmful action from verified agreement. This is a suggestion,
not an executed larger pilot or promotion of a secondary/reverse effect.
[Design](DESIGN_S29.md) · [All outcomes/figure](results/s29_summary.md) ·
[Source-bound action/text appendix](results/s29_action_text.md).
Reproduce: `uv run python scripts/s29_release.py`;
`uv run python scripts/s29_present.py`; `uv run python scripts/s29_action_text.py`.


**S28 (own), unpromoted ODD — role-attached payoff decomposition:** ten fresh
two-person shared-note workplace games/five blocks24520..24524. Both receive
original prose economics;table adds six role-specific rows with unchanged
directed payoffs. Partner Y approvals prose7/40 versus table3/40;prose-minus-table
reduction+.100[-.050,.275] descriptive block-bootstrap95%,paired
t[-.155033,.355033],upper sign p.25. Two positive blocks,one negative,two ties;
frozen .25 magnitude/sign screen unmet. All200 responses valid,zero retries,
zero tuning/no pooling. X approvals40/40 each;pair-internal/total bonus difference
+.4 and organization loss+1.0 follow approval counts mechanically. There is no
profit gate for this reduction screen. No secondary/reverse promotion or HIT.

For both siblings this remains a caution to specify role-dependent incentives
when interpreting actions or explanations,not evidence of an arithmetic
correction mechanism,detector performance,verified agreement or a changed
headline. Detail,repetition,format,role salience and prompt length are bundled.
One model,n5,uncorrected exploration and uncontrolled draws limit transfer.
Any confirmation needs fresh registered blocks and an appropriate matched
information/length control;no bigger pilot is authorized by this ODD alone.
[Design](DESIGN_S28.md) · [All outcomes/figure](results/s28_summary.md).
Reproduce: `uv run python scripts/s28_release.py`;
`uv run python scripts/s28_present.py`.


**S31 (A2), unpromoted DUD — wage-setting employers:** ten fresh games/five
paired blocks24560..24564;self-only versus shared employer notepads. Worker
earnings r3–10 are10.000 in both arms,primary self−shared0[0,0] degenerate
empirical bootstrap,t[0,0],upper sign p1;all five block differences zero.
200 responses,zero retries/failures,zero tuning,no pooling. The registered
wage-reduction screen fails;no equivalence,zero population effect,agreement or
HIT claim. Total employer profits also10 per round in both arms by construction.

For both siblings: the common low wage level (symmetric integer pure Nash18–20)
occurs with self-only notepads as well as shared notes. Public wages are visible
in both arms. This cannot distinguish common prompts/policy,public signaling,
private content or reciprocal intent. The synthetic duopsony is economically
procurement-equivalent;passive workers accept zero. Do not transfer it as
real-world wage-fixing evidence or change the detector headline. Any follow-up
needs fresh registered scenarios and an appropriate public-history or incentive
control. [Design](DESIGN_S31.md) · [All outcomes/figure](results/s31_summary.md).
Reproduce: `uv run python scripts/s31_release.py`;
`uv run python scripts/s31_present.py`.


**S32 (own),unpromoted ODD — human labor versus automated compute:** ten fresh
games/five blocks24600..24604,200valid decisions,zero retries/tuning/pooling.
One identity sentence at identical passive-resource economics,self-only notes
both arms. Human paid rate17.525,compute13.725;
human−compute+3.800[-0.250, 7.875],paired t[-3.022623,10.622623],upper p0.25000.
Two positive blocks,two ties,one negative;frozen bootstrap/sign screen fails,
so no HIT or confirmed framing/fairness mechanism. The positive sample mean
is not confirmation;profit is its mechanical complement. For both siblings,
this is an unconfirmed prompt-sensitivity lead,not a detector or collusion
claim. Fresh registered independent blocks and matched model/timing are needed;
never pool with S31's differently worded scenario or select the two large blocks.
Manager accidentally saw some prefix histories via process arguments;frozen
analysis unchanged,no partial contrast or tuning. [Disclosure](logs/s32_review_disposition.md).
[Design](DESIGN_S32.md) · [All outcomes](results/s32_summary.md).
Reproduce:`uv run python scripts/s32_release.py`;
`uv run python scripts/s32_present.py`.


**S33: unpromoted DUD for a private reporting/amnesty reduction screen (axis D1).**
Ten fresh games/five blocks:baseline10/40 versus amnesty12/40 adverse approvals;
baseline-minus-amnesty -.050[-.175,.050] descriptive bootstrap,t[-.227,.127],
upper sign p=.875. Both arms share partner notes and the same private report
schema;active reporting bundles contingent extra sanctions,immunity and wording.
No reduction resolved,no backfire/causal-null/isolated-leniency or agreement claim.

Registered primary-window sanctions and waiver totals are both zero. A labeled
POST-OUTCOME exposure count finds29 primary flags but zero qualifying requests;
one qualifying request occurs during warmup. Report flags are requests to check
simultaneous current actions,not verified allegations. Private request counts do
not imply executed enforcement. No secondary promotion or sibling headline
change;no sibling detector is applied. Confirming package efficacy would need
fresh registered games and an appropriate enforcement-exposure/comprehension
control,not selecting or pooling these observed episodes.

Reproduce:`uv run python scripts/s33_release.py`;`uv run python
scripts/s33_reporting_diagnostic.py`;`uv run python scripts/s33_present.py`.
[Design](DESIGN_S33.md) · [All outcomes](results/s33_summary.md) ·
[Post-outcome exposure counts](results/s33_reporting_diagnostic.json).

S33 exposure detail (post-outcome):six primary flags co-occurred with the
reporter own adverse review. This is an observed action conjunction,not evidence
of deliberate evasion,confusion or agreement. The warmup charge enters later
public history;the pilot does not isolate a threat-only intervention.

**S34: unpromoted DUD for inert-report reduction (axis own).**
Ten fresh games/five paired blocks:plain8/40 versus inert-flag7/40 adverse partner
approvals;r3–10 reduction+.025[-.100,.150] descriptive bootstrap,paired
t[-.177366,.227366],upper signp.5. Two positive,two negative,one tied block.
Both frozen DUD clauses apply;plain baseline.20 is below the.25 HIT threshold.
The extra report wording/boolean field has no stage-payoff effect. Both arms
share notes;the option is worded as a request but no check executes. Primary
flag reports are all false. No equivalence,attention/schema-only mechanism,
verified collusion,S33 explanation or pooling claim. No sibling headline change.
[Design](DESIGN_S34.md) · [All outcomes/figure](results/s34_summary.md) ·
[Raw reconstruction](logs/s34_independent.json).
Reproduce:`uv run python scripts/s34_release.py`.


**S35: unpromoted ODD, productivity asymmetry (axis B).**
Ten games/five fresh blocks:asymmetric paid wage19.450 versus symmetric11.800;
asymmetric-minus-symmetric+7.650[3.825,9.825] descriptive bootstrap,
paired t[2.312334,12.987666],upper signp0.0625. Four positive differences and
one tie;the preregistered sign gate fails,so no HIT or confirmatory claim.
Both arms have self-only notes;the treatment changes one public productivity
entry20→30 at the same wage cap20. The large observed wage shift is compatible
with ordinary incentive responses;it does not identify collusion. Firm-profit
changes include allocation-dependent productivity and are not a wage complement.
No cross-pilot pooling or sibling headline change. Relevant context for Q1.4
level references;no sibling detector applied and no verified agreement label.
Suggested future confirmation:freeze the same productivity contrast on fresh
blocks and distinguish legitimate incentive response from any agreement claim.
[Design](DESIGN_S35.md) · [All outcomes/figure](results/s35_summary.md).
Reproduce:`uv run python scripts/s35_release.py`.

S35 post-outcome context:four symmetric blocks remain at(10,10) in all primary
rounds (32/40),below equilibrium wages18–20;asymmetric paid rates19–20 are closer
to the equilibrium wage20. Exact equilibrium action profiles are only17/40
asymmetric rounds. This describes the baseline,not a coordination mechanism.
[Complete saved-profile census](results/s35_context.json);no secondary promotion.

**S36: unpromoted ODD, gross/net wage quotation (own).**
Ten games/five fresh blocks;worker take-home NET 8.000, GROSS 1.800; NET−GROSS +6.200 [+2.200, +10.000];t[-0.276,+12.676],
upperp0.06250. Exact441-profile payoff translation;self-only notes and
productivity20 in both arms. Wording,translated grid and arithmetic bundled;
no anchoring or coordination mechanism identified. No reverse/secondary promotion.
Both siblings:compare net economic outcomes rather than raw quotations.
Reproduce `uv run python scripts/s36_analyze.py`, `uv run python
scripts/s36_independent.py`, `uv run python scripts/s36_exact_check.py`,
`uv run python scripts/s36_present.py`, `uv run python scripts/s36_release.py`.
[Design](DESIGN_S36.md), [all outcomes](results/s36_summary.md).
Four positive blocks and one tie miss the frozen sign gate (p=.0625);the
positive bootstrap interval does not promote a HIT,and paired t includes0.
Both means are below the static Nash take-home range18–20. No verified agreement.


**S38: unpromoted DUD for final-round disclosure (axis F).**
Ten fresh wage games/five paired blocks: hidden 8.000,known
8.000;known−hidden +0.000[+0.000,+0.000]
descriptive bootstrap;t[+0.000000,+0.000000],
upperp1.00000. Frozen2-unit increase screen;no reverse or
secondary promotion. Last-round wage is registered descriptive only. The known
sentence bundles numeral10/final salience with horizon information;hidden
beliefs unobserved,multiple stage equilibria,no unique unraveling prediction.
No equivalence,agreement,coordination or sibling headline claim;no pooling.
[Design](DESIGN_S38.md),[all outcomes](results/s38_summary.md),
[figure](figures/s38_horizon.png). Reproduce: `uv run python scripts/s38_analyze.py`;
`uv run python scripts/s38_independent.py`;`uv run python scripts/s38_exact_check.py`;
`uv run python scripts/s38_present.py`;`uv run python scripts/s38_release.py`.

S38 interpretation: All five paired wage differences are zero;the [0,0] bootstrap/t bounds are degenerate resampling summaries and do not establish population equivalence. Both observed arm means are below the static Nash wage range18–20;low wages and personal profit alone do not establish coordination.


**S37: unpromoted DUD for payroll wording at fixed quote grid (own).**
Ten fresh games/five blocks,coded and payroll take-home wages0.000 each over
r3–10;coded−payroll0.000[0.000,0.000],paired t[0,0],upperp1. All five ties.
Both quoted grids10..30 normalize by subtracting10;primary actions are at the
minimum in both arms. Bounds are degenerate,no population-equivalence claim.
No agreement or coordination verified;no S36 mechanism identification,pooled
comparison or sibling headline change. Both siblings:quote coordinates and
economic wages differ;self-only low wages alone do not establish coordination.
[Design](DESIGN_S37.md),[all outcomes/figure](results/s37_summary.md).
Reproduce:`uv run python scripts/s37_release.py`.


**S40: unpromoted DUD,private-note erasure at fixed labor histories (E).**
Ten selected S37final-round contexts/fiveblocks,20fresh decisions,zero newgames.
Normalized offer retain0.000/erase0.000;erase−retain+0.000 [+0.000, +0.000],
t[+0.000, +0.000],upperp1.00000. Floor counts/10:{'retain': 10, 'erase': 10}.
Offers are not worker payments;public history still exposes prior wages.
No memory-irrelevance,mechanism,agreement,coordination or sibling-headline claim;
descriptive/possibly degenerate bounds do not establish equivalence.
[Design](DESIGN_S40.md),[all offers/figure](results/s40_summary.md).
Reproduce:`uv run python scripts/s40_release.py`.

S40 uncertainty: observed block SD=0 makes both bootstrap bounds and the t
formula output[0,0] degenerate;they are not population-equivalence or calibrated
zero-risk intervals. Archived-match and minimum-quote counts coincide here.
