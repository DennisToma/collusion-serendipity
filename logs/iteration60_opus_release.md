# Adversarial review: iteration-60 handoff prose and the suggested future design

**Scope.** I reviewed only the text you supplied: HITS.md, `scripts/export_report.py`, REPORT.md, and the saved S48/S58/S59/S69/S70/S72 summaries and the iteration-54 brief. I ran nothing and opened no files. I couldn't see the S29 or S62 summaries or their JSON, the receipts, the audit, or the README. Within the supplied text I checked one thing myself: the REPORT table has 54 rows, split 29 DUD, 23 ODD and 2 FAILED, which matches the headline. The S29, S62, S48, S58, S59, S69, S70 and S72 numbers agree across REPORT, HITS, the brief and the summaries.

## High

1. **The two judge-facing documents describe different future studies.**
   - `sources()` builds BRIEF from the iteration-54 brief. That brief still says the study would use an "unread-notepad control … as a fixed endpoint: both employees' complete-window gains". It also says this "would separate channel delivery from channel framing more directly."
   - REPORT's new "Future control question" uses three arms: self-only, truthfully undelivered, and delivered. Its outcome is the TYPE-Y approval rate. It says "neither contrast isolates content or beliefs" and leaves the individual-gain endpoint still to be fixed.
   - REPORT's own "Interpretation and next step" paragraph still has the older version (self/shared/unread arms, counterbalanced identities, complete-window gains). So REPORT contradicts itself, and BRIEF contradicts REPORT.
   - The relabel to "Reader edition · Iteration 60" suggests the brief was updated when its content wasn't. HITS.md also still names the iteration-54 brief as the "current handoff."
   - **Fix:** use one future-design paragraph everywhere, or mark the iteration-54 text as superseded inside BRIEF.

2. **The lead is selected without mentioning the other shared-versus-self tests.** "The lead" shows only S29 and S62. The portfolio tested the same channel contrast elsewhere with null or reverse results:
   - S18 (workplace, normative labels): 0/40 vs 0/40.
   - S45 (marketplace): −0.025.
   - S31 (labor market): 0.000.

   These are different settings, but a reader of the takeaway would expect them to be mentioned. "Examples above were selected post hoc" appears only in the later Portfolio paragraph. Add one sentence listing these tests near the lead.

## Medium

3. **No primary contrast is named.** The future design says delivered-minus-undelivered is "a new contrast" and that a shared-minus-self replication "should be declared separately." It doesn't say which one is primary, or whether "separately" means a separate study or a co-primary hypothesis. Name one primary contrast. The other then counts toward the multiplicity correction.

4. **"Replication" isn't defined at the prompt level.** The shared-minus-self contrast only replicates S29 if the self-only and delivered arms are byte-identical to the S29 prompts. The design now adds "truthful" access statements and matched own-note persistence. If the wording changes, this is a modified design, not a replication. State which S29 prompt bytes are kept.

5. **The identifiability limits are understated.** Delivered-minus-undelivered changes two things at once:
   - what the writer expects (whether the partner will read the note), and
   - what the reader sees (the partner's text and its downstream histories).

   This design can't separate those without a 2×2 that would require deception. The prose notes that "neither contrast isolates content or beliefs." It should also say that writer-side and reader-side effects can't be told apart.

6. **The outcome units are unclear.** The new outcome is a game-level ratio pooled across both employees, measured as an approval fraction. The other paragraph names complete-window gains, measured in bonus points per round. The design lists an "individual-gain endpoint/comparator" to fix but doesn't say whether it's primary or secondary. S72 also shows that the gain classification changes with the aggregation window, so leaving the window open is a real risk to how the result gets labelled.

7. **The failure policy is underspecified.** It doesn't define what a "terminal incomplete block" is. It also doesn't cover:
   - restart or resume (S68's precedent is no restart),
   - invalid outputs that differ by arm (S16 had output-validity censoring),
   - whether failure counts are reported by arm,
   - whether a single block failure voids the whole study even when the sample is larger.

8. **The replay-probe paragraph leaves out how unstable the control arm is.** The same archived prompt gave different results in different probes:
   - Same-prompt baselines: S48 retain 4/10, S58 retain 6/10, S59 original 4/10. S58 and S59 both use the exact archived system/user prompt.
   - Case flips between S58 and S59: `s29_24480_shared_B` was 1 then 0, and `s29_24484_shared_A` was 1 then 0.

   Swings this large between identical prompts are as big as the S58/S59 contrasts. That is stronger than the general "single fresh draws" caveat, and it should be stated. The list of probes is also incomplete: S50, S51, S55 and S61 reuse the same ten contexts, which adds to the reuse and multiplicity count.

9. **The "zero game-outcome tuning attempts" header can mislead.** No registered analysis was tuned. But the follow-up questions were chosen after seeing outcomes: S58 says "earlier replay results motivated the question," and S72's windows were chosen after outcomes were known. Suggested wording: "no tuning of registered analyses; follow-up selection was outcome-informed."

10. **HITS.md doesn't match the lead.**
    - It has no S62 entry, although the lead relies on S62.
    - Its S29 entry recommends enough blocks "to resolve the frozen directional screen." That ties sample size to S29's effect, which the new text explicitly rejects.

11. **The lead's numbers aren't fully bound to the source files.** In `scientific_lead()`:
    - The denominator 40 is hard-coded; only integrality is checked, not the number of eligible reviews.
    - For S62, the code doesn't check tied blocks, sign results or freshness, and the lead omits S62's paired t interval (shown for S29; the brief gives [−0.130, +0.330]).
    - The chart claims "five paired blocks each" without checking S69 or S70.
    - The model is named "qwen-3.6-35b" in REPORT and "Qwen-3.6" in the brief and chart.

## Nits

- "Descriptive block bootstrap 95% **CI**" in the lead; the table says "bounds." With n=5, the percentile bootstrap excludes zero where the t interval doesn't.
- PORTFOLIO_NOTICE says "All 54 primary result objects reproduced" but lacks the "consistency checks, not independent validation" caveat that `verification_note()` has.
- Lead paragraphs that should cross-reference each other:
  - S64 (memory reset 0/40) bears on note mediation, but the lead doesn't cite it.
  - S61 (ID-swap variability) supports counterbalanced identities, which the new design drops.
- "Future confirmation should…" is phrased as a confirmation even though nothing was promoted. "Possible follow-up" is safer.

## What holds up

- The future design is clearly marked as not registered and not launched ("not a registration or launched experiment").
- The text explicitly says not to size the study from S29's selected effect.
- Reuse is acknowledged: S48/S58/S59 use reused contexts, S53/S72 reuse trajectories, and none is presented as independent replication.
- No hit is promoted, and neither sibling headline changes.
