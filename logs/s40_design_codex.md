S40’s causal scope and core arithmetic match its design. I read all eight requested files; performed read-only, in-memory checks; made no edits or paid calls. No live S40 archive is present, so execution integrity remains unverified.

**Concrete remaining bugs**

- **Successful output can be lost on accounting failure.** [llm.py:213](/home/factory/collusion/collusion-serendipity/llm.py:213) writes its accounting log before returning the model response. If that write fails, S40 records a transport failure without preserving the returned text. I reproduced this with a mocked backend. The pilot aborts safely, but “retain every response” is not guaranteed.
- **The separate verifier accepts missing published cases.** [s40_independent.py:47](/home/factory/collusion/collusion-serendipity/scripts/s40_independent.py:47) checks only entries supplied in the result’s `cases` array. I confirmed `cases=[]` passes with otherwise correct synthetic data. Require exactly the ten expected case IDs, each once. Release’s full `analyze()` comparison currently catches this omission.
- **Registration replay omits the headroom check.** [s40_replay.py:180](/home/factory/collusion/collusion-serendipity/scripts/s40_replay.py:180) checks receipt equality, ancestry and committed hashes, but does not revalidate the receipt timestamp’s timezone or twenty-minute headroom. The launcher enforces headroom; retrospective validation does not independently establish it.

**Checks that passed**

Selection reconstructs all ten specified histories, with nine owner-only notes each; every archived selected quote is 10. Selection uses roster position without searching action semantics. Retain preserves the archived prompt; erase replaces only its notes array.

The outcome correctly subtracts 10 from the focal quote: **normalized offer**, never realized worker payment. Cases are averaged within five source seeds. Bootstrap enumeration/interpolation, paired-t calculation and inclusive sign flips match the specification; independent numerical spot checks passed.

Scheduling implements two case workers, sequential randomized arms and seed-block barriers. Strict parsing, fixed-model deduplication, source binding, one-shot receipt and rejection of incomplete/failed archives are present. Existing tests mainly exercise dry execution; live registration, runtime drift and transport-failure paths lack comparable direct coverage.

**Acknowledged limits**

This is an observed, floor-enriched challenge, not held-out discovery. Erasure jointly changes note availability, length, factual completeness and consistency with the complete-notepad promise. Public history retains prior behavior; a null cannot establish memory irrelevance. Without floor reproduction in fresh retain controls, a difference cannot explain the original floor.

Five blocks and uncontrolled model draws provide descriptive uncertainty, not calibrated population or equivalence inference. CLI temperature/token settings are unenforced; effective configuration, provider behavior, tool non-use and transient drift remain unattested. No result establishes intent, coordination, collusion or downstream worker-payment effects.