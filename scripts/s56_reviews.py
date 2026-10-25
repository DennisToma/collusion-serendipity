"""Independent bounded reviews requested by CLAUDE.md, including quota fallback."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');a=p.parse_args()
    files=['DESIGN_S56.md','scripts/s56_coalitions.py','scripts/s56_independent.py','scripts/test_s56.py','scripts/s14_analyze.py','sim/tender.py','scripts/s16_reviews.py']
    if a.stage=='final':files+=['results/s56_coalitions.json','results/s56_summary.md','REPORT.md','logs/s56_independent.json']
    instruction=('Independent adversarial research review S56 only; no edits or scientific model calls. Check procurement payoff reconstruction, pair-total versus strict individual Pareto gains, fixed-pair/singleton stability versus strong equilibrium, exact rational deviations, complete posthoc disclosure, original S14 replay/source freeze, independent raw binding coverage, 8 equally reported metrics and 24 bootstrap/t summaries. Separate concrete bugs from acknowledged limitations; finish within600words. ')
    if a.stage=='final':instruction+='Independently reconstruct90rounds/80gamecells/24summaries and3375profile census from raw S14 archive and verify REPORT claims. Do not read other critic reviews. '
    def codex():
        path=Path(f'logs/s56_{a.stage}_codex{a.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],f'/var/tmp/s56_{a.stage}_codex{a.suffix}_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE Codex exit{rc};CLI retained in /var/tmp.\n')
        print(f'codex {a.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s56_{a.stage}_opus{a.suffix}.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+'Supplied-text-only scope,raw archive unavailable. '+context)
        if rc:
            with path.open('a') as f:f.write(f'\nUNAVAILABLE Opus exit{rc}.\n')
        print(f'opus {a.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))


if __name__=='__main__':main()
