"""Generate/check S64-managed report text from frozen numbers and Git baseline."""
import argparse
import json
from pathlib import Path
import re
import subprocess

def managed():
    r=json.loads(Path('results/s64_memory_retention.json').read_text());assert r['pilot']=='S64' and not r['dry']
    p=r['metrics']['pair_bad'];d=p['paired_difference']
    counts={c:round(p[c]['mean']*40) for c in ['reset','persistent']}
    ci='['+', '.join(f'{x:+.3f}' for x in d['ci95'])+']'
    tc='['+', '.join(f'{x:+.3f}' for x in d['paired_t_ci95'])+']'
    summary=(f"**Latest — S64:** ten fresh workplace games/five paired blocks. TYPE-Y approvals with full memory **{counts['persistent']}/40**, per-decision memory reset **{counts['reset']}/40**; persistent−reset **{d['mean']:+.3f} {ci}**, paired t95% {tc}, upper sign-flip p={d['exact_signflip_p_upper']:.5f}. **{r['verdict']} for the frozen .25 directional screen.**\n"
        'Reset removes completed public rounds and both notepads; current round, types, roster, system and stage economics fixed. Memory volume, length, notes and histories change together; no pure reputation, reciprocity, agreement or collusion mechanism follows. Fresh trajectories; zero pooling, reused contexts or outcome-based tuning. [All outcomes and limits](results/s64_summary.md) · [All adverse returned text](results/s64_action_text.md).')
    if d['ci95'][0]<=.25<=d['ci95'][1]:summary+=' The bootstrap bounds include +.25; the screen does not rule out that effect.'
    row=(f"| S64 · F, memory retention | 10 fresh games /5 blocks. TYPE-Y approvals persistent **{counts['persistent']}/40**, reset **{counts['reset']}/40**; persistent−reset **{d['mean']:+.3f} {ci}**. | **{r['verdict']}** for .25 directional screen |")
    block='<!-- S64 summary start -->\n'+summary+'\n<!-- S64 summary end -->'
    details='<!-- S64 details start -->\n## S64 — Fresh memory-retention pilot\n\n'+summary+'\n\n'+f"Five block differences {p['seed_differences']}; lower sign p={d['exact_signflip_p_lower']:.5f}, two-sided={d['exact_signflip_p_two_sided']:.5f}. All five metrics and bootstrap/t intervals in linked results. Pair-bonus gate is mechanically related to approvals. No held-out, multiplicity correction, equivalence or independent S29 replication claim. Sole{r['cached_responses']} returned/200 accepted decisions; retries{r['invalid_attempt_retries']}. CLI roles flattened; served identity/settings/tool non-use unattested. [Design](DESIGN_S64.md), [independent reconstruction](logs/s64_independent.json), [release](logs/s64_release.json)."+'\n<!-- S64 details end -->'
    handoff='<!-- S64 handoff start -->\n## S64 — Fresh memory-retention pilot\n\n'+summary+'\n\nFor both siblings: no confirmation trigger or headline change unless a frozen HIT is promoted after critic review. No agreement, intent or collusion label.\n<!-- S64 handoff end -->'
    if r['verdict']=='HIT':
        handoff=handoff.replace('no confirmation trigger or headline change unless a frozen HIT is promoted after critic review.', 'HIT under the frozen exploratory screen. Confirm on fresh preregistered seeds and a locked analysis before headline use. Run: `uv run python scripts/s64_release.py`. Q2.2 should check whether memory affects action/text separation; Q1.4 should distinguish persistent history from channel labels.')
    readme='<!-- S64 reproduction start -->\nS64 fresh memory retention: `uv run python scripts/s64_release.py` validates the complete raw archive, independent statistics, rendered figure/summary, all adverse text and published S64 blocks without model calls. Full document validation targets the S64 results revision; from later publication revisions, checkout that results commit first. `uv run python -m unittest scripts.test_s64` runs focused checks. [Design](DESIGN_S64.md) · [Results](results/s64_summary.md).\n<!-- S64 reproduction end -->'
    return {'REPORT.md':block,'REPORT_DETAILS.md':details,'HITS.md':handoff,'README.md':readme},row

def apply(check=False):
    blocks,row=managed()
    cfg=json.loads(Path('data/s64_memory_retention/config.json').read_text())
    head=cfg['registration_commit']
    expected={}
    for name,block in blocks.items():
        old=subprocess.check_output(['git','show',f'{head}:{name}'],text=True)
        if name=='REPORT.md':
            old=re.sub(r'<!-- S\d+ summary start -->.*?<!-- S\d+ summary end -->','',old,flags=re.S)
            old=old.replace('Iteration 45','Iteration 46')
            if json.loads(Path('results/s64_memory_retention.json').read_text())['verdict']=='HIT':old=old.replace('**No hits promoted.**','**S64 passes the exploratory HIT screen.**')
            anchor=old.index('| Pilot |')
            old=old[:anchor]+block+'\n\n'+old[anchor:]
            rows=old.splitlines();last=max(i for i,x in enumerate(rows) if x.startswith('| S'))
            rows.insert(last+1,row);old='\n'.join(rows)+'\n'
        else:
            if name=='HITS.md':
                old=old.replace('after iteration 45','after iteration 46')
                if json.loads(Path('results/s64_memory_retention.json').read_text())['verdict']=='HIT':old=old.replace('**No promoted hits after iteration 46.**','**S64 passes the exploratory HIT screen in iteration 46.**')
            old=old.rstrip()+'\n\n'+block+'\n'
        expected[name]=old
    prior=[x for x in subprocess.check_output(['git','show',f'{head}:REPORT.md'],text=True).splitlines() if x.startswith('| S')]
    if check:
        report=Path('REPORT.md').read_text()
        assert all(report.count(x)==1 for x in prior),'Older pilot row changed'
        assert sum(x.startswith('| S64 ') for x in report.splitlines())==1,'Extra or missing S64 pilot row'
        for name,text in expected.items():assert Path(name).read_text()==text,'S64 prose mismatch: '+name
    else:
        for name,text in expected.items():Path(name).write_text(text)
        return apply(True)
    return dict(passed=True,managed_blocks=4,older_pilot_rows=len(prior),new_pilot_rows=1,complete_documents_exact=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args();print(json.dumps(apply(args.check),indent=2))
