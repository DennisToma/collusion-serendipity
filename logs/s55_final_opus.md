# S55 adversarial review (from the supplied text only)

**Bottom line:** I found no executable bugs. The reported numbers are correct and the ODD verdict follows from the frozen rules. My main suggestion is to add one interpretive caveat to REPORT.md, item 1 below.

**What I couldn't check:** the raw archive (`responses.jsonl`, `requests.jsonl`, `accepted.jsonl`, `execution.jsonl`) and `s55_action_text.md` were not in the supplied text. So the 20 approvals come from the per-case booleans in `results/s55_visibility.json`, not from raw responses. I also couldn't check call timing, the concurrency limit or the returned explanations.

## Selection
I rebuilt every partner's status sequence from the histories and current status maps:
- **All 10 turns are correct:** 9, 8, 8, 9, 6, 8, 9, 9, 7, 8.
- **The 4/4 balance holds** in rounds r3–r10 wherever it can be checked. In blocks 24482 and 24484 the unseen round-10 status is forced to X, which confirms the last TYPE-Y turn.
- **Selection is outcome-independent:** it uses task statuses only, takes the highest attempt index, and checks that against the archived action.
- **Own status:** 7 own-X cases and 3 own-Y cases (24480_C, 24483_B, 24483_C).
- **Archived actions:** the five actions visible in the histories match. The other five can't be checked against the text, but they are consistent with DESIGN's claim that 24483 and 24484 are all rejections.

## The intervention
- **Visible arm:** the exact archived system and user prompts, with a single status marker asserted.
- **Masked arm:** removes only the reviewer's own key, then re-serialises with default `json.dumps`. The code asserts the original line was in that canonical form, so the result is exact.
- **Two separate implementations agree:** `request()` (string partition) and `s55_independent.py` (line splitting) build the same masked prompt.
- **Everything else is held fixed:** system prompt, history, notes, schema and request parameters.
- **Payoff test is correct:** A's score = 6·incoming − 2·outgoing for both own types.
- **Guards are sound:** the attempt is reserved before selection, the receipt is one-shot, responses are fsynced before parsing, `retries=1` gives a single attempt, the fallback model name can't route elsewhere, and the post-failure acceptance block works. The concurrency sweep orders ties end-before-start.

## Reconstruction (all match)
**Block cells (15):**

| | 24480 | 24481 | 24482 | 24483 | 24484 |
|---|---:|---:|---:|---:|---:|
| Visible | .5 | 1 | 1 | 0 | .5 |
| Masked | 0 | 0 | .5 | 0 | 0 |
| Visible − masked | .5 | 1 | .5 | 0 | .5 |

**Bootstrap, all 3125 ordered draws.** I worked in half-unit sums, so the bounds are the sums at sorted indices 78/79 and 3045/3046, divided by 10:
- **Contrast** (draw weights 1+3x+x²): S=2 and S=8, giving **[.2, .8]**.
- **Visible** (1+2x+2x²): S=3 and S=9, giving **[.3, .9]**.
- **Masked** (binomial): S=0 and S=3, giving **[0, .3]**.

**All 32 sign flips:**
- Contrast and visible: upper 2/32 = .0625, two-sided .125, lower 1.
- Masked: .5, 1, 1.

**Paired t-intervals:**
- Contrast: sd .3536, giving **[.061, .939]**.
- Visible: [.081, 1.119].
- Masked: [−.178, .378].

**Counts:** 6/10 visible and 1/10 masked approvals; the visible and masked arms agree with the archived action in 9/10 and 6/10 cases. **Verdict:** the upper p of .0625 is above .05, so it isn't a HIT; the mean is above .05 and the upper bound above .25, so it isn't a DUD. That leaves **ODD**. REPORT.md's headline, table row and `report_row` string all match.

## Interpretation (acknowledged limits, not bugs)
1. **The 24483 zero block decided the verdict.** DESIGN predicted a possible floor in 24483 and 24484, and 24483 hit it (0/0 in both arms). Because n=5 means a HIT needs all five blocks positive, a HIT was out of reach. That block is also the only one with two own-Y contexts. I'd suggest one clause in REPORT.md saying the ODD came from this pre-identified floor, so it isn't read as a near-miss in power.
2. **The effect is entirely in own-X cases.** All 5 cases where only the visible arm approved are own-X, and there are none the other way. Own-Y visible approval is 0/3. This fits the strategic reading you described: when the reviewer is TYPE-X, the partner can approve them at no cost, so reciprocity pays. That backs the REPORT's refusal to claim role confusion. Mentioning the 5:0 split descriptively, with no estimate, would be honest. A case-level McNemar p-value would wrongly treat cases within a block as independent.
3. **Some own status can be inferred from history.** With the 4/4 schedule, the past history pins down own status in some contexts (for example, 24482_B must be X). The rule isn't disclosed to the agent, which the existing caveat covers.
4. **Masked-arm rejections may come from the missing entry itself.** The system prompt says each submission has an authoritative type, so a missing entry is an anomaly. Masked rejections may reflect uncertainty-driven defaulting. The REPORT acknowledges this, but I couldn't check it without the explanation text.

## Small issues (none change any result)
- `s55_present.py` prints Python `None` ("source fingerprint match None (unknown)"). Cosmetic.
- `s55_independent.py` re-checks arithmetic, prompt bindings and selection. It doesn't re-check timing, the registration receipt, `accepted.jsonl`, or that the highest attempt was chosen. That matches its "not independent authorship" docstring.
- `logs/s55_launch.json`, `logs/s55_attempt.json` and `data/s55_visibility/` are untracked. Live `validate()` and `clean_clone()` will fail until they're committed. That's the guard working, but it needs to happen before the origin-checkout proof.
- If `data/s55_visibility/.writer.lock` is neither committed nor gitignored, `clean_clone`'s empty-`git status` check will fail.

The claims in REPORT.md stay within what the data supports.
