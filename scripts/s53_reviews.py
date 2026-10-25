"""Independent bounded reviews requested by CLAUDE.md, including quota fallback."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');a=p.parse_args()
    files=['DESIGN_S53.md','scripts/s53_payoffs.py','scripts/s53_independent.py','scripts/test_s53.py']
    if a.stage=='final':files+=['results/s53_payoffs.json','results/s53_summary.md','REPORT.md','logs/s53_independent.json']
    instruction=('Independent adversarial research review S53 only,no edits or scientific model calls. Check static payoff/Nash/regret identities,Pareto comparator,simultaneous mutual-Y definition,denominators,all-six metric reporting,source replay and hash freeze,bootstrap/t intervals,and careful posthoc/noncausal scope. This uses previously inspected S29 games,never new replication or confirmed collusion. Keep within500words;separate concrete bugs from acknowledged limitations. ')
    if a.stage=='final':instruction+='Independently reconstruct all counts and the18 block-bootstrap/t summaries from original game files;also verify REPORT numerical claims. '
    def codex():
        path=Path(f'logs/s53_{a.stage}_codex{a.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],f'/var/tmp/s53_{a.stage}_codex{a.suffix}_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE Codex exit{rc};CLI retained in /var/tmp.\n')
        print(f'codex {a.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s53_{a.stage}_opus{a.suffix}.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+'Supplied-text-only scope,raw archive unavailable. '+context)
        if rc:
            with path.open('a') as f:f.write(f'\nUNAVAILABLE Opus exit{rc}.\n')
        print(f'opus {a.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))


if __name__=='__main__':main()
