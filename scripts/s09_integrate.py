"""Update the one-page log and ledgers only after S09 verified release artifacts exist."""
import json
from pathlib import Path
from datetime import datetime,timezone
r=json.loads(Path('results/s09_replay.json').read_text())
audit=json.loads(Path('logs/s09_release.json').read_text())
assert audit['canonical_result_identical'] and audit['independent']['verdict']==r['verdict']
assert r['dry'] is False
stamp=datetime.now(timezone.utc).isoformat();display=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
q=r['metrics']['quantity'];z=q['paired_difference'];v=r['verdict'];lo,hi=z['ci95'];tlo,thi=z['paired_t_ci95']
row=(f"| S09 · E, transcript-removal replay | 10 six-round continuations / 5 observed prefixes. Pair output r7–12: retain **{q['retain']['mean']:.3f}**, erase **{q['erase']['mean']:.3f}**; difference **{z['mean']:+.3f} [{lo:+.3f}, {hi:+.3f}]**. | **{v}** for directional screen; near-Nash baseline |")
old=Path('REPORT.md').read_text();prior=[line for line in old.splitlines() if line.startswith('| S0') and not line.startswith('| S09')]
intro=('**No hits promoted.**' if v!='HIT' else '**S09 quantity-memory HIT; see HITS.md for narrow handoff.**')
screen=('The directional screen failed; this does not establish equivalence or no message effect.' if v=='DUD' else
        'The prospective quantity screen passed for these prefixes; no profitable-collusion inference.' if v=='HIT' else
        'The prospective screen is inconclusive; no collusion inference.')
fork=r['fork_quantity_difference'];profit=r['metrics']['pair_profit']['paired_difference']
text=f'''# Serendipity log — Beyond Words

{display} · Iteration 5 · {intro} All pilots exploratory; zero tuning attempts.

| Pilot | Result (descriptive 95% bootstrap bounds) | Verdict |
|---|---|---|
'''+ '\n'.join(prior+[row])+f'''

**S09:** erase–retain paired t95% **[{tlo:+.3f}, {thi:+.3f}]**, upper sign-flip **p={z['exact_signflip_p_upper']:.5f}**. {screen} At n5, HIT requires all five positive differences and a mean increase ≥1. Round7-only difference **{fork['mean']:+.3f} [{fork['ci95'][0]:+.3f}, {fork['ci95'][1]:+.3f}]**. Retain output is near symmetric Nash6; the +1 screen would require erase mean {q['retain']['mean']+1:.3f}. Pair-profit difference **{profit['mean']:+.3f}**, t95% [{profit['paired_t_ci95'][0]:+.3f}, {profit['paired_t_ci95'][1]:+.3f}]. [All outcomes and figure](results/s09_summary.md).

Both firms jointly lose messages sent in rounds1–6; round6 messages would first appear in round7, so the intervention blocks incoming information as well as previously seen history. Public history is initially identical and future boxes stay open. All five source prefixes were previously observed, including their original suffixes, and none was selected out. Public actions retain earlier message imprint; new messages may rebuild coordination from public history. Empty-inbox cues and message semantics remain bundled. The original suffix is not a control, and this is not pure forgetting, independent-seed replication or the original channel's causal effect.

**Earlier caveats:** S01 digits are deterministic functions of exact prices; its linear prediction screen cannot identify coding. S02 n3 is inconclusive (exact lower p=.25; paired t [-2.099,+1.136]) and also replayed own sent messages. S04 fails its prespecified routable-exposure screen (17.8%<25%, a screening convention, not calibrated power). S03's output reduction is phase-sensitive cycling from above-Nash controls. S07's mean is dominated by one market-wide low-output block; its rule cue and realized channel use are unseparated. [Full earlier results](REPORT_DETAILS.md).

All fresh markets have three firms, integer output, P=max(0,30-total output), cost6; static Nash q6, P12, profit36. S09 adds only rounds7–12 of each continuation: source rounds1–6 are duplicated context, not new observations. No verified agreement/execution labels; quantity, message influence and profitable coordination are distinct. Tiny samples, exploratory selection and multiple pilots limit claims. Backend/model labels are client metadata; sampling seeds/temperature and OS isolation are not attested. Fresh directories/read-only requests do not prove erased files were inaccessible. No sibling headline change.

[Design S01/S02](DESIGN.md) · [S03](DESIGN_S03.md) · [S04](DESIGN_S04.md) · [S07](DESIGN_S07.md) · [S09](DESIGN_S09.md) · [Reproduce](README.md).
**Next:** cover D, the sole untouched axis, before deepening; own S05/S06/S08/S10 ideas queued.
'''
Path('REPORT.md').write_text(text)
p=Path('REPORT_DETAILS.md');s=p.read_text();heading='## S09 — private-transcript counterfactual replay'
if heading not in s:s+='\n'+heading+'\n\nSee [full S09 results, diagnostics, figure and limitations](results/s09_summary.md).\n'
p.write_text(s)
p=Path('IDEAS.tsv');lines=p.read_text().splitlines()
for i,line in enumerate(lines):
    fields=line.split('\t')
    if len(fields)>1 and fields[1]=='S09':
        fields[5]='complete';fields[6]=(f"10 six-round continuations/5 observed prefixes; pair erase-retain {z['mean']:+.6f} [{lo:+.6f},{hi:+.6f}]; upper p={z['exact_signflip_p_upper']}; {r['cached_responses']} calls; zero tuning")
        fields[7]=v;lines[i]='\t'.join(fields)
