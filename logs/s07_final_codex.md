S07’s numerical results and **DUD for predicted output increase** verdict reproduce. I found **three medium-severity validation/protocol bugs** and several documentation inaccuracies. None changes the completed dataset’s estimate. No files were edited or live models run.

1. **Medium — `--allow-dry` bypasses mandatory verification for live data.**  
   [s07_analyze.py:177](/home/factory/collusion/collusion-serendipity/scripts/s07_analyze.py:177) gates verification on the CLI flag rather than the dataset’s actual `dry` value.

   In memory, I supplied a corrupted trajectory export and invoked the CLI with `--allow-dry`. It accepted the live dataset and reached publication of `dry: false` results without checking the export. The ordinary verifier rejects that corruption.

   **Remedy:** verify every live dataset regardless of `--allow-dry`; preferably verify every publication. Keep permission to analyze synthetic data separate from publication checks.

2. **Medium — restarting forgets the registered terminal failure.**  
   [legality.py:244](/home/factory/collusion/collusion-serendipity/sim/legality.py:244) tracks failures only in the current invocation. Existing `failure_game_*.json` files are ignored. A restart can retry a transport-failed game and then start later blocks, contrary to the registered stop-at-failed-block amendment. [s07_analyze.py:121](/home/factory/collusion/collusion-serendipity/scripts/s07_analyze.py:121) and the verifier also ignore failure markers.

   A synthetic, entirely in-memory restart with an existing failure marker submitted all ten games. Permanent cached parsing failures would still fail again; recoverable transport failures expose the continuation path.

   **Remedy:** persist a terminal experiment status, refuse further calls after a recorded terminal failure, and reject publication when failure records exist. There are **no failure markers in the actual dataset**, so this did not affect this run.

3. **Medium — registration metadata is recorded but not validated.**  
   [s07_analyze.py:95](/home/factory/collusion/collusion-serendipity/scripts/s07_analyze.py:95) checks current source hashes but never resolves `registration_commit` or compares its source blobs with the manifest.

   I replaced the registration commit with forty zeros in memory; full verification still succeeded. Fabricated environment and requested-temperature metadata were also accepted. Hashing the supplied configuration establishes consistency with that input, not its correctness.

   **Remedy:** validate the registration commit and its source blobs, check requested configuration fields, and distinguish recorded execution versions from recomputation versions.

   **Actual-run check:** every frozen source matches both the manifest and commit `fdbd7426…`. All recorded verification hashes match the current artifacts.

The independent numerical reconstruction found no discrepancies:

| Primary-window metric | Neutral | Legality | Difference [bootstrap 95%] | Paired t 95% |
|---|---:|---:|---|---|
| Pair output/firm | 5.800 | 4.844 | −0.956 [−2.889, +0.267] | [−3.592, +1.681] |
| Outsider output | 6.022 | 6.044 | +0.022 [−1.689, +1.444] | [−2.545, +2.589] |
| Price | 12.378 | 14.267 | +1.889 [−1.467, +7.400] | [−5.666, +9.444] |
| Pair profit/firm | 36.400 | 26.000 | −10.400 [−19.467, −3.460] | [−23.717, +2.917] |
| Outsider profit | 38.378 | 34.489 | −3.889 [−13.333, +5.133] | [−17.920, +10.142] |
| Message words | 21.144 | 0.000 | −21.144 [−24.044, −19.244] | [−25.075, −17.214] |
| Nonempty-message fraction | 1.000 | 0.000 | −1.000 [−1.000, −1.000] | [−1.000, −1.000] |

I checked all **210 game/metric/window cells**, all **21 bootstrap intervals**, all **seven paired-t intervals**, seed differences, and every numeric table entry in the summary. All-round and final-round aggregates also match.

The exact primary difference numerators are **[6, −14, 6, 0, −84]**, each divided by 18. Their overall mean is **−43/45 = −0.955555…**. Exhaustive enumeration gives:

- Higher-output p: **26/32 = 0.8125**.
- Lower-output p: **8/32 = 0.25**.
- Verdict: **DUD**, exactly as registered.

For five blocks, the implemented rules simplify to:

- **HIT:** every numerator strictly positive and their sum ≥90.
- **ODD-reverse:** every numerator strictly negative and their sum ≤−90.
- **DUD:** otherwise, sum ≤22.
- **ODD:** remaining cases.

The positive-bootstrap-bound requirement is redundant for HIT. The `.25` mean boundary is unattainable on this denominator. DUD is a screening label; it does not establish equivalence or absence of an effect.

Other checks also reproduce:

- **378 responses = 360 decisions + 18 additional attempts.** Neutral has six additional attempts across five retried decisions; legality has twelve across eleven. All eighteen rejected outputs exceed the reasoning-word cap.
- Messages are **120/120 nonempty neutral versus 0/120 legality**.
- Block 24084 contributes **−4.666667**; the other four average **−0.027778**. Its legality pair has **16/18 zero actions** and mean profit **8**.
- The cited q12-against-12/0 calculation yields **profit 0**, confirming the model note’s arithmetic error.
- All games complete by **16:45:39.639 UTC**, before 17:05.

There are also **low-severity documentation corrections**:

- The supplementary checker’s freeze at **16:33:13.698** followed **60 completed responses**. Calling it “pre-outcome” in [s07_summary.md:84](/home/factory/collusion/collusion-serendipity/results/s07_summary.md:84) overstates its timing. It preceded the first completed game, not observed actions. The production registration predates live calls.
- [DESIGN_S07.md:81](/home/factory/collusion/collusion-serendipity/DESIGN_S07.md:81) says “>35 minutes at launch”; the actual first call left approximately **34 minutes 9 seconds**.
- The archived [Opus HIT wording](/home/factory/collusion/collusion-serendipity/logs/s07_design_opus.md:86) incorrectly implies ≥1 more unit in every block. HIT requires positive differences in every block and an **overall** mean ≥1. Its scalar coalition benchmark is also incomplete: integer pair-total/outsider equilibria are **(7,9), (8,8), (9,7)**. The current design already rejects that oversimplification.

The remaining concerns are **limitations, not demonstrated outcome bugs**. Independently reconstructing all 378 request histories found no harness-mediated same-round, outsider, own-sent-message, or saved-reasoning leakage. Backend filesystem/tool isolation remains unproven because the transport retains final text rather than execution events.

Five blocks, uncontrolled backend sampling, conditional sign-flip assumptions, and portfolio multiplicity limit inference. Every firm receives the cue, including the outsider; the outsider is therefore not an untreated control. The experiment identifies a contrast between these complete prompt packages under the registered retry procedure. It does not identify channel mediation, legal enforcement, verified compliance, or collusion. The current headline respects that scope.

Full cache-only verification passed with model calls blocked. Four existing nonwriting S07 tests passed; I did not rerun tests that create files.