"""Bounded independent critics; compact Opus scope is explicitly supplied text."""
import argparse,json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');a=p.parse_args()
    files=['DESIGN_S69.md','sim/pooled_enforcement.py','scripts/s69_analyze.py','scripts/s69_independent.py','scripts/test_s69.py','scripts/s69_launch.py','scripts/s69_present.py','scripts/s69_release.py']
    prompt='Independent adversarial review S69 only. No edits or new simulated-agent calls. Both arms pool bonuses equally. Low reviewer charge3 gives Yapproval+2 to each; high charge13 gives-3 to each. Xgives+3.5 each. Only numeric penalty/allocated-net/finalY-table values differ. Primary LOW minus HIGH. EXPECTED iff mean>=.25,exact-bootstraplower>0,upper signp<=.05;otherwise UNRESOLVED. EXPECTED maps DUD;unresolved ODD;no HIT/bonusgate. Check game/payoff/memory/timing,cache/provenance,statistics/screen and scope. Flag concrete high/medium correctness issues; distinguish known limits. Be concise,finish within four minutes. '
    if a.stage=='final':
        files+=['REPORT.md','results/s69_pooled_enforcement.json','results/s69_summary.md','logs/s69_independent.json']
        prompt+='Independently reconstruct primary and all bootstrap/sign results from raw games and verify final claims. '
    def codex():
        out=Path(f'logs/s69_{a.stage}_codex{a.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(out.resolve()),prompt+'Read '+', '.join(files)],f'/var/tmp/s69_{a.stage}_codex{a.suffix}_cli.log')
        if rc or not out.exists():out.write_text(f'UNAVAILABLE: exit{rc};CLI retained under /var/tmp.\n')
        return dict(critic='codex',exit=rc)
    def opus():
        chosen=['DESIGN_S69.md']
        if a.stage=='final':chosen+=['results/s69_summary.md','logs/s69_independent.json']
        context='\n\n'.join('FILE '+n+'\n'+Path(n).read_text() for n in chosen)
        if a.stage=='design':
            from sim.pooled_enforcement import prompts
            context+='\nBoth system strings:\n'+repr([prompts('A','C',[],[],c,{'A':True,'C':False})[0] for c in ['low_charge','high_charge']])
            s=Path('scripts/s69_analyze.py').read_text();context+='\n'+s[s.index('def exact_summary'):s.index('def analyze')]
        context+='\nScope: supplied text ONLY,no raw filesystem audit or bootstrap enumeration claimed. Check arithmetic and inference within that scope.'
        out=Path(f'logs/s69_{a.stage}_opus{a.suffix}.md')
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],out,prompt+context)
        return dict(critic='opus_supplied_text',exit=rc)
    with ThreadPoolExecutor(max_workers=2) as pool:result=list(pool.map(lambda f:f(),[codex,opus]))
    Path(f'logs/s69_{a.stage}_review_exits{a.suffix}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
