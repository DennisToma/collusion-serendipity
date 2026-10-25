# Opus review of S67 (read-only, from the supplied text)

**Scope:** I only read the text and code you supplied. I ran nothing, didn't enumerate the 3125 bootstrap draws, and didn't open the raw S65 archive. I did redo the arithmetic below by hand.

**Arithmetic I checked by hand, all consistent:**
- **Settlement:** one approval moves +1/−2 individual and +3.5/+2 pooled. The stage Nash is unique in each arm, and full approval maximises the pair's bonus in both.
- **Regret and shortfall identities:** consistent. Strict Pareto in individual settlement holds only when both approve in a round where both works are Y. In pooled settlement it is impossible.
- **Block totals:** Y approvals 9 vs 20. Regret 18 = 2×9 and 40 = 2×20. Shortfall 124 = 4×31 and 80 = 4×20. Organisation loss 90 and 200.
- **Means and t intervals:** the mean differences +0.275, −0.225, +0.5, +0.55 and −1.1 match. So do the t intervals [−0.111, 0.661], [−0.455, 0.005] and [0.061, 0.939].

**Correctness issues:**

*Medium*
1. **REPORT snapshot isn't checked.** `older_report_rows` is saved in the manifest, but `checked_manifest` never compares it to anything. Meanwhile the working tree shows REPORT.md, HITS.md, README.md and REPORT_DETAILS.md as modified. Someone should confirm by diff that HITS.md doesn't add S67 and that older S-rows are byte-identical. As written, the claim to "snapshot older science artifacts" only holds for the hashed files.
2. **The mutation check is overstated.** `test_independent_exact_fraction_boundaries` only shows that x + 10⁻¹³ ≠ x, which is always true. No test mutates a real round, game total or interval and confirms `verify()` rejects it. Either add those tests or drop "mutation checks" from the claims.

*Low*
3. **The individual-arm Pareto zero may be built in.** Strict Pareto needs a round where both works are Y, but the summary never reports that count (`both_y`). If it is 0, the individual Pareto zero can't happen by construction, the same as pooled. Report the count next to the table.
4. **The no-call guard can be bypassed.** If `scripts.s65_analyze` is already imported and uses `from llm import chat`, patching `llm.chat` misses it. The guard's stated scope covers this in spirit, but name the case.
5. **The second interval check isn't independent.** The "separate" exact-bound checker uses the same rank convention as the main code and NumPy's linear quantile. It checks the arithmetic, not the choice of convention.
6. **Raw request fields are read by position.** The checker unpacks fields 5–8 of the request payload by position (`payload[5:9]`), which is fragile. The 200-unique-key assertion limits the risk.

**Limits you already acknowledge (not defects):**
- The audit is post-hoc and has only 5 blocks.
- The bootstrap and t intervals disagree (Y approvals, costly Y, organisation loss, shortfall).
- With missed X = 0 everywhere, every metric except Pareto is a linear function of the two Y-approval counts.
- Settlement and prompt wording change together, and histories diverge on their own.
- Providers are unattested, and the remote receipt isn't a server timestamp.
- The checker was written by the same manager.

**Verdict:** I found no errors in the economics, identities, units or the hand-checked numbers. The claim limits are appropriate, and S65 correctly stays UNRESOLVED/ODD. Fix items 1–2 before calling the release integrity-complete.
