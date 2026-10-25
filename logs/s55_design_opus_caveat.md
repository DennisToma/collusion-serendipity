# S55 pre-launch review (from the supplied text only)

**Verdict:** I found no executable bug that should block the launch. The intervention, the payoff claim, the guards and the statistics all match the design. The main problem is design power: given the selected cases, a HIT is close to structurally out of reach. The writeup should say this before launch.

## Checks that pass
- **Selection:** `turn=max(t∈2..9 : partner not passed)` uses task statuses only. Every partner has four primary TYPE-Y rounds, so a case always exists. The script takes the last attempt and asserts its parsed action equals the archived one. Approvals, notes and earlier replays are never used. The independent verifier rebuilds the same rule from the S29 task-status RNG. Coverage is 10 cases in 5 blocks, with own types 7 TYPE-X and 3 TYPE-Y.
- **Deletion:** It requires exactly one marker, a canonical `json.dumps` round-trip, both keys present and the partner as TYPE-Y. It removes only the reviewer's key, so the masked map is `{partner:"TYPE-Y"}`. The test diff shows only that one line changes, and the system prompt and request parameters are identical across views. The verifier rebuilds the deletion line by line without calling `request()`.
- **Payoffs:** In `outcome`, the reviewer scores `6·incoming − 2·outgoing` whatever its own type, which the test confirms. The partner gets +1 for approving an own-X reviewer and −2 for an own-Y one, so own type changes the partner's incentives. DESIGN_S55 states both points correctly and rightly makes no role-confusion or irrelevant-information claim.
- **Transport:** `llm.py`'s hash is checked against the S29 source manifest, so the wrapper text is the same as in S29. With `backend='codex'` and `retries=1` there is exactly one subprocess call. `fixed_model` changes nothing because `CODEX_CHEAP` is already gpt-6-luna. A timeout or non-zero exit becomes a `RuntimeError` and aborts the run.
- **Failure and one-shot guards:** The attempt reservation is written before selection, fingerprinting and registration. The receipt file is created exclusive. On failure a `failure.json` is written and the run never reinitialises. Each response is fsynced before parsing. The admission lock serialises abort with admission, and the fault-injection tests cover these paths.
- **Validation:** It checks the 2-call concurrency limit (ends are processed before starts at tied timestamps), sequential views within a case, block barriers, 20-minute headroom, runtime hashes, and a git ancestry and blob match for the sources and the case manifest.
- **Statistics:** The bootstrap uses exact rational linear percentiles over all 3125 draws, matching numpy's `linear` method. The sign-flip tests are inclusive and exact, and `classify` follows the stated rules. One consequence: a single zero block gives an upper p of 2/32 = 0.0625, so a HIT needs 5/5 strictly positive blocks. The design says this.

## Minor executable issues (non-blocking)
1. **Live destination isn't pinned.** S29 pinned its live output directory; `run()` doesn't. A mistyped `--data` would use up the one-shot reservation and leave the archive somewhere `release`/`analyze` won't find it. Add a check that the live destination is `data/s55_visibility`.
2. **Gaps in the independent verifier.** It doesn't confirm that each seed contributes two different agents, or that the chosen request is the highest attempt index. The main validator does cover these.
3. **Unquantified abort risk.** Parsing is strict with no retry, so an output wrapped in a code fence aborts the whole pilot. Before launch, count how often S29 needed attempt > 0. For example, a 3% per-call failure rate gives only about a 54% chance that all 20 calls succeed.
4. **Figure.** The binary lines for the 10 cases plot on top of each other. Add jitter or counts.

## Acknowledged limitations: correctly stated, but some are understated
- **Floor effect (needs adding).** In blocks 24483 and 24484, all four archived actions are rejections. If fresh visible-view choices look like those, the visible-minus-masked difference in those blocks can be at most zero. That makes 5/5 positive blocks, and so a HIT, very unlikely. This doesn't select on outcomes, but it should be written into the design.
- **Own type is confounded with block.** In block 24483 both contexts are own-Y, in the same round, with the same history and notes; only agent identity and labels differ, so they are near-duplicates. A reciprocity account predicts a positive effect for own-X reviewers and a zero or negative one for own-Y. So the block-level rule all but rules out a HIT even if the mechanism is real. The design's pooling caveat should name 24483 explicitly.
- **Other masked-view cues.** Own type can still be partly inferred from history and notes, and the incomplete map is itself a cue. The design states both.
- **Small-n statistics.** With n=5, bootstrap coverage is poor, the gates aren't independent, and a DUD can leave the 0.25 question open. All of this is acknowledged, and calling the bounds descriptive is appropriate.

## Recommendation
Launch once item 1 is fixed (it's a one-line guard) and the S29 retry rate is checked (item 3). Add the floor-effect and 24483 notes to DESIGN_S55 now. Report a DUD or ODD result as a low-power screen with no conclusion either way, not as evidence that own status has no effect.
