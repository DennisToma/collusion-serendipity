# S37 fixed-grid payroll wording pilot

Five fresh paired seeds24800..24804,two conditions(coded,payroll),T10.
Both quote integer10..30;worker take-home and employer cost are quote minus10.
The trajectory `price` field stores the raw quote;`resource_payment` stores
normalized take-home pay. Shares and profits use normalized economic units.
Owner-only notes,public completed rounds,hidden current choices. Ground-truth
agreement/coordination/execution fields stay null;no intent labels are inferred.

`config.json` freezes sources,requested route,local-input fingerprints and
dependency versions. `schedule.json` fixes randomized within-block launch order.
`game_*.json` holds each complete trajectory and provenance. `raw/` retains
fsynced pre-transport admissions,requests,responses and execution receipts.
`trajectories.jsonl` and `ground_truth.jsonl` are canonical complete-game exports.
Interrupted or failed prefixes cannot support effect estimates or live resumption.

See [registered design](../../DESIGN_S37.md),[split index](../SPLITS.md),and
[reproduction instructions](../../README.md). No pooling with S36;the wording
contrast bundles labels,wording and length and cannot identify a mechanism.
