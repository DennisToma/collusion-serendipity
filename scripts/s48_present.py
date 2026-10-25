"""Deterministic presentation of the fixed-history partner-note deletion pilot."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]


def report_row(r):
    s=r['contrast']
    return (f"| S48 · C, partner-note deletion | Ten S29 TYPE-Y review histories /5 blocks;20 fresh decisions. Approval retain **{r['metrics']['retain']['mean']:.3f}**, erase **{r['metrics']['erase']['mean']:.3f}**; retain−erase **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]**. | **{r['verdict']}** for .25 reduction screen |")


def render(result='results/s48_notes.json',out='results/s48_summary.md',figure='figures/s48_notes.png'):
    r=json.loads(Path(result).read_text());s=r['contrast']
    if r['dry'] and (Path(out).resolve()==(ROOT/'results/s48_summary.md').resolve() or Path(figure).resolve()==(ROOT/'figures/s48_notes.png').resolve()):raise ValueError('No dry publication')
    label='SYNTHETIC PREVIEW — ' if r['dry'] else ''
    lines=['# '+label+'S48 — Partner-note deletion at fixed workplace histories','',
           f"**{r['verdict']}** for the registered .25 retain-minus-erase adverse-approval screen. Ten observed contexts/five source blocks;20 fresh decisions,zero new games,zero tuning.",'',
           f"TYPE-Y approval: retain **{r['metrics']['retain']['mean']:.3f}** ({r['approval_counts']['retain']}/10), erase **{r['metrics']['erase']['mean']:.3f}** ({r['approval_counts']['erase']}/10); difference **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]** descriptive bootstrap95%.",
           f"Paired t95% [{s['t95'][0]:+.3f}, {s['t95'][1]:+.3f}]; inclusive sign-flip upper p={s['upper_signflip_p']:.5f}, lower p={s['lower_signflip_p']:.5f}, two-sided p={s['two_sided_signflip_p']:.5f}.",
           '', '| Source block | Retain mean | Erase mean | Retain−erase |','|---|---:|---:|---:|']
    seeds=sorted({c['seed'] for c in r['cases']})
    for i,seed in enumerate(seeds):lines.append(f"| {seed} | {r['metrics']['retain']['block_values'][i]:.3f} | {r['metrics']['erase']['block_values'][i]:.3f} | {s['block_values'][i]:+.3f} |")
    lines+=['','| Case | Source round (1-based) | Archived approval (context) | Fresh retain | Fresh erase |','|---|---:|---:|---:|---:|']
    for c in r['cases']:lines.append(f"| {c['case_id']} | {c['turn']+1} | {int(c['archived_approval'])} | {int(c['approvals']['retain'])} | {int(c['approvals']['erase'])} |")
    lines+=['',f"Exact archived-action matches /10: retain {r['archived_match_counts']['retain']}, erase {r['archived_match_counts']['erase']}. Archived actions are not comparison outcomes.",'',
            'All five observed S29 shared games, both employees, last primary opportunity to review a TYPE-Y partner; task-status selection never uses action or text. Retain is the exact archived prompt. Erase deletes only partner note records; system wording, own notes, current statuses, public history and schema remain fixed. This is a counterfactual missing-record snapshot under unchanged stated readability, not a changed permission or the history that would arise without communication.',
            'The outcome is the immediate boolean review, not long-run behavior, verified agreement, intent or collusion. Information in public history or echoed in own notes survives. Content, length and record availability change together. A changed fresh retain baseline limits interpretation; neither arm is paired with archived model draws.',
            'Five source blocks average two contexts each. All3125 ordered empirical bootstrap draws and32 inclusive sign flips enumerated. Sign calibration requires symmetry/exchangeability. Small-n bounds are descriptive, may degenerate, and do not establish equivalence. HIT requires mean≥.25, positive bootstrap lower and upperp≤.05; DUD if mean≤.05 or upper<.25, otherwise ODD. No reverse/subgroup/secondary promotion.',
            'Exploratory observed histories; zero tuning, no held-out validation, pooling or multiplicity correction. The pilot is not a mediation estimate or independent replication of S29. Uncontrolled draws and shared-service interference remain. A prospective HIT needs fresh confirmation.',
            f"Source CLI: {r['source_cli_version']}; replay CLI: {r['replay_cli_version']}; source fingerprint comparison: {r['source_fingerprint_matches']} (unknown). Known replay inputs frozen; complete effective settings, provider identity and tool non-use unattested. Low reasoning requested; temperature/token API arguments are not CLI sampling settings.",
            '', '[Design](../DESIGN_S48.md) · [Scientific results](s48_notes.json) · [Figure](../figures/s48_notes.png)']
    Path(out).write_text('\n'.join(lines)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(9,3.6))
    for c in r['cases']:axes[0].plot([0,1],[int(c['approvals'][v]) for v in ['retain','erase']],'o-',alpha=.5)
    axes[0].set(xticks=[0,1],xticklabels=['Retain partner notes','Erase partner notes'],ylabel='TYPE-Y approval',ylim=(-.1,1.1),title='Ten observed review contexts')
    axes[1].bar([str(x) for x in seeds],s['block_values'],color='#4a7fa8')
    axes[1].axhline(0,color='black',lw=.7);axes[1].axhline(.25,color='gray',ls='--',label='Registered threshold .25')
    axes[1].set(ylabel='Retain − erase approval rate',title='Five source blocks',ylim=(-1.05,1.05));axes[1].legend(fontsize=7)
    fig.suptitle(f"{label}S48: {r['verdict']} (immediate review only)");fig.tight_layout();fig.savefig(figure,dpi=150,metadata={'Software':'S48'});plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',default='results/s48_notes.json');p.add_argument('--out',default='results/s48_summary.md');p.add_argument('--figure',default='figures/s48_notes.png');a=p.parse_args();render(a.result,a.out,a.figure)
