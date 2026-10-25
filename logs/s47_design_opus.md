# S47 adversarial review (supplied text only)

**Verdict:** I found no blocking bug in the science or the integrity checks. There is one presentation bug that you should fix before registering, because `s47_present.py` is a frozen source. I couldn't check the S42 raw archive, the `sim.entry.outcome` code or the clock, so every "OK" below rests only on the code you supplied.

## Bugs

1. **Copy-paste labels from S44 in `s47_present.py`.** The block-table header says "Descending−low_example", and so does the figure's `axes[1]` y-label ("Descending − low_example offer"). Both should say "High example − low example". This is cosmetic, but a judge-facing figure and table that say "Descending" are wrong. Fix it before the registration commit.

## Checks that pass (as written)

- **Source cases.** All ten S42 games (seeds 24920–24924 × control/entry) are covered. The focal agent is `sorted(assigned_pair)[0]`, asserted equal to the round-1 roster. The round-10 request key `[run,9,agent,0]` is unique and its hash is checked. The round-9 rival offers match the public history. The archived quote matches the round-10 action. Notes are self-authored, 9 of them, covering rounds 1–9. The source code hashes and duplicate responses are rejected. Selection doesn't depend on the agents' actions.
- **Only one prompt difference.** The system text, request fields, table and warning are constants. The test checks that each example string appears exactly once and that the two prompts are identical once it's replaced. `json.dumps` produces exactly `{"rate": 0, "reasoning": "", "note": ""}` and the `rate: 20` version. Both are valid under `strict`. The supplement goes right before the original output contract, and the prompt ending is preserved.
- **Payoff table.** It runs in ascending order over 0..20. The share is 0 below the highest rival offer, otherwise 1/(1+number of tied rivals). It is checked against `sim.entry.outcome` for every 1- and 2-rival profile, and against the realized round-9 share and profit. Productivity 20 and offset 0 are asserted.
- **Unit.** The outcome is the focal agent's offer, never realized wages. The figure title and the summary both say so.
- **Two-unit screen.** The rules are HIT → DUD → ODD in that order. The 3125 draws and the exact linear percentiles match `np.quantile(method='linear')`. The independent check uses doubled integers, so ties are handled exactly. At n=5, an upper p ≤ .05 forces all five block differences to be positive (a zero gives p = 2/32), as the design says. The `lower>0` condition is then redundant but harmless.
- **Schedule.** RNG seed 4747. The two contexts in each block get opposite first-view orders. The check enforces concurrency ≤ 2 (ends sort before starts at tied times), views running in sequence, and full barriers between blocks.
- **Failure handling and registration.** One transport attempt (`retries=1`, single-model `_codex`). The response is fsynced before parsing, and any error aborts the whole pilot and writes `failure.json`. The one-shot external receipt is created with `open('x')`. Before any call, the code checks HEAD == `ls-remote`, a clean diff, that the sources are tracked, and that hashes from `git show` match. There is a 20-minute headroom check at registration, launch and first admission, and admissions stop at 06:30.

## Acknowledged limits (not bugs)

- Selection is post hoc, not held out, with n = 5 blocks, one model, and uncontrolled draws on a shared service.
- Temperature and max_tokens are not sent to codex. Tools are restricted by instruction only. Model identity and effective settings are unattested.
- Numeral, length, salience and the action association change together. Rate 20 is always a zero-profit row in the table, and rate 0 is zero-profit unless a rival offers 0, so an "example = bad action" signal is also confounded. This doesn't isolate anchoring.
- The screen is one-directional, so a DUD doesn't rule out an effect in the opposite direction.
- If the original output contract contains its own example or schema, the two examples may interact. I can't see that text.
- `s47_independent.py` recomputes the statistics only; it doesn't re-check the schedule and journals (`validate` does).

## Before launch

Fix the labels and re-run the tests. Check that `date -u` leaves at least 20 minutes before 06:30 at registration. Then commit, push, and confirm the remote matches.

I make no claim about an anchoring or collusion mechanism.
