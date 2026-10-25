# S58 adversarial review (from the supplied text only)

**Verdict:** I found no executable bug that changes the result. **ODD** is the correct frozen classification, and the REPORT numbers are right. I did not open any files, raw responses or other reviews, so I could not check the 20 verbatim texts against the parsed booleans.

## Numbers I rebuilt by hand

- **20 raw approvals:**
  - Retain arm: 1,0 / 1,1 / 1,1 / 0,0 / 1,0, which is **6/10**.
  - Erase arm: 0,0 / 1,0 / 0,1 / 0,0 / 0,0, which is **2/10**.
  - Matches with the archived actions: retain 9, erase 7. The only retain mismatch is 24484_A. All three counts agree with the report.
- **15 block cells:**
  - Retain: [.5, 1, 1, 0, .5], mean .6.
  - Erase: [0, .5, .5, 0, 0], mean .2.
  - Contrast: [.5, .5, .5, 0, .5], mean .4.
- **Bootstrap (3125 ordered draws per summary):**
  - Contrast: the count of 0.5 draws follows weights 1, 20, 160, 640, 1280, 1024. The order statistics at positions 78.1 and 3045.9 give **[.2, .5]**.
  - Retain: the sum of doubled draws follows (1+2x+2x²)⁵, with weights 1, 10, 50, 160, 360, 592, 720, 640, 400, 160, 32. This gives **[.3, .9]**.
  - Erase: Binomial(5, .4) weights 243, 810, 1080, 720, 240, 32 give **[0, .4]**.
- **Paired t:** the standard errors are .1, .18708 and .12247. With t(.975, 4) = 2.7764, the intervals are [.122, .678], [.081, 1.119] and [−.140, .540]. All three match.
- **32 sign flips:**
  - Contrast: upper 2/32, lower 32/32, two-sided 4/32.
  - Retain: 2/32, 32/32, 4/32.
  - Erase: 8/32, 32/32, 16/32.
- **Screen:** mean .4 ≥ .25 and the lower bound .2 > 0, but the upper p of .0625 is above .05, so it is not a HIT. It is not a DUD either, so the verdict is **ODD**.
- The REPORT, summary and table rows all match these numbers. The statement "HIT needs all five positive" is correct at n = 5.

## Design checks

- **Selection:** I checked each case's turn against the four-of-eight primary TYPE-Y schedule rebuilt from the partner's visible statuses. Example: in 24482_A, partner B is TYPE-Y at indices 2, 3, 4 and 6, so index 9 must be TYPE-X and turn 6 is the last one. All ten cases are consistent.
  - Selection uses statuses only.
  - The independent script rebuilds the schedule RNG separately from `task_status`.
- **Erasure:**
  - The replay script asserts there is exactly one marker, that the history JSON is canonical, and that it is the length of `turn`.
  - It replaces only that list with `[]`.
  - The independent script rebuilds the line by line splitting and asserts the prefix `Round {turn+1}. `.
  - The test suite asserts that exactly one line changes and that the system prompt and request parameters are identical.
  - The notes JSON escapes non-ASCII characters, so `splitlines` cannot split on a stray Unicode line separator.
- **Guards:** these are all sound.
  - A strict parser that rejects duplicate keys and NaN.
  - One transport attempt (`retries=1`, and `fixed_model` stops the fallback to a second model).
  - Responses are fsynced before parsing.
  - An abort flag held under the admission lock, so a worker's in-flight call can finish but is not accepted after another worker fails.
  - The attempt is reserved before selection, the launch receipt survives deleting the archive, and the registered sources are checked with `git show`.
  - The concurrency sweep allows at most two calls, and there are barriers between blocks.
  - Registration was recorded at 07:34:48, which is 85 minutes before the deadline.

## Executable risks (minor, could not verify)

1. **Clean-clone check:** `check()` and `run()` open `data/s58_history/.writer.lock` inside the clone. If that file is neither committed nor gitignored, the `git status --porcelain` check fails. `logs/s58_launch.json`, `logs/s58_attempt.json` and `data/s58_history/` are currently untracked, so they must be committed before the clean-clone proof can pass.
2. **Zero-length intervals:** the concurrency sweep skips calls whose start and end times are equal. This is unlikely to matter.
3. **Constant checks:** the checks on `source_cli_version` and `source_fingerprint_matches` compare values against themselves. They are documentation, not real verification.

## Acknowledged limitations (not bugs)

- **One draw per cell:** within-case sampling noise is not estimated. The 24484 block's +.5 comes from a fresh retain approval that disagrees with the archived rejection.
- **Retain-arm variation:** on what appear to be the same archived prompts, earlier retain or baseline arms ran .4 (S48), .4 (S50), .5 (S51) and .6 (S55). That suggests about ±.1–.2 variation from one draw to the next. Check this against those pilots' designs.
- **Block 24483 tie was predictable:** all three own-TYPE-Y reviewers (24480_C, 24483_B, 24483_C) rejected in both arms, and 24483 is a mutual-Y block. The tie follows from the case structure, not just from the archived rejections. The design mentions only the archived-rejection floor.
- **Residual information in notes:** both erase-arm approvals (24481_A, 24482_B) are in games whose notes recount the partner's approvals. This is post hoc and must not be promoted as a subgroup finding.
- **Overlap with S55:** S58 and S55 use the same ten cases (S55 +.5, ODD). They are not independent, and the earlier pilots count as multiplicity.

## Scope of the claims

The claims are appropriately limited. They say:
- the erasure changes several things together (prompt length, missing-history cues, and past actions and rewards);
- the notes still contain historical information and the round number stays late;
- the empty history alongside the system's memory wording is itself an inconsistency cue;
- no reciprocity or reputation mechanism is identified;
- this is not a replication of S29, and no hit is promoted.

One wording improvement: say "the upper sign-flip gate fails" rather than presenting it as a separate structural rule.
