"""Bounded independent S62 critics, including honest quota-failure records."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');args=p.parse_args()
    files=['DESIGN_S62.md','sim/notepad_qwen.py','scripts/s62_analyze.py','scripts/test_s62.py','sim/common.py','sim/common_qwen.py','llm.py','scripts/s62_independent.py','sim/advisor.py','scripts/s62_launch.py']
    instruction=('Independent adversarial research review, S62 ONLY. Fresh Qwen/Aqueduct generalization, not a controlled cross-family effect. Review gate/probe/API controls and routes.  No edits or live model calls. Check economics, truth/simultaneity, causal scope, cache/replay integrity, frozen configuration, statistic arithmetic, failure handling and screening rule. '
                 'Report concrete remaining bugs with severity and remedies; separate acknowledged limitations. Give a final review within500 words and finish promptly. ')
    if args.stage=='final':
        files+=['REPORT.md','results/s62_notepad_qwen.json','results/s62_summary.md','logs/s62_independent.json','logs/s62_review_disposition.md','data/s62_notepad_qwen/config.json','scripts/s62_independent.py','logs/s62_launch_preflight.json']
        instruction+='Prioritize independently recomputing the S62 primary from raw game review decisions, all3125 bootstrap bounds and32 sign flips; verify matched directed pair stage economics and readability-sentence-only empty-history contrast plus self-only note visibility; verify the frozen verdict and report scope. Earlier pilots are out of scope. Finish within four minutes where possible; state unchecked items rather than repeatedly reading unchanged code. '
    if args.stage=='final' and Path('results/s62_failure.json').exists():
        files=['DESIGN_S62.md','sim/notepad_qwen.py','sim/common_qwen.py','scripts/s62_failure.py','scripts/s62_analyze.py','REPORT.md','results/s62_failure.json','results/s62_summary.md','data/s62_notepad_qwen/config.json','logs/s62_launch_preflight.json']
        instruction='Independent adversarial S62 FAILED-run review. No edits or live calls. Reconstruct all raw prefix decisions and output failures; verify no treatment-effect estimate or partial-arm promotion. Check freeze, causal scope and report counts. State scope and concrete remaining bugs. Finish within500words.'
    def codex():
        path=Path(f'logs/s62_{args.stage}_codex{args.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],f'/var/tmp/s62_{args.stage}_codex{args.suffix}_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE: Codex exit{rc}; retained CLI log /var/tmp/s62_{args.stage}_codex{args.suffix}_cli.log\n')
        print(f'codex {args.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s62_{args.stage}_opus{args.suffix}.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+context)
        if rc:
            with path.open('a') as h:h.write(f'\nUNAVAILABLE: Opus exit{rc}.\n')
        print(f'opus {args.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))

if __name__=='__main__':main()
