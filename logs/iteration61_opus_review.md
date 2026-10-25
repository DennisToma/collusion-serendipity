# Adversarial review: iteration-61 documentation compression

**What I reviewed:** only the text you supplied: `README.md`, `REPORT.md`, `scripts/export_report.py`, `logs/iteration61_exports.json` and `results/iteration58_reproduction.md`. I read nothing on disk and ran nothing. I did not see `scripts/iteration55_claims.py`, `scripts/portfolio_replay.py`, `requirements-export.lock`, `pyproject.toml`, `REPORT_DETAILS.md`, `HITS.md`, the other `results/*.md` files or the iteration-61 logs. Wherever a finding depends on those files, it says so.

**Verdict:** No high-severity documentation issues are visible in the supplied text. Six are medium; the most important is the first, the unevidenced full-replay command.

## Medium

**M1. The full-replay command has no visible test on the current checkout.** The README presents `portfolio_replay.py run/check` as working from the current checkout. But `iteration58_reproduction.md` says the verifier deliberately fails when protected evidence, ledgers or coordination files change. Iteration 61 rewrites `README.md`, `REPORT.md`, `STATUS.md`, the exports and `export_report.py`. None of the listed `logs/iteration61_*` files is a portfolio run. `--check` only re-checks the saved iteration-58 receipt, which doesn't show that a fresh `run` passes at the current HEAD.
- **Fix:** run it once on the committed iteration-61 tree, or say "last executed at `cd3505c`; run from that revision if the current tree fails preservation."

**M2. The README understates what varies across hosts after a rebuild.** It warns only that "other hosts may render different PDF bytes." But `git diff --exit-code` also covers three other things that can change:
- `figures/explorer_handoff.png`, whose matplotlib output depends on fonts.
- `BRIEF.html`, which embeds that PNG as base64.
- `logs/iteration61_exports.json`, which records the file hashes and `chromium_version`.

A clean rebuild on another host will probably fail on the PNG, `BRIEF.html` and the receipt, not just the PDFs.
- **Fix:** list all four, and name the content checks (`--check-pdf`, link targets, row order) as the portable criterion.

**M3. The rebuild overwrites tracked files and the README doesn't warn about it.** `--build` rewrites `README.md`, `REPORT.md`, the exports, the PNG and the receipt in the working tree. A reader who hits a diff is left with a dirty checkout.
- **Fix:** add "run in a clean clone; restore with `git checkout -- .`", or point the build at a scratch copy.

**M4. The call guard's coverage is claimed more broadly than the supplied code shows.** The README says "the check itself uses saved evidence and a scientific call guard," which implies the whole check is guarded. In `export_report.py`, the `--check` path calls `audit.run()`, `iteration54_handoff.products()`, `iteration57_fresh_install.check()` and `portfolio_replay.check()`, and none of them installs a guard in the supplied code. The guard may live in `audit.selected_replay()`, which I didn't see.
- **Fix:** confirm that the guard wraps everything `--check` imports, or narrow the claim to "the selected replays run under an `llm.chat` guard."

**M5. Links in frozen files may now point at a compressed README.** `preservation()` freezes every non-mutable file, including `REPORT_DETAILS.md`, `HITS.md`, `results/*.md` and `data/SPLITS.md`. Any of those that link to `README.md` or its anchors for per-pilot commands now land on a README without that runbook. Those files can't be edited.
- **Mitigation already present:** the README points to the archive.
- **Still needed:** grep the frozen files for `README.md` links and anchors. If any exist, add one sentence: "Links from archived files to README sections refer to the iteration-60 runbook."

**M6. The archive is only reachable through GitHub.** The pinned link needs network access and repository permission. An offline reader with a full clone has no stated route.
- **Fix:** add `git show 73492a929c2245a033f1b1598a03703c3f6f6ee6:README.md`. The README already requires full history, so this costs nothing. The link also assumes `73492a9` is pushed; the recent-commit log suggests it is.

## Low / optional nits

1. The README hard-codes "29 DUD, 23 ODD/context-only and two failed." The REPORT computes those counts from `iteration54_portfolio.json`, but the README sentence isn't produced or checked that way. `verify_sources` binds only 54/307/144. Generating it from the same `values` would close the gap.
2. The `export_report.py` docstring gives `--check` without `--replay-selected`, which differs from `COMMAND`.
3. "S72 uses its **genuine** historical revision": "genuine" invites questions. Use "its pinned result revision `793a641`."
4. The README never names the commit or tag the receipts belong to, and the tree is currently uncommitted. Say "release = commit X" after committing.
5. There is no runtime or disk estimate for `--replay-selected` or for the full replay, which uses disposable pinned checkouts.
6. The export lock must be enough to import `scripts.iteration55_claims`, `iteration54_handoff` and `portfolio_replay` under the export interpreter. The existing `iteration61_final_build.txt` suggests it is, but I couldn't check it.
7. The PDFs' relative links (`BRIEF.pdf` and similar) only resolve when the PDF sits next to the other exports. That's worth half a sentence.
8. After `--build`, the `--check-pdf` comparison is against a receipt written moments earlier, so it adds little. The `git diff` is the real check, which is another reason M2 matters.
9. `playwright install chromium` on Linux may need `--with-deps` (sudo). You already mention the system libraries; naming the flag helps.

## Checks that passed (against the supplied text)

- **Commands:** the README commands match `COMMAND`, the `main()` flag logic and `iteration58_reproduction.md` (including `check --out`). The `uv` flags (`--frozen`, `--python`, `--require-hashes`) are valid.
- **Selected vs. full replay:** the scope is stated consistently in the README, the REPORT and the export code: five selected analyses vs. 52 analyses + 2 failure audits + 50 checkers. The REPORT says plainly that the 54-entry replay is archived and that `--check` doesn't rerun it.
- **Scientific claims:** the README and REPORT don't overstate them. Both pilots stay ODD and no hit is promoted. The S29 numbers (p=0.0625 misses the screen, the tied block, the paired-t interval crosses 0) match the chart values in the receipt. The selection is described as post hoc, the reused data and lack of multiplicity correction are disclosed, and the future work is labelled unregistered.
- **Archive access:** the pinned archive revision equals `PRESERVATION_BASELINE`, which is the preserved pre-iteration-61 tree, so the archived README is the iteration-60 runbook as claimed.
