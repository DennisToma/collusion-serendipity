# S25 adversarial review

**Verdict: no blocking bugs.** I checked the arm contrast, source selection, parser, one-shot guards, provenance and inference. The code largely matches DESIGN_S25.md. There are two small mismatches between the design and the code, and one property of the stopping rule that should be written down before launch. I reviewed the pasted files only, with no edits or model calls.

## Concrete remaining issues (fix before launch)

1. **The data hash check per call is described but not implemented.** The design says "source cases and source data hashes checked each dispatch and completion." `execute()` and the completion step only hash the 10 code files in `SOURCES`. `data/s25_cases.json` and the S19 game/raw files are checked once at start (`cases_obj` comparison) and again in `validate()` through `select_cases()`. The final validation does cover them, so the impact is small. Either add `data/s25_cases.json` and the `source_sha256` files to the per-call hash check, or change the design text.

2. **The stopping rule makes HIT almost unreachable, and the design doesn't say so.** With an inclusive one-sided sign flip over 5 blocks, p ≤ .05 needs **all five block contrasts > 0**. One zero block gives p ≥ 2/32 = .0625. Blocks 24320 and 24321 have only archived rejections at round 3, with no notepad and clear-cut statuses. Both arms will likely approve 0/2 there, so HIT is effectively impossible and the real outcomes are DUD or ODD. Don't change the rule now. Add one sentence saying the screen is unreachable unless every block is positive, so a DUD isn't read as evidence of no effect.

3. **A reverse effect gets labelled DUD.** If reason-first *increases* approvals, the mean is negative, which counts as ≤ .05 and so DUD. In the report, call it "DUD (one-sided; direction X)" and always show the signed mean.

4. **The independent checker doesn't verify the treatment itself.** `s25_independent.py` trusts that `request()` built the prompts correctly; only `validate()` checks them, using the same code. Add an independent check on the raw request text:
   - The action_first prompt should equal `original_prompt + ' Emit the top-level fields in the exact order shown.'` byte for byte. I traced this by hand and it holds: the generated schema reproduces the original separators and author order exactly.
   - The reason_first prompt should differ only by swapping the `reviews` and `reasoning` fields.

   This is cheap and closes the shared-code gap.

## Things to check, not bugs

- **Reproducibility from a clean clone:** `validate()` asserts exact Python, numpy and scipy versions. Confirm the Python version is pinned (e.g. `.python-version`), not just `uv.lock`.
- **Frozen analysis code:** `s25_analyze.py`, `s25_independent.py` and `test_s25.py` are in `SOURCES`, so any fix to them after the run breaks validation for good. Report and figure code must stay outside `SOURCES`.
- **Arm order isn't balanced:** the order of the two arms within each case is random, not counterbalanced. Report how many cases ran action_first first.
- **Cache:** confirm `llm.chat`'s disk cache can't return a hit for these prompts and that a cache hit would be visible in `response`. The added sentence makes collisions with S19 unlikely.
- **Format failures:** one fenced or malformed reply aborts all 20 calls. Check the S19 gpt-6-luna strict-parse failure rate so you know the risk of losing the whole batch.
- **Cosmetic:** notepad prompts end in `"validity. "`, so the added sentence follows a double space. It's identical in both arms; leave it.

## Verified correct

- **Selection:** uses the S21 source keys, negative-type targets, and recorded actions only.
- **Arm difference:** the systems, prefixes and remaining instructions match. In action_first the schema is identical to the original.
- **Parser:** rejects duplicate keys and NaN, and requires the exact fields, the right authors and booleans. Empty notes are enforced when there is no notepad. Field order is kept for the compliance count, and wrong-order replies stay valid.
- **One-shot guards:** the `'x'`-mode receipt, the writer lock, no resuming from `*.jsonl`, raw rows archived before the route and parse checks, `retries=1` with a single call to the transport, a strict-less-than deadline that works with ISO strings, and a barrier between blocks with at most 2 calls at once.
- **Statistics:** they match the independent checker; the full 5^5 bootstrap, t interval and sign-flip computation agree.

## Acknowledged limitations (no action needed)

Cases selected after seeing outcomes, 5 blocks, temperature and token limits not enforced, interference from the shared service, a request for an output order rather than an internal reasoning order, timestamps from the local clock only, and an "abort" that is best effort.
