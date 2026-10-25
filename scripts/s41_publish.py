"""Post-registration presentation only; never changes S41 data, estimators or rules."""
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s41_analyze import analyze
from scripts.s41_independent import verify
from scripts.s41_present import report_row


def replace_block(text,label,body):
    start=f'<!-- {label} start -->';end=f'<!-- {label} end -->'
    block=start+'\n'+body.strip()+'\n'+end
    if start in text:
        return re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda _:block,text,flags=re.S)
    return text.rstrip()+'\n\n'+block+'\n'


def publish():
    r=json.loads(Path('results/s41_ticksize.json').read_text())
    assert not r['dry'] and analyze('data/s41_ticksize')==r
    assert verify()['passed']
    m=r['metrics']['resource_payment'];s=m['paired_difference'];verdict=r['verdict']
    ci=f"[{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]"
    tc=f"[{s['paired_t_ci95'][0]:+.3f}, {s['paired_t_ci95'][1]:+.3f}]"
    headline=(f"Paid wage r3–10: fine **{m['fine']['mean']:.3f}**, coarse **{m['coarse']['mean']:.3f}**; "
              f"fine−coarse **{s['mean']:+.3f} {ci}**; paired t95% {tc}, "
              f"inclusive upper sign-flip **p={s['exact_signflip_p_upper']:.5f}**. Frozen **{verdict}** for the two-unit screen. "
              f"{sum(x>0 for x in m['seed_differences'])} of {r['n_seed_blocks']} block differences are positive; {sum(x==0 for x in m['seed_differences'])} tie.")
    dominant=max(range(len(m['seed_differences'])),key=lambda i:abs(m['seed_differences'][i]))
    seed=sorted({g['seed'] for g in r['games']})[dominant]
    cells={g['condition']:g['primary']['resource_payment'] for g in r['games'] if g['seed']==seed}
    headline+=(f" The largest block gap is {m['seed_differences'][dominant]:+.4f} (coarse {cells['coarse']:.4f}, fine {cells['fine']:.4f}).")
    scope=("Ten fresh games/five paired blocks; zero tuning or pooling. The half-unit grid changes feasible deviations, "
           "equilibria and numerical salience together. This does not isolate representation, competition or anchoring, "
           "and low wages do not verify coordination. The same payoff formula gives coarse pure-Nash wages18–20 and "
           "fine pure-Nash wages19–20. Bounds are descriptive; small-n/sign-calibration limits apply, and any degenerate "
           "interval is not population equivalence. Regret uses each arm's own feasible grid, so its contrast mixes the changed opportunity set with behavior. The local Codex wrapper requests low reasoning effort; served settings remain unattested.")
    link='[All outcomes and figure](results/s41_summary.md)'
    p=Path('REPORT.md');text=p.read_text().replace('Iteration 29','Iteration 30')
    if verdict=='HIT':text=text.replace('**No hits promoted.**','**One exploratory pilot hit promoted (S41).**')
    row=report_row(r)
    if re.search(r'^\| S41 ·',text,re.M):text=re.sub(r'^\| S41 ·.*$',lambda _:row,text,flags=re.M)
    else:text=re.sub(r'(^\| S43 ·.*$)',lambda mt:mt.group(1)+'\n'+row,text,flags=re.M)
    summary='**S41:** '+headline+' '+scope+' '+link+'.'
    if '<!-- S43 summary start -->' in text:
        block='<!-- S41 summary start -->\n'+summary+'\n<!-- S41 summary end -->'
        text=re.sub(r'<!-- S43 summary start -->.*?<!-- S43 summary end -->',lambda _:block,text,flags=re.S)
    else:text=replace_block(text,'S41 summary',summary)
    text=text.replace('Duopoly/control pure-Nash wages18–20;','Integer-wage duopoly/control pure-Nash wages18–20;S41 half-unit pure-Nash wages19–20;')
    text=re.sub(r'^\*\*Next:\*\*.*$', '**Next:** Fresh different-axis/new-world question after own/S41; S44/S39 proposals only, S32 unconfirmed and S30 unrun.',text,flags=re.M)
    p.write_text(text)
    p=Path('HITS.md');text=p.read_text().replace('after iteration 29','after iteration 30')
    if verdict=='HIT':text=text.replace('**No promoted hits after iteration 30.**','**One exploratory promoted hit after iteration 30 (S41).**')
    title=f"**S41: {'exploratory HIT' if verdict=='HIT' else 'unpromoted '+verdict}, wage tick size (own).**"
    body=title+'\n\n'+headline+'\n\n'+scope+'\n\nFive paired differences: '+str(m['seed_differences'])+'.\n'
    body+='Both siblings: action-grid specification and its equilibrium benchmark belong in matched level-screen references. This pilot alone supplies no collusion label. A suggested confirmation would independently repeat the frozen grid comparison with more blocks and another seller family; it is not run here.\n\n[Design](DESIGN_S41.md), '+link+'. Reproduce: `uv run python scripts/s41_release.py`.'
    p.write_text(replace_block(text,'S41 handoff',body))
    p=Path('REPORT_DETAILS.md');p.write_text(replace_block(p.read_text(),'S41 detail','## S41 — Wage granularity\n\n'+body+'\n\nScientific sources stay frozen; `scripts/s41_publish.py` is a later presentation-only generator. Prompt copies bind raw assembly rather than independently proving wording validity. Local-input metadata does not attest served identity or actual tool non-use.'))
    p=Path('README.md');text=p.read_text();start=text.index('\n\nS41 wage-tick pilot') if '\n\nS41 wage-tick pilot' in text else text.index('\n\n<!-- S41 reproduction start -->')
    if '\n\nS41 wage-tick pilot' in text:text=text[:start]
    cmds='\n'.join('uv run python '+cmd for cmd in ['scripts/s41_analyze.py','scripts/s41_independent.py','scripts/s41_exact_check.py','scripts/s41_present.py','scripts/s41_publish.py','scripts/s41_release.py','-m unittest scripts.test_s41'])
    body='S41 wage tick-size pilot completed. '+headline+'\n\n'+scope+'\n\n[Design](DESIGN_S41.md), '+link+'.\n\n```sh\n'+cmds+'\n```\n\n`uv run python scripts/s41_release.py --clean-clone` checks origin with the existing frozen venv,not a fresh dependency installation. Sources require their original checkout after shared-source changes. The external launch lock spans the sole execution; no interrupted resume. `s41_publish.py` was added after registration for presentation only and never changes scientific sources,data,thresholds or estimators.'
    p.write_text(replace_block(text,'S41 reproduction',body))
    print('S41 presentation docs regenerated from validated scientific result; '+verdict)

if __name__=='__main__':publish()
