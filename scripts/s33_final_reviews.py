"""Post-outcome final review launcher including the labeled reporting diagnostic."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded

files=['DESIGN_S33.md','REPORT.md','results/s33_summary.md','results/s33_leniency.json','sim/leniency.py','scripts/s33_analyze.py','scripts/s33_independent.py','scripts/s33_reporting_diagnostic.py','results/s33_reporting_diagnostic.json','logs/s33_independent.json','logs/s33_launch_preflight.json','data/s33_leniency/config.json','data/s33_leniency/raw/completion_preflight.json']
instruction=('Independent adversarial FINAL S33 research review. No edits or live model calls. Do not read other final critic reviews. Earlier pilots out of scope. Verify primary DUD arithmetic, all bootstrap/sign/t claims, implementation/scientific validity and privacy, whether report-exposure diagnostic is correctly labeled post-outcome and avoids mechanism/backfire/causal-null/intent claims. Check raw games to independently reconstruct statistics where tools available. Report concrete bugs versus acknowledged limitations; state unchecked parts. Finish promptly, within500 words. ')
def codex():
    path=Path('logs/s33_final_codex.md')
    rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],'/var/tmp/s33_final_codex_cli.log')
    if rc or not path.exists():path.write_text(f'UNAVAILABLE:Codex exit{rc};retained CLI log /var/tmp/s33_final_codex_cli.log\n')
    print('codex final exit'+str(rc),flush=True)
def opus():
    path=Path('logs/s33_final_opus.md');context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
    rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+context)
    if rc:
        with path.open('a') as f:f.write(f'\nUNAVAILABLE:Opus exit{rc}.\n')
    print('opus final exit'+str(rc),flush=True)
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda fn:fn(),[codex,opus]))
