"""Bounded independent review of fresh-install scope and final report claims."""
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
    files = ['scripts/iteration57_fresh_install.py', 'scripts/export_report.py',
             'scripts/iteration57_release.py', 'results/iteration57_reproduction.md',
             'REPORT.md', 'README.md', 'logs/iteration57_fresh_install.json', 'logs/iteration57_exports.json']
    files = [n for n in files if Path(n).exists()]
    prompt = ('Independent adversarial methodology and final-claim review for iteration57. '
              'No edits, subagents, package installations, rerun of the installation, or scientific model calls. '
              'Finish in four minutes. Review fresh-dependency isolation, pinned revision/source binding, '
              'artifact byte checks, canonical suite and selected replay scope, receipt failure handling, '
              'user reproduction instructions and report claims. Flag concrete remaining high/medium issues. '
              'Known limits: host OS/system libraries/fonts, uv and Python reused; no cross-platform claim; '
              'selected raw scientific replay only; historical narrow synthetic fixtures retained. '
              'Receipt is Git-committed consistency evidence, not external execution attestation. ')

    def codex():
        out = Path('logs/iteration57_codex' + args.suffix + '.md')
        rc = run_bounded(['codex', 'exec', '--skip-git-repo-check', '-s', 'read-only',
            '-C', str(Path.cwd()), '-m', 'gpt-6.1-sol', '-c', 'model_reasoning_effort=high',
            '-o', str(out.resolve()), prompt + 'Read ' + ', '.join(files)],
            '/var/tmp/iteration57_codex' + args.suffix + '_cli.log')
        if rc or not out.exists():
            out.write_text('UNAVAILABLE: exit' + str(rc) + '; CLI log in /var/tmp.\n')
        return {'critic': 'codex', 'exit': rc, 'scope': 'Read-only repository; actual executed checks described in review.'}

    def opus():
        pieces = []
        for name in files:
            if name == 'logs/iteration57_fresh_install.json':
                data = json.loads(Path(name).read_text())
                # Full stage output is available to the repository critic. The
                # supplied-text critic sees explicit metadata and scope only.
                data['commands'] = [{k: v for k, v in s.items() if k not in ['stdout', 'stderr']} for s in data['commands']]
                pieces.append('FILE ' + name + ' (stage output omitted)\n' + json.dumps(data, indent=2))
            else:
                pieces.append('FILE ' + name + '\n' + Path(name).read_text())
        context = '\n\n'.join(pieces)
        out = Path('logs/iteration57_opus' + args.suffix + '.md')
        rc = run_bounded(['claude', '-p', '--model', 'claude-opus-5-5', '--output-format', 'text', '--tools', ''],
                         out, prompt + 'Your scope is supplied text ONLY; no raw filesystem or visual inspection. ' + context)
        return {'critic': 'opus', 'exit': rc, 'scope': 'Supplied text only.'}

    with ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(lambda fn: fn(), [codex, opus]))
    Path('logs/iteration57_review_exits' + args.suffix + '.json').write_text(json.dumps(records, indent=2) + '\n')
    print(json.dumps(records))


if __name__ == '__main__':
    main()
