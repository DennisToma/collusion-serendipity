"""Independent bounded critics for the complete-portfolio replay handoff."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--suffix', default='_design')
    args = parser.parse_args()
    names = ['scripts/portfolio_replay.py', 'scripts/iteration58_verify.py',
             'logs/iteration58_review_disposition.md', 'results/iteration58_reproduction.md',
             'logs/iteration58_portfolio_replay.json', 'REPORT.md']
    names = [n for n in names if Path(n).exists()]
    instruction = ('Adversarial independent review of iteration58 portfolio reproduction. '
        'No edits, subagents, scientific model calls, package installs, or full replay sweep. '
        'Finish within four minutes. Check exact coverage of all54 archived result objects, '
        'revision/source binding, failure-audit treatment, guard-before-import, scientific/archive '
        'preservation, result equality and independent-checker scope. Flag concrete high/medium '
        'bugs and overclaims. Existing validators differ in depth: this is deterministic rerun '
        'consistency, not proof of scientific validity, comprehensive raw provenance, new independent '
        'replication, network isolation, fresh installation, or external execution attestation. ')

    def codex():
        out = Path('logs/iteration58_codex' + args.suffix + '.md')
        code = run_bounded(['codex', 'exec', '--skip-git-repo-check', '-s', 'read-only',
            '-C', str(Path.cwd()), '-m', 'gpt-6.1-sol', '-c', 'model_reasoning_effort=high',
            '-o', str(out.resolve()), instruction + 'Read ' + ', '.join(names)],
            '/var/tmp/iteration58_codex' + args.suffix + '.log')
        if code or not out.exists():
            out.write_text('UNAVAILABLE: exit ' + str(code) + '; CLI log retained in /var/tmp.\n')
        return dict(critic='codex', exit=code, scope='Read-only repo; executed checks only as stated by critic')

    def opus():
        out = Path('logs/iteration58_opus' + args.suffix + '.md')
        pieces = []
        for name in names:
            content = Path(name).read_text()
            if name.endswith('portfolio_replay.json'):
                r = json.loads(content)
                # Explicitly omit checker detail/import-source maps in text view.
                r['records'] = [{k:v for k,v in x.items() if k not in ['independent_checker', 'imported_repo_sources']} for x in r['records']]
                content = json.dumps(r, indent=2)
            pieces.append('FILE ' + name + '\n' + content)
        code = run_bounded(['claude', '-p', '--model', 'claude-opus-5-5', '--output-format', 'text', '--tools', ''],
            out, instruction + 'Supplied text only; no raw filesystem inspection. Receipt checker details/import maps omitted.\n' + '\n\n'.join(pieces))
        return dict(critic='opus', exit=code, scope='Supplied text only; checker details/import maps omitted')

    with ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(lambda fn: fn(), [codex, opus]))
    Path('logs/iteration58_reviews' + args.suffix + '.json').write_text(json.dumps(records, indent=2) + '\n')
    print(json.dumps(records))


if __name__ == '__main__':
    main()
