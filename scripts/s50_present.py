"""Deterministic presentation of the fixed-history final-round disclosure pilot."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]


def report_row(r):
    s=r['contrast']
    return (f"| S50 · F, final-round disclosure | Ten S29 TYPE-Y review histories /5 blocks;20 fresh decisions. Approval hidden **{r['metrics']['hidden']['mean']:.3f}**, final **{r['metrics']['final']['mean']:.3f}**; hidden−final **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]**. | **{r['verdict']}** for .25 reduction screen |")


def render(result='results/s50_terminal.json',out='results/s50_summary.md',figure='figures/s50_terminal.png'):
    r=json.loads(Path(result).read_text());s=r['contrast']
    if r['dry'] and (Path(out).resolve()==(ROOT/'results/s50_summary.md').resolve() or Path(figure).resolve()==(ROOT/'figures/s50_terminal.png').resolve()):raise ValueError('No dry publication')
    label='SYNTHETIC PREVIEW — ' if r['dry'] else ''
    lines=['# '+label+'S50 — Final-round disclosure at fixed workplace histories','',
           f"**{r['verdict']}** for the registered .25 hidden-minus-final adverse-approval screen. Ten observed contexts/five source blocks;20 fresh decisions,zero new games,zero tuning.",'',
           f"TYPE-Y approval: hidden **{r['metrics']['hidden']['mean']:.3f}** ({r['approval_counts']['hidden']}/10), final **{r['metrics']['final']['mean']:.3f}** ({r['approval_counts']['final']}/10); difference **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]** descriptive bootstrap95%.",
           f"Paired t95% [{s['t95'][0]:+.3f}, {s['t95'][1]:+.3f}]; inclusive sign-flip upper p={s['upper_signflip_p']:.5f}, lower p={s['lower_signflip_p']:.5f}, two-sided p={s['two_sided_signflip_p']:.5f}.",
           '', '| Source block | Hidden mean | Final mean | Hidden−final |','|---|---:|---:|---:|']
    seeds=sorted({c['seed'] for c in r['cases']})
    for i,seed in enumerate(seeds):lines.append(f"| {seed} | {r['metrics']['hidden']['block_values'][i]:.3f} | {r['metrics']['final']['block_values'][i]:.3f} | {s['block_values'][i]:+.3f} |")
    lines+=['','| Case | Source round (1-based) | Archived approval (context) | Fresh hidden | Fresh final |','|---|---:|---:|---:|---:|']
    for c in r['cases']:lines.append(f"| {c['case_id']} | {c['turn']+1} | {int(c['archived_approval'])} | {int(c['approvals']['hidden'])} | {int(c['approvals']['final'])} |")
    lines+=['',f"Exact archived-action matches /10: hidden {r['archived_match_counts']['hidden']}, final {r['archived_match_counts']['final']}. Archived actions are not comparison outcomes.",'',
            'All five observed S29 shared games, both employees, last primary opportunity to review a TYPE-Y partner; task-status selection never uses action or text. Hidden is the exact archived system and prompt. Final replaces only the source objective/horizon sentence with the registered same-objective, common-knowledge terminal notice. User prompt, both owners’ notes, current statuses, public history, schema and immediate stage rewards stay byte-identical. The notice says both employees know, but only focal decisions are rerun; no partner response or completed final-round game is observed.',
            'The outcome is the immediate boolean review, not long-run behavior, verified agreement, intent or collusion. The notice bundles endpoint information, stated common knowledge, wording, length and salience. It does not identify strategic foresight or another mechanism. Generic next-round notepad rules, historical continuation cues and the required note field survive; the explicit terminal notice overrides them, but cue conflict limits interpretation. A changed fresh hidden baseline limits interpretation; neither arm is paired with archived model draws.',
            'Five source blocks average two contexts each. All3125 ordered empirical bootstrap draws and32 inclusive sign flips enumerated. Sign calibration requires symmetry/exchangeability. Small-n bounds are descriptive, may degenerate, and do not establish equivalence. HIT requires mean≥.25, positive bootstrap lower and upperp≤.05; DUD if mean≤.05 or upper<.25, otherwise ODD. At n5 the HIT gate reduces to five strictly positive blocks (forcing mean≥.5 and positive bootstrap lower); these are not three independent checks. The .1 mean lattice makes the mean≤.05 DUD condition equivalent to mean≤0. A DUD can leave the .25 target unresolved. Arm-level generic sign statistics test zero approval, not the intervention; only the paired contrast is primary. No reverse/subgroup/secondary promotion.',
            'Exploratory observed histories; zero tuning, no held-out validation, pooling or multiplicity correction. The pilot is not an independent replication of S29 or a long-run terminal-game comparison. S48 outputs form no comparison arm. Uncontrolled draws and shared-service interference remain. A prospective HIT needs fresh confirmation.',
            f"Source CLI: {r['source_cli_version']}; replay CLI: {r['replay_cli_version']}; source fingerprint comparison: {r['source_fingerprint_matches']} (unknown). Known replay inputs frozen; complete effective settings, provider identity and tool non-use unattested. Low reasoning requested; temperature/token API arguments are not CLI sampling settings.",
            '', '[Design](../DESIGN_S50.md) · [Scientific results](s50_terminal.json) · [Figure](../figures/s50_terminal.png)']
    Path(out).write_text('\n'.join(lines)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(9,3.6))
    for c in r['cases']:axes[0].plot([0,1],[int(c['approvals'][v]) for v in ['hidden','final']],'o-',alpha=.5)
    axes[0].set(xticks=[0,1],xticklabels=['Endpoint undisclosed','Known final round'],ylabel='TYPE-Y approval',ylim=(-.1,1.1),title='Ten observed review contexts')
    axes[1].bar([str(x) for x in seeds],s['block_values'],color='#4a7fa8')
    axes[1].axhline(0,color='black',lw=.7);axes[1].axhline(.25,color='gray',ls='--',label='Registered threshold .25')
    axes[1].set(ylabel='Hidden − final approval rate',title='Five source blocks',ylim=(-1.05,1.05));axes[1].legend(fontsize=7)
    fig.suptitle(f"{label}S50: {r['verdict']} (immediate review only)");fig.tight_layout();fig.savefig(figure,dpi=150,metadata={'Software':'S50'});plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',default='results/s50_terminal.json');p.add_argument('--out',default='results/s50_summary.md');p.add_argument('--figure',default='figures/s50_terminal.png');a=p.parse_args();render(a.result,a.out,a.figure)
