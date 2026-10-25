**No unresolved methodology or correctness issue found that blocks a valid live pilot**, subject to the registered launch gates.

- Both parsers catch `RecursionError`; the deep-nesting regression passes.
- [The mocked live test](/home/factory/collusion/collusion-serendipity/scripts/test_s35.py:29) exercises launch/main, 200 mocked non-dry calls, analysis, independent/exact checks, presentation, and completed resume. It also checks interrupted-journal and failure-marker rejection.
- [The actual live checker](/home/factory/collusion/collusion-serendipity/scripts/s35_analyze.py:127) now calls the strict overlap validator.
- Independently recomputed the [historical receipt](/home/factory/collusion/collusion-serendipity/logs/s35_historical_validity.json): all four hashes match; each pilot has 200 valid, zero invalid responses under its own schema. The recorded proceed decision addresses the earlier concern, without guaranteeing future compliance.
- The contrast is consistently **asymmetric minus symmetric**. Independent verification checks **five sign sets, 15 inclusive tails**; the exact companion checks 15 rational summaries.
- The launch lock gap remains advisory: main serializes data writers, exclusive receipt creation prevents a second launch receipt, and incomplete execution journals block publication even if failure-marker writing fails.

Five-block precision, sign-flip assumptions, bundled incentive effects, and limited provider/configuration attestation remain acknowledged limits, not implementation bugs.

**Validation:** 13 read-only-compatible tests passed. The full-suite attempt encountered 10 sandbox errors from prohibited temporary/cache writes, so I could not independently rerun the mocked pipeline here. The existing protocol log reports all 23 tests passing. No edits or live model calls were made.