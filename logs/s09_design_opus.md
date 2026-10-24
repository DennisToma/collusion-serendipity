Exit code: 0
# S09 adversarial review: one issue to check before calls, two decision-rule fixes, the rest minor

I reviewed only the code and design you pasted. I edited no files, ran nothing and made no model calls. I couldn't see `llm.py`, so the most serious item (H1) is something to check, not a confirmed bug.

## Bugs and risks, by severity

### High: check before any live call

**H1. The model may be able to read the erased messages from disk.** The design says fresh CLI contexts "do not attest filesystem isolation" and treats this as a general caveat. In S09 it is more than that. `data/s09_prefix/prefix_*.json`, the S07 game files and `DESIGN_S09.md` all sit in the repo. If `codex exec` runs with its working directory inside the repo, an erase-arm agent could read the messages it was supposed to lose, or read the design. Codex also loads `AGENTS.md` files from the working directory and its parents, which would add unwanted instructions. Any of these defeats the treatment itself, not just provenance.
- **Fix:** confirm in `llm.py` that codex runs in an empty directory under `/var/tmp` with `--skip-git-repo-check`, a read-only or no-file-access sandbox, and no `AGENTS.md` above it. Record the working directory and sandbox settings in `config.json`. Add a dry canary test that fails if the call's working directory is the repo. If you can't confirm this, the limitation should say the erasure may have leaked, not just "isolation not attested".

### Medium

**M1. A large effect in the reverse direction gets labelled DUD.** `classify` returns ODD-reverse only when the mean is ≤ −1 and all five differences are negative. Everything else with mean ≤ .25 is DUD. So mean −3 with four of five blocks negative is a DUD, which reads as "no effect" when it is actually a large effect in the unexpected direction. No data exists yet, so you can fix this legitimately now:
- **Fix:** define DUD as −1 < mean ≤ .25. Mean ≤ −1 without all five negative becomes ODD. Commit this before the registration commit and add a test for it.

**M2. In practice, HIT means all five blocks must go the same way.** The smallest possible one-sided sign-flip p over 32 sign patterns is 1/32. With four positive blocks and one negative (or one zero), p is at least 2/32 = .0625, which fails the .05 cutoff. So HIT requires 5/5 positive numerators summing to ≥ 60. Once that holds, the bootstrap lower bound is automatically > 0, so that condition adds nothing. This isn't a bug, but:
- the design should say it plainly;
- a DUD should be reported as "not detected at n=5", never as "message memory doesn't matter".

**M3. The analysis doesn't fully check where the prefixes came from.** The analysis checks that the file at `prefix['source']` matches its stored hash. It does not check:
- that the path is the S07 neutral game for the same seed (a legality game, or the wrong seed, would pass);
- that the prefix's rows, chat and assigned pair match the source file (only `test_s09.py` checks this, and it isn't called from `analyze`);
- that the source game itself used gpt-6-luna on codex.

Also, no script that generates `data/s09_prefix/` appears in `SOURCES` or in git status.
- **Fix:** assert all of the above inside `analyze()`, and commit the extraction script as a source.

**M4. Analysing dry data can overwrite the real results file.** `s09_analyze.py --data <dry dir> --allow-dry` writes to `results/s09_replay.json` by default, the publication path.
- **Fix:** refuse that default path when `cfg['dry']` is true, or default to `results/s09_dry.json`. Similarly, `sim.replay --dry` defaults to `data/s09_replay`. It fails closed later because of config drift, but it is still a trap.

**M5. The estimand needs wording, not code.** Erasure applies to both pair members together. And since agents carry no state between calls, "memory erasure" really means "transcript removed from the prompt".
- **Fix:** state "joint removal of both members' received-message transcripts", so a reader doesn't take it as one firm forgetting.

### Low

