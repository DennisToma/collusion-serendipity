"""Update the research handoff from the verified S53 result, without new estimates."""
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s53_payoffs import release


def publish():
    release()
    r=json.loads(Path('results/s53_payoffs.json').read_text());c=r['counts'];d=r['metrics']['mutual_y_rounds']['difference']
    now=datetime.now(timezone.utc).isoformat();reg=json.loads(Path('data/s53_registration_receipt.json').read_text())['commit']
    desc=(f"Mutual-Y rounds self{c['self']['mutual_y_rounds']}/40,shared{c['shared']['mutual_y_rounds']}/40;"
          f"shared-minus-self{d['mean']:+.3f}{d['ci95']};pairedt{d['t95']};"
          f"Y approvals self{c['self']['y_approvals']}/40,shared{c['shared']['y_approvals']}/40Y opportunities;")
    row=(f"| S53 · E, static incentive audit | All10 S29 games /5 original blocks; zero new calls. "
         f"Simultaneous mutual-Y rounds self **{c['self']['mutual_y_rounds']}/40**, shared **{c['shared']['mutual_y_rounds']}/40**; "
         f"round-rate difference **{d['mean']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}]**. | **ODD / context-only**, post hoc |")
    detail=(f"**S53 (post hoc):** {c['shared']['mutual_y_edges']}/{c['shared']['y_approvals']} shared-arm adverse approval edges "
            f"occur in simultaneous mutual-Y rounds; self {c['self']['mutual_y_edges']}/{c['self']['y_approvals']}. "
            f"Both arms have {c['self']['both_y']}/40 both-Y opportunity rounds. "
            f"Shared-minus-self pair bonus above one-shot Nash is {r['metrics']['pair_excess']['difference']['mean']:+.3f} per round "
            f"[{r['metrics']['pair_excess']['difference']['ci95'][0]:+.3f}, {r['metrics']['pair_excess']['difference']['ci95'][1]:+.3f}]. "
            "The Pareto-improvement count equals mutual-Y count mechanically; six metrics contain only three independent quantities. "
            "Simultaneity is not agreement or reciprocal intent; other edges allow mixed-status or delayed reciprocity. "
            "Nash-relative gains are static comparisons, not long-run effects. Original S29 ODD remains unchanged. "
            "[All six metrics, all game cells and figure](results/s53_summary.md).")
    p=Path('REPORT.md');txt=p.read_text();txt=re.sub(r'Iteration \d+','Iteration 37',txt,count=1)
    if row not in txt:
        lines=txt.splitlines();last=max(i for i,x in enumerate(lines) if x.startswith('| S'));lines.insert(last+1,row);txt='\n'.join(lines)+'\n'
    if '**S53 (post hoc):**' not in txt:txt+='\n'+detail+'\n'
    txt=re.sub(r'\*\*Next:\*\*[^\n]*','**Next:** Fresh different-axis pilot after E/S53; own/S52 remains proposed, S46/S39/S49 queued, S32 unconfirmed and S30 unrun. Avoid further reuse of the same ten focal histories without a new scientific reason.',txt)
    p.write_text(txt)
    for filename,title,body in [
        ('REPORT_DETAILS.md','## Iteration37 — S53 static incentive and simultaneous-reciprocity audit',row+'\n\n'+detail+'\n\n'+desc+'\n\nAll six metrics were frozen before this decomposition,after S29 and replay outcomes were known. This is a post-hoc diagnostic with no hypothesis threshold,p-values,HIT promotion or independent replication. Regret fixes incoming actions; Nash-relative excess changes both actions. Original full200-key replay and separate original checker pass. New separate same-author implementation checks200rawbindings/80rounds/60gamecells/18bootstrap+t intervals/16stage profiles/32unilateral deviations. Independent critics and their exact scope are recorded in logs/s53_review_disposition.md.'),
        ('HITS.md','### S53 — unpromoted static-incentive context (post hoc)',desc+'\n\n**ODD/context-only by design;no HIT screen or promotion.** '+detail+' Both siblings: distinguish own-stage regret,joint bonus,and strict Pareto improvements from verified coordination. Suggested follow-up only if prioritized: fresh prospectively registered game blocks with mechanically different author/reviewer payoffs;not run. Reproduce:`uv run --frozen python scripts/s53_payoffs.py --release`.'),
        ('README.md','S53 (iteration37): static incentive audit of all S29 workplace games.', '[Design](DESIGN_S53.md),[all six metrics,ten game cells and figure](results/s53_summary.md),[all80 round records and stage profiles](results/s53_payoffs.json). POST-HOC,zero new games or scientific calls;does not alter original S29 results or verify agreements.\n\n```bash\nuv run --frozen python scripts/s53_payoffs.py --release\nuv run --frozen python scripts/s53_independent.py\nuv run --frozen python -m unittest scripts.test_s53\n```\n\nThe release checks the required inputs and both generations of analysis code against the pushed registration commit,reruns all200 original raw bindings,and separately reconstructs80rounds/60gamecells/18bootstrap+t intervals. A second release stages and compares byte-identical JSON/summary/figure with the scientific llm.chat entry point patched to raise;this is not OS network/process isolation. Clean-clone reproduction may reuse the installed frozen venv,which is not a fresh dependency installation.')]:
        p=Path(filename);txt=p.read_text()
        if title not in txt:p.write_text(txt+'\n'+title+'\n\n'+body+'\n')
    p=Path('IDEAS.tsv');lines=p.read_text().splitlines()
    for i,line in enumerate(lines):
        fields=line.split('\t')
        if len(fields)>1 and fields[1]=='S53':fields[5:]=['complete',desc+'All6metrics;zero newgames/calls/tuning','ODD (context-only;posthoc;no promotion screen)'];lines[i]='\t'.join(fields)
    p.write_text('\n'.join(lines)+'\n')
    p=Path('EXPERIMENTS.tsv');txt=p.read_text().replace('pending-s53-registration',reg)
    if '\tS53-result\t' not in txt:txt+=f'{now}\tS53-result\tStatic incentive and simultaneous mutual-Y decomposition of S29\tFixed posthoc all-ten-game audit;original labels unchanged\t10originalgames/5blocks;80primary rounds;zero newgames/calls/tuning\t{desc}Allsix block-bootstrap+t intervals in results/s53_payoffs.json\tinconclusive (ODD/context-only;no promotion screen)\tpending-s53-result\n'
    p.write_text(txt)
    p=Path('STATUS.md');old=p.read_text();log=old[old.index('## Log'):]
    top=f'''# STATUS

## Current state ({now}; Phase2, iteration37 VERIFYING)
- S53(E):posthoc static-incentive audit of all10 S29games/5blocks;zero newgames/scientificcalls/tuning.
- Mutual-Y rounds self{c['self']['mutual_y_rounds']}/40,shared{c['shared']['mutual_y_rounds']}/40;difference{d['mean']:+.3f}{d['ci95']}.
- Shared adverse edges in mutual-Y rounds:{c['shared']['mutual_y_edges']}/{c['shared']['y_approvals']};self{c['self']['mutual_y_edges']}/{c['self']['y_approvals']}.
- Pair excess over stage Nash shared-minus-self:{r['metrics']['pair_excess']['difference']['mean']:+.3f}/round;static comparison only.
- Pareto=mutual-Y identically;6metrics contain3independent quantities,no independent supporting evidence.
- All200original raw bindings/full source replay and separate80rounds/60cells/18bootstrap+t checks PASS.
- Fixed ODD/context-only;original S29ODD unchanged;no HIT,agreement or long-run claim.
- Both initial methodology critics exit0;patch critics recorded separately;final critics next.
- Registration{reg[:7]} pushed/observed before new decomposition;source/input hashes checked.
- Next:finalcritics,postanalysis canonical suite,byte-identical release,origin-clone proof.
- Science queue:fresh different axis;own/S52proposed,S46/S39/S49queued,S32unconfirmed,S30unrun.
- Risks:posthoc selection,n5,one family,synthetic types,draws/shared service,source runtime unattested.

'''
    p.write_text(top+log+f'\n- {now}: S53 complete;{desc}All six fixed diagnostic metrics reported with descriptive block-bootstrap/t intervals. Full original200-key replay and separate200bindings/80rounds/60gamecells/18summaries/16stageprofiles/32deviations PASS. Staged source-checked release verified before publication. No newgames/scientificcalls,tuning,HIT,pooling,labels,sourceS29edits,siblingwrites or DIRECTION deviation. Final independent critics,canonical suite,figure/release and fresh origin clone next.\n')
    print(desc)


if __name__=='__main__':publish()
