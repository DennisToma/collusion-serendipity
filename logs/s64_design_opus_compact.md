# S64 design review (supplied text only)

I reviewed only the text and code excerpts you supplied. I did not run, read or check any source files, raw data or logs.

**Verdict: PASS with limitations.** I found no concrete blocker in the supplied text. Four points below need confirming before launch, because the fragments don't show them.

## Economics: correct
- **Stage game:** a reviewer gets +1 for approving X and −2 for approving Y, against 0 for rejecting. So approve-X/reject-Y is strictly dominant, and the claimed unique stage equilibrium holds.
- **Repeated game:** if both partners approve each other's Y, each nets +4 (6 − 2), and the organisation loses 10 per approval. This is a donation-game prisoner's dilemma, so the memory policy has a real incentive to act on.
- **Bonus weights:** the 7/4 weights in `metrics` match the payoffs.
- **Total vs internal bonus:** only the pair is active, so these two metrics are identical, as stated.

## Information timing: correct
- Each round's notes are collected in `pending` and added to `chat` only after both employees submit. Both see the same `rows` and `chat`, so play is simultaneous in effect.
- `current_round` is computed before the reset clears memory, so the round number survives.
- Round 1 prompts are identical across arms. Cache keys include `run_id` (and so the condition), so the two arms draw independently.
- Task assignments depend only on the seed, so they match across conditions.

## Primary denominator: correct
- Primary rounds 3–10 are `rows[2:10]`, and each employee has 4 primary Y rounds.
- 4 rounds × 2 directions gives the denominator of 8, and the assert enforces it.

## Decision rule: correct
- With n=5, a zero or negative difference makes the one-sided sign-flip p at least 2/32 = .0625, which fails the .05 bar. So a HIT does need all five differences strictly positive, as claimed.
- Checking HIT first is coded correctly.
- Reversed effects come out as DUD, which is acceptable because reverse promotion is excluded up front.

## Confirm before launch (not visible in the supplied code)
1. **`display_status(passed, condition)` takes the condition as an argument.** Confirm its output is byte-identical across arms; otherwise "statuses fixed" is not guaranteed.
2. **Scale of `exact_summary`.** `classify` compares the bounds to 1/4, so the bootstrap must run on per-block rate differences (count/8), not counts. If it runs on counts, `hi<1/4` misclassifies.
3. **The pair-bonus gate.** `pair_internal_bonus_difference` must be the persistent-minus-reset mean in per-round units. It also moves mechanically with approvals, so it is a weak gate.
4. **`Cache` dry mode.** It returns an old market schema (`quantity` and so on) that `parse_action` would reject, which would abort the run. The "full synthetic replay" must use a separate mock that matches the schema. Check which path the tests actually use.

## Limitations to keep in the report
- **Bundled scope:** the reset removes history, own notes, partner notes and prompt length all at once. The result is a total policy effect, not reputation or reciprocity.
- **Reset-arm cue:** the system prompt says outcomes "become public after the round" and calls history "your only memory", but the reset arm gets an empty history at a later round number. That mismatch is a manipulation cue, not just missing information.
- **Small n:** the paired t-interval can degenerate or come out undefined. Sign-flip inference assumes exchangeability. No multiplicity correction after many pilots.
- **Timestamps:** `started_utc` takes the minimum of ISO strings. That is only correct if `now()` and the call timestamps share the same format and offset.
- **Durability:** there is no fsync, so no power-loss durability; this is already disclaimed. Provider identity and settings remain unattested.
