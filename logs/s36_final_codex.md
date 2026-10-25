**S36’s frozen ODD verdict is correct. No result-changing arithmetic, economic, parser, visibility or replay bug found.**

I independently reconstructed all five metrics from the 200 raw rate responses, enumerated all 3,125 bootstrap samples for each of 15 summaries, and checked all 32 sign flips per metric.

- Primary net means by block: **10, 10, 10, 0, 10**; normalized gross: **0, 9, 0, 0, 0**.
- Net−gross differences: **10, 1, 10, 0, 10**; mean **6.2**; exact bootstrap bounds **[2.2, 10]**.
- Inclusive upper p = **2/32 = 0.0625**; two-sided p = **0.125**. Paired t interval **[−0.275727, 12.675727]**.
- The zero block prevents HIT; neither DUD condition holds. **ODD** follows the registered rule.

Exhaustive checks passed for **441 profiles and 18,522 unilateral deviations** under gross-to-net translation. Shares and profits agree exactly; total firm profit is the wage complement. Nash profiles are correctly stated.

Independent normalization, both condition-specific parsers, all 200 prompt bindings, self-only notes and hidden current-round choices passed. Calls are sequential within games without exposing the first firm’s current choice. Paired transport lifetimes overlap, and block barriers hold. Full archive analysis and all-key replay passed, including source/registration hashes, configuration, chronology and canonical exports. Failure handling rejects partial publication and interrupted continuation. REPORT.md and the summary preserve the directional screen and causal scope.

**Concrete guard weakness — medium prospectively; no observed S36 effect:** [s36_runtime.py:19](/home/factory/collusion/collusion-serendipity/scripts/s36_runtime.py:19) hashes environment-variable values but does not hash files referenced by `NODE_OPTIONS`, `CODEX_MANAGED_CONFIG_FILE` or certificate variables. Changing referenced contents while retaining the pathname leaves the fingerprint unchanged; I confirmed this for `NODE_EXTRA_CA_CERTS` using an in-memory mock. These archived variables are null. Remedy: hash referenced configuration/code/certificate contents and directory manifests, or reject unsupported populated variables. This is a specific instance of the acknowledged incomplete-configuration coverage.

**Acknowledged limitations:** five exploratory blocks; bundled wording/grid/arithmetic treatment; sign-flip calibration assumptions; uncontrolled provider draws and possible service interference; passive workers; no isolated anchoring or collusion identification. Provider execution, actual tool non-use and complete effective configuration remain unattested.

**Unchecked:** fresh remote clone/push verification and the write-producing full test suite. No files edited, live model calls made, or other final critic reviews read.