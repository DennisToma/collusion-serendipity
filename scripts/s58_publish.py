"""Presentation-only integration; preserve every older pilot row."""
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import s58_replay as s
from scripts.s58_independent import verify
from scripts.s58_present import render,report_row
from scripts.s58_action_text import export


def replace_block(path,start,end,content):
    p=Path(path);text=p.read_text();block=start+'\n'+content+'\n'+end
    if start in text:text=text[:text.index(start)]+block+text[text.index(end)+len(end):]
    else:text=text.rstrip()+'\n\n'+block+'\n'
    p.write_text(text)


def publish():
    r=s.analyze('data/s58_history');s.write('results/s58_history.json',r)
    s.write('logs/s58_independent.json',verify());render();s.write('logs/s58_action_text.json',export())
    cfg=json.loads(Path('data/s58_history/config.json').read_text());reg=cfg['registration']['commit']
    now=datetime.now(timezone.utc).isoformat();d=r['contrast'];v=r['verdict'];row=report_row(r)
    if v=='HIT':raise AssertionError('HIT requires separate reviewed handoff;scientific artifacts retained')
    retained=r['approval_counts']['retain'];erased=r['approval_counts']['erase']
    narrow=(f"**Latest — S58:** twenty fresh decisions on ten S29 histories/five source blocks. "
            f"TYPE-Y partner approvals with public history retained **{retained}/10**,erased **{erased}/10**; "
            f"retain−erase **{d['mean']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}]**, "
            f"paired t95% [{d['t95'][0]:+.3f}, {d['t95'][1]:+.3f}],upper sign-flip p={d['upper_signflip_p']:.5f}. **{v} for the .25 reduction screen;no promoted hit.**\n"
            "Block24483 ties;the frozen HIT gate requires all five positive,so positive bootstrap/t bounds alone do not promote it. Only the completed-public-round list becomes empty;current round,statuses and notes remain. Notes retain historical information. "
            "Missing-history cues,length and past actions/rewards change together;no reciprocity or reputation mechanism is identified. "
            "[Full results and limits](results/s58_summary.md) · [All returned text](results/s58_action_text.md).")
    p=Path('REPORT.md');text=p.read_text();old_rows=[l for l in text.splitlines() if l.startswith('| S') and not l.startswith('| S58 ')]
    text=re.sub(r'Iteration \d+','Iteration 41',text,count=1)
    if '<!-- S58 summary start -->' in text:
        text=re.sub(r'<!-- S58 summary start -->.*?<!-- S58 summary end -->','<!-- S58 summary start -->\n'+narrow+'\n<!-- S58 summary end -->',text,flags=re.S)
    else:
        text=re.sub(r'<!-- S55 summary start -->.*?<!-- S55 summary end -->','<!-- S58 summary start -->\n'+narrow+'\n<!-- S58 summary end -->',text,flags=re.S)
    if row not in text:
        lines=text.splitlines();last=max(i for i,line in enumerate(lines) if line.startswith('| S'));lines.insert(last+1,row);text='\n'.join(lines)+'\n'
    text=re.sub(r'\*\*Next:\*\*[^\n]*','**Next:** fresh different-axis B/F/own pilot;S57,S59,S52,S49 remain queued. No sibling headline change.',text)
    assert [l for l in text.splitlines() if l.startswith('| S') and not l.startswith('| S58 ')]==old_rows
    p.write_text(text)
    details=(narrow+'\n\nFive paired differences: '+str(d['block_values'])+f";upper sign-flip p={d['upper_signflip_p']:.5f},lower={d['lower_signflip_p']:.5f},two-sided={d['two_sided_signflip_p']:.5f}.\n\n"
             'Selection uses task statuses only,not actions or notes. Earlier replay results motivated the question;the same histories are reused,not independent S29 replication. '
             'Twenty fresh boolean reviews;zero new games/tuning. Five source blocks,descriptive small-n uncertainty,no held-out/multiplicity/equivalence claim. '
             'Only focal decisions rerun;no realized current payoff or partner adaptation. Source runtime equality,served identity,effective settings and tool non-use unattested. '
             '[Design](DESIGN_S58.md) · [Separate raw/statistical verification](logs/s58_independent.json) · [Figure](figures/s58_history.png). '
             'Reservation/receipt files fsynced,parent directories not fsynced;process-level persistence,not verified power-loss durability.')
    replace_block('REPORT_DETAILS.md','<!-- S58 details start -->','<!-- S58 details end -->',details)
    replace_block('HITS.md','<!-- S58 handoff start -->','<!-- S58 handoff end -->',
                  '## S58 — Unpromoted public-history erasure pilot\n\n'+details+'\n\nFor both siblings:no confirmation trigger or headline change. No channel-formation or reciprocity claim follows from one late focal decision.')
    p=Path('HITS.md');p.write_text(re.sub(r'No promoted hits after iteration \d+', 'No promoted hits after iteration 41',p.read_text(),count=1))
    reproduction=('S58(iteration41):completed public history retained versus erased at ten observed S29 histories/five blocks;20fresh decisions,zero games/tuning.\n\n'
                  '[Design](DESIGN_S58.md) · [Full results](results/s58_summary.md) · [All returned text](results/s58_action_text.md).\n\n'
                  '```bash\nuv run --frozen python scripts/s58_replay.py --analyze\nuv run --frozen python scripts/s58_independent.py\nuv run --frozen python scripts/s58_present.py\nuv run --frozen python scripts/s58_action_text.py\nuv run --frozen python scripts/s58_release.py\nuv run --frozen python -m unittest scripts.test_s58\nuv run --frozen python scripts/s58_release.py --clean-clone\n```\n\n'
                  'Completed archives replay with scientific model calls forbidden;interrupted runs cannot resume. '
                  'The origin-clone proof reuses installed frozen dependencies,not a fresh installation. '
                  'Main replay binds all raw requests,replies,source/runtime/registration/time/schedule records;'
                  'the separate checker rebuilds20raw approvals,exact public-history erasure,15blockcells,3125bootstrap draws/32signflips per summary. '
                  'This integrator is outside the frozen scientific manifest;all older pilot rows are preserved.')
    replace_block('README.md','<!-- S58 reproduction start -->','<!-- S58 reproduction end -->',reproduction)
    description=f"Retain{retained}/10,erase{erased}/10;retain-minus-erase{d['mean']:+.3f}{d['ci95']};pairedt{d['t95']};upperp{d['upper_signflip_p']};{v}"
    p=Path('IDEAS.tsv');lines=p.read_text().splitlines()
    for i,line in enumerate(lines):
        fields=line.split('\t')
        if len(fields)>1 and fields[1]=='S58':fields[5]='complete';fields[6]=description+';zero tuning';fields[7]=v+' (.25directional reduction screen)';lines[i]='\t'.join(fields)
    p.write_text('\n'.join(lines)+'\n')
    p=Path('EXPERIMENTS.tsv');text=p.read_text().replace('pending-registration',reg)
    if '\tS58-result\t' not in text:text+=f'{now}\tS58-result\tPublic-history erasure lowers adverse approvals\tFrozen completed-public-rounds list erasure;full archive replay and separate reconstruction\t10observedS29histories/5blocks;20freshdecisions;zero newgames/tuning\t{description}\t'+('discard' if v=='DUD' else 'inconclusive')+' (directional screen)\tpending-results\n'
    p.write_text(text)
    return r

if __name__=='__main__':
    r=publish();print(json.dumps({k:r[k] for k in ['verdict','approval_counts','contrast']},indent=2))
