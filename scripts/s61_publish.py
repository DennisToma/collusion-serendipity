"""Integrate S61 results without changing frozen scientific sources or prior rows."""
from datetime import datetime,timezone
import json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s61_replay import analyze,write
from scripts.s61_independent import verify
from scripts.s61_present import render,report_row
from scripts.s61_action_text import export

def block(path,start,end,content):
    p=Path(path);s=p.read_text();value=start+'\n'+content+'\n'+end
    if start in s:s=s[:s.index(start)]+value+s[s.index(end)+len(end):]
    else:s=s.rstrip()+'\n\n'+value+'\n'
    p.write_text(s)

def publish():
    r=analyze('data/s61_identity');write('results/s61_identity.json',r)
    write('logs/s61_independent.json',verify());render();write('logs/s61_action_text.json',export())
    d=r['contrast'];v=r['verdict'];m=r['mismatch_counts'];now=datetime.now(timezone.utc).isoformat()
    narrow=(f"**Latest — S61:** thirty fresh decisions on ten fixed S29 workplace histories/five source blocks. "
      f"Disagreement with an original-request anchor: renamed employees **{m['swap_mismatch']}/10**,identical-recorded-request repeat **{m['repeat_mismatch']}/10**; "
      f"excess **{d['mean']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}]**,paired t95% [{d['t95'][0]:+.3f}, {d['t95'][1]:+.3f}],upper sign-flip p={d['upper_signflip_p']:.5f}. **{v} for the frozen .25 excess-disagreement screen.**\n"
      "The swap covers system,user,all structured history,notes and output target;applying it twice restores every byte. One repeat per context is a noisy variability control;DUD is a prioritization label and does not establish invariance or equivalence. ID/alphabetical-order cues,call order and serving variability limit attribution;this neither establishes deterministic invariance nor identifies a mechanism for S29. "
      "[All results and limits](results/s61_summary.md) · [All returned text](results/s61_action_text.md).")
    if d['ci95'][0]<=.25<=d['ci95'][1]:narrow+=' The bootstrap bounds include +.25;the screen does not rule out that excess effect.'
    p=Path('REPORT.md');s=p.read_text();rows=[l for l in s.splitlines() if l.startswith('| S') and not l.startswith('| S61 ')]
    s=re.sub(r'Iteration \d+','Iteration 45',s,count=1)
    s=re.sub(r'<!-- S62 summary start -->.*?<!-- S62 summary end -->','<!-- S62 summary start --><!-- S62 summary end -->',s,flags=re.S)
    if '<!-- S61 summary start -->' not in s:
        at=s.index('| Pilot |');s=s[:at]+'<!-- S61 summary start -->\n'+narrow+'\n<!-- S61 summary end -->\n\n'+s[at:]
    else:s=re.sub(r'<!-- S61 summary start -->.*?<!-- S61 summary end -->','<!-- S61 summary start -->\n'+narrow+'\n<!-- S61 summary end -->',s,flags=re.S)
    if not any(l.startswith('| S61 ') for l in s.splitlines()):
        lines=s.splitlines();at=max(i for i,l in enumerate(lines) if l.startswith('| S'));lines.insert(at+1,report_row(r));s='\n'.join(lines)+'\n'
    s=re.sub(r'\*\*Next:\*\*[^\n]*','**Next:** fresh different-axis A/B/F pilot;S63,S57,S52,S49 remain queued. No sibling headline change.',s)
    assert [l for l in s.splitlines() if l.startswith('| S') and not l.startswith('| S61 ')]==rows
    if v=='HIT':s=s.replace('**No hits promoted.**','**One exploratory hit;confirmation required.**',1)
    p.write_text(s)
    details=narrow+'\n\nFive primary block values: '+str(d['block_values'])+'. All six summary intervals and30actions are in the linked results;no secondary promotion. Zero new games,tuning,pooling or held-out claim. Reused late contexts and exploratory multiplicity limit generalization. [Design](DESIGN_S61.md) · [Separate reconstruction](logs/s61_independent.json) · [Figure](figures/s61_identity.png).'
    block('REPORT_DETAILS.md','<!-- S61 details start -->','<!-- S61 details end -->',details)
    block('HITS.md','<!-- S61 handoff start -->','<!-- S61 handoff end -->','## S61 — '+('Exploratory symmetry HIT;confirmation needed' if v=='HIT' else 'Unpromoted employee-ID symmetry pilot')+'\n\n'+details+'\n\nFor both siblings:no agreement,intent or collusion label. '+('Suggested confirmation:fresh histories and multiple same-prompt repetitions,balanced positions and name sets. Run `uv run --frozen python scripts/s61_replay.py --analyze`.' if v=='HIT' else 'No confirmation trigger or sibling headline change.'))
    p=Path('HITS.md');s=p.read_text();s=re.sub(r'No promoted hits after iteration \d+','No promoted hits after iteration 45',s,count=1)
    if v=='HIT':s=s.replace('No promoted hits after iteration 45','One exploratory S61 HIT after iteration45;confirmation required',1)
    p.write_text(s)
    block('README.md','<!-- S61 reproduction start -->','<!-- S61 reproduction end -->',
      'S61(iteration45):consistent active-employee ID swap with identical-recorded-request repeat control. Ten fixed S29 histories/five source blocks;30fresh decisions,zero games/tuning. Primary is excess disagreement,not signed approval. [Design](DESIGN_S61.md) · [Results](results/s61_summary.md).\n\n```bash\nuv run --frozen python scripts/s61_replay.py --analyze\nuv run --frozen python scripts/s61_independent.py\nuv run --frozen python scripts/s61_present.py\nuv run --frozen python scripts/s61_action_text.py\nuv run --frozen python scripts/s61_release.py\nuv run --frozen python -m unittest scripts.test_s61\nuv run --frozen python scripts/s61_release.py --clean-clone\n```\n\nCompleted archives replay with scientific calls forbidden. Failed/interrupted pilots cannot resume. Origin-clone proof uses existing frozen venv,not fresh dependency install. Separate checker uses token splitting rather than the main substitution and reconstructs30decisions,30blockcells and6bootstrap/t/sign summaries.')
    description=f"Swap mismatch{m['swap_mismatch']}/10,repeat mismatch{m['repeat_mismatch']}/10;excess{d['mean']:+.3f}{d['ci95']};pairedt{d['t95']};upperp{d['upper_signflip_p']};{v}"
    p=Path('IDEAS.tsv');lines=p.read_text().splitlines()
    for i,line in enumerate(lines):
        fields=line.split('\t')
        if len(fields)>1 and fields[1]=='S61-proposal':
            fields[5]='activated-as-S61';fields[6]='Activated iteration45 with prospective identical-request repeat control;see S61';fields[7]='see-S61';lines[i]='\t'.join(fields)
        if len(fields)>1 and fields[1]=='S61':fields[5]='complete';fields[6]=description+';zero tuning';fields[7]=v+' (.25excess-disagreement screen)';lines[i]='\t'.join(fields)
    p.write_text('\n'.join(lines)+'\n')
    p=Path('EXPERIMENTS.tsv');s=p.read_text();reg=json.loads(Path('data/s61_identity/config.json').read_text())['registration']['commit'];s=s.replace('pending-registration-S61',reg)
    if '\tS61-result\t' not in s:s+=f'{now}\tS61-result\tID renaming causes excess review disagreement above identical-repeat variability\tFrozen involutive swap;30raw bindings and separate reconstruction\t10fixedS29histories/5blocks;30fresh decisions;zero newgames/tuning\t{description}\t'+('keep' if v=='HIT' else 'discard' if v=='DUD' else 'inconclusive')+' (excess-disagreement screen)\tpending-results-S61\n'
    p.write_text(s)
    return r

if __name__=='__main__':
    r=publish();print(json.dumps({k:r[k] for k in ['verdict','contrast','mismatch_counts','approval_counts']},indent=2))
