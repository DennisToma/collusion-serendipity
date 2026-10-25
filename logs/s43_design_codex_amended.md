S43’s economic calculation and narrow causal scope are consistent. I found two remaining integrity bugs. Review was read-only, with no paid calls; four non-writing tests passed, covering selection/intervention, all 9,702 payoff rows, parsing, and classification.

**Concrete remaining bugs:**

- [s43_replay.py:268](/home/factory/collusion/collusion-serendipity/scripts/s43_replay.py:268) ignores an existing `failure.json` when neither config nor journals exist. A failure before receipt creation can therefore re-enter initialization; another failure overwrites the original failure record. I confirmed this with filesystem mutations mocked out. The external receipt still prevents relaunch once created, and validation rejects the surviving failure marker, so this does not bypass the effect-estimate gate.
- [s43_independent.py:20](/home/factory/collusion/collusion-serendipity/scripts/s43_independent.py:20) lacks the replay module’s optimization guard. Running it with `python -O` removes 31 assertions, including prompt/source bindings, routing, verdict, and failure checks, while permitting a `passed=True` receipt if remaining computations succeed. Normal execution and the combined release path provide stronger protection.

**Checks that passed:**

Selection reproduces the saved manifest: all ten specified source games, round 10, first initial incumbent, with round-9 rivals. Selection is systematic within the post hoc chosen challenge; archived outcomes are not used as experimental controls.

Fresh control preserves the source prompt exactly. Treatment only inserts the ascending 21-row counterfactual table; source system, history, and owner notes remain identical. No archived current response or recommended action is inserted.

The exact table is correct for all observed rival profiles:

| Own offer | Rivals `[10]` or `[10,9]`: share, profit | Rivals `[10,10]`: share, profit |
|---|---|---|
| 0–9 | 0, 0 | 0, 0 |
| 10 | 1/2, 5 | 1/3, 10/3 |
| Each integer 11–20 | 1, `20−offer` | 1, `20−offer` |

The outcome is the **focal offer**, not worker payment. Two cases average within each seed, then five blocks receive equal weight. The 3,125 bootstrap draws, rational interpolation, 32 inclusive sign flips, and HIT/DUD/ODD arithmetic agree with the design. RNG4343, sequential within-case views, two-worker ceiling, block barriers, cutoff, and three headroom checks are implemented.

**Acknowledged limits:**

The intervention bundles arithmetic, scenario salience, length, and ordering; it cannot identify arithmetic error, beliefs, coordination, or trajectory-level effects. Five selected blocks provide limited generalization; sign-flip calibration requires unestablished symmetry/exchangeability. Tool non-use, served-model identity, complete configuration, transient between-check drift, and power-loss accounting remain unattested.

This snapshot is pre-live: S43 sources are untracked and no live archive exists. Registration, completed-run chronology/cache integrity, rendered release, and origin-clone reproduction therefore remain unverified operational steps.