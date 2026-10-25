One unresolved medium finding; no remaining high finding in the latest version inspected.

- **Medium — “exact complete result match” permits type changes.** [portfolio_replay.py:140](/home/factory/collusion/collusion-serendipity/scripts/portfolio_replay.py:140) compares decoded objects using Python equality. I confirmed the expression accepts `{"primary_estimated": false}` versus `{"primary_estimated": 0}`, and counts of `1` versus `true`. This can conceal scientific metadata regressions. Require type-aware recursive equality, treating booleans separately from numbers.

Concurrent changes resolved two earlier findings: S67 now uses its compatible historical revision, and repository output paths are restricted.

Verified read-only:

- Exactly 54 distinct inventory entries and result mappings; all 54 artifacts match their currently selected revisions byte-for-byte.
- S16/S68 use failure audits without estimating effects.
- The `llm.chat` guard precedes analyzer/checker imports.
- Fifty existing checker entry points resolve; S01/S02/S16/S68 have no additional checker in this runner.
- Preservation checks cover tracked files and retained data, excluding writer locks.

**Completion remains unverified:** no iteration58 receipt or reproduction document existed at final inspection. [REPORT.md:7](/home/factory/collusion/collusion-serendipity/REPORT.md:7) still describes iteration57’s selected reproduction and appropriately limits its claims.

No edits, scientific calls, installs, subagents, or replay sweep performed. These checks establish deterministic consistency scope—not scientific validity, comprehensive raw provenance, independent replication, isolation, fresh installation, or external execution attestation.