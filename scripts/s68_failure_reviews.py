"""Independent final failure-claim critics;no behavioral estimate requested."""
from concurrent.futures import ThreadPoolExecutor
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded

def main():
    files=['DESIGN_S68.md','REPORT.md','results/s68_summary.md','results/s68_failure.json','scripts/s68_failure_audit.py','scripts/s68_failure_present.py','scripts/s68_failure_release.py','logs/s68_process_exit.json','logs/s68_source_freeze.json']
    prompt='Independent final adversarial S68 FAILURE review. No edits,no simulated-agent/model calls,NO behavioral aggregation or treatment-effect estimation from partial data. Registered pilot interrupted with process exit143 after30admissions/29returned/29accepted,one missing repeat reply,no completion event. Cause unknown. Verify counts,raw prefix/request/accepted/source/registration/schedule bindings and that incomplete analysis/resume fail without calls;check no scientific estimate or HIT is claimed and older rows retained. Failure evidence/formatting should reproduce without rewriting journals. Flag concrete high/medium issues;distinguish acknowledged limits. Do not read other critics. Finish promptly within600words. '
    def codex():
        out=Path('logs/s68_final_failure_codex.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(out.resolve()),prompt+'Read '+', '.join(files)],'/var/tmp/s68_final_failure_codex_cli.log')
        if rc or not out.exists():out.write_text(f'UNAVAILABLE exit{rc};CLI retained under /var/tmp.\n')
        return dict(critic='codex_failure_raw',exit=rc)
    def opus():
        chosen=['DESIGN_S68.md','results/s68_summary.md','results/s68_failure.json']
        context='\n\n'.join('FILE '+p+'\n'+Path(p).read_text() for p in chosen)
        out=Path('logs/s68_final_failure_opus.md')
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],out,prompt+'Supplied-text-only scope:no raw filesystem/count/provenance replay independently certified. '+context)
        return dict(critic='opus_supplied_text_failure',exit=rc)
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda f:f(),[codex,opus]))
    Path('logs/s68_final_failure_review_exits.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
if __name__=='__main__':main()
