Found two remaining publication-integrity bugs. The economics, hidden-current-action visibility, statistic arithmetic, and HIT/DUD/ODD rule appear internally consistent.

1. **High — rendering bypasses archive eligibility checks.** [s38_present.py:14](/home/factory/collusion/collusion-serendipity/scripts/s38_present.py:14) calls only the independent verifier. That verifier reconstructs actions and statistics but omits the main analyzer’s execution-completion, failure-marker, cutoff, overlap, frozen-source/environment, and registration checks.

   **Concrete reproduction:** an entirely in-memory synthetic archive passed `verify()` with all 200 admissions dated 2099, missing invocation timestamps, and configuration containing no source/environment freeze. Consequently, direct presentation can accept evidence that the main analyzer would reject.

   **Remedy:** require full `analyze()` validation before live rendering, compare its reconstructed result with the supplied result, and retain independent arithmetic verification. Add presentation regressions for interrupted execution, failure markers, late admissions, and source drift.

2. **Medium — displayed audit claims are unverified.** [s38_independent.py:71](/home/factory/collusion/collusion-serendipity/scripts/s38_independent.py:71) does not bind `cached_responses`, `invalid_attempt_retries`, `notes`, or `limitations` to raw evidence or frozen text. [s38_present.py:24](/home/factory/collusion/collusion-serendipity/scripts/s38_present.py:24) prints these supplied fields.

   **Concrete reproduction:** the same verifier accepted `cached_responses=-999`, negative retry counts, fabricated notes metadata, and fabricated limitations while returning `passed=True`.

   **Remedy:** recompute audit counts from raw records and require the registered limitation text; validate every field consumed by presentation.

**Acknowledged limitations, separate from bugs:** five exploratory blocks; unobserved hidden-horizon beliefs; disclosure cannot isolate a belief mechanism; multiple stage equilibria; passive fixed-supply labor; no verified agreement or intent; sign-flip calibration assumptions; unenforced provider sampling parameters; incomplete effective-configuration/provider/tool-use attestation; and invocation overlap that cannot establish provider scheduling. These appropriately constrain causal and confirmatory claims.

Validation: read all twelve requested files; 13 selected tests passed, including exhaustive economics and screening checks. The adversarial reproduction used memory-only fixtures. No edits or live model calls.