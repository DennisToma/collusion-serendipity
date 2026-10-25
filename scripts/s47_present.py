"""Deterministic presentation of saved output-example pilot results; no model calls."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]


def report_row(r):
    s=r['contrast']
    return (f"| S47 · own, output example | Ten S42 histories /5 blocks;20 fresh decisions. Focal offer low example **{r['metrics']['low_example']['mean']:.3f}**, high example **{r['metrics']['high_example']['mean']:.3f}**; high−low example **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]**. | **{r['verdict']}** for two-unit increase screen |")


def render(result='results/s47_example.json',out='results/s47_summary.md',figure='figures/s47_example.png'):
    r=json.loads(Path(result).read_text());s=r['contrast']
    if r['dry'] and (Path(out).resolve()==(ROOT/'results/s47_summary.md').resolve() or Path(figure).resolve()==(ROOT/'figures/s47_example.png').resolve()):raise ValueError('No dry publication')
    label='SYNTHETIC PREVIEW — ' if r['dry'] else ''
    lines=['# '+label+'S47 — Low versus high JSON example rate','',
           f"**{r['verdict']}** for the registered two-unit high-minus-low example offer increase screen. Ten observed contexts/five source blocks;20 fresh decisions,zero new games,zero tuning.",'',
           f"Focal offer: low example **{r['metrics']['low_example']['mean']:.3f}**, high example **{r['metrics']['high_example']['mean']:.3f}**; difference **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]** descriptive bootstrap95%.",
           f"Paired t95% [{s['t95'][0]:+.3f}, {s['t95'][1]:+.3f}]; inclusive sign-flip upper p={s['upper_signflip_p']:.5f}, lower p={s['lower_signflip_p']:.5f}, two-sided p={s['two_sided_signflip_p']:.5f}.",
           '', '| Source block | Low example mean | High example mean | High−low example |','|---|---:|---:|---:|']
    for i,seed in enumerate(range(24920,24925)):
        lines.append(f"| {seed} | {r['metrics']['low_example']['block_values'][i]:.3f} | {r['metrics']['high_example']['block_values'][i]:.3f} | {s['block_values'][i]:+.3f} |")
    lines+=['','| Case / focal firm | Archived offer (context) | Fresh low example | Fresh high example |','|---|---:|---:|---:|']
    for c in r['cases']:lines.append(f"| {c['case_id']} | {c['archived_quote']} | {c['quotes']['low_example']} | {c['quotes']['high_example']} |")
    lines+=['',f"Offers at0 /10: low_example {r['floor_counts']['low_example']}, high_example {r['floor_counts']['high_example']}. Exact archived-offer matches /10: low_example {r['archived_match_counts']['low_example']}, high_example {r['archived_match_counts']['high_example']}.",'',
            'Both fresh arms receive the same source system, public history, own notes, complete ascending payoff table and original output contract. A syntax example with empty reasoning/note differs only in rate0 versus rate20. Both include the same explicit non-recommendation warning. Source histories are the ten observed S42 contexts used in S43/S44; new outputs are fresh uncontrolled model draws. No archived current response is supplied.',
            'Outcome is a focal offer in0–20, not realized worker pay; rivals are not rerun. Five source blocks average two contexts each. All3125 ordered empirical bootstrap draws and32 inclusive sign flips are enumerated. Sign calibration assumes symmetry/exchangeability; enumeration alone does not establish it. With n5, empirical intervals may degenerate and do not establish equivalence. The directional DUD screen does not rule out an opposite effect.',
            'Selection is post hoc and not held out. No pooling, reverse/subgroup/secondary promotion or multiplicity correction. Results cannot identify anchoring, arithmetic errors, coordination, intent or a population prevalence. Example numerals, numeral length, salience and association with an action travel together; shared-service interference, uncontrolled model draws and small n limit transfer.',
            f"Known source CLI {r['source_cli_version']}; replay CLI {r['replay_cli_version']}; known local fingerprints equal: {r['source_fingerprint_matches']}. Complete effective settings/provider identity/tool non-use remain unattested. Codex requests low reasoning; temperature/token arguments are not transmitted as CLI settings.",
            'HIT requires mean≥2,positive bootstrap lower and upperp≤.05;DUD if mean≤0 or upper<2,otherwise ODD. Any HIT requires fresh registered confirmation.',
            '', '[Design](../DESIGN_S47.md) · [Scientific results](s47_example.json) · [Figure](../figures/s47_example.png)']
    Path(out).write_text('\n'.join(lines)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(9,3.6))
    for c in r['cases']:axes[0].plot([0,1],[c['quotes'][v] for v in ['low_example','high_example']],'o-',alpha=.65)
    axes[0].set(xticks=[0,1],xticklabels=['Example rate 0','Example rate 20'],ylabel='Focal offer',ylim=(-.5,20.5),title='Ten fixed-history contexts')
    axes[1].bar([str(x) for x in range(24920,24925)],s['block_values'],color='#4a7fa8')
    axes[1].axhline(0,color='black',lw=.7);axes[1].axhline(2,color='gray',ls='--',label='Registered threshold2')
    axes[1].set(ylabel='High − low example offer',title='Five source blocks',ylim=(-20.5,20.5));axes[1].legend(fontsize=7)
    fig.suptitle(f"{label}S47: {r['verdict']} (offer, not realized wage)");fig.tight_layout();fig.savefig(figure,dpi=150,metadata={'Software':'S47'});plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',default='results/s47_example.json');p.add_argument('--out',default='results/s47_summary.md');p.add_argument('--figure',default='figures/s47_example.png');a=p.parse_args();render(a.result,a.out,a.figure)
