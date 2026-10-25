# S61 adversarial review (supplied text only)

**Verdict:** I found no bug that invalidates the S61 design or would bias the primary contrast. There is one operational hazard to fix before launch and several clarifications for the write-up.

## Design ↔ code agreement (verified)

- **Selection is outcome-independent.** The turn comes only from `task_status` (partner TYPE-Y, `range(2,10)` = rounds 3–10). `max(attempt)` picks the attempt, and archived equality is asserted, not filtered on. The ten cases match S55.
- **The swap is complete and an involution.** `\b[ABC]\b` hits system, user, history keys, notes authors and text, and the output schema. In the six notes texts I scanned, every A/B/C is an ID, with no English article "A". `\u2019` is stored as an escaped backslash, so word boundaries hold. TYPE-X/Y is untouched. Lengths are preserved. The decoded target is the original agent, which is correct. Both rename and decode are tested.
- **Payoff symmetry** is checked exhaustively over 16 profiles.
- **Statistics and screen match the design.** Exact Fraction percentiles match the independent integer-doubled reconstruction. The sign-flip test is inclusive. With half-unit blocks, any zero block gives p ≥ 2/32 = .0625, so HIT really does require all five blocks positive and mean ≥ .5, as the design states.
- **Failure paths are fail-closed.** Responses are persisted before parsing. An abort blocks new admissions. Interrupted or failed archives are never analyzed or resumed. A worker in flight during an abort persists its response, then rejects it.

## Operational hazard (fix before launch)

**The one-shot reservation is consumed by any preflight failure.** `LIVE_ATTEMPT` is written before `registration()`. A routine slip burns S61 permanently, for example:
- the scripts are still untracked (per git status),
- the push was not done,
- `origin != HEAD`.

The test suite treats this as intended. Before the live call, run the registration checks manually: `git ls-files`, `git diff --exit-code`, `ls-remote == HEAD`, and confirm ≥20 min to 11:00 UTC.

## Unacknowledged or under-stated limits (scope, not bugs)

1. **"Byte-identical" holds only at the `llm.chat` level.** `_codex` runs inside a fresh random tempdir (`-C d`). The Codex CLI may also inject environment context such as cwd and possibly date. So the provider never sees identical requests, including anchor vs repeat. This doesn't bias the comparison between arms, but say "identical llm.chat request" rather than "byte-identical."
2. **Provider prompt caching** may treat anchor/repeat (identical prefixes) differently from swapped. That is plausibly irrelevant to sampling but unverifiable. It falls under "service drift," which should mention it.
3. **The anchor/repeat labels are exchangeable by construction** (view order is shuffled). So the primary statistic depends on which identical call is arbitrarily named "anchor." A symmetric alternative is ½[(a≠s) + (r≠s)] − (a≠r). Don't switch now, since that would be post-hoc. Do note that the registered choice adds noise.
4. **Within-block dependence.** In 24483 both cases are the same round with both employees TYPE-Y and mirrored seats. Swapped-B and anchor-C present the same seat with a mirrored history. Blocks are the unit of analysis, which handles this, but cases within a block are far from independent. Three of the ten cases also have own status TYPE-Y; worth one sentence.
5. **Power.** The repeat control can be nonzero, and HIT needs a positive excess in all five blocks. So DUD or ODD is the overwhelmingly likely outcome even if ID sensitivity is moderate. The text says "no absence claim"; REPORT.md should repeat this right next to the verdict.
6. **Alphabetical/key-order cues are bundled with ID labels.** This is acknowledged. Make sure REPORT.md never says "label effect" alone.
7. **The independent script reconstructs arithmetic but not provenance.** It skips journal, registration and timing; those come only from `validate` via release. Its docstring says it is not independent authorship, which is honest.

## Minor

- The concurrency sweep orders an end before a start at equal timestamps, which is permissive. That's fine with second-or-finer stamps.
- `fixed_model` is a no-op, since `CODEX_CHEAP` is already `gpt-6-luna`. It's harmless.
- Sign-flip results on the per-arm approval rates test the meaningless null of zero. They're labeled descriptive; consider dropping them from the summary table to avoid misreading.

**Bottom line:** the methodology and code are consistent with DESIGN_S61, and the claim scope is appropriately narrow. Address the reservation hazard and the "byte-identical" wording.
