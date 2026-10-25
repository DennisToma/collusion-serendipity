# S68 adversarial review (supplied text only)

**Verdict:** I found no confirmed high or medium bug in the supplied text. One possible high-severity issue needs checking before any calls (item 1). I did not read the filesystem, the raw archives or the bootstrap enumeration.

## Must check before launch

1. **Possible high: the local cache could merge anchor and repeat.** Anchor and repeat send byte-identical requests, and the audit asserts `original==request(c,'repeat')`. If llm.py's disk cache, or the "cache-only resume", is keyed on the request content, repeat would just return anchor's answer. Then `1(anchor!=repeat)` would always be 0, the excess would equal the raw inverted disagreement, and the screen would lean toward HIT. The design lists "service caching" as a confound, but it does not show that the local cache key includes the view label and the case. Needed: a regression showing that repeat makes its own dispatch with its own raw record, and that a resumed run returns each view's own response.
2. **Medium (unverified): booleans outside "Completed public rounds".** The clarification only covers public rounds. If "Current authoritative statuses" or the notes snapshot contain true/false encodings (for example `approved: true`), the inverted arm leaves them ambiguous. The tail I saw shows only prose notes. Confirm that statuses carry no booleans, or widen the clarification to cover them in both arms.

## Checked and correct

- **Mapping swap.** The two instruction strings have the same words in a different order, so they are the same length. The `replace(REJECT,APPROVE)==original` check proves the swap is the only difference between the arms. Each prompt contains exactly one mapping string and none of the other. The appended note is identical in both tails.
- **History preservation.** All three markers appear exactly once and their JSON matches across arms. This depends on each JSON block fitting on one line; if it didn't, the audit would fail rather than pass silently.
- **Decoder audit.** It runs the production `decoded()` for 10 cases × 16 profiles × 3 views. The closure in the loop is called within the same iteration, so late binding doesn't matter. The payoffs match the stated economics: approving Y gives the reviewer +1−3 = −2, and the author gets 6. The organisation loss of 10 is only checked indirectly through `bad`. That is a minor gap.
- **Expected-excess formula.** p(1−q)+(1−p)q − 2p(1−p) = (q−p)(1−2p). Correct.
- **Screen.** Block means come in steps of ½. With 32 inclusive sign flips, the one-sided p-value can be ≤.05 only if all five blocks are strictly positive (1/32): a zero block ties and gives 2/32 > .05. So "HIT ⇒ all five positive and mean ≥ .5" holds.

## Known limits (already disclosed, not bugs)

- **Blindness.** The test can't detect a shift at p=.5 and can come out negative even when the shift is real. A DUD therefore does not show invariance, and the claim wording must keep saying so.
- **Changed anchor.** Anchor carries the appended note, so it is not the original S29 request. Report it as "original plus clarification".
- **Noise and order.** A single repeat is noisy, the middle position is not balanced, and the requested temperature and max_tokens are not forwarded by the CLI.
- **Abort risk.** Strict parsing combined with whole-pilot abort raises the chance of losing the run if the inverted instruction confuses the model (for example, it answers "approve" as a string). That is the design working as intended, not bias, but it's a cost. If it happens, report the abort as an observation in its own right.
- **Text versus boolean.** In the inverted arm, reasoning and notes may say "approve" next to `false`. Any analysis of action against text must use the decoded action, not the raw boolean.
- **Unconfirmed claims.** The 13:30 admission cutoff and headroom are taken as stated, not verified. Scope ("response-format pilot, not collusion or mechanism") is stated correctly, and the requirement for fresh confirmation before any HIT reaches a headline is right.

Fix item 1 if it applies and resolve item 2; after that, nothing I saw blocks the launch.
