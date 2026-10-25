"""Independent bounded Codex and supplied-text Opus critics; preserve unavailability."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');a=p.parse_args()
    files=['DESIGN_S61.md','scripts/s61_replay.py','scripts/s61_independent.py','scripts/s61_present.py','scripts/s61_release.py','scripts/test_s61.py','scripts/s37_runtime.py','llm.py','sim/notepad.py','data/s61_cases.json']
    if a.stage=='final':files+=['results/s61_identity.json','results/s61_summary.md','REPORT.md','logs/s61_independent.json','data/s61_identity/config.json']
    instruction=('Independent adversarial S61 research review,no edits or scientific calls. Review outcome-independent case selection,complete simultaneous ID swap of system/user/structured histories/notes/output target;involution,unmodified byte-identical repeat control. Primary is EXCESS mismatch(anchor!=swapped)-(anchor!=repeat),not signed approval. Coupled anchor,small n5,sampling/order limitations,exact statistics/failure/source/runtime/registration guards and claim scope. Check code against design. Distinguish bugs from acknowledged limits. Do not read other critics. Within600words,finish promptly. ')
    if a.stage=='final':instruction+='Independently reconstruct30raw approvals,30blockcells,6exact bootstrap/t/sign summaries;check REPORT numbers/verdict. '
    def codex():
        path=Path(f'logs/s61_{a.stage}_codex{a.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],f'/var/tmp/s61_{a.stage}_codex{a.suffix}_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE Codex exit{rc};CLI log retained in /var/tmp.\n')
        print(f'codex {a.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s61_{a.stage}_opus{a.suffix}.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+'Supplied-text-only review;no raw archive or filesystem access. '+context)
        if rc:
            with path.open('a') as out:out.write(f'\nUNAVAILABLE Opus exit{rc}.\n')
        print(f'opus {a.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))

if __name__=='__main__':main()
