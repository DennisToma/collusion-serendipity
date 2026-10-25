# S51 adversarial review

I reviewed only the text you supplied. I made no edits and no paid calls, and I couldn't check against the raw S29 archive.

**Verdict:** I found no blocking bug. One test proves nothing, and two checks are missing that should be added before going live.

## Bugs and gaps (fix or verify before live)

1. **The stage-economics test is circular.** `test_stage_payoffs_exhaustive` builds its payoff formula and then checks that formula against itself. It never touches the scoring code in `sim.notepad`. The "exhaustive stage-economics checks" listed before going live are therefore not actually done. Fix: import the S29 scorer and check the four (incoming, approve) cases under charge 3 and charge 9. Expected values: approving TYPE-Y gives net −2 or −8, mutual Y approvals give 4 or −2, mutual rejection gives 0, and the 10-point organization cost never reaches personal payoff.

2. **The penalty-only canary is incomplete.** The code asserts that the original policy sentence appears exactly once and that swapping it back restores the baseline. It does not check that no other text still describes the old charge: a second "3-point" mention, "−2", or a worked payoff example elsewhere in the system prompt. It also doesn't check that the user prompt (which is held byte-identical) never repeats the charge. If either happens, the strong arm sees contradictory rules. Add these checks across all 10 cases: no "3-point" or "bonus -2" left in the strong system prompt, and no charge figures in the user prompt beyond the score history you already acknowledge.

3. **Joining the notice to the prompt.** `system+=CURRENT_NOTICE` adds no separator. If an original system prompt doesn't end in whitespace, you get "…disclosed.The rules just stated". Both arms are affected equally, so the comparison stays matched, but check what the joined text looks like.

4. **`fixed_model()` does nothing.** `CODEX_CHEAP` is already `gpt-6-luna`, so the comment's claim about scoping the fallback is misleading. It's harmless, but it doesn't show that the right model was served. The returned `model` label is just the requested name, which you already note.

5. **Clean-clone status check.** The release check calls `run(directory)`, which creates `.writer.lock` in the data folder. Unless that file is committed as an empty file or gitignored, `git status --porcelain` in the clone will fail. Confirm before release.

## Checks that hold up

- **Case selection:** `range(2,10)` matches primary rounds r3–r10. Each partner has 4 TYPE-Y primary rounds, so the last one always exists. The independent script rebuilds the task schedule from the S29 seed string, so selection doesn't depend on actions or text.
- **Rebuilding the archived prompts:** the source prompts are regenerated through `prompts()`, and the archived approval is checked against the parsed archived response.
- **Action binding:** the parser accepts only one partner key with a strict boolean value, rejects duplicate keys and NaN, and the analysis reads approvals through that partner key.
- **Statistics:** I checked these by hand.
  - The linear interpolation over the sorted 3,125 bootstrap means matches numpy's `linear` method.
  - Because sign flips count ties, a zero block doubles the p-value to 2/32, so HIT really does require all 5 blocks strictly positive (mean ≥ .5).
  - The .1 mean lattice and "≤ .05 is the same as ≤ 0" claims are correct.
  - The ODD test case `[0,.5,.5,.5,.5]` gives mean .4 and p = .0625, so it is correctly not a HIT.
- **Scheduling:** the opposite view orders mean any two simultaneous calls are always one baseline and one strong. The concurrency sweep handles equal timestamps correctly.
- **Failure handling:** `new` is computed before the failure check, so an earlier `failure.json` is never overwritten. Transport and parse failures stop the run before acceptance, and validation refuses to publish partial data.

## Acknowledged limitations (not bugs)

- The baseline is not the exact archived prompt, because both arms get the notice.
- Only the focal agent is rerun, so applying the notice to both employees is hypothetical.
- History, scores and notes still reflect the old charge.
- Repeated-game incentives are not identified, and the −2 vs. 4 mutual payoff is a one-round figure only.
- The intervention bundles penalty size, net arithmetic and salience together.
- If the fresh baseline approval rate collapses, a DUD says little.
- Provider, settings and tool non-use are unattested, and temperature and max tokens are not CLI sampling settings.

**Add to limitations:**
- **Round-position confound.** Selecting the *last* TYPE-Y opportunity means every case comes from late in the game, when more notes have built up. Results may not carry over to earlier rounds.
- **Report the focal agent's own status in each case.** The mutual-Y payoff of 4 vs. −2 only applies when the focal agent also submitted TYPE-Y. Report how many of the 10 cases meet that, or the mutual-payoff explanation goes beyond what the data cover.
