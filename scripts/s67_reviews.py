"""Bounded independent Codex/Opus reviews; failures retain their actual scope."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['design', 'final'])
    args = parser.parse_args()
    instruction = ('Independent adversarial S67 review, no edits or scientific model calls. '
        'Posthoc descriptive stage-incentive audit of ALL original S65 individual/pooled games. '
        'Original UNRESOLVED/ODD remains unchanged; no promotion, replication or mechanism inference. '
        'Check settlement arithmetic, unilateral versus Nash/pair-optimal comparators, metric identities, '
        'units, source freeze/replay, exact block statistics and claim limits. '
        'Report concrete correctness issues by severity; separate acknowledged limits. '
        'Finish in 400words and within four minutes if possible. ')
    files = ['DESIGN_S67.md', 'scripts/s67_audit.py', 'scripts/s67_independent.py',
             'scripts/s67_present.py', 'scripts/test_s67.py']
    if args.stage == 'final':
        files += ['results/s67_summary.md', 'logs/s67_independent.json', 'REPORT.md']
        instruction += ('For Codex: independently reconstruct the raw game totals and all24 '
                        'bootstrap/t summaries from results/s67_incentives.json and data/s65_bonus_pooling. '
                        'For Opus: supplied-text/code review only; do not claim raw execution or bootstrap enumeration. ')

    def codex():
        out = Path(f'logs/s67_{args.stage}_codex.md')
        cli = Path(f'logs/s67_{args.stage}_codex_cli.log')
        rc = run_bounded(['codex', 'exec', '--skip-git-repo-check', '-s', 'read-only',
            '-C', str(Path.cwd()), '-m', 'gpt-6.1-sol', '-c', 'model_reasoning_effort=high',
            '-o', str(out.resolve()), instruction+'Read '+', '.join(files)+
            ', DESIGN_S65.md, sim/bonus_pooling.py, scripts/s65_analyze.py.'], cli)
        if rc or not out.exists():
            out.write_text(f'UNAVAILABLE: Codex exit{rc}; retained {cli}.\n')
        print(f'Codex {args.stage} exit{rc}', flush=True)

    def opus():
        out = Path(f'logs/s67_{args.stage}_opus.md')
        context = '\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files if f != 'REPORT.md')
        rc = run_bounded(['claude', '-p', '--model', 'claude-opus-5-5',
                          '--output-format', 'text', '--tools', ''], out,
                         instruction+'Use only supplied text, no execution claims.\n'+context)
        if rc:
            with out.open('a') as f:
                f.write(f'\nUNAVAILABLE: Opus exit{rc}.\n')
        print(f'Opus {args.stage} exit{rc}', flush=True)

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda fn: fn(), [codex, opus]))


if __name__ == '__main__':
    main()
