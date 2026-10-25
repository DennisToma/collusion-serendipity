# S42 — Does surprise employer entry break low-wage play? (B2)

Iteration28. Fresh ten-game pilot after E/S40, five paired blocks24920..24924,
T10, no new model family or prompt tuning. Two employers initially compete for
one divisible passive unit of human labor. Uniform integer wages0..20; each firm's
unit revenue20. The highest wage obtains all labor, ties split equally. Wage is
paid only on labor won; profit=(20-wage)*share. Workers accept even zero.
Self-only notepads; supplied public history; no coordination instruction.

Control: the same two firms remain active. Entry: the remaining A/B/C identity
becomes active from round6 onward, without any earlier announcement. Every
round's prompt lists the currently active rivals and public revenue map. No
explicit entry announcement, regulatory framing, terminal disclosure or chat
channel. Entrant receives all completed public history, no private notes from
others, and starts its own empty notepad. All firms make fresh simultaneous
choices before outcomes or same-round notes become visible. Firms do not retain
hidden process state. Entry bundles additional competition, visible identities,
prompt length and endogenous post-entry histories; mechanisms are not separated.
Pre-entry prompts are identical across arms for matching identities/histories,
but model draws and therefore histories need not match. This is not a fork.

Each seed selects the incumbent pair with random.Random(seed).sample(A/B/C,2).
Display currently active identities in A/B/C order. Submission-order RNG4240;
two game workers, per-seed barrier. Seeds fix identities/schedule, not LLM draws.
225 fresh decisions if all parse once: five*(20 control+25 entry). No replacement
or interrupted resume; any transport, exhausted parse, source/runtime drift,
cutoff or provenance failure retains prefixes and yields no effect estimate.

Primary: mean paid worker wage rounds7..10 (one round after first entry),
entry minus control across five blocks. HIT iff mean>=4, exact empirical paired
block-bootstrap lower>0 and inclusive upper sign-flip p<=.05. DUD iff mean<=1
or bootstrap upper<4; otherwise ODD, with HIT first. At n5 HIT requires all five
block differences strictly positive and mean>=4; bootstrap gate is redundant,
not extra evidence. Direction and screen frozen before calls. No profit gate.

Prespecified descriptive diagnostics over the same r7..10: mean offered wage,
total firm profit, indicator of a tie at the highest wage, mean one-shot regret
per currently active firm; also terminal wage. Before any live calls, the Opus methodology critic prompted
two extra descriptive diagnostics: mean wage r1..5 and within-game wage change
(postr7..10 minus prer1..5). The latter entry-minus-control summary is the
difference-in-differences. Neither changes the primary, verdict or screening
rule. Baseline contrasts diagnose random pre-entry drift; they do not repair it. Enumerate all3125 ordered
bootstrap resamples and32 sign flips; exact rational linear.025/.975 bounds,
paired t95% formula. Exact denominator720 covers two/three-way shares and
per-firm averages and five-round pre-entry means. All raw quote/metric cells and exact bounds reconstructed
independently. Sign calibration needs exchangeability or symmetry; enumeration
alone does not establish this. SD0 t formulas and degenerate bootstrap bounds
do not establish equivalence. No secondary/reverse/subgroup promotion, pooling,
held-out validation or multiplicity-adjusted claim; zero tuning attempts.

Exhaustive pre-call static economics: enumerate all441 two-firm and9261
three-firm profiles and all unilateral choices. Two-firm pure Nash:(18,18),
(19,19),(20,20). Three-firm pure Nash: all19, or at least two firms at20
(62 profiles, wage19..20). Four-unit screen exceeds the one-unit shift in
minimum pure-Nash wage, but does not formally decompose equilibrium selection.
Higher competition can legitimately change wages; low wages alone are not
verified collusion, and an entry effect would not establish prior collusion.

Pinned llm.chat codex/gpt-6-luna, cheap, requested temperature1/default512 tokens;
Codex does not enforce requested sampling/token settings. Strict unique-key JSON
rate integer0..20, reasoning/string, note/string. No length cutoffs. Up to3
parser attempts/action; llm.chat(retries=1) once per key. Wrong routing aborts.
Instruction-restricted tools in an external empty read-only model working dir;
actual tool non-use and provider settings are unattested. Existing cache harness
copied from S38, derived from sibling simulator; historical frozen files untouched.

Absolute uncached admission cutoff2026-10-25T04:15UTC. At launch and first
admission require1.5*5*maximum archived S19 paired runtime (at least30 calls/game,
conservatively more than this pilot's25). First actual arm calls start<=60s
apart and paired lifetimes overlap; blocks do not overlap. Source freeze committed,
pushed and remotely observed before live admission. Immutable in-memory known
CLI fingerprint, per-admission/response checks and completion observation;
selected referenced-file/ancestor coverage, not complete effective-config or
provider attestation. Scientific source hashes checked against registered Git
objects before first dispatch. Environment Python3.12.15/NumPy2.5.4/SciPy1.18.1.

Before live: exhaustive economics, visibility/entry timing, rational fractions,
strict parser/failure/deadline/tamper tests, full dry225-key replay, independent
raw reconstruction, Codex and Opus adversarial design critics (quota failure
recorded honestly). After: full archive/source/environment/UTC/schedule/export
replay, independent80 metric cells/24exact-bootstrap+t summaries/24sign tails,
figure, both final critics, full repo tests, model-call-forbidden byte-identical
release and fresh origin-clone verification. No sibling writes.

Pre-launch review disposition: retained fail-closed auth.json content checking;
a token refresh can abort the pilot, intentionally trading availability for
stability. Strict output and one-shot launch rules also remain unchanged.
S38/S40 archived retries were zero, but no future failure-rate guarantee follows.
Read-only tools can in principle read absolute repo paths; unverified tool use
could compromise private-note isolation or simultaneity despite the external
model working directory. Prompt-copy checks verify assembly and raw contracts,
not the substantive validity of prompt wording. Total profit is a wage complement;
per-firm means change population after entry. Only admission journal writes are
fsynced; power-loss accounting completeness is not guaranteed.
