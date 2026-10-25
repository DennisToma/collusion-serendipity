The narrow scope is mostly resolved. I found one medium issue and no high issues. This review covers only the text you supplied. I did not run anything, look at the filesystem, or check any hashes.

## Resolved
- **Primary vs. secondary contrasts and rationale:** The paragraph names delivered-minus-undelivered partner-addressed notes as primary, and shared-minus-self and individual-gain measures as secondary. The reason for the primary choice is given: it holds addressing fixed while varying delivery together with truthful access expectations.
- **Addressing:** The primary contrast holds addressing fixed, and the self-only comparison is said to "also change addressing." The paragraph also lists what still differs in the primary contrast: access expectations, writer content, self-memory content and later histories.
- **Choices fixed in advance:** The paragraph says to fix model, backend and settings before any calls, along with sample size, window, test direction, decision rule, multiplicity, gain endpoint/comparator and retry limits. It also says S29's effect does not estimate the new contrast, and that an incomplete block fails the whole study.
- **Identical shared paragraph:** The paragraph is the single `FUTURE_WORK` constant, used both in `SCIENCE_LEAD` and as the brief's replacement text. It appears word-for-word the same in `REPORT.md` and `README.md`. The link label "Archived evidence brief, payoff accounting and all intervals" is the same in both files.
- **Framing:** "Not registered or launched" and "an unfinished proposal" frame it as a suggestion, not a protocol.

## Medium
1. **In the exports, the "Archived" brief link goes to the reader edition, so the replacement can't be traced.** `page()` rewrites `results/iteration54_brief.md` to `BRIEF.pdf`. In REPORT.html and REPORT.pdf, the link labelled "Archived evidence brief…" therefore opens the "Reader edition · Iteration 60" brief. That brief contains the new paragraph, not the iteration-54 suggestion. As a result, no exported link reaches the archived suggestion that "This replaces the archived future suggestion" refers to. The Markdown links are fine because they point to the real archived file. Two possible fixes:
   - Pin that one link to the archived file on GitHub, the same way other source links are pinned.
   - Or relabel it in the exports, for example "Evidence brief (reader edition)", and add one pinned link to the archived suggestion.

## Optional nits
- "Could be a new primary contrast… a three-arm block would also include self-only notes" leaves it unclear whether the self-only arm is part of the design or optional.
- "In a fixed window" comes before "window" appears in the list of choices to fix later. That's slightly redundant, but it doesn't contradict anything.
- "Truthful access expectations" could say outright that undelivered-arm writers are told the partner cannot read their notes.
- "Changes control and endpoint priorities" doesn't say that the archived suggestion's "keep generation and judging separate / matched reference" part was dropped. It probably doesn't apply anymore, since the endpoint is approval counts with no judge.
