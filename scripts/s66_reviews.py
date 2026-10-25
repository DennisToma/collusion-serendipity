"""Bounded independent critics; compact Opus scope is explicitly supplied text."""
import argparse,json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');a=p.parse_args()
    files=['DESIGN_S66.md','sim/payoff_order.py','scripts/s66_analyze.py','scripts/s66_independent.py','scripts/test_s66.py','scripts/s66_launch.py','scripts/s66_present.py','scripts/s66_release.py']
    prompt='Independent adversarial review S66 only. No edits or new simulated-agent calls. Both arms have IDENTICAL pooled economics: Yapproval gives +2 to EACH employee. Only complete allocation and settlement/table paragraph positions swap. Check exact information equivalence,game/payoff/memory/timing,cache/provenance,statistics/directional screen and scope. Flag concrete high/medium correctness issues; distinguish known limits. Be concise,finish within four minutes. '
    if a.stage=='final':
        files+=['REPORT.md','results/s66_payoff_order.json','results/s66_summary.md','logs/s66_independent.json','logs/s66_release.json']
        prompt+='Independently reconstruct primary and all bootstrap/sign results from raw games and verify final claims. '
    def codex():
        out=Path(f'logs/s66_{a.stage}_codex{a.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(out.resolve()),prompt+'Read '+', '.join(files)],f'/var/tmp/s66_{a.stage}_codex{a.suffix}_cli.log')
        if rc or not out.exists():out.write_text(f'UNAVAILABLE: exit{rc};CLI retained under /var/tmp.\n')
        return dict(critic='codex',exit=rc)
    def opus():
        chosen=['DESIGN_S66.md']
        if a.stage=='final':chosen+=['results/s66_summary.md','logs/s66_independent.json']
        context='\n\n'.join('FILE '+n+'\n'+Path(n).read_text() for n in chosen)
        if a.stage=='design':
            from sim.payoff_order import prompts
            context+='\nBoth system strings:\n'+repr([prompts('A','C',[],[],c,{'A':True,'C':False})[0] for c in ['allocated_first','final_first']])
            s=Path('scripts/s66_analyze.py').read_text();context+='\n'+s[s.index('def exact_summary'):s.index('def analyze')]
        context+='\nScope: supplied text ONLY,no raw filesystem audit or bootstrap enumeration claimed. Check arithmetic and inference within that scope.'
        out=Path(f'logs/s66_{a.stage}_opus{a.suffix}.md')
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],out,prompt+context)
        return dict(critic='opus_supplied_text',exit=rc)
    with ThreadPoolExecutor(max_workers=2) as pool:result=list(pool.map(lambda f:f(),[codex,opus]))
    Path(f'logs/s66_{a.stage}_review_exits{a.suffix}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
