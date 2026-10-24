"""Integrate verified S11 outcome into the concise portfolio report and ledgers."""
from datetime import datetime,timezone
import json
from pathlib import Path


def main():
    r=json.loads(Path('results/s11_delay.json').read_text());assert not r['dry']
    ind=json.loads(Path('logs/s11_independent.json').read_text())
    p=r['metrics']['absolute_change'];q=r['metrics']['quantity'];d=p['paired_difference'];qd=q['paired_difference'];v=r['verdict']
    f=lambda x:f'{x:+.3f}'
    bounds=lambda xs:'['+', '.join(f(x) for x in xs)+']'
    stamp=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    lines=['# Serendipity log — Beyond Words','',f'{stamp} · Iteration 6 · **'+('S11 timing-screen HIT; no collusion claim.' if v=='HIT' else 'No hits promoted.')+'** All pilots exploratory; zero tuning attempts.','',
           '| Pilot | Result (descriptive 95% bootstrap bounds) | Verdict |','|---|---|---|']
    old=Path('REPORT.md').read_text()
    lines += [line for line in old.splitlines() if line.startswith('| S') and not line.startswith('| S11 ')]
    lines += [f'| S11 · D, delayed feedback | 10 no-message calculator games / 5 fresh blocks. Mean consecutive output change r4–12: immediate **{p["immediate"]["mean"]:.3f}**, delayed **{p["delayed"]["mean"]:.3f}**; reduction **{f(d["mean"])} {bounds(d["ci95"])}**. | **{v}** for timing screen |','',
              f'**S11:** immediate−delayed change, paired t95% **{bounds(d["paired_t_ci95"])}**, upper sign-flip **p={d["exact_signflip_p_upper"]:.5f}**. Four of five block differences are positive; the HIT screen is unmet. At n5, HIT means all five strictly positive differences and mean reduction≥1; its bootstrap/sign conditions are not independent checks. Secondary mean quantity delayed−immediate **{f(qd["mean"])} {bounds(qd["ci95"])}**, t95% {bounds(qd["paired_t_ci95"])}. [All outcomes, blocks and figure](results/s11_summary.md).','',
              'The delay withholds all feedback, including own actions/profits; delayed round2 also lacks the calculator. Both arms retain the same payoff rule and never communicate. Slower consecutive changes do not establish convergence, lower long-run variance, learning or reduced collusion. Delayed best response already predicts slower cycles, so that pattern alone is not surprising evidence of a new coordination mechanism. The short primary window is phase-sensitive; S03 is motivation, not pooled data.','',
              '**Earlier caveats:** S01 digits are deterministic functions of exact prices; its linear screen cannot identify coding. S02 n3 is inconclusive and also replayed own sent messages. S04 fails its routable-exposure gate (17.8%<25%, a screening convention, not calibrated power). S03 is phase-sensitive cycling from above-Nash controls. S07 is dominated by one low-output block, and rule wording and channel use remain bundled. S09 removes incoming round6 information as well as older message history; public imprint and future renegotiation remain, with previously observed prefixes. [Earlier detail](REPORT_DETAILS.md) · [S07](results/s07_summary.md) · [S09](results/s09_summary.md).','',
              'Fresh markets have three firms, integer output, P=max(0,30-total output), cost6; symmetric static Nash q6, P12, profit36. S09 has only six new rounds per continuation; source prefix is context. No verified agreement/execution labels; quantity, message influence and profitable coordination are distinct. Tiny samples, exploratory selection, multiple pilots and shared-backend interference limit inference. Model labels are client metadata; sampling/temperature and OS isolation are not independently attested. No sibling headline change.','',
              '[Design S01/S02](DESIGN.md) · [S03](DESIGN_S03.md) · [S04](DESIGN_S04.md) · [S07](DESIGN_S07.md) · [S09](DESIGN_S09.md) · [S11](DESIGN_S11.md) · [Reproduce](README.md).',
              '**Next:** A/B/C/D/E/F/own portfolio coverage complete. Choose a fresh own-axis invariance pilot (queued denomination S06) or a justified independent confirmation; avoid deepening on a secondary result.','',
              '[S11 replay/release verification](logs/s11_release.json) · [Independent checks](logs/s11_independent.json) · [Review dispositions](logs/s11_review_disposition.md).']
    Path('REPORT.md').write_text('\n'.join(lines)+'\n')
    ideas=Path('IDEAS.tsv').read_text().splitlines()
    for i,line in enumerate(ideas):
        fields=line.split('\t')
        if len(fields)>1 and fields[1]=='S11':
            fields[5]='complete';fields[6]=f'10 games/5 blocks; consecutive-change reduction {d["mean"]:+.6f} {d["ci95"]}; upper p={d["exact_signflip_p_upper"]}; {r["cached_responses"]} cached calls; independent240 cells PASS';fields[7]=v
            ideas[i]='\t'.join(fields)
    Path('IDEAS.tsv').write_text('\n'.join(ideas)+'\n')
    now=datetime.now(timezone.utc).isoformat()
    ledger=Path('EXPERIMENTS.tsv')
    if '\tS11-result\t' not in ledger.read_text():
        decision='keep (timing-screen HIT)' if v=='HIT' else 'inconclusive ('+v+')' if v.startswith('ODD') else 'discard (directional DUD)'
        with ledger.open('a') as handle:handle.write(f'{now}\tS11-result\tDelayed feedback reduces consecutive output change\tFrozen lag1 vs lag2 no-message calculator; mandatory cached replay and independent arithmetic\t10 games/5 fresh blocks24110..24114; r4-12 exploratory zero tuning\tChange reduction {d["mean"]:+.6f} {bounds(d["ci95"])} descriptive bootstrap; t{bounds(d["paired_t_ci95"])}; upper p={d["exact_signflip_p_upper"]}; quantity secondary {qd["mean"]:+.6f}\t{decision}\tpending\n')
    h=Path('HITS.md');text=h.read_text().replace('**No promoted hits after iteration 5.**','**'+('S11 promoted for the timing screen only; no collusion claim.' if v=='HIT' else 'No promoted hits after iteration 6.')+'**')
    text=text.replace('Cover remaining D before deepening.','D was subsequently covered by S11.').replace('Cover D before deeper confirmation on fresh seeds.','D was subsequently covered by S11; any confirmation still needs fresh seeds.').replace('D is the sole\nuntouched axis and should be covered before deepening.','S11 subsequently covers the D axis; all portfolio axes are now covered.')
    if '**S11:' not in text:
        text+='\n\n**S11: '+('HIT for the registered consecutive-change timing screen' if v=='HIT' else 'unpromoted '+v+' for the registered timing screen')+' (axis D3).**\n'
        text+=f'Ten fresh no-message calculator games/five blocks. Immediate−delayed consecutive quantity change r4–12 **{f(d["mean"])} {bounds(d["ci95"])}**, paired t{bounds(d["paired_t_ci95"])}, upper p={d["exact_signflip_p_upper"]:.5f}. Secondary delayed−immediate quantity **{f(qd["mean"])} {bounds(qd["ci95"])}**.\n'
        text+='This tests bundled feedback timing/own recall/warmup. Naive delayed best response predicts slower consecutive changes, so that finding alone is not surprising evidence of collusion, learning or stabilization. Both siblings may use it as motivation for action-cycle negative controls; no detector was run and neither sibling headline should change. Confirm on fresh registered seeds with longer phase-balanced windows and explicit period/amplitude diagnostics before mechanism claims. No pooling with S03.\n\n'
        text+='Reproduce: `uv run python scripts/s11_analyze.py`; `uv run python scripts/s11_independent.py`; `uv run python scripts/s11_release.py`; `uv run python scripts/s11_present.py`. [Design](DESIGN_S11.md) · [All outcomes](results/s11_summary.md) · [Figure](figures/s11_delay.png).\n'
    h.write_text(text)

if __name__=='__main__':main()
