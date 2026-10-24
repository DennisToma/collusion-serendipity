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

Pending completed dataset and independent final reviews. No live estimate yet.
