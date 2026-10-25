"""Bounded independent S41 critics, including honest quota-failure records."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');args=p.parse_args()
    files=['DESIGN_S41.md','sim/ticksize.py','scripts/s41_runtime.py','scripts/s41_analyze.py','scripts/test_s41.py','sim/common.py','sim/advisor.py','scripts/s41_launch.py','scripts/s41_independent.py','sim/resource_cache.py','llm.py','scripts/s41_present.py']
    instruction=('Independent adversarial research review, S41 ONLY. No edits or live model calls. Check economics, truth/simultaneity, causal scope, cache/replay integrity, frozen configuration, statistic arithmetic, failure handling and screening rule. '
                 'Report concrete remaining bugs with severity and remedies; separate acknowledged limitations. Give a final review within500 words and finish promptly. ')
    if args.stage=='final':
        files+=['REPORT.md','results/s41_ticksize.json','results/s41_summary.md','logs/s41_independent.json','data/s41_ticksize/config.json','scripts/s41_independent.py','logs/s41_launch_preflight.json']
        instruction+='Do not read other final critic reviews before independently reconstructing arithmetic. Prioritize independently recomputing the S41 primary from raw rate choices, all3125 bootstrap bounds and32 sign flips; verify the one-sentence ticksize contrast, same payoff formula with changed action grids and equilibrium sets, and fine-minus-coarse direction; check identical parsers and terminal-wage diagnostic and self-only visibility in both arms; inspect prospective local CLI fingerprint guards; verify the frozen verdict and report scope. Earlier pilots are out of scope. Finish within four minutes where possible; state unchecked items rather than repeatedly reading unchanged code. '
    def codex():
        path=Path(f'logs/s41_{args.stage}_codex{args.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],f'/var/tmp/s41_{args.stage}_codex{args.suffix}_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE: Codex exit{rc}; retained CLI log /var/tmp/s41_{args.stage}_codex{args.suffix}_cli.log\n')
        print(f'codex {args.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s41_{args.stage}_opus{args.suffix}.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+context)
        if rc:
            with path.open('a') as h:h.write(f'\nUNAVAILABLE: Opus exit{rc}.\n')
        print(f'opus {args.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))

if __name__=='__main__':main()
