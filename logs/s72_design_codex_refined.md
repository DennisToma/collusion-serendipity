The payoff calculations and descriptive statistics look sound. I found two provenance guard gaps to address before claiming complete protection.

1. **Older-science coverage is incomplete.** [s72_temporal.py:78](/home/factory/collusion/collusion-serendipity/scripts/s72_temporal.py:78) selects tracked files under `data`, `results`, `figures`, `sim`, `scripts`, and `llm.py`. This omits older top-level scientific designs such as `DESIGN_S68.md`; inherited S29/S53 inputs do not provide comprehensive coverage. Such designs can change without triggering the advertised “all older tracked science bytes” protection. Include the older design inventory explicitly.

2. **The standalone registration verifier accepts incomplete manifests.** [s72_independent.py:61](/home/factory/collusion/collusion-serendipity/scripts/s72_independent.py:61) checks hashes supplied by the manifest without validating the required inventory or exact split append. An entirely synthetic, in-memory check confirmed that empty hash dictionaries pass `verify_registration`. The release path additionally invokes the stronger `checked_manifest`, so this is a standalone-checker assurance gap, rather than a demonstrated corruption of released calculations.

The scientific implementation otherwise matches the design:

- The comparator correctly applies both employees’ unique stage Nash actions at fixed statuses. Individual excess and pair excess identities are consistent with directed rewards.
- Actual and benchmark payoffs are summed before requiring strictly positive excess for both employees. Equality fails; positive pair totals cannot substitute for two-person gains.
- All ten games contribute primary rounds 3–10, with fixed single-round, disjoint two-round, and full-window summaries. All seven measures appear in the presentation, with the correct game-level denominators.
- Shared-minus-self differences preserve seed pairing. Bootstrap enumeration uses all \(5^5=3125\) ordered block resamples, rational linear percentile interpolation, and the correct paired \(t\) interval with four degrees of freedom.
- Twelve read-only synthetic tests passed, including exhaustive 16-stage and 256 two-stage profiles. I skipped the two tests that write temporary files.

The acknowledged limitations are appropriately scoped: posthoc selection, five reused blocks, dependent measures, descriptive intervals, arbitrary pair boundaries, and a fixed-status comparator that does not establish repeated-policy effects, agreement, reciprocal intent, or long-run profitability. No new HIT rule or hypothesis test is introduced.

I read all six requested files. No edits, scientific model calls, subagents, or archived S29 outcome inspection occurred. Registration, source replay, release reproducibility, and clone execution remain unverified in this pre-registration review.