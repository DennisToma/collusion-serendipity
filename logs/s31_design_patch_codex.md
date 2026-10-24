No remaining blockers found in the requested prospective S31 fixes.

- **Transport:** [labor_cache.py:57](/home/factory/collusion/collusion-serendipity/sim/labor_cache.py:57) pins `codex/gpt-6-luna` and passes `retries=1`. An independent mock through the real `llm.chat` wrapper confirmed exactly one backend invocation; its first failure propagated, was recorded, set terminal abort, and prevented subsequent admission.
- **Acceptance:** Mocked execution accepted the first valid response immediately, including after an invalid response. The complete independent verifier accepted a synthetic 200-key archive and rejected a modified history that discarded an earlier valid response. Duplicate keys, extra fields, boolean/float wages, and nonfinite values were rejected.
- **Deadline:** [labor.py:101](/home/factory/collusion/collusion-serendipity/sim/labor.py:101) applies the cutoff to uncached admission. Mocked checks confirmed that an admitted response finishing afterward is accepted, subsequent uncached admission is denied, and cached replay remains available. This matches `DESIGN_S31.md`.

The guarantee concerns one logical backend invocation per parsing attempt; Codex CLI internal retries remain unobserved, as documented.

No live model calls, edits, filesystem writes, or historical outcome inspection.