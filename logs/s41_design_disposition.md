# S41 initial design-review disposition

Initial Codex and Opus reviews both exit0. Codex read local files and ran15
selected in-memory tests;Opus only read supplied code/text,no execution or raw
archive access. No high-severity issue found. All changes below precede paid calls.

Accepted:check paired logical invocation timing at the end of each live block,
write a terminal failure marker and abort before later blocks;new non-overlap,
late-start and successful-overlap regressions. Reword stage incentives to say
same payoff/allocation formula with different feasible deviations. Hold a separate
external launch flock through registration checks and main execution;the dataset
writer lock remains inside main. Add an explicit result-field convention that
paired_t_ci95 denotes one-sample t on per-arm summaries and paired t on differences.
Add fine minimum-Nash19 line alongside the clearly labelled coarse18..20band.
Remove unreachable cache_only assignment and normalize negative zero in history.
Add canonical REPORT-row binding and independent stage-economics replay to release.

Both preconditions are enforced by code:tracked source registration pushed and
remotely observed,plus conservative runtime headroom. A legitimate auth refresh
may abort;its probability is unknown,despite the Opus review's uncalibrated
'high' characterization. Strict retries can select valid-format responses;retry
counts will be reported. Seeds do not fix model draws. No representation-only,
coordination,equivalence or provider-attestation claim. Amended reviews pending.

Amended Codex and Opus full reviews both exit0. Accepted the Codex findings:
limit snapshot delimiter splitting to its first occurrence;compare reconstructed
rows using canonical serialized JSON;enforce float quotes and positive-zero
normalization in both validators. The full mocked-live test now cycles low,
high,half-unit,tied and negative-zero inputs and writes a note containing the
snapshot delimiter. A terminal-round integral-representation tamper is rejected.
32scoped tests pass,including complete mocked-live/raw/exact/presentation checks.

Opus amended findings disposition:all required cache/journal/receipt paths are
not ignored and the S19 reference is tracked(logs/s41_tracking_precheck.json).
The run_manager wrapper is the current sequential parent,not a second manager
editing sources;no other explorer run will be launched. Auth refresh remains a
prospective fail-closed risk;no interactive refresh is attempted. Paid responses
are preserved in raw cache before post-response drift rejection,not discarded.
Known-input checks benchmark about0.6s each,under Opus's suggested1s concern;
conservative runtime gate still applies but is no guarantee against service stalls.
KeyboardInterrupt leaves an incomplete execution journal,which forbids resume
and estimates;no additional failure marker is required for validity. Prompt
literal copying verifies assembly/raw contracts,not independent substantive truth
of wording. Routing labels check requested-route consistency,not served identity.
Both histories serialize quotes as floats;only feasible grid differs prospectively,
so Opus's claim of differential float serialization is not adopted. No model use
or statistical threshold/outcome selection changes. Targeted patch critic pending.

Targeted Codex patch critic exit0:no concrete blockers within requested scope.
It passed16in-memory tests and encountered16read-only filesystem errors on
file-writing tests;these are not claimed as passes. Local full32scoped and
488canonical tests all pass with childexit0,including complete varied mocked-live.
All23source hashes match final200-key dry archive;no paid calls yet.
The earlier static receipt still held four pre-patch hashes;the final guard
caught this before launch. Those hashes are preserved under earlier_pre_patch_sources,
and scientific_sources now equals the final dry manifest/current sources.
