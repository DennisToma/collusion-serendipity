"""Bounded independent S60 critics, including honest quota-failure records."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');args=p.parse_args()
    files=['DESIGN_S60.md','sim/author_bonus.py','scripts/s60_runtime.py','scripts/s60_analyze.py','scripts/test_s60.py','sim/common.py','sim/advisor.py','scripts/s60_launch.py','scripts/s60_independent.py','sim/resource_cache.py','llm.py','scripts/s60_present.py','scripts/s60_bootstrap.py','scripts/s60_release.py']
    instruction=('Independent adversarial research review,S60 ONLY. No edits or live model calls. Check16profile economics per arm,author bonus1 versus6 with reviewer payoff fixed,identical paired task schedules,single-number system prompt difference,simultaneity,visibility,raw provenance,freeze,statistic arithmetic,failure handling and screen. Give concrete bugs and remedies,separate limitations,finish within500words. ')
    if args.stage=='final':
        files+=['REPORT.md','results/s60_author_bonus.json','results/s60_summary.md','logs/s60_independent.json','data/s60_author_bonus/config.json','logs/s60_launch_preflight.json']
        instruction+='Independently reconstruct primary from raw reviews,all3125bootstraps/32signflips and verdict. Do not read other critic reviews. Check adverse approvals do not become agreement labels;fresh author-benefit intervention; own incoming reward,joint surplus,numeral salience and downstream histories are bundled; no score gate because bonus changes mechanically. State unchecked scope. '
    def codex():
        path=Path(f'logs/s60_{args.stage}_codex{args.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],f'/var/tmp/s60_{args.stage}_codex{args.suffix}_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE: Codex exit{rc}; retained CLI log /var/tmp/s60_{args.stage}_codex{args.suffix}_cli.log\n')
        print(f'codex {args.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s60_{args.stage}_opus{args.suffix}.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+'Supplied-text-only review;no raw archive or filesystem access. '+context)
        if rc:
            with path.open('a') as h:h.write(f'\nUNAVAILABLE: Opus exit{rc}.\n')
        print(f'opus {args.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))

if __name__=='__main__':main()
