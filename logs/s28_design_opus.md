# S28 adversarial review (static review only)

I had no shell or file tools in this session, so I reviewed only the source you pasted. I ran no tests, made no edits and made no model calls. Every finding below comes from reading the code.

## Checks that passed
- **Economics:** `outcome` gives +6 to the author and +1 to the reviewer for an approval, with an extra −3 for approving a Y. Pair bonus is 7 for an X approval and 4 for a Y approval, and organization loss is 10 × adverse approvals. The table's six rows match the per-review payoffs, and so do the "mutual Y = 4 each" and "rejecting saves 2" claims.
- **Truth/simultaneity:** each agent gets 1 X and 1 Y in rounds 1–2, then 4 X and 4 Y in rounds 3–10. `rows` and `chat` only change after both agents act, current-round notes are held separately until then, and private reasoning never reaches a prompt.
- **Statistics:** the exact bootstrap quantile at position p·3124 matches NumPy's default linear quantile. The 32-flip sign test gives p = 1/32 only when all five differences are strictly positive. A zero difference raises p to at least 2/32, so it blocks a HIT, as the design says. `classify` and the independent recomputation follow the frozen rule, and the `/8` denominators give exact counts.
- **Abort serialization:** `AdmissionAbort.set` is never called while the admission lock is held, so it cannot deadlock. Any failure (bad parse, wrong route, transport) leads to a failure marker, and the analysis then refuses to publish.

## Remaining bugs
1. **Medium: an output parser can wrongly invalidate a good run that can't be repeated.** `s28_independent.verify` reads the notes with `user.split('Notes file snapshot: ')[1]`. If any model note contains that literal phrase, the split cuts the JSON short and `json.loads` raises. That is an uncaught failure, so a valid live run fails publication with no rerun allowed. The dry adapter and the tests use the same pattern.
   *Fix:* split on the first occurrence only (`split(marker, 1)` or `partition`) and add a canary note containing the marker text.
2. **Medium: presentation-only scripts are frozen as scientific sources.** `SOURCES` includes `s28_present.py`, `s28_release.py`, `s28_reviews.py` and `s16_reviews.py`. Any later fix to a figure or to the report renderer then fails `analyze`'s source-drift check, and the archive becomes INVALID.
   *Fix:* before registration, drop these from `SOURCES`, or record in `STATUS.md` that they are frozen until S28 is published.
3. **Medium (operational): the run can be killed mid-way.** The dispatch guard rehashes `SOURCES` before every new request. If the run outlasts a manager iteration, the next iteration editing `DESIGN_S28.md` or any listed script aborts the whole pilot. Separately, the wrapper's `git add -A` will commit partial raw data.
   *Fix:* put an explicit "S28 in flight, don't edit these files" lock in `STATUS.md` or `DIRECTION.md`, and run S28 detached under `nohup`.
4. **Low: timestamps are compared as strings.** Checks like `previous_completed <= call_started_utc` compare ISO strings. `isoformat()` leaves out microseconds when they are zero, and within the same second that reverses the order. The chance is about 1e-6 per comparison, but a false failure here would be permanent.
   *Fix:* parse with `datetime.fromisoformat` everywhere.
5. **Low: a gap between the two locks.** `launch()` releases `.writer.lock` before `main()` takes it again, so another process could slip in. The receipt file is opened with `open('x')`, which mostly covers this.
6. **Low: publication depends on files outside the frozen set.** `analyze` recomputes the runtime gate from the `data/s19_labels` hashes. Any later change to that data retroactively invalidates S28.
7. **Cosmetic:**
   - The submission-order shuffle (RNG 2840) does nothing when there are two workers and two games per block; it only changes export order.
   - The independent verifier's branch for an agent outside the pair is dead code.
   - A `RecursionError` from deeply nested JSON escapes the parser and aborts the run instead of using up a retry. That still fails closed.

## Limitations you have already acknowledged (not bugs)
- The treatment bundles several changes: detail, repetition, format, role salience and length.
- The prose prompt already states "−2", so the baseline may have almost no adverse approvals and the screen may tell you nothing.
- With n = 5, the bootstrap intervals are anti-conservative.
- A large negative effect is classed as DUD and not promoted.
- There is no profit gate.
- The model and route labels are self-reported by the client, and provider draws are uncontrolled.
- Tool use is restricted only by instructions, and nothing confirms the tools went unused.
- There is one model and many uncorrected pilots.
- Two-person bonuses and organization loss follow mechanically from approval counts.

## Verdict
The design and the analysis code are sound. Fix #1 before launch; it's a one-line change that protects a run you can't repeat. Settle #2 and #3 before registration, because changing them afterwards would invalidate the archive. Nothing else blocks launch.
