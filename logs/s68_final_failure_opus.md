# S68 failure review (supplied text only)

**Scope.** I read only DESIGN_S68.md, results/s68_summary.md and results/s68_failure.json as you pasted them. I made no edits and no model calls, and read no files or other critics. So I have not independently checked the raw journals, hashes, bindings, test runs or the "no calls" guarantee. Every "consistent" below means the three texts agree with each other, not that I verified the data. I also did not see HITS.md, EXPERIMENTS.tsv or REPORT.md, so I can't confirm "no HIT claimed" or "older rows retained" for those files.

## Internal consistency checks (pass)
- **Counts:** 30 planned, 30 admitted, 29 returned, 29 accepted, 9 of 10 cases complete, 0 retries. The summary and JSON match exactly, and one missing reply in one case gives exactly 9 complete cases.
- **Schedule:** The design says each case runs its views one after another and repeat is never the middle view. Thirty admissions is only possible if the missing repeat for `s29_24484_shared_B` was that case's last view. That fits the rules, but whoever has the repository should confirm it against `schedule.json`.
- **Timing:** The missing repeat was admitted at 11:31:11.002. The last archived return was at 11:31:12.213, about a second later, and fits the other worker finishing its final call. Nothing was admitted after that, which fits 30/30. All of this is before the 13:30 admission cutoff.
- **No estimate claimed:** The JSON has `scientific_verdict: null` and `behavioral_estimates_computed: false`. The summary reports no approval rates, disagreements, intervals, p-values, subgroups or completed-case figures. The S68 texts make no HIT or promotion claim.
- **No resume or relaunch:** Both texts say analysis and resume rejected the incomplete archive with calls forbidden and bytes preserved. They also say there was no restart, redraw or substitution, and that raw journals were not repaired. Each file's hash is listed, so the formatted failure record can be checked against them.

## Medium issues
1. **Admissions vs. prefix bindings (29 vs. 30).** The summary says the audit binds "all 30 admissions", but the table and JSON report only 29 verified prefix bindings. The unanswered request should still have a recorded request row whose prefix can be checked against the schedule and source with no response needed. Either verify it and report 30, or say plainly that the 30th admitted request's prefix is not bound and why. As written, the two claims look contradictory.
2. **An obvious local cause hasn't been ruled out.** Exit 143 (SIGTERM) came about 1.4 minutes after the last archived activity and about 3.3 minutes after the first admission. A local cause, such as a wrapper or tool-call timeout or the iteration runner killing a foreground process, is plausible. It can be checked from local logs (`s68_launch.json`, `s68_live_run.log`, runner logs) with no model calls. "Cause unknown" is honest. But the record should say whether this check was done and what it found, without promoting a guess to a finding. If the harness was launched in a way that could time out, that's a launch-procedure lesson to record for any future registered pilot. It does not justify resuming S68.

## Low issues and acknowledged limits
- **"Retries 1" vs. "logical retries 0".** The design sets llm.chat to retry once, while the results report 0 logical retries. The text doesn't say whether a transport-level retry could have been in progress inside the missing call. Add one line distinguishing the two.
- **Exit time.** `local_exit_observation_utc` is when the exit was noticed, not when it happened. This is correctly labeled, and the actual kill time can't be known from what's recorded.
- **Acknowledged limits, correctly stated:** whether the provider served or billed the missing call, provider identity, settings and caching, and power-loss persistence. No completion or harness-failure event is expected after SIGTERM if no signal handler was installed. These are honest disclosures, not defects.
- **Readability.** DESIGN_S68.md has many dropped spaces ("anchor,repeat,inverted", "author6,reviewerX+1/Y-2"). This is cosmetic and makes it harder for judges to read; if the file must stay byte-identical, fix the wording in the presentation copy instead.
- **"Prior scientific paths unchanged 1450" and "18 registered sources."** Both are stated but not checkable within this review's scope.

## Verdict
There are no high-severity issues within the supplied text. The failure record handles the interruption soundly: no estimate is made from partial data, no HIT is claimed, and resume and relaunch are forbidden. Before release, fix the 29/30 binding wording and add the non-call check for a local SIGTERM source.
