One decision-rule bug remains, plus a reporting gap. Review was read-only, with offline arithmetic reproductions and no live model calls.

**Remaining issues**

- **Floating-point thresholds can change the verdict.** The [analyzer](/home/factory/collusion/collusion-serendipity/scripts/s14_analyze.py:157) subtracts floating game means before bootstrapping. I reproduced five exact payment differences of **1**, with zero pair-profit differences: the bootstrap upper becomes `0.9999999999999991`, producing **DUD instead of ODD**. The [independent checker](/home/factory/collusion/collusion-serendipity/scripts/s14_independent.py:78) accepts the interval within tolerance and reuses its reported bound, so this error survives verification. Separately, rounding equal rational pair profits can produce a tiny positive difference and a false HIT in the analyzer; the independent exact-profit check catches that case. Keep decision quantities exact through threshold comparisons, and independently derive the verdict from reconstructed bounds.

- **Registered reporting is incomplete.** The [analysis output](/home/factory/collusion/collusion-serendipity/scripts/s14_analyze.py:171) omits sent/nonempty/actually available incoming message counts and payment comparisons against the pure-Nash payment set `{6,7}`. These remain reporting obligations; the independent checker does not verify them.

**Acknowledged limitations**

Five selected exploratory blocks, multiple screens, conditional sign-flip validity, shared-backend interference, bundled channel/role/prompt effects, and the restricted procurement environment are already disclosed. They limit causal and external claims; a HIT would support this bundled intervention in this pilot, not establish collusion or naturalistic tender behavior.

I found no additional treatment-timing error. Recipient filtering, delayed delivery, sealed current bids, exact-request replay, and source/cache guards address the earlier concerns. Hash consistency alone does not independently establish that registration was publicly pushed before calls.