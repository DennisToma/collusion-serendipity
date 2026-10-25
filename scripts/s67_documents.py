"""Publish/check the S67 handoff from verified results, preserving prior pilot rows."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.s67_audit import checked_manifest, release


def content():
    r = json.loads(Path('results/s67_incentives.json').read_text())
    c, m = r['counts'], r['metrics']
    d = m['stage_regret']['difference']
    row = (f"| S67 · E, settlement-aware incentive audit | All10 S65 games /5 original blocks;zero new calls. "
        f"Costly Y approvals individual **{c['individual']['costly_y_approvals']:g}**, pooled **{c['pooled']['costly_y_approvals']:g}**; "
        f"pooled Y rejections forgoing +2 **{c['pooled']['profitable_y_rejections']:g}/40**. "
        f"Stage-regret difference **{d['mean']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}]** final bonus points/round; "
        "[all8 metrics](results/s67_summary.md). | **ODD / context-only**, post hoc |")
    latest = (f"**Latest — S67 (post hoc):** Of S65's Y approvals, individual settlement has "
        f"**{c['individual']['costly_y_approvals']:g}** that each cost the reviewer2 at that stage; "
        f"pooling has **{c['pooled']['y_approvals']:g}** that each add2. The pooled arm also rejects "
        f"**{c['pooled']['profitable_y_rejections']:g}/40** profitable Y opportunities. "
        "This accounting audit adds no replication or collusion label; S65 stays UNRESOLVED/ODD. "
        "[All eight measures, uncertainty, stage profiles and caveats](results/s67_summary.md).")
    desc = (f"Stage regret individual{c['individual']['stage_regret']:g}/pooled{c['pooled']['stage_regret']:g};"
        f"pooled-minus-individual{d['mean']:+.3f}{d['ci95']};pairedt{d['t95']};"
        f"pair shortfall{c['individual']['pair_shortfall']:g}/{c['pooled']['pair_shortfall']:g};"
        f"orgloss{c['individual']['organization_loss']:g}/{c['pooled']['organization_loss']:g}")
    return r, row, latest, desc


def check():
    manifest = checked_manifest()
    r, row, latest, desc = content()
    report = Path('REPORT.md').read_text()
    assert report.count(row) == report.count(latest) == 1
    assert all(report.count(old) == 1 for old in manifest['older_report_rows'])
    rows = [x for x in report.splitlines() if x.startswith('| S')]
    assert len(rows) == len(manifest['older_report_rows'])+1
    assert 'Iteration 48' in report
    for p, heading in [('REPORT_DETAILS.md', '## Iteration48 — S67 settlement-aware incentive audit'),
                       ('HITS.md', '## S67 — Unpromoted settlement-aware accounting'),
                       ('README.md', '## S67: archived S65 stage-incentive accounting')]:
        assert Path(p).read_text().count(heading) == 1
        assert 'results/s67_summary.md' in Path(p).read_text()
    return dict(passed=True, prior_pilot_rows_preserved=len(manifest['older_report_rows']),
                current_pilot_rows=len(rows), generated_claims_checked=True)


def publish():
    release()
    r, row, latest, desc = content()
    report_path = Path('REPORT.md')
    report = report_path.read_text()
    if '| S67 ·' not in report:
        report = re.sub(r'Iteration \d+', 'Iteration 48', report, count=1)
        report = re.sub(r'<!-- S65 summary start -->.*?<!-- S65 summary end -->',
            '<!-- S65 summary start --><!-- S65 summary end -->', report, flags=re.S)
        report = report.replace('| Pilot |', '<!-- S67 summary start -->\n'+latest+'\n<!-- S67 summary end -->\n\n| Pilot |', 1)
        lines = report.splitlines()
        last = max(i for i, line in enumerate(lines) if line.startswith('| S'))
        lines.insert(last+1, row)
        report = '\n'.join(lines)+'\n'
        report = re.sub(r'\*\*Next:\*\*[^\n]*',
            '**Next:** different-axis pilot; own S66,S63,S57,S52,S49 remain queued. No promoted HIT or sibling headline change.', report)
        report_path.write_text(report)
    for p, heading, body in [
        ('REPORT_DETAILS.md', '## Iteration48 — S67 settlement-aware incentive audit',
         latest+'\n\n'+row+'\n\n'+desc+'\n\nAll32 settlement/status/action profiles and64 unilateral deviations are enumerated; '
         'all80 primary rounds and200 raw action/note/reason bindings are retained. Eight related measures are all reported. '
         'The regret contrast uses different settlement-specific incentive schedules and cannot rank optimization quality. '
         'Five-block descriptive bootstrap/t intervals; no new test, promotion, replication or mechanism claim. '
         '[Design](DESIGN_S67.md) · [Full audit](results/s67_summary.md) · [Figure](figures/s67_incentives.png).'),
        ('HITS.md', '## S67 — Unpromoted settlement-aware accounting',
         latest+'\n\n'+desc+'\n\nFor both siblings: organization-harming approvals need incentive-aware interpretation. '
         'Pooled Y approvals are individually profitable; individual Y approvals cost the reviewer at that stage. '
         'Neither verifies agreement. These are related posthoc bookkeeping measures on S65, not independent confirmation. '
         'S65 UNRESOLVED/ODD unchanged; no confirmation request or headline change. '
         'Reproduce `uv run --frozen python scripts/s67_audit.py release`.'),
        ('README.md', '## S67: archived S65 stage-incentive accounting',
         '[Design](DESIGN_S67.md) · [All eight measures and limits](results/s67_summary.md) · [Figure](figures/s67_incentives.png).\n\n'
         'POST-HOC descriptive audit; zero new seller/auditor trajectories. Uses all ten original S65 games. '
         'The release validates pushed registration/source hashes, preserves older scientific artifacts, replays S65, '
         'and verifies separate raw/statistical reconstruction before publishing deterministic outputs. '
         'The actual replay llm.chat transport is patched; this is not OS network/process isolation. '
         'The existing pinned environment is reused; no fresh-install claim.\n\n'
         '```bash\nuv run --frozen python scripts/s67_audit.py release\n'
         'uv run --frozen python scripts/s67_independent.py\n'
         'uv run --frozen python -m unittest scripts.test_s67\n'
         'uv run --frozen python scripts/s67_integrity.py\n'
         'uv run --frozen python scripts/s67_documents.py --check\n```\n\n'
         '`scripts/s67_clone.py` additionally reproduces a pushed result revision in a fresh full-history origin clone. '
         'The freeze/register-remote commands are one-time registration steps and must not be repeated.')]:
        path = Path(p)
        if heading not in path.read_text():
            with path.open('a') as f:
                f.write('\n'+heading+'\n\n'+body+'\n')
    print(json.dumps(check(), indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    if args.check:
        print(json.dumps(check(), indent=2))
    else:
        publish()
