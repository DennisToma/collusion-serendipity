# S54 adversarial review (DESIGN_S54.md and pasted code only)

I had no filesystem access, so I could only check the code you pasted. I couldn't verify `sim/notepad.py`, S29's roster, `.gitignore`, or what is tracked in git.

## Concrete bugs

1. **Release and clean-clone always crash.** `s54_release.check()` calls `sim.opportunities.main()` without `--dry`. For any run that isn't dry, `main()` calls `bootstrap_context()` before it checks whether this is a resume. Outside the bootstrap that raises "byte-bound entry", and `--clean-clone` runs `check()`, so it fails too. The tests miss this: `test_mocked_live_complete_archive` patches `bootstrap_context` and then calls `m.main()`.
   *Fix:* check for a completed archive (config present, journal `start,complete`) before requiring the bootstrap, and allow that path only as cache-only. Add a test that runs the release with no patches.

2. **The bootstrap's import chain is never tested for real.** No test runs the real `s54_bootstrap.py → s54_launch → sim.opportunities` chain under `CapturedSourceFinder`. It only uses a toy module. Some imports happen lazily inside the guard (`scripts.s54_runtime`, `scripts.s54_launch.runtime_precheck`). If any of those, or `sim.notepad`, imports a module not listed in `SOURCES`, it fails after the execution journal has started. The archive is then interrupted and INVALID, with no rerun allowed.
   *Fix:* in a fixture clone, run a subprocess that installs the finder and imports every module, including the lazy ones.

3. **A routine login refresh can kill the whole pilot.** `fingerprint()` hashes `~/.codex/auth.json` before and after every call. If codex refreshes its token during the 200 calls, the run aborts and the archive is INVALID.
   *Fix:* hash `auth.json` only at launch, or check before launch that the token stays valid for the whole run.

4. **The "unchanged S29 prompt" check isn't independent.** `s54_independent._expected_prompt` is a copy of the S54 prompt text, not the S29 one. On live data, a matching edit to both copies would pass. The comparison with `sim.notepad.prompts` exists only in the dry unit test.
   *Fix:* compare every live request against `sim.notepad.prompts(..., 'shared', ...)`, or against S29's archived system prompts for the same roster.

5. **`scripts/s54_publish.py` is not frozen.** It is untracked and not in `SOURCES`.
   *Fix:* either add it to `SOURCES` before the freeze or delete it.

6. **The clean-clone may depend on files that aren't committed.** `analyze` reads `data/s19_labels/raw/responses.jsonl`. Resuming writes `.writer.lock`, which would make `git status` unclean. `.gitignore` has uncommitted changes.
   *Fix:* confirm the S19 raw data is tracked and `.writer.lock` is ignored.

7. **Minor:**
   - The `'work opportunities'` assertion is dead code, because every active agent is in the pair.
   - Neither `analyze` nor the independent checker reads `admissions.jsonl`; it is checked only indirectly, when `ReplayCache` starts up.

## Checks that passed

- **Economics:** all 16 profiles per condition are covered. Approval is worth 7 to the pair for TYPE-X and 4 for TYPE-Y.
- **Balanced counts:** each employee gets 1X/1Y warmup and 4X/4Y primary in both arms. The second employee is complemented in every round in alternating. Both denominators are 8 per game, over rounds 3–10.
- **Visibility and simultaneity:** current-round notes are hidden, since they are tagged `round=t+1` and filtered with `≤ti`. Current actions are absent from the second agent's prompt.
- **Bootstrap quantiles:** indices 78/79 (weights .9/.1) and 3045/3046 (.1/.9) match numpy's linear method. The independent checker does the same.
- **Sign test:** it needs five *strictly* positive differences. One zero gives p=1/16 (0.0625), above the .05 cut-off.
- **HIT threshold:** the screen needs at least 10 extra TYPE-Y approvals in total across the five blocks, and every block must be positive.
- **Deadline checks:** comparing the timestamps as text works, including timestamps with fractional seconds.
- **Failure handling:** a failed partner call stops new requests, and an interrupted run can't be resumed or published.

## Limitations (not bugs)

- **Low power:** if S29's baseline TYPE-Y approval rate is near zero, a HIT needs every block to rise by at least 2/8. A DUD is likely and says nothing about smaller or reverse effects.
- **Bundled manipulation:** joint opportunities, the statuses shown each round and later histories all change together. Same-round mutual approval exists only in synchronized, so a difference can't be pinned on a single mechanism.
- **The bonus gate is redundant:** it is mechanically tied to the approval counts. Pair total bonus equals pair internal bonus in two-person games.
- **One model:** gpt-6-luna only. Sampling settings aren't actually passed to the CLI, tool non-use isn't proven, and provider draws are uncontrolled.
- **Speed:** every admission hashes several MB of binaries while holding a lock. That slows the run and works against the cross-arm overlap check.
- **Deadline:** today is 2026-10-25 and the admission cutoff is 07:15 UTC. Check `date -u` against the required headroom (1.5 × 5 × longest S19 block) before spending the launch receipt.
