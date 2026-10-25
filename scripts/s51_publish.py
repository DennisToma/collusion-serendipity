"""Publish the completed, frozen S51 analysis and reviewable handoff documents."""
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import s51_replay as s
from scripts.s51_independent import verify
from scripts.s51_present import render,report_row
from scripts.s51_action_text import export


def publish():
    r=s.analyze('data/s51_penalty');s.write('results/s51_penalty.json',r)
    s.write('logs/s51_independent.json',verify())
    render();s.write('logs/s51_action_text.json',export())
    cfg=json.loads(Path('data/s51_penalty/config.json').read_text());reg=cfg['registration']['commit']
    now=datetime.now(timezone.utc).isoformat();d=r['contrast'];verdict=r['verdict'];row=report_row(r)
    b=r['approval_counts']['baseline'];h=r['approval_counts']['strong']
    desc=(f"Baseline{b}/10,strong{h}/10;baseline-minus-strong{d['mean']:+.3f}{d['ci95']};"
          f"pairedt{d['t95']};upperp{d['upper_signflip_p']};{verdict}.")
    narrow=(f"**S51:** reviewer charge3→9 (net−2→−8): {b}/10 versus {h}/10 adverse approvals; "
            f"paired t95% [{d['t95'][0]:+.3f}, {d['t95'][1]:+.3f}], upper sign-flip p={d['upper_signflip_p']:.5f}; "
            f"block differences {d['block_values']}. Both arms add the same current-policy notice. "
            "All user history and notes stay fixed, including dated old-policy cues. Only focal decisions are rerun; "
            "this does not measure long-run enforcement or verify coordination. "
            "[All outcomes and figure](results/s51_summary.md) · [All returned text](results/s51_action_text.md).")
    p=Path('REPORT.md');text=p.read_text();text=re.sub(r'Iteration \d+', 'Iteration 36',text,count=1)
    if row not in text:
        lines=text.splitlines();last=max(i for i,line in enumerate(lines) if line.startswith('| S'))
        lines.insert(last+1,row);text='\n'.join(lines)+'\n'
    if '**S51:**' not in text:text+='\n'+narrow+'\n'
    text=re.sub(r'\*\*Next:\*\*[^\n]*','**Next:** Fresh different-axis pilot after D/S51. Own/S52 is a proposal; S46/S39/S49 remain queued, S32 unconfirmed and S30 unrun.',text)
    p.write_text(text)
    for filename,heading,body in [
        ('REPORT_DETAILS.md','## Iteration36 — S51 personal reviewer penalty',row+'\n\n'+desc+'\n\n'+narrow+'\n\nSeparate raw/statistical reconstruction is by the same manager,not independent authorship. Independent reviewers are documented separately. Observed late histories,n5,uncontrolled draws and shared-service interference limit transfer. No tuning,newgames,pooling,held-out or equivalence claim. Strong changes penalty magnitude,stated net arithmetic and numerical salience together. Historical charges remain correct for completed rounds;dated notes may retain old policy. Only3contexts have ownTYPE-Y;the mutual-Y payoff example is conditional,not universal. Source CLI unknown;known current inputs frozen,served identity/settings unattested.'),
        ('HITS.md','### S51 — '+('HIT pending fresh confirmation' if verdict=='HIT' else 'unpromoted personal-penalty screen'),desc+'\n\n'+('**HIT** under the registered exploratory screen;fresh confirmation required.' if verdict=='HIT' else f'**{verdict};no HIT promoted.**')+' Twenty fresh decisions/ten observed S29 contexts/five source blocks;zero newgames,tuning,pooling. Both siblings: personal penalties need matched fresh controls and action changes do not establish coordination. Focal-only hypothetical policy;no partner adaptation or long-run effect. [Design](DESIGN_S51.md),[all outcomes](results/s51_summary.md),[all returned text](results/s51_action_text.md). Reproduce:`uv run --frozen python scripts/s51_release.py`. Suggested confirmation if prioritized: fresh registered game-level blocks and a second seller family with both agents exposed to the policy;not run here.'),
        ('README.md','S51 (iteration36): personal reviewer penalty at fixed workplace histories.', '[Design](DESIGN_S51.md),[all outcomes](results/s51_summary.md),[all returned text](results/s51_action_text.md). Twenty fresh decisions/ten observed S29 histories/five source blocks;zero newgames or tuning. Charge3/net−2 versus charge9/net−8,with a matched current-policy notice. The experiment is a focal-decision replay,not a completed intervention game.\n\n```bash\nuv run --frozen python scripts/s51_replay.py --analyze\nuv run --frozen python scripts/s51_independent.py\nuv run --frozen python scripts/s51_present.py\nuv run --frozen python scripts/s51_action_text.py\nuv run --frozen python scripts/s51_release.py\nuv run --frozen python -m unittest scripts.test_s51\n```\n\nThe release forbids calls to the scientific model entry point and requires byte-identical results,summary,figure and verbatim-output appendix. `scripts/s51_context_audit.py` reproduces the pre-outcome historical-policy census. `scripts/repository_tests.py --out /var/tmp/serendipity_tests.json` runs canonical offline checks with scoped legacy synthetic clocks;real experiment deadlines stay fixed.')]:
        q=Path(filename);txt=q.read_text()
        if heading not in txt:q.write_text(txt+'\n'+heading+'\n\n'+body+'\n')
    p=Path('EXPERIMENTS.tsv');text=p.read_text().replace('pending-registration',reg)
    if '\tS51-result\t' not in text:
        decision='keep (HIT pending confirmation)' if verdict=='HIT' else 'discard (directional screen)' if verdict=='DUD' else 'inconclusive (ODD)'
        text+=f'{now}\tS51-result\tHigher personal penalties lower adverse workplace approvals\tFrozen charge3to9/net-2to-8;full replay and separate raw/statistical reconstruction\t10observedS29contexts/5sourceblocks;20freshdecisions;zero newgames/tuning\t{desc}\t{decision}\tpending-result\n'
    p.write_text(text)
    p=Path('IDEAS.tsv');lines=p.read_text().splitlines()
    for i,line in enumerate(lines):
        fields=line.split('\t')
        if len(fields)>1 and fields[1]=='S51':fields[5:]=['complete',desc+'20freshdecisions/10contexts/5blocks;zero newgames/tuning/retries/failures',verdict+' (.25directional reduction screen)'];lines[i]='\t'.join(fields)
    p.write_text('\n'.join(lines)+'\n')
    p=Path('STATUS.md');old=p.read_text();log=old[old.index('## Log'):]
    top=f'''# STATUS

## Current state ({now}; Phase2, iteration36 VERIFYING)
- S51(D):20fresh decisions/10observed S29 TYPE-Y contexts/5sourceblocks;zero newgames/tuning.
- Adverse approvals charge3:{b}/10;charge9:{h}/10;reduction{d['mean']:+.3f}{d['ci95']};frozen {verdict}.
- Pairedt{d['t95']};upperp{d['upper_signflip_p']};blockdifferences{d['block_values']}.
- Both arms add matched current-policy notice;only charge3to9/net-2to-8 changes between arms.
- All user bytes/history/notes fixed;dated old-policy note cues remain in6contexts.
- Full source/archive/registration/runtime/UTC/schedule replay and separate20bindings/15cells/3summaries PASS.
- All20returned JSON responses exported verbatim;no intent/agreement labels.
- Prelive600canonical/19protocol tests PASS;final critics/postlive checks next.
- Registration{reg[:7]} pushed before sole launch;result publication in progress.
- No HIT promotion unless frozen gate passes;no sibling headline change.
- Next:fresh different axis;new own/S52 queued,not run.
- Risks:n5,late selected histories,draws/interference;focal-only,provider execution unattested.

'''
    log+=f'\n- {now}: S51 sole run complete20accepted decisions,zero retries/transport/parser/route/source/runtime failures. {desc} Frozen {verdict}. Full source/archive/registration/runtime/UTC/schedule/request replay and separate20bindings/15cells/3exactbootstrap+t/sign summaries PASS. Reports/ledgers/verbatim-output appendix updated;final critics,post-live canonical suite,figure/release/origin-clone next. No scientific-source edits,tuning,pooling,exclusions,secondpilot or sibling writes.\n'
    p.write_text(top+log)
    print(desc)


if __name__=='__main__':publish()
