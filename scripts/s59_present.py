"""Deterministic presentation of frozen lossless public-history table pilot."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]


def report_row(r):
    s=r['contrast']
    return (f"| S59 · own, lossless public-history table | Ten S29 TYPE-Y histories /5 blocks;20 fresh decisions. Approval original **{r['metrics']['original']['mean']:.3f}**, compact **{r['metrics']['compact']['mean']:.3f}**; original−compact **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]**. | **{r['verdict']}** for .25 reduction screen |")


def render(result='results/s59_history.json',out='results/s59_summary.md',figure='figures/s59_history.png'):
    r=json.loads(Path(result).read_text());s=r['contrast']
    if r['dry'] and any(Path(p).resolve()==(ROOT/q).resolve() for p,q in [(out,'results/s59_summary.md'),(figure,'figures/s59_history.png')]):raise ValueError('No dry publication')
    label='SYNTHETIC PREVIEW — ' if r['dry'] else ''
    lines=['# '+label+'S59 — Completed lossless public-history table','',
           f"**{r['verdict']}** for the registered .25 original-minus-compact TYPE-Y approval screen. Ten observed contexts/five source blocks;20 fresh decisions,zero new games,zero tuning.",'',
           f"Approvals: original **{r['approval_counts']['original']}/10**, compact **{r['approval_counts']['compact']}/10**; contrast **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]** descriptive bootstrap95%.",
           f"Paired t95% [{s['t95'][0]:+.3f}, {s['t95'][1]:+.3f}]; inclusive sign flips upper={s['upper_signflip_p']:.5f}, lower={s['lower_signflip_p']:.5f}, two-sided={s['two_sided_signflip_p']:.5f}.",'',
           '| Source block | Original | Compact | Original−compact |','|---|---:|---:|---:|']
    seeds=sorted({c['seed'] for c in r['cases']})
    for i,seed in enumerate(seeds):lines.append(f"| {seed} | {r['metrics']['original']['block_values'][i]:.3f} | {r['metrics']['compact']['block_values'][i]:.3f} | {s['block_values'][i]:+.3f} |")
    lines+=['','| Case | Round (1-based) | Own true type | Archived (context) | Original | Compact |','|---|---:|---|---:|---:|---:|']
    for c in r['cases']:lines.append(f"| {c['case_id']} | {c['turn']+1} | {c['own_status']} | {int(c['archived_approval'])} | {int(c['approvals']['original'])} | {int(c['approvals']['compact'])} |")
    lines+=['','Construction diagnostics (UTF-8 bytes of public-history JSON value only):',
            '| Case | Original bytes | Compact bytes |','|---|---:|---:|']
    for c in r['cases']:lines.append(f"| {c['case_id']} | {c['history_bytes']['original']} | {c['history_bytes']['compact']} |")
    lines+=['',f"Archived action matches /10: original {r['archived_match_counts']['original']}, compact {r['archived_match_counts']['compact']};context only,never a comparison arm.",'',
            'All five S29 shared games,both employees,last primary TYPE-Y-partner opportunity,selected using task statuses only. Original is the exact archived system/user. Compact replaces only the completed-public-round JSON value with a column_paths/rows table. All nine per-round fields and primitive values are preserved and exact JSON roundtrip checked;system,current round,both authoritative statuses,all notes,payoffs and schema remain fixed.',
            'Length,field repetition,JSON shape and reading burden change together. Lossless external reconstruction does not establish equal model comprehension;the table may be less familiar or salient. Notes retain historical information. No reciprocity,reputation,context-length or representation-specific mechanism is identified. Only focal choices rerun;partner adaptation,realized current payoffs and later behavior unobserved. Boolean decisions and unverified explanations do not establish agreement,intent or collusion.',
            'Five source blocks are the resampling unit,with two contexts averaged within each. All3125ordered bootstrap draws,linear percentiles and32inclusive sign flips enumerated;enumeration does not establish symmetry/exchangeability. Bounds descriptive and may degenerate,no equivalence claim. HIT requires mean>=.25,bootstrap lower>0,upperp<=.05;DUD mean<=.05 or upper<.25,else ODD. At n5,HIT implies5/5positive blocks,forcing mean>=.5;gates are not independent evidence. DUD can leave.25 unresolved. Arm-level generic sign summaries test zero approval,not the registered paired hypothesis.',
            'Zero tuning,no held-out validation or multiplicity correction,no reverse/secondary/subgroup promotion. Observed late histories,reused source blocks and uncontrolled fresh draws limit generalization. Archived rejections in24483/24484 create a possible original-arm floor;fresh choices need not repeat them. Cases and screen retained without replacement. Earlier replay results motivated the question;they are neither comparison arms nor independent replications. All earlier exploratory tests count as multiplicity. Any HIT needs fresh registered confirmation.',
            f"Source CLI {r['source_cli_version']};replay CLI {r['replay_cli_version']};source fingerprint match {r['source_fingerprint_matches']} (unknown). Known current local inputs frozen;served identity,effective settings and actual tool non-use unattested. Temperature/token requests are not effective CLI sampling settings.",
            'External reservation and launch receipt files fsynced;parent directories not fsynced. Process-level persistence,not verified power-loss durability. Local git/timestamps do not attest provider timing.','',
            '[Design](../DESIGN_S59.md) · [Scientific JSON](s59_history.json) · [All returned text](s59_action_text.md) · [Raw archive](../data/s59_history/responses.jsonl) · [Figure](../figures/s59_history.png)']
    Path(out).write_text('\n'.join(lines)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(9,3.6))
    for c in r['cases']:axes[0].plot([0,1],[int(c['approvals'][v]) for v in ['original','compact']],'o-',alpha=.5)
    axes[0].set(xticks=[0,1],xticklabels=[f"Original ({r['approval_counts']['original']}/10)",f"Compact ({r['approval_counts']['compact']}/10)"],ylabel='TYPE-Y approval',ylim=(-.1,1.1),title='Ten fixed review contexts')
    axes[1].bar([str(x) for x in seeds],s['block_values'],color='#4a7fa8');axes[1].axhline(0,color='black',lw=.7);axes[1].axhline(.25,color='gray',ls='--')
    axes[1].set(ylabel='Original − compact approval rate',title='Five source blocks',ylim=(-1.05,1.05))
    fig.suptitle(f"{label}S59: {r['verdict']} (immediate review only)");fig.tight_layout();fig.savefig(figure,dpi=150,metadata={'Software':'S59'});plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',default='results/s59_history.json');p.add_argument('--out',default='results/s59_summary.md');p.add_argument('--figure',default='figures/s59_history.png');a=p.parse_args();render(a.result,a.out,a.figure)
