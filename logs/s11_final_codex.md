S11’s reported **ODD** verdict is correct. I found one remaining failure-path bug; no numerical or treatment-timing error affecting the completed dataset.

**Remaining bug — low severity:** the abort flag is set by the results collector only after it receives a failed future ([delay.py:252](/home/factory/collusion/collusion-serendipity/sim/delay.py:252)). Between a worker’s terminal failure and collector handling, its partner can start another uncached request. I reproduced this with in-memory synthetic responses: three invalid attempts raised a terminal error, the flag remained unset, and a partner request proceeded. The existing guard works once set; the remaining issue is delayed propagation. No terminal failure appears in this dataset.

**Independent numerical checks:** starting from raw games, I reproduced all 240 metric/window cells, 24 bootstrap intervals, and eight paired t intervals.

- Primary arm means: **2.429630 immediate**, **1.525926 delayed**.
- Exact block differences: **[11, −25, 57, 27, 52]/27**; mean reduction **122/135 = 0.903704**.
- Bootstrap 95% bounds: **[−0.088889, 1.814815]**; paired t bounds: **[−0.630379, 2.437787]**.
- Exact sign-flip tails: upper **3/32 = 0.09375**, lower **30/32 = 0.9375**. These correctly yield **ODD**.
- Secondary results and the analytical toy reduction **20/9** also match.

Treatment delivery is correct: immediate sees through t−1, delayed through t−2, with no same-round leakage. Cache-only replay reproduced the result byte-for-byte with writes and live calls forbidden. All 366 request/response keys, 13 registered source hashes, and release artifact hashes checked out. Recorded chronology places registration observation before the first call and all calls before cutoff.

**Acknowledged limitations, not remaining bugs:** withholding own feedback and the round-2 calculator difference are bundled into treatment; five blocks, exploratory multiplicity, backend interference, and uncontrolled sampling limit inference. Consecutive smoothness cannot establish convergence, lower long-run variance, learning, or collusion reduction. Sign-flip validity remains conditional, and timestamps/model identity lack independent attestation. The current claims respect these limits, and the frozen HIT/DUD rules are implemented correctly.

No edits or live model calls were made.