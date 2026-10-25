S43’s **DUD classification is correct** for the registered one-unit offer screen. I independently reconstructed all 20 raw offers, 15 block cells, 3,125 bootstrap draws per summary, and 32 sign flips per summary. No edits, paid calls, or other critic reviews.

| Seed | Control | Table | Difference |
|---|---:|---:|---:|
| 24920 | 9.5 | 10 | 0.5 |
| 24921 | 10 | 10.5 | 0.5 |
| 24922 | 10 | 10.5 | 0.5 |
| 24923 | 10 | 10 | 0 |
| 24924 | 10 | 10 | 0 |

Means are **9.9 versus 10.2**; contrast **+0.3**, exact bootstrap interval **[0.1, 0.5]**, paired t95% **[−0.04004, 0.64004]**, inclusive upper sign-flip **p=4/32=0.125**. The bootstrap upper bound below 1 triggers DUD. All reconstructed values match [the saved result](/home/factory/collusion/collusion-serendipity/results/s43_payoff.json).

Selection matches registration: all ten S42 games, round 10, first initial incumbent; five equally weighted seed blocks. The challenge was selected post hoc, but individual cases were not filtered by action. Both arms use fresh responses; archived responses serve only descriptive comparisons.

Intervention isolation passes at the prompt level: identical system, public history, and owner-only notes; exact source control prompt; treatment adds only the specified table and framing. Every inserted row matches round-9 rivals. Actual profiles are `[10]`, `[10,10]`, and `[10,9]`. Below 10, share/profit are zero; at 10, they are respectively **1/2, 5**, **1/3, 10/3**, and **1/2, 5**; at 11–20, share is 1 and profit is `20−offer`. All 9,702 exhaustive profile/action checks pass. Treatment supplies no recommendation and explicitly disclaims forecasting.

Registration/source hashes, case bindings, request/response hashes, acceptance journals, and chronology validate. RNG4343 ordering, sequential within-case views, block barriers, and maximum concurrency two hold. Registration occurred at 03:32:24 UTC; execution completed at 03:33:15, comfortably before the 04:30 admission cutoff. Failure handling and cache paths prohibit replacement/restart; no failure artifacts exist.

**Concrete remaining bugs/gaps:** No result-changing arithmetic, selection, schedule, or classification bug found. Promised origin-clone reproduction remains unevidenced: its receipt is absent, and archive/results are untracked at this snapshot. The local release receipt establishes local reproduction only.

**Acknowledged limits:** The outcome is a **focal offer**, not worker payment. The intervention bundles arithmetic, scenario salience, length, and order. Five selected blocks and one draw per arm limit inference; enumeration does not establish sign-exchangeability. Provider identity, effective settings, and actual tool non-use remain unattested. The source/replay fingerprint mismatch is PATH-only. Neither explanations nor this contrast establish arithmetic correction, coordination, or trajectory-level effects.