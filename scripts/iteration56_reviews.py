"""Bounded export/claim critics requested by CLAUDE.md; no scientific calls."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--suffix', default='')
    args = parser.parse_args()
    instruction = ('Independent adversarial review of iteration56 reader exports. No edits, subagents or scientific model calls. '
        'Finish within four minutes, report concrete high/medium correctness issues. '
        'This is a presentation-only export of frozen explorer evidence, not a new experiment. '
        'Check claim scope, interval labels, original-table preservation, HTML/PDF coverage, source binding, '
        'freshness, reproducibility and user commands. Known limits: selected/posthoc brief, five paired blocks, '
        'no full-portfolio raw reproduction, no collusion/equivalence claim. '
        'Verify the current reporting wrapper with uv run --frozen python scripts/export_report.py --check if useful. '
        'Final fixes, if present: portable relative PDF URI annotations are rewritten and checked; figure marker/count guarded; '
        'complete table rows checked in order; pinned link targets checked in Git; brief reconstructed through historical products(); '
        'plain check explicitly labels saved coverage, full extraction requires check-pdf. '
        'Closure fixes guard every editorial replacement, verify sources before the render receipt, '
        'preserve the historical probe receipt by exact Git hash while explicitly not rerunning its probes, '
        'check PDF link targets against pinned HTML, and derive the replay count. '
        'Repeat/relocation receipts are actual executed checks; no broader environment claim. Verify actual code, not this summary. ')
    def codex():
        out = Path('logs/iteration56_codex' + args.suffix + '.md')
        names = ['scripts/export_report.py', 'README.md', 'REPORT.md', 'logs/iteration56_exports.json',
                 'results/iteration54_brief.md', 'scripts/iteration55_claims.py']
        rc = run_bounded(['codex', 'exec', '--skip-git-repo-check', '-s', 'read-only', '-C', str(Path.cwd()),
            '-m', 'gpt-6.1-sol', '-c', 'model_reasoning_effort=high', '-o', str(out.resolve()),
            instruction + 'Read ' + ', '.join(names)], '/var/tmp/iteration56_codex' + args.suffix + '_cli.log')
        if rc or not out.exists():
            out.write_text(f'UNAVAILABLE: exit{rc}; CLI log under /var/tmp.\n')
        return {'critic': 'codex', 'exit': rc, 'scope': 'Repository read-only review; see actual review for checks executed.'}
    def opus():
        names = ['scripts/export_report.py', 'results/iteration54_brief.md', 'logs/iteration56_exports.json',
                 'logs/iteration56_repeat_build.json', 'logs/iteration56_relocation.json', 'logs/iteration56_negative_checks.json']
        context = '\n\n'.join('FILE ' + n + '\n' + Path(n).read_text() for n in names)
        out = Path('logs/iteration56_opus' + args.suffix + '.md')
        rc = run_bounded(['claude', '-p', '--model', 'claude-opus-5-5', '--output-format', 'text', '--tools', ''],
            out, instruction + 'Your scope is supplied text ONLY; do not claim filesystem, raw-cache or PDF visual inspection. ' + context)
        return {'critic': 'opus', 'exit': rc, 'scope': 'Supplied text only; no raw/source filesystem or visual audit.'}
    with ThreadPoolExecutor(max_workers=2) as pool:
        result = list(pool.map(lambda fn: fn(), [codex, opus]))
    Path('logs/iteration56_review_exits' + args.suffix + '.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
