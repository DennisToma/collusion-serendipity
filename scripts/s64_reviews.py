"""Bounded independent S64 critics, including honest quota-failure records."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');args=p.parse_args()
    files=['DESIGN_S64.md','sim/memory_retention.py','scripts/s64_analyze.py','scripts/test_s64.py','sim/common.py','sim/common_memory.py','llm.py','scripts/s64_independent.py','sim/advisor.py','scripts/s64_launch.py']
    instruction=('Independent adversarial research review, S64 ONLY. Fresh persistent-versus-reset memory games, NOT a pure reciprocity or reputation mechanism test. No readiness probe; luna/Codex route pinned. Review all-history and both-notepad deletion, preserved round/system/status bytes, and failure/route handling.  No edits or live model calls. Check economics, truth/simultaneity, causal scope, cache/replay integrity, frozen configuration, statistic arithmetic, failure handling and screening rule. '
                 'Report concrete remaining bugs with severity and remedies; separate acknowledged limitations. Give a final review within500 words and finish promptly. ')
    if args.stage=='final':
        files+=['REPORT.md','results/s64_memory_retention.json','results/s64_summary.md','logs/s64_independent.json','logs/s64_review_disposition.md','data/s64_memory_retention/config.json','scripts/s64_independent.py','logs/s64_launch_preflight.json']
        instruction+='Prioritize independently recomputing the S64 primary from raw game review decisions, all3125 bootstrap bounds and32 sign flips; verify matched directed pair stage economics and identical-system/initial-request contrast plus complete history and both-notepad deletion in reset arm; verify the frozen verdict and report scope. Earlier pilots are out of scope. Finish within four minutes where possible; state unchecked items rather than repeatedly reading unchanged code. '
    def codex():
        path=Path(f'logs/s64_{args.stage}_codex{args.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],f'/var/tmp/s64_{args.stage}_codex{args.suffix}_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE: Codex exit{rc}; retained CLI log /var/tmp/s64_{args.stage}_codex{args.suffix}_cli.log\n')
        print(f'codex {args.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s64_{args.stage}_opus{args.suffix}.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+context)
        if rc:
            with path.open('a') as h:h.write(f'\nUNAVAILABLE: Opus exit{rc}.\n')
        print(f'opus {args.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))

if __name__=='__main__':main()
