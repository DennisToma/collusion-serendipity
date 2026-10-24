"""Bounded independent S27 critics, including honest quota-failure records."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);args=p.parse_args()
    files=['DESIGN_S27.md','sim/concentration.py','scripts/s27_analyze.py','scripts/test_s27.py','sim/common.py','sim/advisor.py','scripts/s27_launch.py']
    instruction=('Independent adversarial research review, S27 ONLY. No edits or live model calls. Check economics, truth/simultaneity, causal scope, cache/replay integrity, frozen configuration, statistic arithmetic, failure handling and screening rule. '
                 'Report concrete remaining bugs with severity and remedies; separate acknowledged limitations. Give a final review within500 words and finish promptly. ')
    if args.stage=='final':
        files+=['REPORT.md','results/s27_concentration.json','results/s27_summary.md','logs/s27_independent.json','logs/s27_review_disposition.md','data/s27_concentration/config.json','scripts/s27_independent.py','logs/s27_launch_preflight.json']
        instruction+='Prioritize independently recomputing the S27 primary from raw game review decisions, all3125 bootstrap bounds and32 sign flips; verify matched directed pair stage economics and the roster/count/schema-only empty-history contrast; verify the frozen verdict and report scope. Earlier pilots are out of scope. Finish within four minutes where possible; state unchecked items rather than repeatedly reading unchanged code. '
    def codex():
        path=Path(f'logs/s27_{args.stage}_codex.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],f'/var/tmp/s27_{args.stage}_codex_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE: Codex exit{rc}; retained CLI log /var/tmp/s27_{args.stage}_codex_cli.log\n')
        print(f'codex {args.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s27_{args.stage}_opus.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+context)
        if rc:
            with path.open('a') as h:h.write(f'\nUNAVAILABLE: Opus exit{rc}.\n')
        print(f'opus {args.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))

if __name__=='__main__':main()
