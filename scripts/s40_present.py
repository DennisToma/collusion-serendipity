"""Render saved S40 data; no model calls or changes to earlier reports."""
import argparse
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def render(result='results/s40_memory.json',out='results/s40_summary.md',figure='figures/s40_memory.png'):
    r=json.loads(Path(result).read_text());s=r['contrast']
    if r['dry'] and (Path(out).resolve()==(ROOT/'results/s40_summary.md').resolve() or Path(figure).resolve()==(ROOT/'figures/s40_memory.png').resolve()):raise ValueError('No dry publication')
    label='SYNTHETIC PREVIEW — ' if r['dry'] else ''
    lines=['# '+label+'S40 — Private notepad erasure at fixed labor histories','',
           f"**{r['verdict']}** for the registered two-unit increase screen; ten selected cases/five source blocks; twenty fresh decisions, zero new games and zero tuning.",'',
           f"Normalized focal offer: retain **{r['metrics']['retain']['mean']:.3f}**, erase **{r['metrics']['erase']['mean']:.3f}**; erase−retain **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]** descriptive bootstrap95%.",
           f"Paired t95% [{s['t95'][0]:+.3f}, {s['t95'][1]:+.3f}]; inclusive upper sign-flip p={s['upper_signflip_p']:.5f}.",
           '', '| Source block | Retain mean offer | Erase mean offer | Erase−retain |','|---|---:|---:|---:|']
    for i,seed in enumerate(range(24800,24805)):
        lines.append(f"| {seed} | {r['metrics']['retain']['block_values'][i]:.3f} | {r['metrics']['erase']['block_values'][i]:.3f} | {s['block_values'][i]:+.3f} |")
    lines+=['','| Case / selected firm | Archived quote | Fresh retain quote | Fresh erase quote |','|---|---:|---:|---:|']
    for c in r['cases']:lines.append(f"| {c['case_id']} | {c['archived_quote']} | {c['quotes']['retain']} | {c['quotes']['erase']} |")
    lines+=['',f"Minimum quote10 counts /10: retain {r['floor_counts']['retain']}, erase {r['floor_counts']['erase']}. Exact archived-quote matches /10: retain {r['archived_match_counts']['retain']}, erase {r['archived_match_counts']['erase']}.",'',
            'Quotes10–30 are normalized by subtracting10. Outcomes are focal offers, not realized worker wages; the rival is not replayed. Five source blocks, each averaging its two source-arm cases, are the resampling unit. All3125 empirical bootstrap draws and32 inclusive upper sign flips are enumerated.',
            'Both fresh arms use the same source system/public history; erasure changes only the private-note array to[]. No current archived response is supplied. The retain prompt exactly matches the source prompt.',
            '', f"Source CLI version {r['source_cli_version']}; replay CLI version {r['replay_cli_version']}; known source/replay fingerprint equal: {r['source_fingerprint_matches']}. This is local metadata, not served-model identity.", '', 'The manager selected this challenge after observing S37 floor behavior. Retained public history reveals the same earlier actions. Note availability, prompt length and consistency with the complete-notepad promise change together. This does not isolate a memory mechanism or explain the original trajectory. Stochastic model draws and shared service interference limit transfer. A null does not show memory is irrelevant. Degenerate bounds do not establish population equivalence. No agreement, intent or coordination is verified.',
            '', 'HIT requires mean≥2, positive bootstrap lower and upperp≤.05; DUD if mean≤0 or upper<2, otherwise ODD. No reverse, subgroup or secondary promotion. Known local CLI fingerprints are not complete effective-configuration or provider attestation; tools are discouraged in prompts but actual tool non-use is unattested.',
            '', '[Design](../DESIGN_S40.md) · [Scientific results](s40_memory.json) · [Figure](../figures/s40_memory.png)']
    Path(out).write_text('\n'.join(lines)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(9,3.6))
    for i,(case) in enumerate(r['cases']):
        axes[0].plot([0,1],[case['quotes'][v]-10 for v in ['retain','erase']],'o-',alpha=.65,label=case['case_id'])
    axes[0].set(xticks=[0,1],xticklabels=['Retain private notes','Erase private notes'],ylabel='Normalized focal offer',ylim=(-.5,20.5),title=f"Ten cases; floor counts retain/erase {r['floor_counts']['retain']}/{r['floor_counts']['erase']}")
    axes[1].bar([str(x) for x in range(24800,24805)],s['block_values'],color='#4a7fa8')
    axes[1].axhline(0,color='black',lw=.7);axes[1].axhline(2,color='gray',ls='--',label='Registered size threshold2')
    axes[1].set(ylabel='Erase − retain offer',title='Five source blocks',ylim=(-20.5,20.5));axes[1].legend(fontsize=7)
    fig.suptitle(f"{label}S40: {r['verdict']} (offer, not realized wage)");fig.tight_layout();fig.savefig(figure,dpi=150,metadata={'Software':'S40'});plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',default='results/s40_memory.json');p.add_argument('--out',default='results/s40_summary.md');p.add_argument('--figure',default='figures/s40_memory.png');a=p.parse_args();render(a.result,a.out,a.figure)
