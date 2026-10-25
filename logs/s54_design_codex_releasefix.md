The concrete release correction is present. I found no remaining executable blocker in the reviewed paths.

- [main()](/home/factory/collusion/collusion-serendipity/sim/opportunities.py:393) requires bootstrap for new live generation and rechecks it under the writer lock. Existing archives must have exactly `start, complete` journal events; interrupted runs fail closed.
- Completed live archives reach full analysis without bootstrap, current CLI fingerprinting, or credential checks. Replay rejects missing keys before transport and requires every cached/request key exactly once.
- [Archive validation](/home/factory/collusion/collusion-serendipity/scripts/s54_analyze.py:131) compares every saved request against the unchanged S29 shared prompt, including prior rounds and partner notes. My read-only check passed all 200 synthetic requests and rejected a mutation to the final request.
- A fresh subprocess successfully imported the real simulation, analysis, release, and test module chain under `CapturedLoader`, with scientific calls forbidden. This check captured working bytes; it did not exercise Git registration.

Validation remains partial: 12 tests passed; 11 stopped at temporary-fixture creation because the filesystem is read-only. No live S54 archive exists here, so completed-live resume and release reproduction could not be exercised end to end. The added tests cover those paths, but I cannot claim they passed in this session.

No edits or scientific model calls were made.