S37-only review completed across all 12 requested files. No edits, live model calls, or write-producing tests. This is a static review; no S37 live archive was available.

Two concrete issues remain:

- **Low — Dry presentations lack a visible dry label.** [s37_present.py](/home/factory/collusion/collusion-serendipity/scripts/s37_present.py:12) permits dry rendering to alternate destinations, but the generated summary and figure present HIT/DUD/ODD without identifying synthetic data. Canonical-path protection prevents overwriting official outputs, but copied artifacts remain misleading. **Remedy:** prominently label both outputs “DRY / SYNTHETIC” whenever `r['dry']` is true.

- **Low — Economics audit count includes unchanged actions.** [DESIGN_S37.md](/home/factory/collusion/collusion-serendipity/DESIGN_S37.md:10) calls 18,522 evaluations “unilateral deviations.” That count includes 882 choices retaining the original action; there are 17,640 action-changing deviations. **Remedy:** describe “18,522 unilateral action evaluations, including 17,640 deviations.” Payoff calculations and equilibrium detection are unaffected.

I found no blocking implementation bug in the other requested areas:

- Both arms implement identical normalized wages, employer costs, allocations and profits. The three stated pure Nash profiles are correct.
- Sequential model invocation preserves informational simultaneity: current choices and notes remain unavailable to the partner; reasoning is never replayed.
- Cache replay binds reconstructed prompts, attempts, actions, notes, reasoning and provenance, consumes every key once, and checks unchanged raw bytes.
- The main analysis rejects incomplete execution, failure evidence, unmatched admissions and source/configuration drift. Admission checks serialize terminal aborts with new admissions.
- Metric denominators, rational bootstrap interpolation, inclusive sign-flip tails and screening precedence are consistent. At five blocks, HIT indeed requires every contrast strictly positive and mean ≥2.

**Acknowledged limitations, separate from bugs:** the treatment bundles labels, wording and length; five selected exploratory blocks provide limited inference; sign-flip calibration needs assumptions beyond enumeration; bootstrap bounds are descriptive; local fingerprints do not attest complete effective configuration, provider execution or actual tool non-use. These restrictions are stated adequately and preclude mechanism, coordination, replication or equivalence claims.