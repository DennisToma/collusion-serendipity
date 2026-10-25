# S60 adversarial review (supplied text only; nothing executed)

**Verdict:** The design is largely sound. Economics, paired schedules, simultaneity, visibility and the statistics arithmetic check out by hand. I found no bug that would invalidate an estimate. The issues below are test gaps and launch risks, so fix them before freeze.

## Bugs and remedies

1. **High arm's equilibrium is never tested.** `test_unique_stage_equilibria_and_temptation` checks only `'low'`. The design's claims "unique in each arm" and "+4 versus −1" are therefore untested for `high`.
   *Remedy:* loop over both conditions. Assert mutual both-Y approval gives (4,4) in high and (−1,−1) in low, and that unilateral rejection gains +2 in both.

2. **The one-numeral contrast is assumed, not asserted.** `assert_s29_request_identity` and the S29 test use `.replace('author 6 bonus points', …)`. If the S29 text contained that substring twice, both copies would change silently.
   *Remedy:* assert `count('author 6 bonus points')==1` on the S29 system text. Also assert that a character diff between arms is exactly one character.

3. **Token refresh can abort the whole pilot.** `fingerprint()` hashes `~/.codex/auth.json` bytes before every admission and after every response. A routine token refresh mid-run would abort the pilot, mark it INVALID and waste quota. The design acknowledges this, but nothing mitigates it.
   *Remedy:* refresh credentials immediately before launch, and check token expiry against the headroom. Alternatively, fingerprint stable identity fields (account and plan) rather than raw bytes, decided before freeze.

4. **`classify` takes a dead parameter.** Its third argument, `pair_internal_bonus_difference`, is unused, and `analyze` computes `score` only to pass it in. This reads like a hidden bonus gate.
   *Remedy:* remove both.

5. **Dead test branch.** In `test_active_team_and_simultaneous_visibility`, the `else:` branch never runs because every active agent is in the pair. The `'work author_bonus'` assertion inside it checks nothing.
   *Remedy:* delete the branch, or replace it with an explicit check that the second speaker's prompt contains neither the partner's current-round review nor its note.

6. **Cosmetic.** `assert cfg['environment']==EXPECTED_ENV, author_bonus` (two places) uses a function object as the assertion message.
   *Remedy:* use a string message.

7. **Freeze precondition.** `DESIGN_S60.md` and every `scripts/s60_*.py` file are currently untracked. `capture_registration` and `git ls-files --error-unmatch` will fail until all SOURCES are committed and pushed together.

## Verified OK

- Arithmetic of the 16 profiles per arm.
- Reviewer payoff is identical across arms (1, or −2 for Y).
- `task_status` ignores condition, so schedules are identical; 4X/4Y primary per agent gives an 8/8 denominator.
- Notes are tagged `round=t+1` and filtered `<=ti`, so current writes are hidden.
- Exact bootstrap indices 78/79 and 3045/3046 match `numpy` linear quantiles.
- Inclusive sign-flip p ≤ .05 forces all five differences strictly positive.
- ISO string comparisons stay ordered even when microseconds are omitted.
- Admission/response/request journals fail closed.
- Abort is serialized with admission.

## Limitations (not bugs)

- **Both-Y rounds vary by block.** Joint both-Y rounds are hypergeometric per block (0–4). The immediate +4/−1 contrast applies only there; mixed rounds test intertemporal reciprocity. Report both-Y counts per block descriptively.
- **Bundled changes.** Own reward, joint surplus, score scale and numeral salience change together. The low arm also reads the ungrammatical "1 bonus points".
- **Tool non-use and model draws are unattested.** The cache holds stripped adapter text only; codex event streams and possible CLI-side memory or personalization state are not archived. A future fix would be to archive `codex exec --json` events.
- **Small n.** With n=5, the screen has low sensitivity if the low-arm Y baseline is already high, or if the effect falls below 2 approvals per game. A strong reverse effect is classified DUD by construction.
- **Selection.** No multiplicity correction is applied despite selection from prior exploration. There is one model and one synthetic workplace.
- **Unconfirmed launch window.** The 1.5× S19 headroom heuristic is not a guarantee: in-flight calls may finish after 09:00 UTC, and launch must happen early enough on 2026-10-25 to pass the gate.
