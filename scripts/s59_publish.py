"""Presentation integration only; never changes frozen scientific sources."""
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import s59_replay as s
from scripts.s59_independent import verify
from scripts.s59_present import render,report_row
from scripts.s59_action_text import export


def replace_block(path,start,end,content):
    p=Path(path);text=p.read_text();block=start+'\n'+content+'\n'+end
    if start in text:text=text[:text.index(start)]+block+text[text.index(end)+len(end):]
    else:text=text.rstrip()+'\n\n'+block+'\n'
    p.write_text(text)


def publish():
    r=s.analyze('data/s59_history');s.write('results/s59_history.json',r)
    s.write('logs/s59_independent.json',verify());render();s.write('logs/s59_action_text.json',export())
    cfg=json.loads(Path('data/s59_history/config.json').read_text());reg=cfg['registration']['commit']
    now=datetime.now(timezone.utc).isoformat();d=r['contrast'];v=r['verdict'];row=report_row(r)
    a=r['approval_counts']['original'];b=r['approval_counts']['compact']
    narrow=(f"**Latest — S59:** twenty fresh decisions on ten S29 histories/five source blocks. "
            f"TYPE-Y partner approvals with original public history **{a}/10**,lossless compact table **{b}/10**; "
            f"original−compact **{d['mean']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}]**, "
            f"paired t95% [{d['t95'][0]:+.3f}, {d['t95'][1]:+.3f}],upper sign-flip p={d['upper_signflip_p']:.5f}. **{v} for the .25 reduction screen.**\n"
            "All nine historical fields survive exact roundtrip;only their JSON representation changes. Length,field repetition,shape and reading burden change together;lossless external reconstruction does not establish equal model comprehension. "
            "These reused histories supply no independent S29 replication or mechanism claim. "
            "[Full results and limits](results/s59_summary.md) · [All returned text](results/s59_action_text.md).")
    p=Path('REPORT.md');text=p.read_text();old_rows=[l for l in text.splitlines() if l.startswith('| S') and not l.startswith('| S59 ')]
    text=re.sub(r'Iteration \d+','Iteration 42',text,count=1)
    if '<!-- S59 summary start -->' in text:
        text=re.sub(r'<!-- S59 summary start -->.*?<!-- S59 summary end -->','<!-- S59 summary start -->\n'+narrow+'\n<!-- S59 summary end -->',text,flags=re.S)
    else:
        text=re.sub(r'<!-- S58 summary start -->.*?<!-- S58 summary end -->','<!-- S59 summary start -->\n'+narrow+'\n<!-- S59 summary end -->',text,count=1,flags=re.S)
        text+='\n<!-- S58 summary start --><!-- S58 summary end -->\n'
    if row not in text:
        lines=text.splitlines();last=max(i for i,line in enumerate(lines) if line.startswith('| S'));lines.insert(last+1,row);text='\n'.join(lines)+'\n'
    text=re.sub(r'\*\*Next:\*\*[^\n]*','**Next:** fresh different-axis B/F/A pilot;S57,S52,S49 remain queued. No sibling headline change.',text)
    assert [l for l in text.splitlines() if l.startswith('| S') and not l.startswith('| S59 ')]==old_rows
    if v=='HIT':text=text.replace('**No hits promoted.**','**One exploratory hit;confirmation needed.**',1)
    p.write_text(text)
    details=(narrow+'\n\nFive paired differences: '+str(d['block_values'])+f";upper sign-flip p={d['upper_signflip_p']:.5f},lower={d['lower_signflip_p']:.5f},two-sided={d['two_sided_signflip_p']:.5f}.\n\n"
             'Selection uses task statuses only,not actions or notes. Earlier outcomes motivated the question;these are reused late histories. '
             'Twenty fresh boolean reviews;zero new games/tuning. Five source blocks,descriptive small-n uncertainty,no held-out/multiplicity/equivalence claim. '
             'Only focal decisions rerun;no realized current payoff or partner adaptation. Source runtime equality,served identity,effective settings and tool non-use unattested. '
             '[Design](DESIGN_S59.md) · [Separate raw/statistical verification](logs/s59_independent.json) · [Figure](figures/s59_history.png). '
             'Reservation/receipt files fsynced,parent directories not fsynced;process-level persistence,not verified power-loss durability.')
    replace_block('REPORT_DETAILS.md','<!-- S59 details start -->','<!-- S59 details end -->',details)
    handoff=('## S59 — '+('Exploratory HIT: lossless public-history table' if v=='HIT' else 'Unpromoted lossless-history representation pilot')+'\n\n'+details+
             '\n\nFor both siblings:representation sensitivity can affect action observations without changing economic information. No agreement,intent or collusion claim. '+
             ('Suggested confirmation:fresh registered source blocks,matched sampling and a separate length/format control before interpreting a mechanism. Run `uv run --frozen python scripts/s59_replay.py --analyze`.' if v=='HIT' else 'No confirmation trigger or sibling headline change.'))
    replace_block('HITS.md','<!-- S59 handoff start -->','<!-- S59 handoff end -->',handoff)
    p=Path('HITS.md');text=p.read_text();text=re.sub(r'No promoted hits after iteration \d+', 'No promoted hits after iteration 42',text,count=1)
    if v=='HIT':text=text.replace('No promoted hits after iteration 42','One exploratory S59 HIT after iteration 42;confirmation required',1)
    p.write_text(text)
    reproduction=('S59(iteration42):lossless original-record versus column-table public history at ten observed S29 histories/five blocks;20fresh decisions,zero games/tuning.\n\n'
                  '[Design](DESIGN_S59.md) · [Full results](results/s59_summary.md) · [All returned text](results/s59_action_text.md).\n\n'
                  '```bash\nuv run --frozen python scripts/s59_replay.py --analyze\nuv run --frozen python scripts/s59_independent.py\nuv run --frozen python scripts/s59_present.py\nuv run --frozen python scripts/s59_action_text.py\nuv run --frozen python scripts/s59_release.py\nuv run --frozen python -m unittest scripts.test_s59\nuv run --frozen python scripts/s59_release.py --clean-clone\n```\n\n'
                  'Completed archives replay with scientific model calls forbidden;interrupted runs cannot resume. '
                  'The origin-clone proof reuses installed frozen dependencies,not a fresh installation. '
                  'Main replay binds raw requests,replies,source/runtime/registration/time/schedule records;'
                  'the separate checker rebuilds20raw approvals,lossless table encoding,15blockcells,3125bootstrap draws/32signflips per summary. '
                  'This integrator is outside the frozen scientific manifest;all older pilot rows are preserved.')
    replace_block('README.md','<!-- S59 reproduction start -->','<!-- S59 reproduction end -->',reproduction)
    description=f"Original{a}/10,compact{b}/10;original-minus-compact{d['mean']:+.3f}{d['ci95']};pairedt{d['t95']};upperp{d['upper_signflip_p']};{v}"
    p=Path('IDEAS.tsv');lines=p.read_text().splitlines()
    for i,line in enumerate(lines):
        fields=line.split('\t')
        if len(fields)>1 and fields[1]=='S59':fields[5]='complete';fields[6]=description+';zero tuning';fields[7]=v+' (.25directional reduction screen)';lines[i]='\t'.join(fields)
    p.write_text('\n'.join(lines)+'\n')
    p=Path('EXPERIMENTS.tsv');text=p.read_text().replace('pending-registration',reg)
    if '\tS59-result\t' not in text:text+=f'{now}\tS59-result\tLossless public-history table lowers adverse approvals\tFrozen exact roundtrip;full archive replay and separate reconstruction\t10observedS29histories/5blocks;20freshdecisions;zero newgames/tuning\t{description}\t'+('keep' if v=='HIT' else 'discard' if v=='DUD' else 'inconclusive')+' (directional screen)\tpending-results\n'
    p.write_text(text)
    return r

if __name__=='__main__':
    r=publish();print(json.dumps({k:r[k] for k in ['verdict','approval_counts','contrast']},indent=2))
