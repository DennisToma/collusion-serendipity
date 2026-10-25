# S44 review: payoff-row order (DESIGN_S44.md, supplied text only)

**Verdict: DUD is correct.** The descending-minus-ascending contrast is −0.1. I found no bug that changes the primary result. Five items still need checking or fixing, listed under Remaining bugs.

## Reconstruction

The raw archive wasn't available, so I worked from the 20 per-case quotes in `results/s44_payoff.json`. I could not check them against the raw response text.

- **Block cells (15).** Ascending: 10, 10.5, 10, 10.5, 10.5, mean 10.3. Descending: 10, 10, 10, 10.5, 10.5, mean 10.2. Contrast: 0, −0.5, 0, 0, 0, mean −0.1. All match.
- **Bootstrap (3125 samples).**
  - Contrast: the number of times the −0.5 block is drawn follows Binomial(5, 1/5), giving 1024/1280/640/160/20/1 samples. The 2.5% position is 78.1, which falls in the k=3 group, so the lower bound is −0.3. The 97.5% position is 3045.9, in the k=0 group, so the upper bound is 0. **[−0.3, 0] matches.**
  - Ascending: Binomial(5, 3/5) gives [10.1, 10.5]. Descending: Binomial(5, 2/5) gives [10.0, 10.4]. Both match.
- **t interval.** SD 0.2236, SE 0.1, critical value 2.776, giving [−0.378, +0.178]. Matches.
- **Sign flips (32).** Only one block is nonzero, so 16 of the 32 sums are −0.5 and 16 are +0.5. Upper p = 1, lower p = 0.5, two-sided p = 1. Matches.
- **Secondary counts.** Offers at 0: 0 in both arms. Matches to the archived offer: 7 ascending, 8 descending. Both match.
- **Arithmetic and verdict.** The payoff tie rule is the same in the replay and independent scripts. The exhaustive test covers 462 rival profiles = 21 + 21²; correct. Mean ≤ 0 means DUD is applied correctly.

## Scope and isolation: pass

- Same source selection as S43, and no source action is used to select cases.
- The focal agent is `initial[0]`, i.e. the first name in sorted `assigned_pair`.
- Rival offers are taken from `rows[8]`, which is round 9, and are checked against the public history and the round-9 profit and share.
- The only difference between arms is that the row list is reversed. The tests confirm the header, rival list, system prompt and tail are identical, with no recommendation.
- The measured unit is `parsed.rate`, the focal offer, not realized worker pay.
- Schedule: first-view order is opposite for the two contexts within each block, blocks are separated by barriers, and at most 2 calls run at once.
- Integrity checks are in place: fsync before parsing, a one-shot `open('x')` receipt, abort when another worker fails, and a commit/remote/source check at the registration commit. Registration was at 04:50:40, about 69 minutes before the 06:00 cutoff.

## Remaining bugs and checks

1. **Origin-clone reproduction isn't possible yet.** `data/s44_payoff/` and `logs/s44_launch.json` are untracked. `validate` needs both, so the fresh-clone step can't pass until they are committed. No `logs/s44_remote_clean_clone.json` exists yet.
2. **Stray lock file could fail the clean-clone check.** `check()` calls `run(directory)`, which creates `data/s44_payoff/.writer.lock`. Unless that file is committed or gitignored, `git status --porcelain` in the clone will not be empty.
3. **Level-metric sign-flip p-values look like significance.** In the results JSON, the ascending and descending upper p = 0.03125 tests against an offer of 0, which means nothing. Label or drop them. The primary result isn't affected.
4. **Possible view-order effect to check (descriptive only).** In blocks 24923 and 24924, one context has ascending = 11 and the other has descending = 11, with opposite first-view orders. Checking `schedule.json` would show whether the 11s line up with first-versus-second call position. This must not be promoted.
5. **The independent script isn't independent on the archived quote.** It takes `archived_quote` from the archive manifest rather than re-parsing the S42 response. `select_cases` is only re-run inside `validate`. This is minor.

## Acknowledged limits (correctly disclosed)

- Selection is post hoc and n = 5. Four of five blocks tie, so the bootstrap and sign test are effectively degenerate.
- `source_fingerprint_matches=false`: the local Codex setup differed from S42's. This affects only the comparison to archived offers, not the two fresh arms.
- Provider settings and temperature aren't enforced or attested, and tools are restricted only by instruction.
- Row order changes position and recency together.
- In the mocked live test, concurrency checking is vacuous because all timestamps are equal. The synthetic timing tests cover it.
- Not stated, but worth adding: offers stick at 10 (archived-match rate 7–8/10). That leaves little room to detect an effect, and the DUD doesn't rule out small or reverse effects.
