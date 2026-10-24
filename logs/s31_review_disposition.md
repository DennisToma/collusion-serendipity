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
