"""Integrate completed S55 results without altering prior scientific pilot rows."""
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import s55_replay as s
from scripts.s55_independent import verify
from scripts.s55_present import render,report_row
from scripts.s55_action_text import export


def replace_block(path,start,end,content):
    p=Path(path);text=p.read_text()
    block=start+'\n'+content+'\n'+end
    if start in text:text=text[:text.index(start)]+block+text[text.index(end)+len(end):]
    else:text=text.rstrip()+'\n\n'+block+'\n'
    p.write_text(text)


def publish():
    r=s.analyze('data/s55_visibility');s.write('results/s55_visibility.json',r)
    s.write('logs/s55_independent.json',verify());render();s.write('logs/s55_action_text.json',export())
    cfg=json.loads(Path('data/s55_visibility/config.json').read_text());reg=cfg['registration']['commit']
    now=datetime.now(timezone.utc).isoformat();d=r['contrast'];v=r['verdict'];row=report_row(r)
    if v=='HIT':raise AssertionError('HIT requires separate explicit reviewed handoff;scientific artifacts retained')
    visible=r['approval_counts']['visible'];masked=r['approval_counts']['masked']
    narrow=(f"**Latest — S55:** twenty fresh decisions on ten S29 histories/five source blocks. "
            f"TYPE-Y partner approvals with own status visible **{visible}/10**,masked **{masked}/10**; "
            f"visible−masked **{d['mean']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}]**, "
            f"paired t95% [{d['t95'][0]:+.3f}, {d['t95'][1]:+.3f}],upper sign-flip p={d['upper_signflip_p']:.5f}. **{v} for the .25 reduction screen;no promoted hit.**\n"
            "Only own current authoritative status entry is deleted. Block24483 ties,consistent with the baseline-floor risk noted before calls;the frozen HIT gate requires all five positive. Historical cues can still reveal own type;missing-entry cues also change. "
            "Own type may affect beliefs about the partner's incoming review,so no role-confusion mechanism is identified. "
            "[Full results and limits](results/s55_summary.md) · [All returned text](results/s55_action_text.md).")
    p=Path('REPORT.md');text=p.read_text();old_rows=[l for l in text.splitlines() if l.startswith('| S') and not l.startswith('| S55 ')]
    text=re.sub(r'Iteration \d+','Iteration 40',text,count=1)
    if '<!-- S56 summary start -->' in text:
        text=re.sub(r'<!-- S56 summary start -->.*?<!-- S56 summary end -->','<!-- S55 summary start -->\n'+narrow+'\n<!-- S55 summary end -->',text,flags=re.S)
    elif '<!-- S55 summary start -->' in text:
        text=re.sub(r'<!-- S55 summary start -->.*?<!-- S55 summary end -->','<!-- S55 summary start -->\n'+narrow+'\n<!-- S55 summary end -->',text,flags=re.S)
    if row not in text:
        lines=text.splitlines();last=max(i for i,line in enumerate(lines) if line.startswith('| S'));lines.insert(last+1,row);text='\n'.join(lines)+'\n'
    text=re.sub(r'\*\*Next:\*\*[^\n]*','**Next:** fresh different-axis B/C/F pilot;S57,S52,S49,S46,S39 remain queued. No sibling headline change.',text)
    assert [l for l in text.splitlines() if l.startswith('| S') and not l.startswith('| S55 ')]==old_rows
    p.write_text(text)
    details=(narrow+'\n\nFive paired differences: '+str(d['block_values'])+f";upper sign-flip p={d['upper_signflip_p']:.5f},lower={d['lower_signflip_p']:.5f},two-sided={d['two_sided_signflip_p']:.5f}.\n\n"
             'Same outcome-independent source selection as S51,not an independent S29 replication. Twenty fresh boolean reviews;zero new games or tuning. Visible is the exact source prompt;archived actions are context only. '+
             'Five blocks,descriptive small-n uncertainty,no held-out/multiplicity/equivalence claim. Source runtime equality,served identity,effective settings and tool non-use unattested. '+
             '[Design](DESIGN_S55.md) · [Separate raw/statistical verification](logs/s55_independent.json) · [Figure](figures/s55_visibility.png). '+
             'Reservation and receipt files were fsynced;parent directories were not fsynced. This supplies process-level persistence,not verified power-loss durability.')
    replace_block('REPORT_DETAILS.md','<!-- S55 details start -->','<!-- S55 details end -->',details)
    replace_block('HITS.md','<!-- S55 handoff start -->','<!-- S55 handoff end -->',
                  '## S55 — Unpromoted own-status visibility pilot\n\n'+details+'\n\nFor both siblings:no confirmation trigger or headline change. Any model/role-confusion explanation needs a fresh design with partner responses and own-type inference controlled.')
    p=Path('HITS.md');p.write_text(re.sub(r'No promoted hits after iteration \d+', 'No promoted hits after iteration 40',p.read_text(),count=1))
    reproduction=('S55(iteration40):own current task-status visible versus deleted at ten observed S29 histories/five blocks;20fresh decisions,zero games/tuning.\n\n'
                  '[Design](DESIGN_S55.md) · [Full results](results/s55_summary.md) · [All returned text](results/s55_action_text.md).\n\n'
                  '```bash\nuv run --frozen python scripts/s55_replay.py --analyze\nuv run --frozen python scripts/s55_independent.py\nuv run --frozen python scripts/s55_present.py\nuv run --frozen python scripts/s55_action_text.py\nuv run --frozen python scripts/s55_release.py\nuv run --frozen python -m unittest scripts.test_s55\nuv run --frozen python scripts/s55_release.py --clean-clone\n```\n\n'
                  'Completed archives replay with scientific model calls forbidden;interrupted runs cannot resume. '
                  'The origin-clone proof reuses the installed frozen venv,not a fresh dependency installation. '
                  'The primary replay binds all requests,raw replies,source/runtime/registration/time/schedule records;'
                  'the separate checker rebuilds raw approvals,prompt deletion,15blockcells,all3125bootstrap draws/32signflips. '
                  'This documentation integrator is outside the frozen scientific manifest;all earlier pilot rows are preserved.')
    replace_block('README.md','<!-- S55 reproduction start -->','<!-- S55 reproduction end -->',reproduction)
    p=Path('README.md');text=p.read_text().replace('checks generated report prose against frozen JSON and preserves all prior rows.', 'checked the iteration39 generated prose against frozen JSON. Run that historical presentation checker at commit `0db3286`;later iterations extend the front log. Scientific S56 reproduction above remains current.')
    p.write_text(text)
    description=f"Visible{visible}/10,masked{masked}/10;visible-minus-masked{d['mean']:+.3f}{d['ci95']};pairedt{d['t95']};upperp{d['upper_signflip_p']};{v}"
    p=Path('IDEAS.tsv');lines=p.read_text().splitlines()
    for i,line in enumerate(lines):
        fields=line.split('\t')
        if len(fields)>1 and fields[1]=='S55':fields[5]='complete';fields[6]=description+';zero tuning';fields[7]=v+' (.25directional reduction screen)';lines[i]='\t'.join(fields)
    p.write_text('\n'.join(lines)+'\n')
    p=Path('EXPERIMENTS.tsv');text=p.read_text().replace('pending-registration',reg)
    if '\tS55-result\t' not in text:text+=f'{now}\tS55-result\tOwn-current-status deletion lowers adverse approvals\tFrozen own-key deletion;full archive replay and separate reconstruction\t10observedS29histories/5blocks;20freshdecisions;zero newgames/tuning\t{description}\t'+('discard' if v=='DUD' else 'inconclusive')+' (directional screen)\tpending-results\n'
    p.write_text(text)
    return r

if __name__=='__main__':
    r=publish();print(json.dumps({k:r[k] for k in ['verdict','approval_counts','contrast']},indent=2))
