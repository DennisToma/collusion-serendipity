# Adversarial review: iteration 60 handoff prose (HITS.md) and the suggested future design

**What I checked:** only the text you pasted: HITS.md, the S48/S58/S59/S69/S70/S72 summaries and the iteration54 brief. I didn't read any files, run anything, make model calls or recompute numbers. I couldn't see the S29 and S62 summaries, iteration58_reproduction.md, the DESIGN files, the JSON files or the "historical handoff below", so their claims are checked only against the brief.

**Overall:** I found no fabricated or inflated numbers. HITS.md matches the summaries on labels, counts and the fact that no hit was promoted. The problems are about how evidence is framed, and about parts of the future design that aren't yet specified enough to run.

## High

None.

## Medium

**M1. The table hides that most of the workplace evidence comes from the same five games.**
- S48, S58, S59 and S72 all reuse the same five S29 source blocks (seeds 24480–24484). S58 and S59 rerun the same ten focal contexts, and S72 re-analyses the original S29 actions.
- HITS flags this reuse only for S58/S59 and S72. The S48 row doesn't mention it.
- Read as five rows of "existing evidence", the table can look like accumulating support. In fact the workplace lead rests on one ten-game pilot (S29) plus one fresh, unresolved follow-up (S62). Only S62, S69 and S70 are fresh games, and S69/S70 use different (pooled) payoffs.
- **Fix:** add one sentence saying S48, S58, S59 and S72 all derive from the same five S29 blocks and are not independent of S29 or of each other.

**M2. "Decisions can change when the visible record or its representation changes" overstates the evidence.**
- Each arm is a single uncontrolled fresh draw per context. A decision differing between arms is confounded with ordinary draw-to-draw variation.
- S48 shows that variation directly: 3 of 10 contexts disagree between arms while the overall rates are identical, and fresh retain matches the archived action in only 7 of 10.
- S59's bootstrap interval reaches 0 and its paired t interval spans zero (two-sided sign p = 0.5). S58's t interval excludes zero, but it misses its registered screen (upper p = 0.0625).
- **Fix:** report it descriptively. For example: "S58 approvals were lower with history erased (6/10 vs 2/10); S59 lower with the compact table (4/10 vs 1/10); neither passes its screen, and single draws per arm cannot separate the intervention from sampling variability."

**M3. The sample-size sentence points at a pilot estimate that doesn't exist.**
- "Rather than treating this post hoc selected pilot estimate as a confirmed effect" has no valid referent. No pilot has ever measured delivered-minus-unread.
- The only candidate, S29's +0.325, is a shared-minus-self contrast. It was also selected as the lead, so it is likely inflated (winner's curse).
- **Fix:** state explicitly that no existing estimate should be used to power the primary contrast, and that S29's shared-minus-self number is neither the estimand nor an unbiased effect size for it.

**M4. The future primary contrast is not the one that motivated it, and the linked brief contradicts HITS.**
- S29 motivated a shared-minus-self contrast. The proposed primary is delivered-minus-unread. That's a defensible choice, but it tests a new question; it doesn't confirm S29. HITS should say so.
- The iteration54 brief, which HITS links as source-checked, still says "Suggested future **confirmation**". It makes complete-window gains the fixed endpoint, and claims the design "would separate channel delivery from channel framing more directly".
- HITS instead makes adverse approvals the primary outcome, and correctly says delivered-vs-unread does not isolate content or beliefs.
- **Fix:** state that the iteration60 design supersedes the iteration54 suggestion, and that "confirmation" there is not a registration.

**M5. The outcome unit and the experimental unit are ambiguous.**
- "Game/seed block" merges two different things. In earlier pilots the independent unit is the paired seed block (one game per arm), and the estimate is the mean of differences within blocks.
- With three arms, the design must say whether every seed is run in all three arms.
- It must also define the rate: TYPE-Y approvals divided by TYPE-Y opportunities, pooled over both employees per game. That is 8 per game in r3–10 under the earlier schedule. S72 shows how easily per-review (16) and per-status (8) denominators get mixed up.
- "Fixed complete window" should name the rounds (e.g. r3–10, warmup excluded).
- "Complete-window gains" needs a unit and a comparator: points per round per employee, the both-gain indicator, or minimum excess.

**M6. The failure policy can't be followed as written.**
- "Retain every registered block … never substitute incomplete-case estimates" doesn't say what happens when a block cannot be completed. The block can be neither kept nor dropped. S68 shows this is a real risk.
- Missing data could also differ by arm, because delivered-arm prompts are longer, which risks retries and rate limits.
- **Fix:** pre-specify one rule. Either (a) any terminal failure marks the whole study failed with no estimate, matching current practice, or (b) a stated worst-case/bounds rule. Also fix retry limits, and treat failure rates by arm as a reported outcome.

**M7. The control arms are not fully identifiable as specified.**
- In the unread arm, describing access truthfully means telling writers their partner-addressed notes won't be read. "Addressing" a known non-reader is an unusual framing that has no counterpart in the delivered arm.
- Own notes written to a partner may also store different self-memory than self-only notes. So "own-note persistence matched" holds for persistence but not for content.
- The reader-side prompt also differs ("partner notes are not shared" vs partner notes present).
- HITS acknowledges bundling in general terms. It should list these specific components so a future reader doesn't interpret unread-minus-self as "framing only".

## Nits (optional)

- **Registration wording.** The second paragraph opens with an imperative ("Pre-register…"). Quoted on its own, it reads like a protocol. Suggest "A future registration would specify…".
- **Missing label.** The S48 row omits its frozen label (DUD); the other rows give theirs.
- **Undefined "independent".** "Larger independent block sample" should say fresh seeds, disjoint from 24480–24484, 25420–25424 and 25460–25464, and from any viewed data.
- **Decision rule not stated.** Sidedness, test, alpha and decision rule for the primary (HIT/DUD-style thresholds) are left under "freeze analysis". Say they must be fixed alongside the minimum effect of interest.
- **Provenance carry-forward.** Restate that temperature isn't forwarded by the Codex CLI, and that the served model and tool non-use are unattested. Choosing one model/backend doesn't solve either.
- **Comparator naming.** "Same-status one-shot payoff comparator" (HITS) and "Nash comparator" (brief) should use one name. The stage-optimality of approve-X/reject-Y for S29 payoffs isn't shown in the supplied text.
- **Unfound reference.** "Historical handoff below is preserved verbatim" — nothing follows it in the supplied text, so I couldn't check this.

## Confirmed consistent in the supplied text

- **No headline change:** "No promoted hit", no change to sibling headlines, and S68 interrupted with no estimate and no restart.
- **S69/S70:** S69 is described as an expected calibration and S70 as missing its screen without any equivalence claim.
- **S72:** described as post hoc and not a replication.
- **Future design:** marked "not registered or launched", and agreement and intent are kept out of the action counts.
