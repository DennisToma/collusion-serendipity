# S42 adversarial review: no blocking bugs found, three medium issues to fix before launch

I reviewed the pasted files only. I ran nothing, made no edits and made no model calls. The S42 files are still untracked, so these fixes can go in before registration.

## Checked and correct
- **Economics:** The design's pure Nash sets are correct: two firms give (18,18), (19,19), (20,20); three firms give 62 profiles. If both arms played pure Nash, the difference would be between −1 and +2, so the threshold of 4 can't be reached by equilibrium selection alone.
- **Timing:** `turn>=5` means entry at round 6, and `rows[6:10]` covers rounds 7–10. Notes become visible only in the next round. Pre-entry prompts are the same in both arms, but cache keys differ by `run_id`, so draws are independent.
- **Arithmetic:** The largest denominator in any metric is 72 (regret), so 144 works. The bootstrap quantile matches NumPy's linear method on 3125 samples. An upper sign-flip p ≤ .05 requires all five differences to be strictly positive (one zero gives 2/32). The screen order is right and the boundary tests match.
- **Integrity:** Responses, requests and admissions are cross-checked. A torn or mismatched file is refused rather than repaired. The abort flag can't deadlock: the code calls `Event.set` directly while it already holds the lock. Replay requires a cache hit for every key.

## Remaining bugs
1. **Medium: a routine login refresh could kill the whole run.** `fingerprint()` hashes `~/.codex/auth.json` and is checked before every request and after every response. If codex refreshes its login token during the run, that file changes and the pilot aborts with no estimate. This doesn't bias anything, but it can waste the one launch. **Fix:** remove `auth.json` (and any other file codex rewrites itself) from the check, or hash only stable fields such as auth mode and account ID, and record the rest without gating on it.
2. **Medium: nothing checks whether the arms already differ before entry.** Histories diverge from round 1, so a HIT could come from one arm drifting to low wages by round 5 rather than from entry. **Fix:** before launch, preregister the mean wage over rounds 1–5 per arm and a difference-in-differences as descriptive outputs that don't affect the verdict.
3. **Low: one parse failure anywhere ends the pilot.** A single run of three bad replies (for example, JSON wrapped in code fences) gives no estimate. The design accepts this, but the expected failure rate from the S38/S40 parse-retry counts should be stated.
4. **Low: `launch()` releases the writer lock before `main()` takes it again.** This leaves a short window for a second writer. Keep the lock held, or pass it into `main()`.
5. **Low: `started_utc=min(...)` compares ISO timestamp strings.** It happens to order correctly even when microseconds are missing, but that is fragile. Compare parsed `utc()` values instead.
6. **Low: only the admissions file is fsynced.** Responses, requests and transport-failure logs are not, so a crash could lose the failure record. Damaged files are still refused.
7. **Low: prompt wording.** The prompt says "the higher take-home offer", which is unclear once there are three firms; use "highest". It's a one-word fix and doesn't change the economics.

## Already-acknowledged limitations that should be stated more strongly
- **Tool non-use is unverified, and the consequence isn't stated.** Codex runs in a `-s read-only` sandbox that can still read the repository, including the cache, the other arm's replies and other firms' notes. A model using tools could break the private notepads and simultaneity. The design should say so. **Fix:** capture codex `exec --json` event logs to show no commands were run, or report the risk explicitly.
- **The "independent" prompt check isn't independent.** `expected_prompts` is a verbatim copy of `prompts`, so it confirms the prompts were assembled correctly but can't catch problems in their wording.
- **Some diagnostics aren't separate evidence.** `firm_profit` is always 20 minus the wage, so it carries no extra information. Offered wage and per-firm regret average over two firms in control but three after entry.
- **Already stated in the design:** temperature and token settings aren't enforced by codex; the bootstrap gate is redundant at n=5; a zero-variance t interval is meaningless; the runtime headroom is a heuristic; entry bundles several mechanisms; low wages don't prove collusion.

**Verdict:** I found no bugs that bias the result or break integrity. Fix #1 before registration, since it alone could lose the run. Add #2 as a preregistered descriptive output so a HIT can be interpreted.
