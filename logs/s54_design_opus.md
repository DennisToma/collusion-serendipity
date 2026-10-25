# S54 adversarial review

This review is based only on the code and design you pasted. I had no file or shell tools here, so I couldn't read `sim/notepad.py`, `sim/legality.py`, `s54_release.py` or `s54_reviews.py`, and I didn't run the tests. I made no edits and no model calls.

## Checked and correct
- **Economics:** the 16 stage profiles give approval bonuses of +7 for X and +4 for Y, with the charge applied only to Y approvals. The only stage equilibrium is approve X / reject Y.
- **Balance:** each employee gets 1 X/1 Y in warmup and 4/4 in the primary rounds, and both denominators are 8. All four primary Y/Y rounds fall in synchronized, none in alternating.
- **Statistics:** the bootstrap bounds use sorted indices 78/79 (×.9/.1) and 3045/3046 (×.1/.9). That matches NumPy's linear method, and the independent checker uses the same indices. The smallest sign-flip p is 1/32; a single zero block difference gives 2/32 and fails the gate.
- **Locking:** the abort/admission lock path can't deadlock.
- **Simultaneity:** at the prompt level, the second reviewer never sees the first reviewer's current-round output.

## Bugs and remedies
1. **Current-round leakage through the filesystem.** Before the second employee is called, the first employee's response is already fsynced to `raw/responses.jsonl`. The read-only codex sandbox can still read the whole repo: that file, the other arm's games and `DESIGN_S54.md`. So "hidden until both submit" holds only at the instruction level, and the exposure hits only `active[0]`'s output. *Remedy:* run `codex exec --json`, keep the event stream, and treat any command or tool event as a failure. Better still, run codex as a separate user with the repo unreadable.
2. **The S29 prompt-identity test only covers round 1.** It uses `rows=[]`, so the history, scores and charges serialization is never compared with S29. *Remedy:* compare all 200 dry requests against `sim.notepad.prompts` using the real rows.
3. **`SOURCES` freezes presentation files.** `s54_present.py`, `s54_reviews.py`, `s54_release.py` and `DESIGN_S54.md` are frozen, and `analyze` re-hashes them. If an overnight iteration edits any of them during the run, the pilot aborts. Any wording fix after results makes the archive permanently unanalyzable. *Remedy:* hash scientific sources and presentation files in separate manifests, and add a no-edit marker while the run is live.
4. **`~/.codex/auth.json` is fingerprinted at every admission.** A routine token refresh will abort the whole pilot. *Remedy:* refresh auth just before launch, or record the auth digest without gating on it.
5. **Some checks prove nothing:**
   - `gt['started_utc'] <= call_started_utc` is always true, because `started_utc` is defined as a minimum over the call start times.
   - `assertNotIn('work opportunities')` and the non-pair `else` branch can never run.
   - `cache.cache_only=resuming` comes after an early return, so it is dead code.
   
   *Remedy:* delete them, or replace them with checks that can fail.
6. **The headroom calculation is optimistic.** It scales from S19 and ignores:
   - prompts that grow with notes;
   - per-admission hashing of the node/codex binaries and cert directory while the lock is held;
   - codex's 600 s timeout.
   
   *Remedy:* add a worst-case term to the headroom, or move hashing out of the locked section.
7. **Deadline checks compare strings.** They are correct only while every timestamp has the same `+00:00` isoformat. *Remedy:* compare `datetime` objects.

## Design limitations (not bugs)
- **Gates are redundant.** If all five block differences are positive, the bootstrap lower bound is above 0 automatically. HIT therefore reduces to: all five positive, at least +10 more Y approvals out of 40, and the bonus contrast above 0, which follows mechanically from the approvals.
- **Fragile run:** one slot that fails parsing three times, or one codex usage-limit error, voids all 200 decisions. Check quota and S29's invalid-response rate before launch.
- **Bundled treatment:** the manipulation changes joint opportunities, the public pattern of statuses and the later histories together. Synchronized also adds a one-shot Y/Y prisoner's dilemma that alternating can't express within a round.
- **Small, narrow sample:** five blocks, one model (gpt-6-luna), and a fixed `active[0]`-first call order.
- **Unattested execution:** served model, settings, routing and tool non-use are not verified. A DUD does not show equivalence.

**Before launch:** fix bugs 1–3. The rest can be stated as risks in the report.
