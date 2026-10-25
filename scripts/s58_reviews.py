"""Independent bounded Codex and supplied-text Opus critics; preserve unavailability."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');a=p.parse_args()
    files=['DESIGN_S58.md','scripts/s58_replay.py','scripts/s58_independent.py','scripts/s58_present.py','scripts/s58_release.py','scripts/test_s58.py','scripts/s37_runtime.py','llm.py','sim/notepad.py','data/s58_cases.json']
    if a.stage=='final':files+=['results/s58_history.json','results/s58_summary.md','REPORT.md','logs/s58_independent.json','data/s58_history/config.json']
    instruction=('Independent adversarial research review S58 ONLY,no edits or live scientific calls. Read source files. Check outcome-independent last-TYPE-Y S29 selection,exact replacement ONLY of completed public rounds list with [],identical system/current statuses/notes/round/payoffs,schema and failure/source/registration/runtime guards. Notes retain historical information and current round remains late;this tests one explicit public record,not all memory. Erasure changes length,missing-history cues,and past reward/action information together. No reciprocity or reputational mechanism identified. Source cases reused across many exploratory tests;no independent S29 replication. Review fixed paired block statistics and scope. Distinguish executable bugs from acknowledged limitations. Do not read other critic reviews. Within600words,finish promptly. ')
    if a.stage=='final':instruction+='Independently reconstruct20raw approvals,15blockcells,3125bootstrap and32signflips;check final REPORT numbers and claims. '
    def codex():
        path=Path(f'logs/s58_{a.stage}_codex{a.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],f'/var/tmp/s58_{a.stage}_codex{a.suffix}_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE Codex exit{rc};CLI log retained in /var/tmp.\n')
        print(f'codex {a.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s58_{a.stage}_opus{a.suffix}.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+'Supplied-text-only review;no raw archive or filesystem access. '+context)
        if rc:
            with path.open('a') as out:out.write(f'\nUNAVAILABLE Opus exit{rc}.\n')
        print(f'opus {a.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))

if __name__=='__main__':main()
