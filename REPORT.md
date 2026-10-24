# Serendipity log — Beyond Words

2026-10-24 15:00 UTC · Iteration 1 · **No hits promoted.** Discovery pilots; zero tuning attempts.

| Pilot | Result (descriptive 95% bootstrap bounds) | Verdict |
|---|---|---|
| S01 · C, price digits | 104 games scanned; primary on 32 luna / 15 deepseek channel games. Pair-minus-other-pairs prediction gain **+0.00175 [-0.00184, +0.00631]** / **+0.00899 [-0.04249, +0.05535]** squared price units. | **DUD** for this screen |
| S02 · A, Cournot quantities | 6 complete games, 3 seed blocks, gpt-6-luna. Pair output r4–12: none **5.870**, private **5.389**; difference **-0.481 [-1.222, +0.000]** units/firm. | **ODD**, inconclusive |

**S01:** last digits are determined by integer prices; this cannot identify
intentional coding or rule out signaling. Deepseek no-channel gain is
+0.00569 [+0.00088, +0.01019], consistent with price nonlinearity. Fixed
five-fold game-held-out ridge; bootstrap treats overlapping fitted models as
fixed and omits refit uncertainty. No game excluded.

**S02:** three firms choose quantities 0..12; P=max(0,30−total output), cost 6.
Nash q=6; all-firm optimum q=4. Pair messages arrive next round; no coordination
instruction. Seed differences -0.222, -1.222, +0.000;
exact lower-output p=0.25; t interval
[-2.099, +1.136]. With three
blocks, bootstrap bounds equal the observed range; minimum exact p=1/8 prevents
HIT. The largest reduction also includes an outsider output cut.

| Secondary r4–12 outcome | Private minus none (descriptive bounds) |
|---|---|
| Outsider quantity | +0.074 [-0.778, +1.000] |
| Total quantity | -0.889 [-3.222, +0.556] |
| Market price | +0.889 [-0.556, +3.222] |
| Pair per-firm profit | +0.056 [-4.556, +4.722] |

Pair profit is essentially unchanged. Round-12 pair output: none
6, 5, 6; private
6, 4.5, 6. Lower output alone does not
establish profitable coordination; pair-only coalition benchmarks differ from
the all-firm optimum ([enumeration and full results](REPORT_DETAILS.md)).

**Runtime deviation:** planned Qwen gateway stalled (4
starts, 1 decision, no complete games). Preserved as
incomplete; the amended six-game fallback uses the remaining ten-game budget,
never pooling models. Randomized execution slots; 216 cached decisions,
0 invalid-output retries. Model labels reflect client
routing; Codex temperature/seed are not controlled. Prompt and delivery are bundled;
agreement/execution labels remain unverified. No confirmatory claim.

![Cournot trajectories](figures/s02_cournot.png)
*Means; shading is the range across games, not a CI.*

[Design](DESIGN.md) · [Full results/methods](REPORT_DETAILS.md) ·
[Reproduce](README.md) · [Reviews and fixes](logs/review_disposition.md).
**Next:** cover B/D/E/F/own before deepening; S03 calculator idea queued, not run.
