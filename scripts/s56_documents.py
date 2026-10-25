"""Post-outcome S56 documentation only; no scientific writes or calls."""
import hashlib
import json
from pathlib import Path

r=json.loads(Path('results/s56_coalitions.json').read_text())
release=json.loads(Path('logs/s56_release.json').read_text())
assert hashlib.sha256(Path('results/s56_coalitions.json').read_bytes()).hexdigest()==release['artifacts']['results/s56_coalitions.json']
assert r['verdict']=='ODD/context-only'
assert all(m['difference'][kind][0]<=0<=m['difference'][kind][1] for m in r['metrics'].values() for kind in ['ci95','t95'])
counts=r['totals'];metrics=r['metrics']
nash={tuple(x) for x in r['census']['nash_profiles']};stable_set={tuple(x) for x in r['census']['pair_singleton_stable_profiles']}
assert stable_set<nash and (6,6,7) in nash and (6,6,7) not in stable_set
interpretation='''# S56 — Interpreting the static benchmark

Post-outcome presentation supplement prompted by final review. No new observed-data
metric,endpoint,subgroup analysis or hypothesis test. All frozen scientific artifacts
remain unchanged;S56 remains ODD/context-only and original S14 remains ODD.

The fixed-pair/singleton stable set is a strict subset of the ordinary three-player
Nash set in this grid. For example,(6,6,7),ordered as pair,pair,outsider,is an
ordinary Nash profile at the cost floor. It fails the pair test:both pair members
can bid7 while the outsider stays7,changing each member's profit from0 to1/3.
Thus a profile can be competitively priced and ordinary Nash while allowing a
strict joint improvement for the fixed pair. Such a counterfactual is not evidence
of observed coordination. The nesting and example are checked against the frozen
full3375-profile census;no observed-game subgroup counts are added.

Conversely,every payment above7 is outside the fixed-partition stable set by
construction. The stability metric supplies information only about the remaining
low-payment rounds;it cannot independently validate high prices as a cartel label.
Observed counts29 versus19 refer to45 rounds per arm and include repeated bid
profiles. The census counts44 distinct Nash and30 distinct fixed-partition stable
profiles across the whole grid,not independent game observations.

Pair-total regret allows sacrificing a member;strict_pair_improvement separately
requires both to gain without transfers. Neither is strong equilibrium,coalition-
proofness,repeated-game stability,agreement,intent or actual policy behavior.

[All eight frozen metrics and48 descriptive intervals](s56_summary.md) ·
[Full scientific artifact](s56_coalitions.json) · [Design](../DESIGN_S56.md).
'''
fmt=lambda a:'['+', '.join(f'{v:+.3f}' for v in a)+']'
stable=metrics['coalition_stable']['difference']
headline=(f"**Latest — S56 (post hoc):** all ten original S14 tender games/five blocks;zero new scientific model calls. Over45 primary rounds per arm (none→private): payments above the maximum static Nash payment **{counts['none']['above_nash']}→{counts['private']['above_nash']}**;fixed-pair/singleton stable rounds **{counts['none']['coalition_stable']}→{counts['private']['coalition_stable']}**;rounds permitting a strict profit increase for BOTH pair members **{counts['none']['strict_pair_improvement']}→{counts['private']['strict_pair_improvement']}**. Stable-fraction contrast **{stable['mean']:+.3f} {fmt(stable['ci95'])}**,paired t95% {fmt(stable['t95'])}. **ODD/context-only;no promotion.**\n"
          "The eight fixed descriptive metrics and all24 bootstrap/t summaries are [reported equally](results/s56_summary.md). Pair-total gains may sacrifice a member;the strict-both-gain diagnostic requires no transfers. Some ordinary Nash profiles also fail this pair-deviation criterion;payments above7 fail it by construction. [Interpretation](results/s56_interpretation.md). These static counterfactuals do not establish agreement or repeated-game stability. All contrast intervals span zero;the original S14 ODD and its original bootstrap remain unchanged.\n")
report=Path('REPORT.md').read_text();before_rows=[x for x in report.splitlines() if x.startswith('|') and not x.startswith('| S56 ·')]
if '<!-- S56 summary start -->' in report:
 start=report.index('<!-- S56 summary start -->');end=report.index('<!-- S56 summary end -->')+len('<!-- S56 summary end -->')
else:
 start=report.index('<!-- S54 summary start -->');end=report.index('<!-- S54 summary end -->')+len('<!-- S54 summary end -->')
