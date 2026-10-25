"""Bounded independent S54 critics, including honest quota-failure records."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');args=p.parse_args()
    files=['DESIGN_S54.md','sim/opportunities.py','scripts/s54_runtime.py','scripts/s54_analyze.py','scripts/test_s54.py','sim/common.py','sim/advisor.py','scripts/s54_launch.py','scripts/s54_independent.py','sim/resource_cache.py','llm.py','scripts/s54_present.py','scripts/s54_bootstrap.py','scripts/s54_release.py']
    instruction=('Independent adversarial research review,S54 ONLY. No edits or live model calls. Check16profile workplace economics,balanced marginal counts with synchronized versus complementary schedules,unchanged shared system prompts,simultaneity,visibility,raw provenance,freeze,statistic arithmetic,failure handling and screen. Give concrete bugs and remedies,separate limitations,finish within500words. ')
    if args.stage=='final':
        files+=['REPORT.md','results/s54_opportunities.json','results/s54_summary.md','logs/s54_independent.json','data/s54_opportunities/config.json','logs/s54_launch_preflight.json']
        instruction+='Independently reconstruct primary from raw reviews,all3125bootstraps/32signflips and verdict. Do not read other critic reviews. Check adverse approvals do not become agreement labels;fresh opportunity-correlation intervention at fixed marginal task counts;second employee per-round types differ and joint status composition/history are bundled. State unchecked scope. '
    def codex():
        path=Path(f'logs/s54_{args.stage}_codex{args.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],f'/var/tmp/s54_{args.stage}_codex{args.suffix}_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE: Codex exit{rc}; retained CLI log /var/tmp/s54_{args.stage}_codex{args.suffix}_cli.log\n')
        print(f'codex {args.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s54_{args.stage}_opus{args.suffix}.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+context)
        if rc:
            with path.open('a') as h:h.write(f'\nUNAVAILABLE: Opus exit{rc}.\n')
        print(f'opus {args.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))

if __name__=='__main__':main()
