"""Post-outcome presentation supplement; never changes frozen S53 science."""
import json
from pathlib import Path
import re


def refine():
    r=json.loads(Path('results/s53_payoffs.json').read_text());a=r['counts']['self'];b=r['counts']['shared']
    m=r['metrics']['pair_excess']['difference']
    row=(f"| S53 · E, static incentive audit | All10 original S29 games /5 blocks; no new calls. Totals over40 rounds/arm (self→shared): "
         f"Y approvals **{a['y_approvals']}→{b['y_approvals']}**; missed X **{a['missed_x']}→{b['missed_x']}**; mutual-Y **{a['mutual_y_rounds']}→{b['mutual_y_rounds']}**; "
         f"strict Pareto **{a['strict_pareto_rounds']}→{b['strict_pareto_rounds']}**; stage regret **{a['stage_regret']}→{b['stage_regret']}**; pair excess **{a['pair_excess']}→{b['pair_excess']}** bonus points. "
         "[All six bootstrap/t intervals](results/s53_summary.md). | **ODD / context-only**, post hoc |")
    detail=(f"**S53 (post hoc):** {b['mutual_y_rounds']}/{b['both_y']} shared and {a['mutual_y_rounds']}/{a['both_y']} self-only both-Y opportunities "
            f"had simultaneous mutual-Y approvals ({b['mutual_y_rounds']}/40 rounds per arm). "
            "These zero-width empirical bootstrap/t intervals are degenerate and do not establish population absence or equivalence. "
            "No missed X approvals occurred. In these data the regret and pair-excess contrasts are exactly two and four times S29’s original approval contrast; "
            "they add no independent finding. "
            f"The pair-excess contrast is {m['mean']:+.3f} bonus points/round, bootstrap95% [{m['ci95'][0]:+.3f}, {m['ci95'][1]:+.3f}], "
            f"paired t95% [{m['t95'][0]:+.3f}, {m['t95'][1]:+.3f}]. "
            "Strict Pareto improvement equals mutual-Y mechanically. Same-round results do not exclude mixed-status or delayed reciprocity, "
            "or both employees gaining across multiple rounds; they do not verify an agreement. Original S29 ODD is unchanged. "
            "[All six metrics, game cells and figure](results/s53_summary.md).")
    for name in ['REPORT.md','REPORT_DETAILS.md','HITS.md']:
        p=Path(name);txt=p.read_text()
        txt=re.sub(r'^\| S53 ·[^\n]*',row,txt,flags=re.M)
        txt=re.sub(r'\*\*S53 \(post hoc\):\*\*[^\n]*',detail,txt)
        if name=='REPORT.md':
            txt=re.sub(r'\*\*Next:\*\*[^\n]*','**Next:** Fresh different-axis pilot after E/S53; own/S54 opportunity-correlation idea and own/S52 framing remain proposed. S46/S39/S49 queued, S32 unconfirmed and S30 unrun. Avoid reusing the same ten focal histories without a new scientific reason.',txt)
        p.write_text(txt)
    print('S53 report presentation refined; frozen results, summary, figure and scientific sources unchanged.')


if __name__=='__main__':refine()