report=report[:start]+'<!-- S56 summary start -->\n'+headline+'<!-- S56 summary end -->'+report[end:]
report=report.replace('· Iteration 38 ·','· Iteration 39 ·')
row=(f"| S56 · A1, tender coalition audit | All10 original S14 games/5blocks;no new calls. Counts/45 rounds (none→private): above-Nash **{counts['none']['above_nash']}→{counts['private']['above_nash']}**,fixed-pair stable rounds **{counts['none']['coalition_stable']}→{counts['private']['coalition_stable']}**,strict-both gain available **{counts['none']['strict_pair_improvement']}→{counts['private']['strict_pair_improvement']}**. Stable fraction contrast **{stable['mean']:+.3f} {fmt(stable['ci95'])}**;[all8 metrics](results/s56_summary.md). | **ODD / context-only**, post hoc |")
report='\n'.join(x for x in report.splitlines() if not x.startswith('| S56 ·'))+'\n'
last=next(x for x in report.splitlines() if x.startswith('| S54 ·'));report=report.replace(last,last+'\n'+row)
report=report.replace('**Next:** fresh different-axis A/B pilot;own/S55,S52,S49,S46,S39 remain queued. No sibling headline change.',
 '**Next:** fresh different-axis B/C/F pilot;own/S55,S57,S52,S49,S46,S39 remain queued. No sibling headline change.')
assert before_rows==[x for x in report.splitlines() if x.startswith('|') and not x.startswith('| S56 ·')]
Path('REPORT.md').write_text(report)
Path('results/s56_interpretation.md').write_text(interpretation)
section='''\n\n<!-- S56 context start -->
## S56 — Post-hoc procurement coalition-deviation audit

''' + headline+'''
All original S14 primary rounds4..12 retained:90 profiles,45/arm,five source
blocks24200..24204. Buyer payment and pair-total profit reproduce S14 and supply
no independent evidence. The new full-grid comparison holds outsider bids fixed
for225 pair choices and holds pair bids fixed for15 outsider choices. Coalition
stability here means zero joint pair-total and outsider regrets;it is a competitive
static benchmark,not strong equilibrium,coalition-proofness or repeated-game
stability. This stable set is strictly smaller than the ordinary Nash set;some competitively
priced ordinary Nash profiles permit a joint pair deviation. All above7 payments
fail fixed-partition stability by construction;this metric is not independent
validation of high prices as a cartel label. Observed counts refer to rounds,
including repeated profiles;the census counts distinct profiles.
[Post-review interpretation supplement](results/s56_interpretation.md).
Side payments are absent,and the separate strict-both-profit criterion
requires no transfer. None of these metrics labels agreement,intent or collusion.

[All eight metrics,48 intervals,counts,limits and figure](results/s56_summary.md)
· [All90 records,80game cells,24summaries and3375-profile census](results/s56_coalitions.json)
· [Registered design](DESIGN_S56.md).

The new decomposition is post hoc and uses exhaustive3125 empirical block
resamples;S14 originally used10000 random draws. Its payment contrast therefore
has new descriptive bounds[-5.600,+10.000],whereas the unchanged S14 original
bounds are[-5.600,+9.733]. No pooling,endpoint selection,significance tests,tuning,
HIT screen,held-out validation or independent replication. All eight contrast
bootstrap and t intervals span zero. Provider settings/tool non-use unattested.

Complete original S14 raw/request/cache/source replay and separate original
statistical verifier pass. S56 separately binds360final actions/all376requests,
reconstructs90rounds/80cells/24summaries,and enumerates all3375profiles. The raw
checker does not independently rebuild full request histories or classify rejected
attempts;those eligibility checks use original S14 replay. Forty source/input
files are matched against the pushed registration. Local records are not signed
provider attestations. [Reviews and disposition](logs/s56_review_disposition.md).

A canonical-suite check exposed an older presentation renderer expecting prose
removed from the compact front report. Its presentation-only repair renders the
S25 standalone summary using a temporary anchor and preserves compact REPORT bytes;
S25 scientific sources,results and data are unchanged. Initial failure retained.
<!-- S56 context end -->
'''
details=Path('REPORT_DETAILS.md').read_text()
if '<!-- S56 context start -->' in details:details=details[:details.index('<!-- S56 context start -->')]+section.lstrip()+details[details.index('<!-- S56 context end -->')+len('<!-- S56 context end -->'):].lstrip('\n')
else:details+=section
Path('REPORT_DETAILS.md').write_text(details)
