"""Deterministic presentation of the registered penalty pilot."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]


def report_row(r):
    s=r['contrast']
    return (f"| S51 · D, reviewer penalty | Ten S29 TYPE-Y review histories /5 blocks;20 fresh decisions. Approval charge3 **{r['metrics']['baseline']['mean']:.3f}**, charge9 **{r['metrics']['strong']['mean']:.3f}**; baseline−strong **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]**. | **{r['verdict']}** for .25 reduction screen |")


def render(result='results/s51_penalty.json',out='results/s51_summary.md',figure='figures/s51_penalty.png'):
    r=json.loads(Path(result).read_text());s=r['contrast']
    if r['dry'] and (Path(out).resolve()==(ROOT/'results/s51_summary.md').resolve() or Path(figure).resolve()==(ROOT/'figures/s51_penalty.png').resolve()):raise ValueError('No dry publication')
    label='SYNTHETIC PREVIEW — ' if r['dry'] else ''
    lines=['# '+label+'S51 — Personal reviewer penalties at fixed workplace histories','',
           f"**{r['verdict']}** for the registered .25 baseline-minus-strong adverse-approval screen. Ten observed contexts/five source blocks;20 fresh decisions,zero new games,zero tuning.",'',
           f"TYPE-Y approval: baseline charge3 **{r['metrics']['baseline']['mean']:.3f}** ({r['approval_counts']['baseline']}/10), strong charge9 **{r['metrics']['strong']['mean']:.3f}** ({r['approval_counts']['strong']}/10); reduction **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]** descriptive bootstrap95%.",
           f"Paired t95% [{s['t95'][0]:+.3f}, {s['t95'][1]:+.3f}]; inclusive sign-flip upper p={s['upper_signflip_p']:.5f}, lower p={s['lower_signflip_p']:.5f}, two-sided p={s['two_sided_signflip_p']:.5f}.",
           '', '| Source block | Charge3 mean | Charge9 mean | Baseline−strong |','|---|---:|---:|---:|']
    seeds=sorted({c['seed'] for c in r['cases']})
    for i,seed in enumerate(seeds):lines.append(f"| {seed} | {r['metrics']['baseline']['block_values'][i]:.3f} | {r['metrics']['strong']['block_values'][i]:.3f} | {s['block_values'][i]:+.3f} |")
    lines+=['','| Case | Source round (1-based) | Own status | Archived approval (context) | Fresh charge3 | Fresh charge9 |','|---|---:|---|---:|---:|---:|']
    for c in r['cases']:lines.append(f"| {c['case_id']} | {c['turn']+1} | {c['own_status']} | {int(c['archived_approval'])} | {int(c['approvals']['baseline'])} | {int(c['approvals']['strong'])} |")
    lines+=['',f"Exact archived-action matches /10: baseline {r['archived_match_counts']['baseline']}, strong {r['archived_match_counts']['strong']}. Archived actions are not comparison outcomes.",'',
            'All five observed S29 shared games, both employees, last primary opportunity to review a TYPE-Y partner; task-status selection never uses action or text. Both fresh arms append the same current-policy notice. Strong changes only the deterministic charge3 to9 and the corresponding stated reviewer net payoff -2 to -8; user bytes, public history, notes, statuses, horizon and other rewards stay fixed. Baseline is not the exact archived system because of the common notice. Historical scores remain under the original policy. Selecting the last TYPE-Y opportunity gives late histories with accumulated notes, limiting transfer to earlier rounds.',
            'Rejecting TYPE-Y saves the reviewer2 or8 holding incoming approval fixed. If both submissions are Y, mutual approvals pay each4 at charge3 and -2 at charge9. These are stage-payoff identities, not equilibrium or long-run claims. Future incentives remain possible. Only focal decisions are rerun; partner adaptation and realized current or later payoffs are unobserved. The outcome is an immediate boolean review, not verified agreement, intent or collusion. The manipulation bundles penalty magnitude, net arithmetic and numeral salience; it identifies no isolated mechanism. Historical notes can retain obsolete advice.',
            'Five source blocks average two contexts each. All3125 empirical ordered bootstrap draws and32 inclusive sign flips enumerated. Sign calibration requires symmetry/exchangeability. Small-n bounds are descriptive and may degenerate, without establishing equivalence. HIT requires mean≥.25, positive bootstrap lower and upperp≤.05; DUD if mean≤.05 or upper<.25, else ODD. At n5 HIT reduces to5/5positive blocks (forcing mean≥.5), not three independent checks. Mean≤.05 equals mean≤0 on the .1 lattice; a DUD may leave the .25 target unresolved. Only the paired contrast is the registered hypothesis; arm-level generic sign statistics test zero approval. No reverse/subgroup/secondary promotion.',
            'Exploratory observed histories; zero tuning, no held-out validation, pooling or multiplicity correction. Earlier replay outcomes form no comparison arm. A vanished fresh baseline limits intervention interpretation. Uncontrolled draws and shared-service interference remain; this is not an independent S29 replication. Any HIT requires fresh confirmation.',
            f"Source CLI: {r['source_cli_version']}; replay CLI: {r['replay_cli_version']}; source fingerprint comparison: {r['source_fingerprint_matches']} (unknown). Known replay inputs frozen; complete effective settings, served identity/routing and tool non-use unattested. Response model/backend checks validate requested labels only. Low reasoning requested; temperature/token API arguments are not CLI sampling settings.",
            '', '[Raw returned text](../data/s51_penalty/responses.jsonl) · [Design](../DESIGN_S51.md) · [Scientific results](s51_penalty.json) · [Figure](../figures/s51_penalty.png)']
    Path(out).write_text('\n'.join(lines)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(9,3.6))
    for c in r['cases']:axes[0].plot([0,1],[int(c['approvals'][v]) for v in ['baseline','strong']],'o-',alpha=.5)
    axes[0].set(xticks=[0,1],xticklabels=['Charge3 (net -2)','Charge9 (net -8)'],ylabel='TYPE-Y approval',ylim=(-.1,1.1),title='Ten observed review contexts')
    axes[1].bar([str(x) for x in seeds],s['block_values'],color='#4a7fa8')
    axes[1].axhline(0,color='black',lw=.7);axes[1].axhline(.25,color='gray',ls='--',label='Registered threshold .25')
    axes[1].set(ylabel='Baseline − strong approval rate',title='Five source blocks',ylim=(-1.05,1.05));axes[1].legend(fontsize=7)
    fig.suptitle(f"{label}S51: {r['verdict']} (immediate review only)");fig.tight_layout();fig.savefig(figure,dpi=150,metadata={'Software':'S51'});plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',default='results/s51_penalty.json');p.add_argument('--out',default='results/s51_summary.md');p.add_argument('--figure',default='figures/s51_penalty.png');a=p.parse_args();render(a.result,a.out,a.figure)
