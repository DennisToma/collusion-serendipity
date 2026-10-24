# S19 normative versus neutral labels

Ten exploratory repeated workplace-review games; fresh blocks24320..24324,
normative/neutral semantic framing. T10; primary rounds3..10; zero tuning.
Both arms have shared notepads. Incentives, assigned pairs and boolean task schedules
are matched; generation uses arm-specific displayed PASS/FAIL or TYPE-X/TYPE-Y.

`trajectories.jsonl` contains public review actions, archived boolean statuses,
individual bonuses and organization losses. Boolean `market.passed` is the internal
positive-type flag in both arms; the neutral prompt never exposes PASS/FAIL words.
`ground_truth.jsonl` and per-game ground truth include pair identity, private notes,
private reasoning, call provenance and arm metadata; they are not detector input.
Agreement, coordinated-actions and realized-collusion fields are null/unverified.
No detector is fitted or evaluated in this pilot.

All raw responses and exact prompts/keys are retained under `raw/`, including
invalid-output attempts. `config.json` binds the pushed source registration,
19 source hashes, dependency versions and absolute logical-call cutoff. The
one-invocation execution journal and launch receipt preserve local chronology;
no provider/server time attestation is claimed. Failed/incomplete archives must
not be analyzed or restarted. No selected-subset estimates or pooling.

Design: ../../DESIGN_S19.md. Release: `uv run python scripts/s19_release.py`.
