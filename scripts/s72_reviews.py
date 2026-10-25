"""Bounded independent critics; Opus is supplied-text-only."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=['design', 'final'])
    p.add_argument('--suffix', default='')
    args = p.parse_args()
    files = ['DESIGN_S72.md', 'scripts/s72_temporal.py', 'scripts/s72_independent.py',
        'scripts/s72_present.py', 'scripts/test_s72.py', 'scripts/s72_clone.py']
    instruction = ('Independent adversarial research review S72 only. No edits, scientific model calls or subagents. '
        'Review design, payoff comparator/aggregation, exact block statistics, provenance/release guards, and claim scope. '
        'Zero new games; posthoc audit of all original S29 primary outcomes. All seven measures reported, no HIT or hypothesis tests. '
        'Concrete correctness bugs versus acknowledged limits. Finish within four minutes and500words. ')
    if args.stage == 'final':
        files += ['results/s72_summary.md', 'results/s72_temporal.json', 'REPORT.md', 'logs/s72_independent.json']
        instruction += 'Independently reconstruct all window counts/individual excesses and intervals from original raw/game files; verify displayed claims. '
    else:
        instruction += 'Do not inspect or aggregate archived S29 outcomes before registration. Synthetic checks only. '
    def codex():
        out = Path(f'logs/s72_{args.stage}_codex{args.suffix}.md')
        rc = run_bounded(['codex', 'exec', '--skip-git-repo-check', '-s', 'read-only',
            '-C', str(Path.cwd()), '-m', 'gpt-6.1-sol', '-c', 'model_reasoning_effort=high',
            '-o', str(out.resolve()), instruction+'Read '+', '.join(files)],
            f'/var/tmp/s72_{args.stage}_codex{args.suffix}_cli.log')
        if rc or not out.exists():
            out.write_text(f'UNAVAILABLE:exit{rc}; CLI receipt retained in /var/tmp.\n')
        print(f'codex {args.stage} exit{rc}', flush=True)
        return dict(critic='codex', exit=rc)
    def opus():
        chosen = ['DESIGN_S72.md']
        if args.stage == 'final':
            chosen += ['results/s72_summary.md', 'logs/s72_independent.json']
        else:
            source = Path('scripts/s72_temporal.py').read_text()
            chosen += []
        context = '\n\n'.join('FILE '+n+'\n'+Path(n).read_text() for n in chosen)
        if args.stage == 'design':
            context += '\n'+source[source.index('def stage('):source.index('def analyze(')]
        out = Path(f'logs/s72_{args.stage}_opus{args.suffix}.md')
        rc = run_bounded(['claude', '-p', '--model', 'claude-opus-5-5', '--output-format', 'text', '--tools', ''],
            out, instruction+'Supplied text ONLY,no raw archive/source audit or bootstrap enumeration claimed. '+context)
        if rc:
            with out.open('a') as f:
                f.write(f'\nUNAVAILABLE: exit{rc}.\n')
        print(f'opus {args.stage} exit{rc}', flush=True)
        return dict(critic='opus_supplied_text', exit=rc)
    with ThreadPoolExecutor(max_workers=2) as pool:
        exits = list(pool.map(lambda f: f(), [codex, opus]))
    Path(f'logs/s72_{args.stage}_review_exits{args.suffix}.json').write_text(json.dumps(exits, indent=2)+'\n')


if __name__ == '__main__':
    main()
