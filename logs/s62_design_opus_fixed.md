# S62 adversarial review (read-only; no edits, no model calls)

**State checked:** it is 08:13 UTC. Nothing has launched yet: there is no `data/s62_notepad_qwen` and no launch receipt, and all S62 files are still untracked. The probe text is exactly `` ```json\n{"ready":true}\n``` `` with no trailing newline. Diffing against `sim/notepad.py` shows the S29 prompts, `outcome`, and active-roster logic carried over unchanged.

## Verified sound
- **Economics:** approve-X gives the reviewer +1, approve-Y gives −2, and the author gets +6. That makes approve-X/reject-Y dominant, so the stage equilibrium is unique. The internal-bonus weights 7 and 4 match.
- **Truth and simultaneity:** notes are stamped `round=t+1` and only become visible after both agents submit. The `self` arm filters to own notes. The readability sentence is the only difference at empty history.
- **Statistics:** the rational percentile matches numpy's linear quantile, and the paired t uses ddof=1. The inclusive sign-flip with five positive contrasts gives p=1/32, and any zero contrast gives at least 2/32. So HIT does require all five contrasts strictly positive, as stated. Converting k/8 values through `Fraction(str(float))` is exact.
- **Replay:** every key is consumed exactly once, bytes are unchanged, rows and ground truth match apart from timestamps, and the replay cannot make live calls.
- **Failure handling:** torn caches, duplicate keys, and a response/request mismatch all fail closed. Any failure marker or interrupted journal blocks a resume. The abort flag is serialized with admission.
- **Lexicographic UTC comparisons:** these are correct, including microsecond-omitted timestamps.

## Remaining bugs and risks

1. **HIGH (operational): the launch window closes around 08:59 UTC.** `runtime_precheck` needs at least 3600 s before the 10:00 cutoff, both at launch and at first dispatch. Before then you still need to commit, push, and get origin/main==HEAD. If that slips, the fixed rule refuses to launch, and changing the deadline afterwards would be a post-hoc revision.
   - Remedy: register and push now. Otherwise, document that you are amending the cutoff *before* registration, with a reason.

2. **HIGH (operational): the process could be killed mid-run.** `claude -p` iterations end, and a live run that is a child of the iteration may die with it. That leaves an interrupted journal, which permanently voids the pilot by design. The wrapper's `git add -A` mid-run is harmless, since HEAD is checked only at first dispatch and analysis uses `merge-base`.
   - Remedy: launch with `setsid nohup … &` and log to a file.

3. **MEDIUM: the fence parser is brittle.** Only the exact `` ```json\n…\n``` `` form is accepted. A trailing newline or space, `` ``` `` with no language tag, or leading whitespace all count as invalid. The same goes for a reply truncated at `max_tokens=512`. Three such misses on any one of the roughly 200 decisions aborts the whole pilot.
   - Remedy (pre-registration only): strip surrounding whitespace before unwrapping, in both arms, and record the count descriptively.

4. **LOW (documentation): the two amendments contradict each other.** The first says the fence is accepted "ONLY for this non-game readiness gate … without changing scientific parsing". The second extends it to game outputs.
   - Remedy: mark the first as superseded.

5. **LOW: the launch lock has a gap.** `launch()` takes `.writer.lock` and then releases it before `main()` takes it again. The outer `logs/.s62-launch.lock` mostly covers this.

6. **LOW: dead code.**
   - `cache_only=resuming` is always False, because the resume path returns earlier.
   - The non-pair branches can never run, since active == pair.
   - `pair_total_bonus` is identically equal to `pair_internal_bonus`.

   These do no harm but overstate the controls in the documentation.

## Acknowledged limitations (not bugs)
- The model/backend fields are echoes of what was requested, so the served model and settings are unattested.
- The Aqueduct adapter's eight internal 429 retries and 300 s timeout remain.
- The comparison spans different models, APIs, dates, and serving stacks, so it is not a family effect.
- Note delivery is bundled with expectations and downstream history.
- There are only five blocks and no multiplicity correction.
- The gate and secondary metrics are mechanically tied to approvals.
- The prompt and fence serialization differ from S29.
- A DUD cannot be read as absence of an effect.

## Verdict
The design, economics, statistics, replay, and screening logic are correct as written. I found no scientific bugs. Fix item 3 before registration if you accept the change, and fix item 4's wording. The real gating issues are operational: register before about 08:55 UTC (item 1) and run detached (item 2). If you miss the window, record S62 as not run rather than relaxing the cutoff after the fact.
