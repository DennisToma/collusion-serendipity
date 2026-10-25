# S56 adversarial review (I only had the supplied text; the raw archive wasn't available)

## Concrete bugs

1. **`test_joint_gain_can_sacrifice_member` is wrong and should fail.** At (7,7,20) each pair member earns 1/2. If both pair members bid 19, each earns 13/2, which is a strict gain for both with no transfers. So `decompose` correctly returns `strict_pair_improvement=1`, and the assertion that it equals 0 fails. Of the five design-mandated test categories, this one ("sacrifice versus Pareto") currently has no valid example. A correct one is **(18,20,20)**: pair joint regret is 1 (13 − 12), and no pair bid choice raises both members, since (19,19) gives 13/2 < 12 and (20,20) gives 14/3 < 12.
2. **`test_missing_manifest_file_detected` tests nothing.** It patches `required_files` but then calls `p.digest('/nonexistent')` directly, so the error is guaranteed. `checked_manifest` never runs.
3. **Several promised corruption tests don't exist.** There are no tests for:
   - wrong or swapped `assigned_pair`;
   - changed or missing archive or source bytes passing through `checked_manifest`;
   - tampered round records, game cells, totals or census passing through `verify()`;
   - raw-binding tampering.

   The only tampering test edits `ci95_exact`.
4. **Half-done "byte-equivalent as parsed JSON" check.** The code compares the live `original_analyze(...)` object with `json.loads(file)`, but never round-trips the live object through JSON. Tuples, NaN, or non-string keys would cause false mismatches, and the check is not what the design describes. It fails loudly, not silently. Fix: compare `json.loads(json.dumps(original, sort_keys=True))`.
5. **The replay isn't visible in this code.** The design requires an "all-key exact-request replay". The code only re-runs `s14_analyze.analyze` and `s14_independent.check`. Unless `check` replays the cached requests itself (I couldn't confirm), that step isn't implemented.
6. **The summary table doesn't report all 24 summaries.** `s56_summary.md` shows arm means without intervals and gives intervals only for the 8 contrasts. The 16 arm-level bootstrap and t intervals exist only in the JSON. The design says arm means and contrasts are "all" reported with both intervals.

## Fragile or unverified (needs the raw archive)

- **Round window.** Both the production script and the "independent" one assume `rows[3:12]` and 0-based `row['round']`. Neither checks `rows[i]['round']==i` or `len(rows)==12`. The cross-check of payment and pair_profit against S14 partly guards this, but the independent script shares the assumption.
- **Request identity.** `payload[5:9]` is assumed to be (run_id, round, agent, attempt). A wrong guess would fail loudly, but the meaning isn't stated anywhere.
- **Archived profits.** Only production compares computed profits with archived ones, using exact float equality. The independent script never compares its payoffs with the archived profits. If archived profits are scaled ("bonus units") or rounded, the run aborts.
- **Remote receipt.** It is self-attested: `remote_main==commit` is written and checked by the same process, and the remote isn't re-queried at analysis time.
- **Raw bindings.** These check that the last attempt's bid matches the price and that every response is used. They don't check that earlier attempts actually failed, or that prompt content matches the game history.

## Checked and correct

- **Payoffs.** The two implementations agree. The maximum pure-Nash payment is 7: (8,8,8) can be undercut for 1 > 2/3, while (7,7,7) holds.
- **Stable set (my hand derivation).** The fixed-pair/outsider stable set is the 29 profiles with outsider = 6 and min(pair) = 6, plus (7,7,7): 30 profiles, payments {6,7}. The census logic should reproduce this, but nothing asserts it against an external expectation. Worth adding.
- **Metric 7 is almost determined by metric 3.** Being stable implies payment ≤ 7, so `coalition_stable` ≤ 1 − `above_nash` in every round. That should be stated, not just covered by "metrics may be related".
- **Strong-equilibrium caveats.** They are stated correctly. `pair_joint_regret` checks pair-total gains with the outsider fixed and `strict_pair_improvement` checks gains for both members; no individual-member or grand-coalition checks are claimed.
- **Bootstrap.** All 3125 ordered resamples, type-7 linear interpolation with exact fractions, and the same five blocks for arms and differences, matching the independent script.
- **t intervals.** A ddof=1 float compared with the exact `statistics.stdev` at 1e-12 is fine, and degenerate zero-variance cases are handled.
- **Model-call blocking.** The `llm.chat` patch is applied before the S14 imports, so `from llm import chat` binds the mock. This would break if those modules were already imported, for example by a test run in the same process.
- **Release.** Staging, byte-identity, and the all-or-none artifact check look sound.

## Acknowledged limitations (not bugs)

- post-hoc reuse of outcomes;
- n=5 blocks with uncorrected intervals;
- one model;
- static counterfactuals that don't re-run any agent;
- no real transfers;
- divisible ties and a bounded bid grid;
- unattested provider identity and OS-level non-use of tools;
- the bootstrap differs from S14's;
- reuse of the existing venv.

All are disclosed adequately.

## Verdict

Fix bugs 1–3 before freezing. They are in `test_s56.py`, which is in the hash manifest, so a fix after registration breaks the manifest. Then either confirm or implement the replay (5), and add the 16 arm intervals to the markdown table (6). The ODD/context-only verdict is appropriate; nothing here supports promoting a HIT.
