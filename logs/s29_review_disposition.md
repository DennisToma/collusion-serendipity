# S29 critic dispositions

## Methodology, before scientific calls

[Codex](s29_design_codex.md): exit0,static review of requested files and call
wrapper;no tests/live calls. No substantive design/implementation bug. Its
prelaunch untracked-source blocker is resolved only by the upcoming frozen
source commit/push and matching-remote observation. Its non-atomic caveat describes
an earlier snapshot; [targeted Codex patch review](s29_design_atomic_codex.md)
exit0 confirms serialization of abort transition and logical admission. The
manager's deterministic concurrency regression executes the ordering. Transport
start/completion after a prior admission remains expressly allowed.

[Opus](s29_design_opus.md): exit0,supplied-text-only review,no shell or raw-data
access. Snapshot preceded the atomic patch,latest wording and backend canary.

- Potential repo-working-directory leakage: checked actual frozen llm._codex;
  it already launches from a new empty external temporary directory with
  `-s read-only` and direct-answer/no-commands instruction. Added mocked command
  canary checking external empty directory,sandbox,output path and absence of repo
  path in the supplied scenario. This verifies invocation construction only;
  read-only does not prohibit all filesystem reads,tools are not disabled,and
  actual non-use remains unverified. No claim of OS read isolation or independently
  observed runtime tool behavior. Do not alter historical llm.py.
- Accepted clearer common wording: `work notepad`, `No one else can read either
  notepad`;one truthful readability sentence remains the only initial contrast.
- Accepted explicit completed-but-invalid disposition: log INVALID/no estimate,
  preserve paid evidence,no rerun. This adds no statistical/exposure gate.
- Launch lock gap retained with exclusive one-shot receipt/config fail-closed
  checks;no scientific restart. Already-admitted requests may finish after abort.
- Accepted hard_negative-null validation. Repository-root invocation documented;
  code/design/renderer/release sources freeze before live and remain untouched.
- Floor/ceiling noted prospectively;report both fresh baselines,no equivalence or
  communication-absence claim from DUD. No outcome-based exposure exclusion.
- Declined suggested population false-HIT bound:32 sign patterns are arithmetic,
  not an unconditional error-rate guarantee;randomization/exchangeability and
  multiple exploratory choices are not established by that count. Report only
  frozen descriptive statistics and exploratory screen.
- Cosmetic unused outsider branches left for archive lifecycle compatibility;
  generation and replay enforce exactly two active employees in both arms.

Final prelaunch manager checks:14 S29 tests,full dry200-key exact replay,
independent50 raw metric cells/15 bootstrap+t summaries/all15 sign-tail sets,
200 histories/200 note snapshots;full suite225 checks PASS after final edits (14 scoped historical S21 synthetic
clock overrides;real S21 archive separately passes original cutoff).
Actual scientific calls:zero when these methodology dispositions were written.

## Final claims

All ten games/200 decisions completed;frozen ODD result and full reconstruction
available. Independent final reviews requested;dispositions pending. The
post-outcome17-event appendix was prepared before final-review launch,although
it is outside the fixed final-review file list and scientific source manifest;
do not treat it as separately critic-certified without an explicit reviewer check.

### Final disposition

Both final critics exit0: [Codex](s29_final_codex.md) and
[Opus](s29_final_opus.md). Both confirm primary0.325[0.100,0.575],paired
t[-0.048790,0.698790],upperp0.0625 and ODD. No estimate-changing bug found.

Codex independently reconstructs all50 metric cells,15 exhaustive bootstrap+t
summaries and32 inclusive sign patterns per metric from raw reviews;all200
request hashes/decisions/history/snapshots,18 registration hashes,canonical
cache-only replay and timing/publication checks pass. Six selected tests run.
Figure,appendix,full suite and clean clone remain manager checks,not Codex claims.

Opus is supplied-text-only:hand-recomputes counts,primary bootstrap multiplicities,
t/sign arithmetic,bonus and screen;no raw archive/tool/hash/git execution. Its
publication/findings list describes pending snapshot obligations,not verified
current git state. Results/commit/clean-clone steps are completed and logged
separately. Existing final Codex process was running concurrently with Opus.
Accepted explicit `post-outcome` label for REPORT appendix;all-event selection
has no semantic labels or inferred intent. Dead outsider branch/stale literal and
unused compatibility variables do not execute in two-person games;retain frozen
source bytes.

Codex identifies a real scope gap in the STANDALONE independent checker:it does
not raw-bind final emitted note text or independently verify the registered
nonempty-note metadata. Canonical replay already rejects both mutations and the
present archive is valid. Added separate post-outcome verifier
[s29_auxiliary_check.py](../scripts/s29_auxiliary_check.py),outside frozen science,
which raw-binds all200 emitted notes/explanations including20 final-round outputs
and verifies self100/100,shared99/100 nonempty-note counts. Two adversarial
in-memory regressions reject the precise final-note and count mutations reported
by Codex. [Receipt](s29_raw_auxiliary_check.json). No frozen code,data,metric,
threshold,exclusion or result change. This companion verification was written
after final critics,so it is manager-verified,not independently critic-certified.

Manager inspected the figure. All17 primary adverse events in the separate
post-outcome appendix bind accepted raw action/reason/note and actual prior-note
snapshot;two forbidden-model-call runs reproduce both supplement artifacts
byte-for-byte,all scientific files/result unchanged. [Receipt](s29_supplement_check.json).
Full pre-companion suite225 PASS;final227-test suite and pushed clean-clone
publication receipt are the remaining final checks at this entry's timestamp.

Presentation-regression note:condensing REPORT removed the prose anchor required
by the historical S25 safe renderer. The first post-companion227-test sweep had
one presentation error (no scientific failure). Restored the exact archived S25
paragraph;focused legacy regression PASS and final full sweep rerun. REPORT is
46 lines;older context remains archived verbatim. No historical source changed.

Final full227-test suite PASS after anchor restoration;all18 original source
hashes and canonical result SHA0b8e2562 unchanged. Final analyze/independent/
present/release/cache-resume reproduce six core artifacts byte-for-byte;raw
auxiliary check and all17-event supplement PASS. Results push/remote-clone receipt
are recorded in STATUS and logs/s29_remote_clean_clone.json after publication.

Publication COMPLETE:results commit 3c4438fa436de1b79e19dfcd1a351e3101aee115 pushed.
[Fresh origin-remote clean clone](s29_remote_clean_clone.json) passes17 checks,
all registered offline validation and nine byte-identical artifacts,including
raw auxiliary and supplement outputs;clone git status clean. Existing frozen
dependency environment reused explicitly. Full227-test root suite PASS.
No further scientific call or frozen-source/result change.
