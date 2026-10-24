**S18’s frozen DUD is correct.** No edits or live model calls were made.

Independently reconstructed from raw game decisions:

- Partner FAIL approvals: **0/40 self, 0/40 shared**; all five paired differences zero.
- Enumerated **3,125 bootstrap resamples per interval**, reproducing all 21 intervals exactly with rational arithmetic. Primary bounds: **[0,0]**.
- Enumerated all **32 sign flips**, reproducing every reported tail probability. Primary upper-tail **p=1**.
- Reproduced all t intervals and the supporting pair-bonus difference **−3/20 points/round**. Registered screening logic yields **DUD**.

Full cache-only replay consumed all **300 request/response keys exactly once** and reproduced the saved result exactly. All 13 frozen source hashes, registration ancestry, exports, chronology, paired overlap and block barriers passed validation. Six non-writing tests passed, including exhaustive stage incentives, truth balance, visibility, parsing, screening and invalid-response abort behavior. Approval incentives and reciprocal payoffs are correct; sequential execution exposes no current-round decisions or notes to later employees.

**Concrete remaining bug — Low severity:** [scripts/s18_independent.py](/home/factory/collusion/collusion-serendipity/scripts/s18_independent.py) does not require the complete prespecified aggregate metric set and hardcodes `sign_tests=21`. An in-memory negative probe removed `organization_loss`; verification still returned `passed=true`, reporting 18 bootstrap intervals but 21 sign tests. Remedy: assert the exact seven metric keys, required summary fields and denominators; calculate verification counts from checks actually performed. The canonical artifact contains all seven metrics, and my independent reconstruction verified them, so this does **not** change the current verdict.

**Acknowledged limitations:** Five selected exploratory blocks; degenerate empirical bounds do not establish population zero risk or equivalence. The intervention bundles access wording, received notes, context length and endogenous writing. Public histories permit reciprocity in both arms; the bonus gate is mechanically related to approvals. Provider execution, model identity and sampling remain client observations. Internal transport retries, cutoff races and non-atomic cancellation are explicitly disclosed.

The report appropriately confines conclusions to synthetic labeled submissions and this directional screen; it does not establish realistic workplace behavior, agreement or collusion.

Unchecked: fresh clean-clone reproduction, crash/disk-loss fault injection and provider-side attestation. Earlier pilots were not reviewed.