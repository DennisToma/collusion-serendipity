# S22 review: no launch-blocking bugs found

I reviewed only the pasted S22 files. I made no edits, made no model calls and did not run any tests.

## Checks that passed (traced by hand)
- **Economics:** a certain approval nets 1−3 = −2. A lottery approval nets ¼(−11) + ¾(+1) = −2. The −2 is stated in both prompts. A reciprocal partner pair nets +4 expected each, and the organization loses 20.
- **Denominators:** pair→partner, pair→outsider and outsider→pair are each 8, and TYPE-X approvals are 24 per game, all asserted.
- **Exact-count recovery:** every metric is an integer over 8, except TYPE-X approvals (over 24), so recovering exact counts works.
- **Truth and simultaneity:** the prompt only uses earlier rounds' rows. Notes are appended after all three calls. Unused audit draws only ever appear as 0, which looks the same as an unaudited approval. The outsider note must be empty, and the canary test covers note leakage.
- **Statistics:** the bootstrap percentile matches numpy's linear method. The paired t uses df=4. The sign-flip test is inclusive. The HIT/DUD/ODD order matches the design.
- **Replay:** keys are rebuilt from the payload. Each key must be used exactly once. Cache bytes are compared before and after. Live calls are patched out. Torn or mismatched files are refused rather than repaired.
- **Failure handling:** any game exception sets the abort flag and writes a failure marker. The journal stays at start-only, so a resume is refused. Analysis refuses failure markers, transport-failure logs and partial arms.

## Remaining bugs (most serious first)
1. **Medium: the freeze and environment checks will break reproduction and presentation.** `analyze` checks working-tree hashes of all 19 SOURCES and requires the exact Python, numpy and scipy versions. So any edit after the run to `DESIGN_S22.md`, `s22_present.py`, `s22_release.py` or `test_s22_publication.py` makes analysis permanently fail. A clean clone on a different numpy fails too.
   *Fix:* finalize the presentation and release scripts before registering. Or split the sources into a frozen science set (sim, analyze, llm, lock files) and a presentation set that is versioned separately. The existing `git show <registration_commit>` check already covers the freeze, so the working-tree check can go. Record the environment and compare it with a logged warning.
2. **Low: lock race at launch.** `s22_launch.launch()` releases `.writer.lock` before `main()` takes it again.
   *Fix:* hold the lock across the receipt and the run, or skip the second lock when called from launch.
3. **Low: dead or misleading guards.**
   - `cache.cache_only=resuming` is always False, because the resume branch has already returned. `test_deadline_and_archive_no_live` tests a path the live run never uses; archive safety actually comes from the early return plus `ReplayCache`.
   - The abort check is duplicated.
   - The `if cfg['dry']` checks in the git-show loop are redundant.

   *Fix:* delete these, or wire `cache_only` in properly and test the real path.
4. **Low: abort and deadline checks are not atomic across the two threads.** A partner game can start an uncached call just after the other game aborts.
   *Fix:* re-check abort under `self.lock` right before `llm.chat`. The design already lists in-flight calls as a limitation.
5. **Low: the wording test only covers round 1.** `test_enforcement_wording_and_hidden_draws` uses an empty history, so its `assertNotIn('charges')` check proves little. The timing test does indirectly confirm that published charges equal realized penalties.
   *Fix:* add a lottery test with all-reject or TYPE-X-only history asserting that no 12 appears for edges with no TYPE-Y approval.
6. **Low: the source manifest misses some dependencies.** It omits `sim/__init__.py` and `scripts/__init__.py` if they exist, the codex CLI version and config, and the `compute.env` that `llm.py` reads. The backend is pinned and checked, so risk is small.
   *Fix:* hash these into the config, or list them as limitations.

## Limitations the design already acknowledges (not bugs)
- Realized lottery charges are not balanced on these schedules, and the realized-charge histories are endogenous.
- The treatment bundles risk, wording and salience together.
- The pair-score gate is mechanically tied to approvals.
- HIT needs all five blocks strictly positive: one zero block gives p = 2/32.
- A strong reverse effect is labelled DUD. I'd add a "reverse" flag to the result so readers don't confuse it with a null.
- There are only 5 blocks, with no correction for multiple comparisons.
- Model, backend and temperature come from client metadata only.
- The shuffled arm order means little, because both arms are submitted to the two workers at once.
- Sign-flip exchangeability may not hold under API interference.

## Verdict
I found no launch-blocking bugs. Fix #1 before the receipt is consumed, since afterwards it can't be undone; #2–#6 can wait. Then run `scripts/test_s22.py` and a dry run plus replay, which I did not run here. The design is then fit for its narrow exploratory screen.
