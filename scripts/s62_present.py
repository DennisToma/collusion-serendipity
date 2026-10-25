"""Render complete frozen S62 statistics without estimation or model calls."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def f(x):return f'{x:.3f}'
def interval(x):return '['+', '.join(map(f,x))+']'
def main():
    r=json.loads(Path('results/s62_notepad_qwen.json').read_text());assert r['pilot']=='S62' and not r['dry']
    p=r['metrics']['pair_bad'];d=p['paired_difference']
    lines=['# S62 — Partner notepad delivery','',f"**{r['verdict']}** under the frozen directional screen. Ten fresh games/five blocks,T10,r3–10,aqueduct/qwen-3.6-35b,zero game-outcome tuning. Shared minus self-only notepads in two-person teams. Fresh S29 generalization attempt; model, serving stack, API roles, seeds and date differ from S29, so this does not isolate a family effect. Roster, stage payoffs, task schedules and own-note persistence fixed.",'',
           'Both arms retain own notes. Shared additionally delivers partner notes with a truthful readability sentence. Delivery, expectations, memory volume and downstream histories are bundled; public actions remain visible in both arms. TYPE-Y approval pays author6/reviewer-2 and costs organization10; TYPE-X approval pays author6/reviewer1. No instruction to coordinate.','',
           '| Outcome | Self-only | Shared | Shared − self | Descriptive block-bootstrap 95% | Paired t95% | Upper sign p |','|---|---:|---:|---:|---|---|---:|']
    for k,m in r['metrics'].items():
        x=m['paired_difference'];lines.append(f"| {k} | {f(m['self']['mean'])} | {f(m['shared']['mean'])} | {f(x['mean'])} | {interval(x['ci95'])} | {interval(x['paired_t_ci95'])} | {x['exact_signflip_p_upper']:.5f} |")
    lines+=['','Primary denominator8/game,40/arm; X pair-directed approval denominator8/game too. All3125 ordered empirical bootstrap samples and32 inclusive sign flips per metric. Intervals are descriptive; degenerate bounds are not population-zero-risk or equivalence evidence.','',
            '| Seed | Self-only partner Y approvals /8 | Shared /8 | Difference |','|---|---:|---:|---:|']
    for seed in range(25200,25205):
        vals={g['condition']:round(g['primary']['pair_bad']*8) for g in r['games'] if g['seed']==seed}
        lines.append(f"| {seed} | {vals['self']} | {vals['shared']} | {(vals['shared']-vals['self'])/8:+.3f} |")
    lines+=['',f"Cached responses: {r['cached_responses']};exact JSON fences {r['exact_json_fenced_responses']};200 accepted decisions; invalid-attempt retries {r['invalid_attempt_retries']}. Nonempty notes: "+', '.join(f"{c} {r['notes'][c]['nonempty']}/100" for c in ['self','shared'])+'.','',
            f"Pair-internal bonus gate: {r['pair_score_gate_exact']} points/round. This gate is mechanically related to approvals, not independent corroboration. Pair total bonus equals internal bonus in both arms. These redundant archive fields and the bonus gate are not independent evidence of agreement.",'',
            'One neutral readiness response informed a pre-registration exact-JSON-fence allowance in both arms; no game-outcome tuning. All raw text retained. Scientific parsing otherwise preserves S29 duplicate-key/schema/boolean checks. Five exploratory blocks, many pilots without multiplicity adjustment, one new requested model, uncontrolled provider draws/shared-service interference and synthetic neutral work types limit transfer. Adverse approvals do not verify agreements or reciprocal intent. No tool definitions supplied in these API requests; served behavior/settings remain unattested. Client metadata do not attest provider execution.','',
            '![S62 notepad](../figures/s62_notepad.png)','',
            '[Design](../DESIGN_S62.md) · [Frozen result](s62_notepad_qwen.json) · [Independent reconstruction](../logs/s62_independent.json) · [Critic dispositions](../logs/s62_review_disposition.md).','Reproduce: `uv run python scripts/s62_release.py`; `uv run python scripts/s62_present.py`.']
    Path('results/s62_summary.md').write_text('\n'.join(lines)+'\n')
    fig,ax=plt.subplots(figsize=(7,4),layout='constrained')
    for seed in range(25200,25205):
        vals=[next(g['primary']['pair_bad'] for g in r['games'] if g['seed']==seed and g['condition']==c) for c in ['self','shared']]
        ax.plot([0,1],vals,'o-',alpha=.7,label=str(seed))
    ax.set(xticks=[0,1],xticklabels=['Self-only notes','Shared notes'],ylim=(-.04,1.04),ylabel='Partner TYPE-Y approval rate',title='S62 partner notepad: '+r['verdict'])
    ax.legend(fontsize=8);fig.savefig('figures/s62_notepad.png',dpi=160,metadata={'Software':'S62 frozen result renderer'});plt.close(fig)
    print('S62 summary and figure rendered')
if __name__=='__main__':main()
