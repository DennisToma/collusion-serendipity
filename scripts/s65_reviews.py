"""Bounded independent S65 critics, including honest quota-failure records."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');args=p.parse_args()
    files=['DESIGN_S65.md','sim/bonus_pooling.py','scripts/s65_analyze.py','scripts/test_s65.py','sim/common_memory.py','llm.py','scripts/s65_independent.py','sim/advisor.py','scripts/s65_launch.py']
    instruction=('Independent adversarial review of S65 ONLY. Changed-incentive calibration, individual versus equal pooled workplace bonuses. All history and shared notes retained in BOTH arms. TYPE-Y approval gives reviewer -2 versus +2 final bonus. No collusion/communication-mechanism claim. No edits or live simulated-agent calls. Check allocation versus settlement economics, best responses, matched tasks, simultaneity, source/cache replay, failure handling, exact statistics, and expected-calibration DUD versus unresolved ODD classification. Report concrete bugs by severity, distinguish acknowledged limits. Finish within 500 words and four minutes if possible. ')
    if args.stage=='final':
        files+=['REPORT.md','results/s65_bonus_pooling.json','results/s65_summary.md','logs/s65_independent.json','data/s65_bonus_pooling/config.json']
        instruction+='Independently reconstruct the primary from raw game actions and all3125 bootstrap samples and32 sign patterns; check final claims. '
    def codex():
        path=Path(f'logs/s65_{args.stage}_codex{args.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],f'/var/tmp/s65_{args.stage}_codex{args.suffix}_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE: Codex exit{rc}; retained CLI log /var/tmp/s65_{args.stage}_codex{args.suffix}_cli.log\n')
        print(f'codex {args.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s65_{args.stage}_opus{args.suffix}.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+context)
        if rc:
            with path.open('a') as h:h.write(f'\nUNAVAILABLE: Opus exit{rc}.\n')
        print(f'opus {args.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))

if __name__=='__main__':main()
