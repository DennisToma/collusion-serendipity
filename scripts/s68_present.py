"""Deterministic presentation of the registered boolean-output polarity screen."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]

def report_row(r):
    s=r['contrast'];m=r['mismatch_counts']
    return f"| S68 · own, boolean-output polarity | Ten S29 histories/5blocks;30fresh decisions. Polarity disagreement **{m['polarity_mismatch']}/10**,identical-repeat **{m['repeat_mismatch']}/10**;excess **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]**. | **{r['verdict']}** for .25 excess-disagreement screen |"

def render(result='results/s68_polarity.json',out='results/s68_summary.md',figure='figures/s68_polarity.png'):
    r=json.loads(Path(result).read_text());s=r['contrast'];m=r['mismatch_counts']
    if r['dry'] and any(Path(p).resolve()==(ROOT/q).resolve() for p,q in [(out,'results/s68_summary.md'),(figure,'figures/s68_polarity.png')]):raise ValueError('No dry publication')
    label='SYNTHETIC PREVIEW — ' if r['dry'] else ''
    lines=['# '+label+'S68 — Boolean-output polarity with repeat-call control','',
           f"**{r['verdict']}** for the registered .25 excess-disagreement screen. Ten observed contexts/five source blocks;30fresh decisions,zero new games,zero tuning.",'',
           f"Polarity disagreements **{m['polarity_mismatch']}/10**,identical-repeat disagreements **{m['repeat_mismatch']}/10**;excess **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]** descriptive bootstrap95%.",
           f"Pairedt95% [{s['t95'][0]:+.3f}, {s['t95'][1]:+.3f}];inclusive sign flips upper={s['upper_signflip_p']:.5f},lower={s['lower_signflip_p']:.5f},two-sided={s['two_sided_signflip_p']:.5f}.",'',
           '| Metric | Mean | Bootstrap95% | Pairedt95% |','|---|---:|---|---|']
    for name,metric in r['metrics'].items():lines.append(f"| {name} | {metric['mean']:.3f} | {metric['ci95']} | {metric['t95']} |")
    lines+=['','| Source block | Polarity disagreement | Repeat disagreement | Excess |','|---|---:|---:|---:|']
    seeds=sorted({c['seed'] for c in r['cases']})
    for i,seed in enumerate(seeds):lines.append(f"| {seed} | {r['metrics']['polarity_mismatch']['block_values'][i]:.3f} | {r['metrics']['repeat_mismatch']['block_values'][i]:.3f} | {s['block_values'][i]:+.3f} |")
    lines+=['','| Case | Round | Agent→partner | Own type | Archived(context) | Anchor | Repeat | Inverted(decoded) | Polarity mismatch | Repeat mismatch |','|---|---:|---|---|---:|---:|---:|---:|---:|---:|']
    for c in r['cases']:lines.append(f"| {c['case_id']} | {c['turn']+1} | {c['agent']}→{c['partner']} | {c['own_status']} | {int(c['archived_approval'])} | {int(c['approvals']['anchor'])} | {int(c['approvals']['repeat'])} | {int(c['approvals']['inverted'])} | {int(c['polarity_mismatch'])} | {int(c['repeat_mismatch'])} |")
    lines+=['',f"Approval counts /10: {r['approval_counts']}. Archived matches /10(context only): {r['archived_match_counts']}.",'',
      'All five S29 shared games,both employees,last primary TYPE-Y-partner opportunity selected from task statuses only. Anchor/repeat are separate calls with identical recorded llm.chat request bytes;fresh Codex cwd/environment may differ and full provider requests are not attested. All arms append the same historical-encoding clarification. Inverted replaces only the equal-length output instruction: raw false means approve and raw true means reject. Full system,current statuses,public history,notepads,IDs,output keys and economics remain fixed. Historical reviews retain true=approve;raw returned JSON remains untouched and only fresh outcomes are decoded. Returned text is unverified.',
      'Primary is (anchor!=inverted)-(anchor!=repeat),averaged within five source blocks. Shared anchor couples indicators;one repeat per case is noisy and arbitrarily choosing anchor adds variance. Provider caching is unknown. Cases within source blocks can be mirrored/dependent;block24483 contains two own-Y contexts. Under independent stationary Bernoulli choices with original p and inverted q,expected excess=(q-p)*(1-2p);it is blind at p=.5 and can be negative despite a real shift toward the original modal action. This is not an omnibus invariance test. This measures observed excess disagreement and does not establish deterministic invariance or isolate response-polarity sensitivity from order,service variability or comprehension. Only focal choices rerun;no partner adaptation,realized current payoff or future behavior observed. Actions/text do not verify agreement,intent or collusion. Reused late source histories provide no independent S29 replication.',
      'All3125ordered empirical block-bootstrap draws,linear rational percentiles and32inclusive sign flips enumerated for all six summaries. Bounds descriptive,may degenerate;enumeration does not establish symmetry/exchangeability. Arm-level generic sign summaries test zero,not the primary paired hypothesis. HIT requires mean>=.25,bootstrap lower>0,upperp<=.05;DUD mean<=.05 or upper<.25;otherwise ODD. With n5,HIT requires all five positive half-unit blocks. DUD does not establish invariance,absence,equivalence or rule out a .25 effect. Zero tuning,no held-out validation,multiplicity correction,pooling,secondary or subgroup promotion. Any HIT needs fresh registered confirmation.',
      'RNG6868 reverses the first context view order for the second context in each block,leaving their middle view in the same position;not exact position balance. Two workers and full block barriers;source seeds do not seed provider draws. The output instruction and its interpretation change together;observed shifts may reflect instruction-following under inverted encoding:no isolated default-true,acquiescence,comprehension or other cognitive mechanism. Runtime and source/request/response chronology verified locally;served identity,effective settings (CLI forwards neither requested temperature nor max_tokens),actual tool non-use and provider timing unattested. Source CLI fingerprint unrecorded;current known local inputs frozen. File fsync is not verified power-loss durability.',
      f"Source CLI {r['source_cli_version']};replay CLI {r['replay_cli_version']};source fingerprint match {r['source_fingerprint_matches']} (unknown).",'',
      '[Design](../DESIGN_S68.md) · [Scientific JSON](s68_polarity.json) · [All returned text](s68_action_text.md) · [Raw archive](../data/s68_polarity/responses.jsonl) · [Figure](../figures/s68_polarity.png)']
    Path(out).write_text('\n'.join(lines)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(9,3.6))
    axes[0].bar(['Inverted','Identical repeat'],[m['polarity_mismatch']/10,m['repeat_mismatch']/10],color=['#487ea8','#888888']);axes[0].set(ylabel='Disagreement with anchor',ylim=(0,1.05),title='Ten fixed review contexts')
    axes[1].bar(list(map(str,seeds)),s['block_values'],color='#487ea8');axes[1].axhline(0,color='black',lw=.7);axes[1].axhline(.25,color='gray',ls='--');axes[1].set(ylabel='Polarity − repeat disagreement',ylim=(-1.05,1.05),title='Five source blocks')
    fig.suptitle(f"{label}S68: {r['verdict']} (immediate decisions)");fig.tight_layout();fig.savefig(figure,dpi=150,metadata={'Software':'S68'});plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',default='results/s68_polarity.json');p.add_argument('--out',default='results/s68_summary.md');p.add_argument('--figure',default='figures/s68_polarity.png');a=p.parse_args();render(a.result,a.out,a.figure)
