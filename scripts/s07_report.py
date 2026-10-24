"""Render S07 tables and figure from complete frozen analysis, without calls."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

def interval(d): return f'{d[0]:+.3f}, {d[1]:+.3f}'

def main():
    r=json.loads(Path('results/s07_legality.json').read_text())
    assert not r['dry']
    m=r['metrics'];q=m['quantity'];d=q['paired_difference']
    desc=(f'**S07:** **{r["verdict"]} for predicted higher output**; legality-neutral '
          f'{d["mean"]:+.3f} [{interval(d["ci95"])}] units/firm, paired t '
          f'[{interval(d["paired_t_ci95"])}], exact higher-output p={d["exact_signflip_p_upper"]:.5f}. '
          'Both arms have private boxes; the rule cue has no implemented sanctions. '
          'No agreement/execution labels or no-channel control; this does not identify collusion. '
          '[All S07 outcomes](results/s07_summary.md).')
    summary=f'''# S07 — explicit anti-coordination rule

{desc.replace("(results/s07_summary.md)","(s07_summary.md)")}

Five fresh exploratory blocks (24080..24084), ten T12 Cournot games, codex/gpt-6-luna.
Primary: pair output/firm r4–12; zero tuning. Signs/thresholds frozen before calls.
Cached calls: {r['cached_responses']}; all games complete. Retries by arm: {r['retries_by_arm']}. [Design](../DESIGN_S07.md),
[analysis](s07_legality.json), [verification](../logs/s07_verification.json).

| r4–12 metric | Neutral mean | Legality mean | Difference [descriptive bootstrap 95%] | Paired t 95% |
|---|---:|---:|---|---|
'''
    for key,x in m.items():
        dd=x['paired_difference']
        summary+=f'| {key} | {x["neutral"]["mean"]:.3f} | {x["legality"]["mean"]:.3f} | {dd["mean"]:+.3f} [{interval(dd["ci95"])}] | [{interval(dd["paired_t_ci95"])}] |\n'
    summary+=f'\nNeutral pair output minus symmetric Nash6: {q["neutral"]["mean"]-6:+.3f}; neutral pair minus outsider output: {q["neutral"]["mean"]-m["outsider_quantity"]["neutral"]["mean"]:+.3f}. These are reference descriptions, not collusion labels.\n'
    summary+='\nMessage summaries count messages sent in the named window; final-round messages are never received.\n'
    summary+='\nPrimary seed differences (seed order): '+', '.join(f'{v:+.6f}' for v in q['seed_differences'])+'.\n'
    summary+='\n| Window | Metric | Neutral mean | Legality mean | Difference |\n|---|---|---:|---:|---:|\n'
    for window in ['all_rounds','final']:
        for key in m:
            means={c:sum(g[window][key] for g in r['games'] if g['condition']==c)/5 for c in ['neutral','legality']}
            summary+=f'| {window} | {key} | {means["neutral"]:.3f} | {means["legality"]:.3f} | {means["legality"]-means["neutral"]:+.3f} |\n'
    summary+='\n![S07 paths and seed contrasts](../figures/s07_legality.png)\n\n'
    summary+='The neutral comparator also states market rules and the profit formula; length, normative valence and semantic content are not matched. '
    summary+='The effect is of this exact cue package across all firms; it does not isolate the private channel, moral reasoning or real enforcement. '
    summary+='Message length/emptiness are descriptive measures, not agreement labels. All primary-window secondaries and all-round/final summaries are shown; no secondary drives a HIT. '
    summary+='Bootstrap bounds use five blocks and omit prompt/model uncertainty. Sign-flip inference assumes symmetric/exchangeable block differences; concurrent backend sampling may violate this. '
    summary+='The horizon is short and undisclosed, model labels are client-reported, and temperature/API seeds are uncontrolled. '
    summary+='The logical-call deadline does not bound internal transport retries. All raw starts are checked in the publication audit.\n'
    Path('results/s07_summary.md').write_text(summary)
    p=Path('REPORT.md');report=p.read_text()
    lines=report.splitlines()
    lines[2]=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')+' · Iteration 4 · **No hits promoted.** Exploratory pilots; zero tuning attempts.'
    lines=[x for x in lines if not x.startswith('| S07 ·') and not x.startswith('**S07:**')]
    last=max(i for i,x in enumerate(lines) if x.startswith('| S'))
    lines.insert(last+1,f'| S07 · F, anti-coordination rule | 10 games, 5 blocks. Pair output r4–12: neutral **{q["neutral"]["mean"]:.3f}**, legality **{q["legality"]["mean"]:.3f}**; difference **{d["mean"]:+.3f} [{interval(d["ci95"])}]**. | **{r["verdict"]} for predicted increase** |')
    lines.insert(last+3,desc)
    lines=[x.replace('**Next:** cover D/E/F before deepening; own S05 authority-label and S06 denomination ideas queued.', '**Next:** cover D/E before deepening; own S05/S06/S08 ideas queued.') for x in lines]
    p.write_text('\n'.join(lines)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig,axes=plt.subplots(1,3,figsize=(12,3.6))
    for c,color in [('neutral','#3675a9'),('legality','#bd6928')]:
        games=[json.loads(p.read_text()) for p in Path('data/s07_legality').glob(f'game_*_{c}.json')]
        values=np.array([[np.mean([a['quantity'] for a in row['agents'] if a['id'] in g['ground_truth']['assigned_pair']]) for row in g['rows']] for g in games])
        words=np.array([[np.mean([len(x['text'].split()) for x in g['ground_truth']['private_chat'] if x['round']==t]) for t in range(1,13)] for g in games])
        for ax,v in zip(axes[:2],[values,words]):
            ax.plot(range(1,13),v.mean(axis=0),label=c,color=color)
            ax.fill_between(range(1,13),v.min(axis=0),v.max(axis=0),alpha=.13,color=color)
            ax.set_xlabel('Round; bands = five-game range')
    axes[0].axhline(6,ls='--',color='gray',label='symmetric Nash')
    axes[0].set_ylabel('Pair mean output / firm');axes[0].legend(fontsize=8)
    axes[1].set_ylabel('Mean private-message words')
    axes[2].bar(range(1,6),q['seed_differences'],color='#3675a9');axes[2].axhline(0,color='gray')
    axes[2].set_xlabel('Fresh seed block');axes[2].set_ylabel('Legality − neutral output, r4–12')
    fig.tight_layout();fig.savefig('figures/s07_legality.png',dpi=160);plt.close(fig)

if __name__=='__main__':main()