p.write_text('\n'.join(lines)+'\n')
p=Path('EXPERIMENTS.tsv');s=p.read_text()
if '\tS09-result\t' not in s:
    decision='keep (HIT: quantity-memory only)' if v=='HIT' else 'discard (DUD for predicted increase)' if v=='DUD' else f'inconclusive ({v})'
    s+=f"{stamp}\tS09-result\tPrior message transcripts restrain continuation output\tFrozen matched transcript-removal replay; mandatory cache-only and independent full-stat checks\tTen r7-12 continuations/5 observed neutral S07 prefixes24080..24084; exploratory\t{z['mean']:+.6f} [{lo:+.6f},{hi:+.6f}] descriptive bootstrap; t[{tlo:+.6f},{thi:+.6f}]; upper p={z['exact_signflip_p_upper']}; fork{fork['mean']:+.3f}\t{decision}\tpending\n"
p.write_text(s)
p=Path('STATUS.md');s=p.read_text();a=s.index('## Current state');b=s.index('\n## Log',a)
current=f'''## Current state ({display}; Phase2, iteration5 results)
- Prior pilots S01/S03/S07 DUD; S02 ODD; S04 ODD/UNINFORMATIVE. S09 {v}.
- S09:10 six-round continuations of all5 observed neutral S07 prefixes; {r['cached_responses']} cached calls, retries{r['retries_by_arm']}; no failures.
- Pair output erase-retain {z['mean']:+.3f}[{lo:+.3f},{hi:+.3f}], t[{tlo:+.3f},{thi:+.3f}], upper p={z['exact_signflip_p_upper']:.5f}.
- Fork round7 output difference {fork['mean']:+.3f}; full outcomes/figure in results/s09_summary.md.
- Public prefix identical; both transcripts jointly removed, including unread r6 messages; later renegotiation remains possible.
- Full cache-only replay, source/registration/prefix/export/payoff checks PASS; cached resume byte-identical.
- Independent210 cells,22 bootstrap and7 t intervals, exact primary/p/verdict PASS;19 new/52 discovered tests PASS.
- Registration4474418 pushed before all calls; every response completed before17:48 cutoff.
- Opus design complete; Codex first transport-timeout/partial audit retained; retry/final status below.
- Next: complete independent final reviews and push; then D is sole uncovered portfolio axis.
- Risks: n5 observed prefixes, empty-inbox cues, public imprint/new-message repair, no OS isolation/truth labels.
'''
s=s[:a]+current+s[b:]
s+=f"\n- {stamp}: S09 complete and verified: all10 continuations, {r['cached_responses']} cached calls/retries{r['retries_by_arm']}, no failed game. Frozen screen {v}; pair output erase-retain{z['mean']:+.6f}[{lo:+.6f},{hi:+.6f}], t[{tlo:+.6f},{thi:+.6f}], upper p={z['exact_signflip_p_upper']}. Full mandatory cache-only replay and prefix/registration/export/payoff checks PASS, independently210 metric/window cells/22 bootstrap/7 t intervals/exact verdict reproduced; release cached resume leaves every byte unchanged. No source edits, tuning, excluded prefixes, extra pilot or original-suffix pooling. Final independent reviews to follow. No direction deviation.\n"
p.write_text(s)
print('Updated REPORT, STATUS, DETAILS and both ledgers from verified S09 output:',v)
