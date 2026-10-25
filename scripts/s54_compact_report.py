"""Post-outcome presentation only: preserve every pilot row and archive full prose."""
import hashlib
import json
from pathlib import Path
import re


def main():
    report=Path('REPORT.md').read_text();detail=Path('REPORT_DETAILS.md').read_text()
    result_path=Path('results/s54_opportunities.json')
    r=json.loads(result_path.read_text())
    snapshot=json.loads(Path('logs/s54_archive_snapshot.json').read_text())
    assert hashlib.sha256(result_path.read_bytes()).hexdigest()==snapshot['scientific_result_sha256']
    rows=[line for line in report.splitlines() if line.startswith('|')]
    assert rows[0].startswith('| Pilot |') and rows[-1].startswith('| S54 ·')
    archive_start='<!-- Iteration38 front-report prose archive start -->'
    archive_end='<!-- Iteration38 front-report prose archive end -->'
    if archive_start not in detail:
        body=report.split(rows[-1],1)[1].strip()
        detail+='\n\n'+archive_start+'\n## Front-report caveats preserved during iteration38 compaction\n\nThe following is the full former front-report prose,archived verbatim when the\nfront page was shortened. Methods/results above remain the substantive record;\nprospective queue statements below are a historical snapshot.\n\n'+body+'\n'+archive_end+'\n'
    else:assert detail.count(archive_start)==detail.count(archive_end)==1
    p=r['metrics']['pair_bad'];d=p['paired_difference']
    counts={c:sum(round(g['primary']['pair_bad']*8) for g in r['games'] if g['condition']==c) for c in ['alternating','synchronized']}
    assert r['verdict']=='DUD' and all(x<0 for x in p['seed_differences'])
    bounds=lambda vals:'['+', '.join(f'{v:+.3f}' for v in vals)+']'
    metadata=report.splitlines()[2]
    lines=['# Serendipity log — Beyond Words','',metadata,'',
      '<!-- S54 summary start -->',
      f"**Latest — S54:** ten fresh workplace games/five blocks. TYPE-Y approvals: complementary **{counts['alternating']}/40**, synchronized **{counts['synchronized']}/40**; synchronized−control **{d['mean']:+.3f} {bounds(d['ci95'])}** (descriptive bootstrap95%), pairedt95% {bounds(d['paired_t_ci95'])}, upper sign p={d['exact_signflip_p_upper']:.5f}. **DUD for the predicted increase.** All five differences are negative;the reverse pattern stays descriptive and unpromoted.",
      'Both arms have shared notes and balanced marginal task counts. Joint status composition,own status and downstream histories change together. This does not verify coordination or replicate S29’s channel comparison. “Alternating” in frozen files means complementary employee types within a round,not alternation over time. [All outcomes and figure](results/s54_summary.md) · [Every adverse returned text](results/s54_action_text.md).',
      '<!-- S54 summary end -->','',*rows,'',
      'Five paired blocks are the resampling unit unless stated otherwise. Bootstrap bounds are descriptive;small-n t/sign/bootstrap summaries may disagree or degenerate. No multiplicity correction,held-out validation or equivalence claim. Zero observed approvals do not establish population absence. DUD/ODD/HIT are frozen exploratory prioritization screens. Actions,notes,rewards and explanations do not verify an agreement,intent,profitable collusion or mechanism. Provider identity/settings and tool non-use remain unattested.','',
      'S29 remains ODD because one block ties;its bootstrap-positive bound alone does not meet its screen. S53 reuses those outcomes:regret and pair-excess are rescalings,and its six metrics add no independent replication. Earlier operational,wording,timing,provenance and interpretation limits remain in the linked details.','',
      '[All methods,per-pilot caveats,uncertainty and figures](REPORT_DETAILS.md) · [Reproduction](README.md) · [Unpromoted handoffs](HITS.md).','',
      '**Next:** fresh different-axis A/B pilot;own/S55,S52,S49,S46,S39 remain queued. No sibling headline change.','']
    # Preserve the established front-report anchors required by older frozen
    # presentation tools,without retaining their duplicated long prose here.
    markers=sorted(set(re.findall(r'<!-- (S\d+) summary start -->',report)) - {'S54'},key=lambda x:int(x[1:]))
    lines+=['<!-- Historical presentation anchors;full prose archived in REPORT_DETAILS.md. -->']
    lines += [f'<!-- {key} summary start --><!-- {key} summary end -->' for key in markers]
    compact='\n'.join(lines)+'\n'
    assert [line for line in compact.splitlines() if line.startswith('|')]==rows
    for key in ['S54',*markers]:
        assert compact.count(f'<!-- {key} summary start -->')==compact.count(f'<!-- {key} summary end -->')==1
    Path('REPORT_DETAILS.md').write_text(detail);Path('REPORT.md').write_text(compact)
    print(json.dumps(dict(passed=True,pilot_rows_unchanged=len(rows)-2,former_prose_preserved=True,report_lines=len(lines),scientific_result_unchanged=True)))

if __name__=='__main__':main()
