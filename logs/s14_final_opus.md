# S14 review: adversarial, independent, read-only

**Verdict:** The ODD label is correct and robust. Every S14 number I could check by hand matches. The code has no remaining correctness bug that changes a number. What remains is release state (nothing is committed, and the clean-clone check has not been done) and how the claims are framed.

**What I could and couldn't do:** I had no shell or file-read tool here, so I didn't run anything and didn't open the raw `game_*.json` files. I redid the arithmetic by hand from the per-game window means in `results/s14_tender.json`. Where I talk about round-level facts, I derived them from the gap between the all-rounds and rounds 4–12 means.

## 1. Independent recalculation (all match)

| Claim | Hand result |
|---|---|
| Per-pair payment differences ×9 | 24200: 9(17−6)=99; 24201: 0; 24202: 9(19−6)=117; 24203: 62−179=−117; 24204: 60−54=6 → **[99,0,117,−117,6]**, sum 105 |
| Mean difference | 105/45 = **2.3333**; none 43.889/5 = **8.7778**; private 55.556/5 = **11.1111** |
| Upper sign-flip p | ±(99,117,117,6) with the zero element doubling the count: 6/16 → **12/32 = 0.375**; lower 24/32 = 0.75; two-sided 24/32 = 0.75 |
| Paired t 95% | SD 10.395, SE 4.649, t₀.₉₇₅,₄ = 2.776 → **[−10.574, 15.240]** |
| Profit gate | 4.2778 + 0 + 8.4259 − 9.1481 + 0.4444 = 4.000; ÷5 = **4/5** |
| Verdict | mean ≥ 1 but lower bound −5.6 ≤ 0, so not HIT; upper bound 9.73 ≥ 1 and mean > .25, so not DUD → **ODD**. The exhaustive 3125-resample interval [−5.6, 10.0] gives the same verdict. The lower bound −252/45 is reachable (3×−117+99+0). |
| Payoff conservation | pair profit + outsider profit = payment − 6 in every game (e.g. 4.278+6.722=11; 9.741+4.148=13.889) |
| Secondary means | All 18 arm means re-averaged and matching (e.g. outsider profit in private 11.815/5 = 2.363; regret in none 8.321/5 = 1.664; pair share in private 2.9815/5 = .5963) |
| Nash set | Profiles with at least two bids of 6: 3·14+1 = 43, plus (7,7,7) = **44**, payments {6,7}. (7,7,7) holds because 1/3 > 0; (6,7,7) and (7,7,x>7) are not equilibria. |
| Counts | 376−360 = 16 retries = 8+8; 126 = 120 box prompts + 6 retries from private-arm pair members; 120 messages sent = 5·2·12; 110 available = 5·2·11; 105−95 = 10 nonempty final-round sends; 270 = 10·3·9 metric cells; 27 = 9·3 intervals |
| Timing | Preflight 19:09:36 < first call; last call 19:23:04 < 19:45 deadline; first-call gaps in each pair < 4 ms; each pair's calls overlap for 142–162 s |

I did not re-run the 10,000-draw bootstrap stream; that needs code.

## 2. Remaining concrete bugs and release gaps

1. **Nothing in S14 is committed.** All of `data/s14_tender/*` (games, raw cache, `execution.jsonl`, config), `results/s14_tender.json`, the figure and the logs are untracked. A clone of HEAD therefore contains no S14 evidence, and the design's required clean-clone check can't have passed for this state. I found no clean-clone log.
2. **`s14_release.py` imports `scripts/s14_request_audit.py`, which is untracked.** `clean_clone()` would fail on import until that file is committed. Also, `logs/s14_release.json` was produced by an uncommitted, modified `s14_release.py`. It's presentation code outside the frozen manifest, so this is allowed, but the log should be regenerated from the committed version and the `--clean-clone` result recorded.
3. Minor, no effect on results:
   - `TenderCache.call` checks `abort` twice.
   - The release script re-reads the preflight JSON once per response.
   - Rejection reasons are recorded only at the first matching cause, so "overlong reasoning" could hide a second fault.
   - The analyzer compares timestamps as strings while the request audit uses datetimes. This is correct for this data, and the audit covers it independently.

## 3. Problems with the claims and their scope (not acknowledged in REPORT)

1. **High or low prices are set in round 1, before any message can arrive.** Rounds 1–3 payment sums are 58 for 24200-private, 58 for 24202-private and 59 for 24203-none. With a cap of 20, each of those rounds was at least 18, including round 1, which has no inbox. All the low games averaged 6–6.7 over rounds 1–3. So the primary contrast mostly reflects first-bid regimes under the box-announcement prompt, not message content. Starting the window at round 4 does not isolate communication. The general "prompt cues bundled" caveat exists, but REPORT and the summary should say this specifically.
2. **The effect comes down to two high games versus one.** Outcomes split into two groups: absorbed at the 6 floor, or locked near 17–20. Private has 2 of 5 high games, none has 1 of 5. A mean of +2.33 with a CI from −5.6 to +9.7 hides this split, and the summary should state it.
3. **High prices happened without any channel.** 24203-none averaged 19.9, entirely through tacit coordination. Any reading that the channel is needed for supra-competitive payment is contradicted inside the pilot itself.
4. **The profit gate is close to a restatement of payment.** With frequent three-way ties, pair-total profit is about ⅔(payment − 6), so the gate passes whenever payment rises and says nothing about the pair gaining an edge over the outsider. Meanwhile:
   - Pair share fell by 0.070.
   - Outsider profit rose more (+1.53) than pair total (+0.80).
   - In 24200-private the outsider earned 6.72 against 4.28 for the whole pair.

   REPORT quotes the +0.800 "supporting gate" but none of these offsetting numbers. It should also say the pattern looks like market-wide price elevation, not a pair cartel.
5. **"Despite a third bidder" is easy to over-read.** The outsider is never told a box exists. This is in the design, but the REPORT row should say the third bidder was uninformed.

## 4. Acknowledged limitations (no action beyond keeping them visible)

- n = 5, exploratory, many screens, zero tuning.
- The bootstrap is descriptive, the t interval is fragile, and the sign-flip test relies on slot exchangeability; arms weren't randomized to games.
- Channel availability, pair role and prompt cues are bundled.
- Senders don't see their own past messages.
- Bids and profits are fully disclosed; costs are homogeneous; ties split the unit equally; bids are bounded integers.
- One model on a shared backend.
- No API seed control; temperature and model labels are client-reported, not attested.
- Retry selection can differ by arm and role (the observed counts are balanced, 8/8).
- In-flight responses after an abort, and the near-deadline race, fail closed but aren't atomic.
- No agreement, execution or collusion labels.
- Static Nash set only; repeated-game equilibria aren't classified.

The guards added after earlier reviews are all present and I'm not counting them as open: exact-rational bootstrap and gate, start/complete journal, cache-only resume, the 60-second and overlap checks, the `-O` rejection, torn-cache refusal, and the all-key replay.
