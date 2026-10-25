"""Bounded editorial critics; no simulated-agent generation or scientific edits."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    names = ['README.md', 'REPORT.md', 'scripts/export_report.py',
             'logs/iteration61_exports.json', 'results/iteration58_reproduction.md']
    hashes = {n: hashlib.sha256(Path(n).read_bytes()).hexdigest() for n in names}
    prompt = (
        'Adversarial review of iteration61 documentation compression. No edits, subagents, '
        'installations, scientific calls, full portfolio replay or canonical test suite. '
        'Finish within four minutes. The README replaces a 106KB historical runbook with '
        'current reader/reproduction instructions and a pinned link to the full archive. '
        'Check command correctness, preservation of access to archived material, '
        'selected versus full replay scope, setup requirements, export reproducibility '
        'and scientific overclaims. The frozen science is unchanged. Report concrete '
        'high/medium issues, separate optional nits, and state the scope actually reviewed. '
        'Prior methodology/raw scientific reviews exist; this is a documentation review.\n')
    supplied = '\n\n'.join('FILE ' + n + '\n' + Path(n).read_text() for n in names)
    Path('logs/iteration61_review_prompt.md').write_text(prompt + supplied)

    def review(kind):
        out = Path('logs/iteration61_' + kind + '_review.md')
        if kind == 'codex':
            code = run_bounded([
                'codex', 'exec', '--skip-git-repo-check', '-s', 'read-only',
                '-C', str(Path.cwd()), '-m', 'gpt-6.1-sol',
                '-c', 'model_reasoning_effort=high', '-o', str(out.resolve()),
                prompt + 'Read logs/iteration61_review_prompt.md and actual relevant files.'],
                'logs/iteration61_codex_cli.log')
            scope = 'repository read-only; actual scope in critique'
        else:
            code = run_bounded(['claude', '-p', '--model', 'claude-opus-5-5',
                                '--output-format', 'text', '--tools', ''], out,
                               prompt + 'Supplied text only; no filesystem/execution attestation.\n' + supplied)
            scope = 'supplied text only'
        return {'critic': kind, 'exit': code, 'scope': scope}

    with ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(review, ['codex', 'opus']))
    record = {'reviews': records, 'source_hashes_at_launch': hashes,
              'sources_unchanged_during_review': all(
                  hashlib.sha256(Path(n).read_bytes()).hexdigest() == h for n, h in hashes.items())}
    Path('logs/iteration61_reviews.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record))


if __name__ == '__main__':
    main()
