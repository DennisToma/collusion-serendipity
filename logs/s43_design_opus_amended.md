# S43 adversarial review

I reviewed only the text you supplied. I made no edits, made no calls and did not touch the raw archive.

## Verified as correct
- **Payoffs:** `payoff_table` gives the whole labor share to the highest offer and splits ties equally, with a value of 20. The independent rebuilder uses `all(wage>=x)` and gets the same result. The 21 + 441 = 462 rival profiles are each checked against all 21 own wages. Against rivals at 10, an offer of 11 earns 9, versus 5 or 10/3 for matching at 10. That supports the one-unit threshold.
- **Intervention:** the control prompt equals the source prompt exactly. The treatment differs only by text inserted just before `\nReturn strict JSON only`, and a test checks this. There is no recommended action, joint-payoff table or collusion wording.
- **Unit:** the outcome is the focal firm's quoted offer, not worker pay. Each source seed's two cases are averaged into one block, and the results summary says "offer, not realized wage."
- **Statistics:** 3125 = 5⁵ bootstrap draws and 32 = 2⁵ sign flips. The linear percentile at p·(n−1) matches numpy. A HIT needs all five block differences strictly positive: one zero block gives p = 2/32 = .0625, which fails. The 20 calls (10 × 2) and 15 block cells (5 × 3) add up.
- **No retries:** `retries=1`, and `dict.fromkeys` collapses the model list to just `gpt-6-luna`, so each request gets exactly one Codex attempt.

## Bugs still open
1. **The table may show information the agent never saw.** Nothing checks that the round-9 rival offers actually appear in the public history inside `original_prompt`. If the history only showed the winning wage or the allocation, the table gives away private information. That is a confound beyond the bundle the design already admits to. Add a check that each rival rate appears in the prompt's round-9 history.
2. **The payoff rule is never checked against S42.** The highest-offer-wins rule and the value of 20 are assumed, not matched to the simulator or to the archived round-9 outcomes. Add a check that `payoff_table` at the real round-9 offers reproduces the focal firm's archived round-9 share and profit.
3. **Later edits will break validation.** `validate` and `check_inputs` require the current files to match the recorded hashes for every file in SOURCES. That list includes `CLAUDE.md` (the user and director edit it), `DESIGN_S43.md` (you plan to update it after the run), `llm.py`, `pyproject.toml` and `uv.lock`. Any later edit or `uv add` makes analysis, release and the clean-clone check fail permanently. Check against the committed copies at the registered commit instead (the live path already does this).
4. **The time margin is too small.** Only 20 minutes of headroom is required, but the run has 10 back-to-back stages, each allowed up to 600 s plus a 5 s sleep. Any request admitted after 04:30 marks the pilot unclassified after calls are already spent. Require headroom of at least the realistic run time, e.g. 60 minutes.
5. **A response can be accepted after an abort.** Once one worker fails, the other worker's in-flight response still reaches `accepted.jsonl`, because nothing checks `abort.is_set()` before that write. It's harmless, since the run is marked failed, but the journal then shows acceptances after the failure.
6. **The clean-clone check depends on files the registration step doesn't check.** It needs `data/s43_payoff/`, `logs/s43_launch.json`, the S42 raw archive and `logs/s42_launch_preflight.json` to be committed and not gitignored. I can't tell from the supplied text whether they are.

## Limits the design already acknowledges (fine as stated)
- The challenge was chosen after reading S42 transcripts.
- The table bundles arithmetic, rival salience, length and row order, so it can't isolate a mechanism.
- Rivals are not rerun, so this says nothing about realized pay or coordination.
- Each case gets one draw per arm, so sampling noise and differences between histories are mixed. With n = 5, the bootstrap gate adds nothing beyond the sign test, and there is no equivalence claim.
- Codex ignores temperature and max_tokens.
- The `response['model']`/`backend` checks only echo the requested model name, not what was actually served. Tool non-use, the full effective settings and accounting after power loss are unattested. A read-only sandbox can still read the S42 archive by absolute path.
- There is no held-out validation and no correction for multiple comparisons. A HIT alone doesn't change the sibling repo's headline.
