# Serendipity log — Beyond Words

2026-10-24 17:10 UTC · Iteration 5 (S09 registered; no new result yet) · **No hits promoted.** Exploratory pilots; zero tuning attempts.

| Pilot | Result (descriptive 95% bootstrap bounds) | Verdict |
|---|---|---|
| S01 · C, price digits | 104 games scanned; primary on 32 luna / 15 deepseek channel games. Pair-minus-other-pairs prediction gain **+0.00175 [-0.00184, +0.00631]** / **+0.00899 [-0.04249, +0.05535]** squared price units. | **DUD** for this screen |
| S02 · A, Cournot quantities | 6 games, 3 seed blocks. Pair output r4–12: none **5.870**, private **5.389**; difference **-0.481 [-1.222, +0.000]** units/firm. | **ODD**, inconclusive |
| S04 · B, shared advisor sample | 10 games, 5 seed blocks. Pair output r4–12: independent **5.422**, shared **4.911**; difference **-0.511 [-1.222, +0.122]** units/firm. | **ODD / UNINFORMATIVE** |
| S03 · own, conditional calculator | 10 games, 5 blocks. Mean output/firm r4–12: none **6.719**, calculator **5.837**; difference **-0.881 [-1.170, -0.489]**. | **DUD for predicted increase** |
| S07 · F, anti-coordination rule | 10 games, 5 blocks. Pair output r4–12: neutral **5.800**, legality **4.844**; difference **-0.956 [-2.889, +0.267]**. | **DUD for predicted increase** |

**S07:** **DUD for predicted output increase** (paired t [-3.592, +1.681], higher-output sign-flip p=0.81250). Nonempty message slots: legality **0/120**, neutral **120/120** (all 12 rounds; prespecified descriptive secondary). Neutral output 5.8 is near Nash 6; the +1 HIT threshold would require 6.8. The lower mean is dominated by one market-wide low-output block, including the outsider. Pair-profit t bounds span zero. No implemented sanctions or verified agreement/execution labels; direct cue and channel-use effects remain unseparated. [All S07 outcomes](results/s07_summary.md).

**S03:** **DUD for the predicted increase**; controls produced above Nash 6. All five **r4–12** differences are negative (t [-1.433, -0.330], registered higher-output p=1.00000); over all 12 rounds, 4/5 are negative and calculator mean is 6.006. Paths oscillate: absolute change rises +2.689; lag-conditioned regret falls 2.570→0.119 (table-adherence check), current-rivals regret rises 2.630→8.259. The primary window has an extra low-output phase; price/profit/endpoints are phase-sensitive. Profit t [-0.364, +13.149] spans zero. Arithmetic, salience and lagged-response cues remain bundled; no collusion claim. [All S03 outcomes](REPORT_DETAILS.md#s03--exact-conditional-own-profit-calculator).

**S04:** routable advice disagreement **17.8%** in r4–12, **28.3%** all rounds. This fails the prespecified exposure screening convention (<25%), which is not a calibrated power threshold. Pair-profit difference +3.367 [+0.322, +5.444]; paired t interval [-0.838, +7.571] spans zero. The unadvised outsider output difference is -0.533, similar to the pair. These descriptive outcomes do not establish pair-specific restraint, a null effect or collusion. Early advice and subsequent public-history divergence may affect later behavior. [Full S04 results and limitations](REPORT_DETAILS.md#s04--shared-public-information-advisor).

**S01:** digits are determined by integer prices: nonlinear prediction gains
cannot identify intentional coding or rule out signaling. Bootstrap omits
refit uncertainty. **S02:** n3, exact lower-output p=0.25,
t interval [-2.099, +1.136];
pair-profit difference +0.056 [-4.556, +4.722].
Lower output alone does not establish profitable coordination. S02 also replayed
own sent messages, bundling partner communication with self-message memory.

All fresh games use three firms, integer output, P=max(0,30-total output),
cost 6; static Nash q=6, P=12, profit 36. S02's original gateway stalled;
four partial starts were preserved, and the registered six-game fallback was
never pooled with them. S04 uses fresh seeds and matched advice opportunities.
Client model labels are not independent attestation; Codex temperature and
sampling seeds are uncontrolled. Fresh contexts and no-tools instructions
do not prove filesystem isolation. Tiny exploratory samples and unverified
agreement/execution labels limit all claims. No sibling headline change.

[Design S01/S02](DESIGN.md) · [Design S03](DESIGN_S03.md) · [Design S04](DESIGN_S04.md) · [Design S07](DESIGN_S07.md) · [Design S09](DESIGN_S09.md) ·
[Full results, figures and limitations](REPORT_DETAILS.md) · [Reproduce](README.md).
**Running next:** S09 (E), matched counterfactual message-memory replay; then cover D. Own ideas queued.
