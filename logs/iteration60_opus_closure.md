## Review: iteration 60 future-work prose and handoff claims

**What I checked:** only the text you pasted: `scripts/export_report.py`, `REPORT.md`, part of `README.md`, the `logs/iteration60_exports.json` receipt, and the S48/S58/S59/S69/S70/S72 summaries plus `results/iteration54_brief.md`. I did not open any files or run anything. So I haven't checked hashes, the field-audit counts (307/144), the replay counts (54/52/2/50), the rendered PDF/HTML, or whether `REPORT.md`/`README.md` match `documents()` byte for byte. Reading by eye, the prose matches the exporter constants. I also haven't seen STATUS, HITS, REPORT_DETAILS, the S29/S62 summaries or the archived brief at its pinned revision.

**Arithmetic I could check from the text:** 2/40→15/40 gives +0.325 and 3/40→7/40 gives +0.100. 29+23+2 = 54. The S48 retain/erase rates (4/10 vs 4/10) match "equal". The probe baselines (S48 4/10, S58 6/10, S59 4/10, all under the exact archived prompt) support "identical retained prompts produced different aggregate baselines". The sentence doesn't claim those differences are significant, which is correct at n=10.

### High
None. Nothing in the lead, portfolio, verification or future-work prose claims more than the saved evidence shows. The follow-up is consistently labelled "not registered or launched" and "not a finished protocol". In the reader brief, `sources()` replaces the archived "Suggested future confirmation" paragraph and guards that swap with a count check. No confirmation or registration wording survives in the shipped exports.

### Medium
1. **The confound sentence doesn't say which comparison it covers.** "Addressing, access expectations, self-memory content and subsequent histories still differ" follows a primary contrast in which both arms are partner-addressed. Addressing differs only in the secondary self-only comparison. Read as written, it either understates what the primary contrast holds fixed or makes the confound list look wrong. Suggested fix: "In the primary contrast, access expectations, writer content and later histories still differ; the self-only comparison also changes addressing."

2. **The primary contrast and the lead don't line up, and the paragraph doesn't say why.** The lead is shared minus self (S29, ODD). The suggested primary contrast is delivered vs undelivered partner-addressed notes, and the contrast behind the lead becomes secondary. This is defensible, but:
   - no reason is given;
   - a reader may not notice that a positive shared-minus-self result would then be a multiplicity-adjusted secondary, not a replication of the lead.

   One clause would fix it. For example: the primary contrast holds addressing fixed, so it targets the effect of delivery rather than of addressing; the lead's own contrast is secondary.

3. **The list of things to fix before running omits the model, backend and decision rule.** "Fix the sample size, window, tests, multiplicity, gain endpoint/comparator and retry limits" leaves out:
   - the model, backend and settings. This is the most consequential choice, given that S29 (gpt-6-luna) and S62 (qwen-3.6-35b) disagree.
   - the direction or sidedness of the hypothesis, and any threshold or decision rule.
   - the number of arms. "Run every arm" implies three (delivered, undelivered, self-only), but this is never stated.

   You said not to require a finished protocol, so this isn't a demand for one. It's a gap in an enumerated list that a reader would take as complete. Adding "model/backend/settings, arm count, direction" would close it.

4. **"Refines" undersells what changed from the archived suggestion.** The archived text made "both employees' complete-window gains" a fixed endpoint, used an unread-notepad control, and added generation/judging separation with a matched reference. The new text demotes gains to secondary, changes the control, and drops the last two items. Elsewhere the repo treats changed endpoints as material, so "This replaces the archived suggestion (gain endpoint now secondary; control changed)" would be more accurate. On GitHub, the "Source-checked brief" link in `README.md`/`REPORT.md` opens `results/iteration54_brief.md`, which still carries the old suggestion. The exports rewrite that link to `BRIEF.pdf`, but the Markdown view does not. So two future paragraphs that disagree can be one click apart.

### Optional nits
- **The outcome unit is ambiguous.** "Each game's TYPE-Y approvals divided by eligible TYPE-Y reviews" is clear per game. If a block has more than one game per arm, it doesn't say whether to average the game rates or pool them into one ratio. "Eligible" also needs defining for invalid or missing outputs. With matched schedules (8 per game, as in S29) the denominators are fixed, but stating the rule removes the ambiguity.
- **Failure policy:** "Any terminal incomplete block should fail the entire study" is coherent, and "report failures by arm" covers failures that depend on the arm. Optionally note that partial data is still reported descriptively (as in S16/S68), and define "terminal" relative to the retry limit.
- **Replication condition:** "preserving S29 prompts would be required for a direct replication claim" is true as a necessary condition. A direct replication would also need the same model and settings, so "prompts and model" is tighter.
- **Tone:** the imperatives ("Run…", "Match…", "Declare…", "should fail") read like protocol text, while the frame is conditional ("would"). Keeping one conditional mood throughout makes the non-registration status clearer.
- **Chart label:** "Qwen-3.6" is hard-coded in `chart()`, while the prose uses `obj['model']` (qwen-3.6-35b). It's harmless, but the label isn't checked against the source.
- **README spacing:** `FRESH_NOTICE` ends with `\n\n` and another `'\n\n'` is appended after it, which leaves extra blank lines before "Render with…". Cosmetic.
- **"Fresh seed block":** this implies new seeds, but the text never says S29 seeds and histories must not be reused. Saying so would make the independence explicit, given how much the replay probes reused.
