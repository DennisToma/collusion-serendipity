# HITS — surprising pilot results for the sibling repos

**No promoted hits after iteration 14.** S01 is DUD; S02 is ODD/inconclusive;
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
is queued in IDEAS.tsv; no additional pilot or sibling headline change.
