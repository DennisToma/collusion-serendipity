"""Deterministic guarded integration of frozen S68 results and reproduction links."""
import json,re,subprocess
from pathlib import Path
from scripts.s68_present import report_row
DOCS=['REPORT.md','REPORT_DETAILS.md','README.md','HITS.md']

def expected_documents(result,commit):
    r=result;s=r['contrast'];m=r['mismatch_counts'];v=r['verdict']
    old={name:subprocess.check_output(['git','show',f'{commit}:{name}'],text=True) for name in DOCS}
    summary=(f"Polarity disagreement **{m['polarity_mismatch']}/10**,identical-repeat **{m['repeat_mismatch']}/10**; "
             f"excess **{s['mean']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]**, "
             f"paired t95% [{s['t95'][0]:+.3f}, {s['t95'][1]:+.3f}], upper sign-flip p={s['upper_signflip_p']:.5f}. "
             f"**{v}** for the registered .25 excess-disagreement screen.")
    narrow='**Latest — S68:** '+summary+'\nThirty fresh choices on ten fixed workplace contexts/five reused blocks. Only the output instruction reverses boolean meaning;all choices are decoded before comparison. One repeat is a noisy variability control;no invariance or collusion claim. [All outcomes and limits](results/s68_summary.md).'
    report=old['REPORT.md'];report=re.sub(r'Iteration \d+','Iteration 51',report,count=1)
    report=re.sub(r'<!-- S69 summary start -->.*?<!-- S69 summary end -->','<!-- S69 summary start --><!-- S69 summary end -->',report,flags=re.S)
    at=report.index('| Pilot |');report=report[:at]+'<!-- S68 summary start -->\n'+narrow+'\n<!-- S68 summary end -->\n\n'+report[at:]
    lines=report.splitlines();at=max(i for i,line in enumerate(lines) if line.startswith('| S'));lines.insert(at+1,report_row(r));report='\n'.join(lines)+'\n'
    report=re.sub(r'\*\*Next:\*\*[^\n]*','**Next:** different-axis A/C/F or E;queued S70/S63/S57/S52/S49 require fresh designs. Pilots stop14:30UTC. No sibling headline change.',report)
    if v=='HIT':report=report.replace('**No hits promoted.**','**One exploratory hit;confirmation required.**',1)
    old_rows=[l for l in old['REPORT.md'].splitlines() if l.startswith('| S')]
    assert [l for l in report.splitlines() if l.startswith('| S')][:-1]==old_rows
    section='\n\n## S68 — Boolean output polarity\n\n'+summary+'\n\nFull input histories and incentives are fixed;returned booleans are decoded under the requested mapping. Not an omnibus invariance test or independent S29 replication. [All results,raw text and limits](results/s68_summary.md).\n'
    details=section+'\n[Design](DESIGN_S68.md) · [Separate reconstruction](logs/s68_independent.json) · [Figure](figures/s68_polarity.png).\n'
    readme=section+'\nReproduce with `uv run python scripts/s68_release.py`; focused checks: `uv run python -m unittest scripts.test_s68`; clean origin clone: `uv run python scripts/s68_release.py --clean-clone`. Existing frozen venv reused;no fresh-install claim.\n'
    handoff=section+('\nHIT: representation sensitivity only;requires a fresh registered confirmation with more blocks and repeat controls before changing any sibling claim.\n' if v=='HIT' else '\nUnpromoted;no confirmatory request or sibling headline change.\n')
    return dict(zip(DOCS,[report,old['REPORT_DETAILS.md']+details,old['README.md']+readme,old['HITS.md']+handoff])),old

def guard_documents(expected,old):
    for name in DOCS:
        if Path(name).read_text() not in [old[name],expected[name]]:
            raise RuntimeError('Intervening document change: '+name)


def publish():
    from scripts.s68_replay import analyze,write
    from scripts.s68_independent import verify
    from scripts.s68_present import render
    from scripts.s68_action_text import export
    r=analyze('data/s68_polarity');cfg=json.loads(Path('data/s68_polarity/config.json').read_text())
    expected,old=expected_documents(r,cfg['registration']['commit'])
    # Validate every document before any scientific/presentation/document write.
    guard_documents(expected,old)
    write('results/s68_polarity.json',r);write('logs/s68_independent.json',verify());render();write('logs/s68_action_text.json',export())
    for name,value in expected.items():Path(name).write_text(value)
    return r
if __name__=='__main__':
    r=publish();print(json.dumps({k:r[k] for k in ['verdict','contrast','approval_counts','mismatch_counts']},indent=2))
