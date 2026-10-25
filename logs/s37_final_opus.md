# S37 adversarial review (S37 only; no edits, no model calls, other critics' reviews not read)

**Verdict: no bug changes the frozen DUD.** I didn't run any code or open the raw files. Every arithmetic check below is my own reconstruction from the archived numbers.

## Arithmetic, reconstructed
- **Rate choices are pinned down by the outputs.** Normalized offers are never negative, and their mean is 0. So both firms quoted 10 in every round from r3 to r10, in all 10 games. That gives take-home pay 0, a tie rate of 1 and total firm profit of 20. The regret of 9 per firm checks out: at (0,0) each firm earns 10, and moving to a take-home of 1 would earn 19. The 200 responses equal 10 games × 10 rounds × 2 firms with zero retries, which matches.
- **Bootstrap.** All five paired differences are 0, so all 3,125 resample means are 0 and the bounds are exactly [0,0]. The paired t interval is [0,0] because the spread is zero.
- **Sign flips.** All 32 flipped sums equal 0, which is at least the observed 0. So the upper, lower and two-sided p-values are all 32/32 = 1.
- **Screening rule.** The mean of 0 is ≤ 0, so the result is DUD. At n=5, an upper p ≤ .05 needs p = 1/32, which only happens if every difference is strictly positive. A positive bootstrap lower bound then follows automatically, so that gate is redundant, as the report already says.
- **Denominators.** Every metric is an integer total divided by 32 (paid/8, offers/16, ties/8, profit/16, regret/16), so the ×32 numerators are exact.

## Economics and contrast
- `outcome()` never receives the condition, so stage payoffs are identical in both arms. The 441 profiles, 18,522 evaluations (17,640 action-changing) and the Nash quotes (28,28), (29,29), (30,30) are all correct.
- Both wordings say take-home pay and employer cost are "quote minus 10". The user messages are identical, and the parser, offset and history schema are the same in both arms. The contrast direction is coded − payroll.
- **Simultaneity holds.** Notes written this round are held back until both firms have answered, and the second firm's prompt only uses completed rounds. Each firm's notes snapshot only contains its own notes.

## Remaining issues
1. **Medium: the report leaves out a key fact.** Both arms sat at the joint-profit-maximizing floor: zero pay, regret 9 per firm, far from the static Nash wage of 18–20. Because pay was already at 0, the wording could only have shown an effect by raising wages. The data also can't tell apart tacit coordination, misreading the quote, or anchoring on the "accepts zero take-home" line. **Fix:** add one sentence saying this to the REPORT row and the summary.
2. **Low: only the admissions journal is synced to disk.** The requests and responses logs are flushed but not synced, so a crash would fail closed through the admission mismatch. This is acceptable; disclose it.
3. **Low: the CLI fingerprint has gaps.** It doesn't cover `AGENTS.override.md` (repo, temp dir, `~/.codex`), MCP or plugin programs referenced from `config.toml`, or other files under `~/.codex`. It's also only checked before and after each call, so a change that is reverted during a call goes unnoticed. **Fix:** list these gaps in the limitations.
4. **Low: the independent check reuses the prompt text.** `expected_prompts` is a verbatim copy, so it proves the prompts didn't drift, not that the wording is correct. The wording itself is only covered by the string tests.
5. **Low: guard and dead-code clutter.** Each admission hashes the node and codex binaries while holding the admission lock, which forces the two workers to take turns. That could narrow the timing overlap between paired games, though the overlap check reportedly passed. There's also dead code (`cache.cache_only=resuming`, which can never run) and a duplicate overlap check.

## Already acknowledged limitations
- Labels, wording and sentence length change together.
- Requested temperature and model are not enforced or attested, and actual tool non-use is not verified.
- n=5, exploratory, no correction for multiple comparisons, no equivalence claim.
- The sign-flip test assumes exchangeable or symmetric differences.
- Auth refresh triggers an abort.
- The result doesn't explain S36.

## Not checked
- Raw responses, game files, the actual call timestamps and overlap, and the real launch-to-dispatch timing.
- Test-suite results, the figure, and byte-identical regeneration.
- Release: at session start the S37 data, results and logs were untracked and REPORT was modified, so the commit, push and clean-clone check are still pending.
