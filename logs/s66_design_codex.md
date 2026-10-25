One medium issue; no high-severity issue found.

- **Medium — presentation can erase intervening documentation changes.** [s66_present.py:43](/home/factory/collusion/collusion-serendipity/scripts/s66_present.py:43) loads four documents from the registration commit, then overwrites their current versions. Any subsequent sibling additions would disappear. Release reproduction uses the same reconstruction, so it would not detect that loss. Add a baseline guard or preserve intervening changes.

By inspection, the scientific implementation matches the design: exact economic-section permutation, identical initial user bytes, identical pooled payoffs (+2 **each** per Y approval), retained history, hidden current-round notes, paired schedules and admission cutoff. Cache replay and failure handling appear consistent. Exact bootstrap quantiles, inclusive sign flips and the directional HIT/DUD/ODD screen are implemented correctly.

Known limits are appropriately separated: five exploratory blocks, endogenous histories, mechanically related bonus/loss outcomes, symmetry assumptions and no collusion-mechanism identification. Temperature 1 reaches the wrapper but is not forwarded by its Codex CLI implementation.

Static review only: no edits, tests or simulated-agent calls. No live S66 dataset was present for empirical verification.