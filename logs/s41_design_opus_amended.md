# S41 adversarial review (static reading only)

I had no shell or file tools in this session, so I reviewed only the files you pasted. I ran no tests and couldn't check `.gitignore`, git state or the clock.

## What I checked and found correct
- **Economics:** the pure Nash sets are right. Coarse is {18,19,20}; fine is {19,19.5,20}. At (18,18) the deviation payoff equals the current one; at (17,17) moving to 18 pays more.
- **Exact arithmetic:** every metric sits on a 1/64 grid; regret is the binding case, quarter-units over 16 firm-rounds. Values round-trip through float without loss.
- **Bootstrap:** the 3125 resamples use the same interpolation as numpy's linear quantile.
- **Sign-flip:** with 32 flips, inclusive p≤.05 holds exactly when all five differences are strictly positive (a zero gives .0625). The HIT/DUD/ODD order is correct, and the bootstrap gate adds nothing beyond that.
- **Simultaneity and notes:** each round's wages and notes are added only after both firms' calls, and each firm sees only its own notes.
- **Parser:** -0.0 is normalized; `1e400` (parses as inf) is rejected by the range check; duplicate keys, NaN and bools are rejected.
- **One transport attempt per call:** confirmed (`retries=1`, no waits for codex, a single model in `_codex`).
- **Replay:** it can't rewrite the cache, because the torn-file check runs before the base class's repair code.

## Remaining bugs
1. **Release-blocking check, unverified (Medium).** A fresh clone can only re-run `analyze` if these are tracked in git: `data/s19_labels/**` including `raw/responses.jsonl`, `logs/s41_launch_preflight.json`, and all of `data/s41_ticksize/raw/*`. `.gitignore` has uncommitted edits. *Fix:* run `git check-ignore -v` on each path before launch.
2. **Likely abort from outside changes (Medium).** The guard hashes `~/.codex/auth.json`, `CLAUDE.md` and every file in SOURCES before each admission and after each response. Two things could change them mid-run: a codex token refresh, or the wrapper or next manager iteration editing those files. The after-response check also throws away a response that was already paid for. *Fix:* pause `run_manager.sh` or keep it away from SOURCES during the run; make sure the auth token is fresh before the launch receipt is taken; report any abort as an abort.
3. **Unmeasured guard cost (Low–Medium).** Every guard call re-hashes the node and native codex binaries, twice per decision, and the pre-admission check holds the global admission lock, so both workers queue behind it. The S19-based headroom figure doesn't include this cost. *Fix:* time one `guard()` call. If it takes more than about 1 s, cache the binary digests keyed by (inode, mtime, size), or raise the 1.5× factor.
4. **No failure marker on interrupt (Low).** `except Exception` around `future.result()` misses KeyboardInterrupt/SystemExit, so no `failure_*.json` gets written. The run still fails closed because the journal never records `complete`. *Fix:* catch `BaseException` when writing the marker.
5. **Fine grid barely tested (Low).** The dry adapter only produces integers 0–12, so the 200-key dry replay never tests half-unit wages or wages above 12. The mocked live run uses only the constants 10.5 and 10. *Fix:* add a mocked fixture that varies fine quotes (19.5, 20.0, -0.0, ties) to cover regret and the exact-arithmetic path.
6. **The independent check isn't fully independent (Low).** `expected_prompts` and the grid check are copied verbatim, so an error in either would show up in both and never be caught. *Fix:* describe it as an independent re-check of arithmetic and statistics only, or add a test comparing a fixed prompt string against the DESIGN wording.
7. **Model check proves nothing (Low).** The model/backend comparison always passes because `_codex` returns the model name it was asked for. The design already says the served model is unattested; drop the check from any list of evidence.

## Limitations the design already acknowledges (not bugs)
- **Confounded contrast:** the treatment changes the grid, the equilibrium set, which numbers stand out, and float serialization all at once. The coarse prompt is also not an exact S38 replay.
- **Low wages aren't proof of collusion:** with a hidden horizon, many repeated-game equilibria are possible.
- **Statistics are descriptive only:** n=5 blocks; sign-flip p-values assume exchangeability; DUD means "screen failed", not "no effect".
- **Within-game calls are sequential:** the firms are simultaneous only in what they can see.
- **Unattested by design:** sampling settings, served model, tool non-use and full codex settings are not attested; timestamps come from the local clock; only the admission journal is fsynced.
- **Hard deadline:** no live call can start after 05:00 UTC, and the headroom check must also pass at launch. Check `date -u` first, since today is the deadline day.

## Verdict
I found no bug that invalidates the science. You can launch once item 1 checks out and item 2 is dealt with operationally; items 3–5 are worth a quick fix if there's time. The design's caveats are adequate, provided REPORT presents S41 as an exploratory screen of a confounded manipulation.
