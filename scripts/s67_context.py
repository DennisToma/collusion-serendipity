"""Post-review display of ALREADY registered both-Y opportunity counts; no new metric."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.s67_audit import checked_manifest
from scripts.s67_independent import verify


def render(check=False):
    checked_manifest()
    r = json.loads(Path('results/s67_incentives.json').read_text())
    verify(r)
    counts = r['counts']
    individual, pooled = counts['individual'], counts['pooled']
    text = ('# S67 opportunity denominator — post-review presentation supplement\n\n'
        'These opportunity counts were already exported by the frozen S67 analysis. '
        'This supplement adds no metric, hypothesis, scientific calls, exclusions or estimates.\n\n'
        '| Primary-window opportunity/event | Individual | Pooled |\n|---|---:|---:|\n'
        f"| Both-Y opportunity rounds / all primary rounds | {individual['both_y']}/40 | {pooled['both_y']}/40 |\n"
        f"| Strict stage-Nash-relative Pareto rounds | {individual['strict_pareto_rounds']} | {pooled['strict_pareto_rounds']} |\n\n"
        'Individual-arm strict Pareto improvement requires both submissions Y and both reviews approved. '
        'Its observed zero is therefore not forced by absent both-Y opportunities. '
        'The pooled-arm comparator already maximizes the pair total, making strict improvement impossible by definition. '
        'These statements have different logical status: neither verifies an agreement or rules out delayed reciprocity. '
        'Zero observed events do not establish a population absence.\n\n'
        '[Frozen eight-metric summary](s67_summary.md) · [Full frozen records](s67_incentives.json).\n')
    paragraph = (f"**S67 opportunity context:** Both arms have **{individual['both_y']}/40** both-Y rounds. "
        f"Individual-arm strict Pareto improvement occurs in **{individual['strict_pareto_rounds']}/{individual['both_y']}** such opportunities; "
        'pooled-arm strict improvement is impossible by its benchmark. '
        '[Opportunity counts and limits](results/s67_opportunity_context.md).')
    command = 'uv run --frozen python scripts/s67_context.py --check'
    readme_line = ('\nS67 post-review opportunity display: [counts and limits](results/s67_opportunity_context.md). '
        'Check with `'+command+'`. Core registered analysis and result bytes remain unchanged.\n')
    path = Path('results/s67_opportunity_context.md')
    if check:
        assert path.read_text() == text
    else:
        path.write_text(text)
    for filename in ['REPORT.md', 'REPORT_DETAILS.md', 'HITS.md']:
        p = Path(filename)
        if check:
            assert p.read_text().count(paragraph) == 1
        elif paragraph not in p.read_text():
            if filename == 'REPORT.md':
                source = p.read_text().replace('<!-- S67 summary end -->', '<!-- S67 summary end -->\n\n'+paragraph)
                p.write_text(source)
            else:
                with p.open('a') as f:
                    f.write('\n'+paragraph+'\n')
    readme = Path('README.md')
    if check:
        assert readme.read_text().count(readme_line) == 1
    elif command not in readme.read_text():
        with readme.open('a') as f:
            f.write(readme_line)
    print(json.dumps(dict(passed=True, existing_exported_counts_only=True,
                         individual_both_y=individual['both_y'], pooled_both_y=pooled['both_y']), indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    render(p.parse_args().check)
