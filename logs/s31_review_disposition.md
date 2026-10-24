# S31 methodology review disposition (before live calls)

Codex read repository files and ran an entirely mocked backend probe. Opus reviewed
supplied text only; no shell/raw-cache access. Both original reviews retained.

- Codex high transport retry bug accepted: copied archived common cache into
  S31-only sim/labor_cache.py, pinned codex/luna, llm.chat(retries=1). A mocked
  backend first failure triggers exactly one invocation, writes transport failure,
  terminal abort and no later admission. Historical frozen sources untouched.
  Codex CLI itself may retry internally; provider execution is not attested.
- Codex independent-acceptance gap accepted: separate unique-key/schema/type
  validator now checks every response and rejects discarded valid earlier outputs.
- Opus cutoff boundary accepted: validate logical admission against cutoff, allow
  transport start/completion later; raw chronology still enforced.
- Opus interruption recording accepted: BaseException from workers records failure;
  parent invocation interruption also records cause. Hard process death may leave
  only incomplete execution journal, which blocks resume/publication.
- Opus prefix wording accepted: partial evidence preserved in raw request/response
  caches; no promise that unfinished games have game JSON.
- Opus gitignore question checked: both required historical and future raw paths
  are unignored. Full remote clean-clone check remains a release gate.
- Removed always-false cache_only assignment in fresh path. Duplicate completion
  source check is harmless and retained. Model metadata/provider execution,
  synthetic world, n5 and tool restrictions remain explicit limits.
- Added exchangeability/symmetric-difference calibration caveat for sign flips.

Final dry archive: all200 keys replayed, 50 independent metric cells,
15 exhaustive bootstrap+t summaries, five complete sign-tail sets and all200
notes/reasons including final outputs PASS. Twelve scoped checks PASS. Full
257-test repository suite PASS (14 scoped historical S21 synthetic clock overrides; real original-cutoff S21 release separately PASS). No live outcomes existed during these fixes.
Patch-specific independent Codex check PASS before freeze: independently mocked transport/abort/deadline/first-valid acceptance, full synthetic200-key verification and discarded-valid-response mutation. No remaining blockers. Eighteen final scientific source hashes recorded in logs/s31_readiness.json.


## Final-claim reviews (after outcomes)

Codex independently reconstructed raw wage decisions,all five metrics/bootstrap
bounds/sign tails,all200 cached prompts and the18-source freeze before reading
any other final critic review. It also invoked the independent verifier. Opus
reviewed supplied source/result summaries only and checked arithmetic/analytic
stage equilibria without raw data or shell;no other final critique read. Both
confirm DUD and primary0[0,0],t[0,0],upperp1.

- Opus medium ambiguous "verifies no agreement" accepted: REPORT now says the
  wage level "does not establish an agreement". Added joint-profit wage0 to
  distinguish the observed mean10 from both benchmark extremes. Declined any
  diagnosis of an even-split habit or strategy from this post-outcome pattern.
- Codex medium CLI execution provenance accepted as an unresolved limitation:
  source/experiment configuration and Python dependencies were frozen,but the
  Codex executable/effective inherited configuration were not. Explicit in
  REPORT/README/DETAILS. New separate post-run runtime observation records
  current version/launcher+available binary hashes/config-file hash without
  revealing configuration contents. It is not retrospective attestation or
  a controlled effective-configuration reconstruction. A future experiment
  should preregister those inputs and a controlled config directory.
- Opus low replay patch alias documented: sim.common.llm and
  sim.labor_cache.llm refer to the same imported module;the forbidden-call patch
  therefore covers both. Frozen source kept. Low lexical deadline comparison
  documented: now() generates the fixed UTC ISO format used by the cutoff;
  parsed-datetime validation covers recorded chronology. No format-general claim.
- Opus low hard-coded notes denominator: the independent verifier reconstructs
  both notes per round and checks all20/game,with five games per arm. New
  post-run runtime observation separately counts actual100 written/nonempty
  notes per arm and binds them to the unchanged result.

No frozen scientific source,result,screen,tuning,exclusion or model call changed.
Figure inspection,post-run observation,release and remote-clone checks are
manager validation outside the critics' fixed input sets. Remote clone pending.
