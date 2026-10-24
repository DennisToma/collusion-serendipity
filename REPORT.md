# Serendipity log — Beyond Words

2026-10-24 15:13 UTC · Iteration 2 · **No hits promoted.** Exploratory pilots; zero tuning attempts.

| Pilot | Result (descriptive 95% bootstrap bounds) | Verdict |
|---|---|---|
| S01 · C, price digits | 104 games scanned; primary on 32 luna / 15 deepseek channel games. Pair-minus-other-pairs prediction gain **+0.00175 [-0.00184, +0.00631]** / **+0.00899 [-0.04249, +0.05535]** squared price units. | **DUD** for this screen |
| S02 · A, Cournot quantities | 6 games, 3 seed blocks. Pair output r4–12: none **5.870**, private **5.389**; difference **-0.481 [-1.222, +0.000]** units/firm. | **ODD**, inconclusive |
| S04 · B, shared advisor sample | Registered ten games, five fresh seed blocks, T12. Shared vs independent identical-prompt advisor responses; running, no partial outcome estimate. | **PENDING** |

**S04 running:** seller prompts hide shared identity; both arms sample two advisor responses per round. Low routable advice variation will yield UNINFORMATIVE. This tests common sampling, not a persistent strategic hub.

**S01:** digits are determined by integer prices: nonlinear prediction gains
cannot identify intentional coding or rule out signaling. Bootstrap omits
refit uncertainty. **S02:** n3, exact lower-output p=0.25,
t interval [-2.099, +1.136];
pair-profit difference +0.056 [-4.556, +4.722].
Lower output alone does not establish profitable coordination.

All fresh games use three firms, integer output, P=max(0,30-total output),
cost 6; static Nash q=6, P=12, profit 36. S02's original gateway stalled;
four partial starts were preserved, and the registered six-game fallback was
never pooled with them. S04 uses fresh seeds and matched advice opportunities.
Client model labels are not independent attestation; Codex temperature and
sampling seeds are uncontrolled. Tiny exploratory samples and unverified
agreement/execution labels limit all claims. No sibling headline change.

[Design S01/S02](DESIGN.md) · [Design S04](DESIGN_S04.md) ·
[Full results, figures and limitations](REPORT_DETAILS.md) · [Reproduce](README.md).
**Next:** cover D/E/F/own before deepening; own S03 calculator proposal queued.