- **L1. Deadline race.** `ReplayCache` checks `now() < DEADLINE`, and only afterwards does `Cache.call` stamp `call_started_utc`. A call that passes the check in the last microseconds could be stamped at or after the deadline. The analysis's strict `call_started_utc < DEADLINE` would then reject the whole experiment. **Fix:** take one timestamp and use it for both the check and the record.
- **L2. A torn cache line after a crash is silently re-sampled.** `Cache.__init__` truncates a torn last line, so that request goes out live again under the same key, and the analysis can't tell. **Fix:** refuse publication if any `raw/*.torn.*` file exists, or at least report them.
- **L3. Gaps and mislabels in the secondary metrics.**
  - The design calls the outsider's round-7 action a negative control, but it is never summarised. It only appears inside each game's per-game record.
  - The fork-only message metrics (`message_words`, `nonempty_messages`) actually cover messages from rounds 7–12.
  - The round-12 message metrics count messages that were never delivered.
  - **Fix:** add an outsider fork difference summary and relabel or drop the others.
- **L4. "Registered before calls" rests only on a local commit.** Commit times are set locally. **Fix:** push the registration commit before any calls and record the remote SHA and push time.
- **L5. Terminal failure leaves nothing to publish.** That is by design, but write the failure row into `EXPERIMENTS.tsv` so it isn't dropped quietly.
- **L6. Current state.** Every S09 file is untracked, so a live run will stop at `git ls-files --error-unmatch`. That's correct behaviour. Commit the design, code, tests and prefixes together as the registration commit, after making the M1/M3/M4 fixes.

## Already acknowledged, and I agree they are limitations rather than bugs

- **Empty-inbox cue.** An empty box after six rounds is itself a signal (partner silence or a reset). From round 8 the round labels starting at 7 add another cue. This is the main reason a HIT can't be read as "message meaning".
- **Leftovers of the erased messages.** The public history still reflects earlier coordination, and new messages from round 8 can restore it, so the result is an estimate of total effect.
- **Prefixes were already seen.** "Not selected by content" covers which prefixes were chosen. It doesn't cover the decision to run S09 at all. Say whether the S07 neutral rounds 7–12 had been looked at.
- **Weak inference.** Temperature and sampling seeds aren't controlled, the model label isn't independently confirmed, and n=5 gives a minimum p of 1/32. The sign-flip test also relies on symmetric differences under the null, not on a randomised assignment. There's no multiplicity correction across the S-series.
- **No ground truth for agreement or execution.** Lower output is not evidence of collusion; the design already says this.

## Checked and correct

- **Message timing:** a message labelled `t+1` is sent at 0-indexed round `t` and seen from `t+1` on. Erasing `round ≤ 6` removes exactly what was sent in rounds 1–6. Nothing leaks from the current round, since delivery happens after all three actions.
- **Prompts:** the system prompt and the text before the inbox are identical across arms, and the outsider's prompt at the fork is identical. The retain arm's round-7 prompt is byte-identical to S07's original.
- **Cache keys:** they keep dry vs live and S07 vs S09 (via `run_id`) apart, so the arms draw independent samples. Nothing from S07's cache is reused.
- **Numerators:** the exact integer numerators, the `Fraction` mean and the sign-flip p all use integers, so there's no floating-point tolerance problem.
- **Cache-only replay:** it rebuilds every request, uses each key exactly once, compares rows and provenance, and confirms the raw files weren't changed.
- **Schedule and seeds:** the schedule, block barrier, failure stop, config-drift check and source-vs-registration hash check are all sound.

## How far a result can be claimed

- **HIT:** "For these five previously observed prefixes, removing both firms' transcripts of earlier received messages raised later pair output by at least 1 unit per firm on gpt-6-luna." It says nothing about what the messages meant (the empty-inbox cue is mixed in), nothing about collusion or profit, and doesn't count as independent replication.
- **DUD:** "Not detected." A HIT needs 5/5 blocks, so a DUD is very weak evidence of no effect.
