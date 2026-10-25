"""Two independent bounded critics, preserving unavailability honestly."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');a=p.parse_args()
    files=['DESIGN_S48.md','scripts/s48_replay.py','scripts/s48_independent.py','scripts/s48_present.py','scripts/s48_release.py','scripts/test_s48.py','scripts/s37_runtime.py','llm.py']
    if a.stage=='final':files+=['results/s48_notes.json','results/s48_summary.md','REPORT.md','logs/s48_independent.json','data/s48_notes/config.json']
    instruction=('Independent adversarial research review S48 ONLY,no edits or paid calls. Check last-TYPE-Y case selection from S29, exact retain prompt versus partner-only note deletion, own-note/public-history preservation, boolean action binding, source/failure/registration integrity and block statistics. No mediation or long-run effect claims;fresh baseline may disappear. Separate bugs and acknowledged limitations. Within500words,finish promptly. ')
    if a.stage=='final':instruction+='Independently reconstruct primary from20raw responses,15blockcells,3125bootstrap and32signflip enumerations. Do not read other critic reviews. '
    def codex():
        path=Path(f'logs/s48_{a.stage}_codex{a.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],f'/var/tmp/s48_{a.stage}_codex{a.suffix}_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE Codex exit{rc};CLI log retained in /var/tmp.\n')
        print(f'codex {a.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s48_{a.stage}_opus{a.suffix}.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+'Supplied-text-only review;raw archive unavailable. '+context)
        if rc:
            with path.open('a') as out:out.write(f'\nUNAVAILABLE Opus exit{rc}.\n')
        print(f'opus {a.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))

if __name__=='__main__':main()
