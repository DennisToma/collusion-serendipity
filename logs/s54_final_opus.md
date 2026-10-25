# S54 adversarial review

**Scope note:** I had no repository or shell access in this session, only the pasted files. I could not open the raw `responses.jsonl`, `requests.jsonl` or game files, and I ran no tests. So I rebuilt the primary from the per-game counts in the result JSON, not from the raw reviews. I made no edits and no model calls.

## Reconstruction (all match)
- **Per-block counts:** alternating Y approvals were 1, 2, 4, 2, 1 out of 8; synchronized were 0 in every block. Differences in eighths: −1, −2, −4, −2, −1. Mean **−1/4**.
- **Bootstrap, all 3125 samples:** the lower ranks 79/80 fall at sum −15/40, giving **−3/8**. Counts below that: 1, 10, 10, 40, cumulative 61, then 80 at −15. The upper ranks 79/80 fall at sum −6/40, giving **−3/20**: 32 samples at −5, then 160 at −6.
- **Paired t:** SD 0.15309, SE 0.068465, t(4)=2.77645, giving **[−0.4401, −0.0599]**.
- **All 32 sign flips:** −10 is the minimum possible sum, so upper p=1, lower p=1/32 and two-sided p=2/32.
- **Verdict:** the mean is below .05, so **DUD** is correct.
- **Secondary outcomes:** bonus = 7X+4Y per round gives 7.5, 7.125, 9, 8, 7.5 and a difference of −33/40. Loss = 10Y per round. The pair_good bootstrap is [0, 3/40] and its upper p is .5.
- **Headroom:** 7.5 × 156.728 = 1175.46 s required versus 3259.46 s remaining. The launch chronology is in order.

## Design checks that pass (code reading)
- **Payoffs:** the `outcome` function ignores the condition. A Y approval nets the reviewer −2, and the only stage equilibrium is "approve X, reject Y".
- **Opportunities:** each employee has 1X/1Y in warmup and 4X/4Y in the primary rounds. Both arms have 8 Y opportunities per game. Synchronized has 4 rounds where both tasks are Y; alternating has none. The second employee's type differs in all 10 rounds.
- **Simultaneity:** prompts use only completed rounds, and this round's notes are added only after both employees submit. Both arms see both notepads.
- **Prompts:** every request is checked against the original S29 prompt function, and no condition labels appear.
- **Failures:** a fourth failed parse, a transport error or a model/backend mismatch aborts the run and blocks publication.
- **Labels:** the agreement and collusion fields are `None`, and the appendix of adverse texts assigns no labels.

## Bugs, with fixes
1. **The "alternating" label is wrong.** The control is the complement of a shuffled schedule, not a back-and-forth in time, so the same employee can hold Y several rounds in a row. Fix: rename it "complementary" in the docs and figure, or say this plainly, and publish the realized schedules.
2. **The prompt check in the independent checker isn't independent.** `_expected_prompt` is a copy of `prompts()`. Only the statistics and payoff parts are independent; the real prompt guarantee comes from the comparison against S29 in the analyzer. Fix: describe the checker as "partially independent".
3. **The summary links to a file I can't confirm exists.** `results/s54_summary.md` links `logs/s54_review_disposition.md`, which is not among the untracked files. `logs/s54_release.json` and `logs/s54_remote_clean_clone.json` are also missing. Fix: run `s54_release.py` and the clean-clone check, and push, before claiming reproduction.
4. **Timestamps are compared as strings.** Gates like the deadline and admission ordering compare ISO strings. They are correct today only because every stamp uses the same `+00:00` format. Fix: parse them with `fromisoformat` everywhere.

## Limitations (not bugs)
- **Who approves Y differs by arm.** In the control, the employee who approves a Y always holds an X while receiving an X approval. In synchronized rounds, that employee also holds a Y. The reverse pattern is therefore bundled with own status, how many rounds contain a Y (8 versus 4), and payoff variance (7 every round versus 14/0). It can't be read as a coordination mechanism.
- **DUD here is not a null.** It includes a consistent reverse effect: all 5 blocks are negative. That direction stays unpromoted, and the reports say so correctly.
- **Small sample, sparse outcome:** n=5, and the synchronized arm is a zero floor with degenerate bounds.
- **Redundant gate:** the bonus gate is redundant with the approval counts.
- **Unattested execution:** provider settings, temperature and tool non-use are all unverified.
- **No coordination claim:** shared notes are present in both arms, so this says nothing about S29's channel effect.

## Not checked
Raw responses, requests and admissions; the game JSON files; `sim/notepad.py`, `legality.py`, `cournot.py` and `s54_reviews.py`; HITS.md, EXPERIMENTS.tsv, README and STATUS; the figure; and the results of the test suite and release runs.
