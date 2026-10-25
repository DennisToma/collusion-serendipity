"""Render saved S43 data; no model calls or changes to earlier reports."""
import argparse
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def report_row(r):
    s=r['contrast']
    return (f"| S43 · D, own-payoff table | Ten S42 histories /5 blocks;20 fresh decisions. Focal offer control **{r['metrics']['control']['mean']:.3f}**, table **{r['metrics']['table']['mean']:.3f}**; table−control **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]**. | **{r['verdict']}** for one-unit offer screen |")


def render(result='results/s43_payoff.json',out='results/s43_summary.md',figure='figures/s43_payoff.png'):
    r=json.loads(Path(result).read_text());s=r['contrast']
    if r['dry'] and (Path(out).resolve()==(ROOT/'results/s43_summary.md').resolve() or Path(figure).resolve()==(ROOT/'figures/s43_payoff.png').resolve()):raise ValueError('No dry publication')
    label='SYNTHETIC PREVIEW — ' if r['dry'] else ''
    lines=['# '+label+'S43 — Counterfactual payoff tables at fixed labor histories','',
           f"**{r['verdict']}** for the registered one-unit increase screen; ten selected cases/five source blocks; twenty fresh decisions, zero new games and zero tuning.",'',
           f"Focal wage offer: control **{r['metrics']['control']['mean']:.3f}**, table **{r['metrics']['table']['mean']:.3f}**; table−control **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]** descriptive bootstrap95%.",
           f"Paired t95% [{s['t95'][0]:+.3f}, {s['t95'][1]:+.3f}]; inclusive upper sign-flip p={s['upper_signflip_p']:.5f}.",
           '', '| Source block | Control mean offer | Table mean offer | Table−control |','|---|---:|---:|---:|']
    for i,seed in enumerate(range(24920,24925)):
        lines.append(f"| {seed} | {r['metrics']['control']['block_values'][i]:.3f} | {r['metrics']['table']['block_values'][i]:.3f} | {s['block_values'][i]:+.3f} |")
    lines+=['','| Case / selected firm | Archived quote | Fresh control quote | Fresh table quote |','|---|---:|---:|---:|']
    for c in r['cases']:lines.append(f"| {c['case_id']} | {c['archived_quote']} | {c['quotes']['control']} | {c['quotes']['table']} |")
    lines+=['',f"Minimum quote0 counts /10: control {r['floor_counts']['control']}, table {r['floor_counts']['table']}. Exact archived-quote matches /10: control {r['archived_match_counts']['control']}, table {r['archived_match_counts']['table']}.",'',
            'Allowed focal wages are0–20. Outcomes are focal offers, not realized worker wages; rivals are not replayed. Five source blocks, each averaging its two source-arm cases, are the resampling unit. All3125 empirical bootstrap draws and32 inclusive upper sign flips are enumerated.',
            'Both fresh arms keep the source system, public history and private notes; treatment inserts all21 hypothetical own-payoff rows with rivals fixed at their last public offers. No current archived response is supplied. The control prompt exactly matches the source prompt.',
            '', f"Source CLI version {r['source_cli_version']}; replay CLI version {r['replay_cli_version']}; known source/replay fingerprint equal: {r['source_fingerprint_matches']}. This is local metadata, not served-model identity.", '', 'The challenge was selected after reading S42 low-wage explanations. A table bundles redundant arithmetic, fixed-rival scenario salience, length and row order; it is not a forecast. This does not isolate arithmetic or beliefs or explain the original trajectory. Stochastic model draws and shared service interference limit transfer. A null does not show payoff information is irrelevant. Degenerate bounds do not establish population equivalence. No agreement, intent or coordination is verified.',
            '', 'HIT requires mean≥1, positive bootstrap lower and upperp≤.05; DUD if mean≤0 or upper<1, otherwise ODD. No reverse, subgroup or secondary promotion. Known local CLI fingerprints are not complete effective-configuration or provider attestation; tools are discouraged in prompts but actual tool non-use is unattested.',
            '', '[Design](../DESIGN_S43.md) · [Scientific results](s43_payoff.json) · [Figure](../figures/s43_payoff.png)']
    Path(out).write_text('\n'.join(lines)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(9,3.6))
    for i,(case) in enumerate(r['cases']):
        axes[0].plot([0,1],[case['quotes'][v] for v in ['control','table']],'o-',alpha=.65,label=case['case_id'])
    axes[0].set(xticks=[0,1],xticklabels=['Control prompt','Payoff table'],ylabel='Focal wage offer',ylim=(-.5,20.5),title=f"Ten cases; floor counts control/table {r['floor_counts']['control']}/{r['floor_counts']['table']}")
    axes[1].bar([str(x) for x in range(24920,24925)],s['block_values'],color='#4a7fa8')
    axes[1].axhline(0,color='black',lw=.7);axes[1].axhline(1,color='gray',ls='--',label='Registered size threshold1')
    axes[1].set(ylabel='Table − control offer',title='Five source blocks',ylim=(-20.5,20.5));axes[1].legend(fontsize=7)
    fig.suptitle(f"{label}S43: {r['verdict']} (offer, not realized wage)");fig.tight_layout();fig.savefig(figure,dpi=150,metadata={'Software':'S43'});plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',default='results/s43_payoff.json');p.add_argument('--out',default='results/s43_summary.md');p.add_argument('--figure',default='figures/s43_payoff.png');a=p.parse_args();render(a.result,a.out,a.figure)
