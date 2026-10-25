"""Independent bounded Codex and supplied-text Opus critics; preserve unavailability."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');a=p.parse_args()
    files=['DESIGN_S59.md','scripts/s59_replay.py','scripts/s59_independent.py','scripts/s59_present.py','scripts/s59_release.py','scripts/test_s59.py','scripts/s37_runtime.py','llm.py','sim/notepad.py','data/s59_cases.json']
    if a.stage=='final':files+=['results/s59_history.json','results/s59_summary.md','REPORT.md','logs/s59_independent.json','data/s59_history/config.json']
    instruction=('Independent adversarial research review S59 ONLY,no edits or live scientific calls. Read source files. Check outcome-independent last-TYPE-Y S29 selection,lossless column_paths/rows encoding ONLY of completed public history,identical other prompt bytes/system/statuses/notes/round/payoffs/schema. Every primitive must survive exact roundtrip;independent checker must reconstruct without main encoder. Length,field repetition,JSON shape and interpretation burden change together;no mechanism inference. Reused cases,no independent S29 replication. Review fixed paired block statistics and all failure/source/registration/runtime guards. Distinguish executable bugs from acknowledged limitations. Do not read other critic reviews. Within600words,finish promptly. ')
    if a.stage=='final':instruction+='Independently reconstruct20raw approvals,15blockcells,3125bootstrap and32signflips;check final REPORT numbers and claims. '
    def codex():
        path=Path(f'logs/s59_{a.stage}_codex{a.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],f'/var/tmp/s59_{a.stage}_codex{a.suffix}_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE Codex exit{rc};CLI log retained in /var/tmp.\n')
        print(f'codex {a.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s59_{a.stage}_opus{a.suffix}.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+'Supplied-text-only review;no raw archive or filesystem access. '+context)
        if rc:
            with path.open('a') as out:out.write(f'\nUNAVAILABLE Opus exit{rc}.\n')
        print(f'opus {a.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))

if __name__=='__main__':main()
