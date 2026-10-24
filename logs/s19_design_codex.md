Reviewed all eight requested files. Six read-only tests passed, covering economics, balance, parsing, visibility, labels and screening arithmetic. No edits or live model calls.

**Remaining bugs**

- **Medium — Completed-archive invocation skips replay and rewrites exports.** In [sim/labels.py:293](/home/factory/collusion/collusion-serendipity/sim/labels.py:293), a completed journal enables cache-only mode, but existing games are skipped; schedule and exports are subsequently rewritten without validating those games against cached responses. A modified game can therefore propagate into exports while the command reports success. The analyzer’s mandatory replay should reject it later, limiting publication risk. **Remedy:** make the completed-invocation branch validate every game and consume every cache key before returning; preserve existing exports.

- **Low — Recorded analysis environment is unenforced.** [scripts/s19_analyze.py:115](/home/factory/collusion/collusion-serendipity/scripts/s19_analyze.py:115) checks frozen sources and experimental settings but never compares `cfg['environment']` with the running Python/NumPy/SciPy versions. Hashing `uv.lock` does not establish that its environment is active. Reanalysis can silently use different numerical dependencies, particularly for t intervals. **Remedy:** enforce the recorded versions or explicitly record and flag the reproduction environment.

- **Low — Failed transport attempts lack start timestamps.** [sim/labels.py:85](/home/factory/collusion/collusion-serendipity/sim/labels.py:85) journals the request, error and failure time, but the start timestamp created inside `Cache.call` is lost when transport raises. This leaves failed-attempt timing incompletely archived. **Remedy:** capture the logical-call start before transport and include it in failure records.

**Checks without a remaining defect**

Payoffs implement author +6 and reviewer +1/−2 correctly. Matched truth schedules and denominators 8/8/8/24 agree with the design. Sequential requests preserve informational simultaneity: current actions and notes remain hidden, and reasoning is never replayed. Bootstrap interpolation, inclusive sign flips, contrast direction, bonus gate and HIT-first screening match registration. Publication analysis requires complete-key replay and rejects failed or incomplete datasets.

**Acknowledged limitations**

Five selected exploratory blocks, bundled semantic framing, unverified agreement or intent, mechanically related bonus gating, uncontrolled API draws/shared-service interference, client-only timestamps, and deadline/cancellation races are already disclosed. They constrain interpretation rather than constitute newly discovered bugs.

This reviews implementation and tests; it does not certify a completed live archive.