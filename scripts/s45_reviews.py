"""Bounded independent S45 critics, including honest quota-failure records."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');args=p.parse_args()
    files=['DESIGN_S45.md','sim/reviewring.py','scripts/s45_runtime.py','scripts/s45_analyze.py','scripts/test_s45.py','sim/common.py','sim/advisor.py','scripts/s45_launch.py','scripts/s45_independent.py','sim/resource_cache.py','llm.py','scripts/s45_present.py']
    instruction=('Independent adversarial research review,S45 ONLY. No edits or live model calls. Check16profile economics,simultaneity,visibility,raw provenance,freeze,statistic arithmetic,failure handling and screen. Give concrete bugs and remedies,separate limitations,finish within500words. ')
    if args.stage=='final':
        files+=['REPORT.md','results/s45_reviewring.json','results/s45_summary.md','logs/s45_independent.json','data/s45_reviewring/config.json','logs/s45_launch_preflight.json']
        instruction+='Independently reconstruct primary from raw reviews,all3125bootstraps/32signflips and verdict. Do not read other critic reviews. Check factual labels do not become agreement labels; only synthetic marketplace adaptation,no comparison across worlds; bundled partner delivery/readability intervention. State unchecked scope. '
    def codex():
        path=Path(f'logs/s45_{args.stage}_codex{args.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],f'/var/tmp/s45_{args.stage}_codex{args.suffix}_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE: Codex exit{rc}; retained CLI log /var/tmp/s45_{args.stage}_codex{args.suffix}_cli.log\n')
        print(f'codex {args.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s45_{args.stage}_opus{args.suffix}.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+context)
        if rc:
            with path.open('a') as h:h.write(f'\nUNAVAILABLE: Opus exit{rc}.\n')
        print(f'opus {args.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))

if __name__=='__main__':main()
