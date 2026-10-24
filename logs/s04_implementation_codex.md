One blocking bug found: **floating-point arithmetic can change the registered verdict** at [s04_analyze.py:92](/home/factory/collusion/collusion-serendipity/scripts/s04_analyze.py:92).

A complete synthetic analysis with exact quantity effect **−1**, five negative seed differences, bootstrap upper <0, exact p=.03125, positive profit difference, and exposure=1 returned **ODD**. Floating-point averaging produced `−0.9999999999999997`, failing `mean <= -1`.

**Fix:** use integer totals or rational arithmetic for quantity thresholds, seed signs, and the positive-profit screen; convert to floats for reporting and intervals. Add this boundary regression test.

No other blocking bug found in prompts, cache separation, routing/simultaneity, analysis unit, exposure gate, or cache-only replay. Server randomness, backend drift, n=5 inference, and context-isolation limits are already acknowledged design limitations.

No live outcomes/raw responses inspected, model calls made, or files edited.