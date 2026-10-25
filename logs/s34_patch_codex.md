One remaining blocker: **zero-duration transport overlap still passes**. [s34_analyze.py:125](/home/factory/collusion/collusion-serendipity/scripts/s34_analyze.py:125) uses `latest_start <= earliest_completion`. An in-memory fixture with serial intervals `[4s,40s]` and `[40s,75s]` passed. Require strict `<` to establish positive-duration overlap, and add an endpoint-touching canary.

The preflight/headroom gap appears fixed:

- `runtime_precheck` records `checked_utc` and calculates remaining time from that exact timestamp.
- Publication validation recomputes headroom and enforces runtime-check → dispatch receipt → first admission; per-request checks then enforce admission ≤ transport start.
- `TenderCache.call` rechecks required headroom at first admission. A mocked insufficient-headroom case rejected before transport.

The new mutation test passes, but its coverage needs strengthening. The `serial` mutation also exceeds the 60-second start limit, so it cannot independently detect removal of the overlap check. The `late_runtime` mutation also invalidates remaining-time arithmetic. Add isolated mutations and a persistent first-admission rejection test.

Scoped, in-memory checks confirmed rejection of disjoint intervals whose starts differ by only 37 seconds, overlapping intervals starting 61 seconds apart, and late runtime timestamps with otherwise consistent arithmetic.

No edits or model calls. No live archive was available; this review establishes synthetic behavior only.