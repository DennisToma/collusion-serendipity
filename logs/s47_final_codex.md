S47’s **DUD classification reproduces. No material bug found** in the audited result or protocol implementation.

I independently parsed all **20 raw responses**: nineteen offers were 10; the low-example response for `24924_control_B` was 11. Reconstructed all **15 block cells**, ordered by seeds 24920–24924:

- Low example: `[10, 10, 10, 10, 10.5]`
- High example: `[10, 10, 10, 10, 10]`
- High−low: `[0, 0, 0, 0, −0.5]`

Separately enumerating **3,125 ordered bootstrap draws and 32 sign flips for each of the three summaries** reproduces the saved statistics. Primary mean is **−0.100 offer units**, bootstrap95% **[−0.300, 0]**, paired t95% **[−0.377645, +0.177645]**; inclusive upper/lower/two-sided sign-flip probabilities are **1 / 0.5 / 1**. The fixed two-unit directional screen correctly returns DUD. These are **focal offers, not realized wages**. [Results](/home/factory/collusion/collusion-serendipity/results/s47_example.json)

All ten cases bind to S42 round10 requests, both source arms across five blocks, selecting the alphabetically first incumbent. I checked all nine public-history rounds against source games. Original system, history, own notes and output contract are preserved. Between fresh arms, the **only prompt difference is the valid JSON example’s rate 0 versus 20**. Both carry the identical non-recommendation warning and complete ascending 21-row payoff table; table arithmetic checks out.

Source hashes and registered git content validate. Registration precedes execution; timing satisfies cutoff/headroom requirements. Archived intervals satisfy opposite first-view orders within blocks, sequential views per case, full block barriers and concurrency≤2. There are exactly 20 admissions, responses and acceptances, with no failure archive. Code inspection confirms response fsync before parsing, strict validation, one logical transport attempt, and rejection of failed/interrupted continuation. Seven read-only protocol tests passed. [Harness](/home/factory/collusion/collusion-serendipity/scripts/s47_replay.py)

**Acknowledged limits, not discovered bugs:** five observed blocks, post hoc selection, uncontrolled draws, shared-service interference, unverified sign calibration, and descriptive empirical bounds. DUD establishes neither equivalence nor absence of smaller/reverse effects. Source/replay fingerprints differ only in recorded PATH; this is disclosed. Provider identity, effective settings and tool non-use remain unattested; requested temperature/token limits are not transmitted. [Summary](/home/factory/collusion/collusion-serendipity/results/s47_summary.md)

No edits, paid calls, or other critic reviews. I did not execute release routines that write artifacts.