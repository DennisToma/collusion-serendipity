"""Bounded independent critics; Opus scope is supplied-text arithmetic/design."""
import argparse,json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);p.add_argument('--suffix',default='');a=p.parse_args()
    files=['DESIGN_S68.md','scripts/s68_replay.py','scripts/s68_independent.py','scripts/s68_present.py','scripts/s68_release.py','scripts/test_s68.py','scripts/s68_context_audit.py','scripts/s68_publish.py','data/s68_cases.json']
    prompt='Independent adversarial S68 review,no edits or simulated-agent calls. This reverses ONLY output boolean encoding,not history semantics: anchor/repeat true=approve;inverted false=approve. Both arms append identical historical-encoding clarification. Same system/full original history/status/notes/keys/economics. Primary EXCESS disagreement(anchor!=decoded-inverted)-(anchor!=repeat),not signed approval. Check exact raw decoding,strict parser,source/registration/runtime/abort/scheduling/statistics/screen and claim scope. Distinguish known limits from high/medium bugs. Finish promptly within500words. Do not read other critics. '
    if a.stage=='final':
        files+=['REPORT.md','results/s68_polarity.json','results/s68_summary.md','logs/s68_independent.json']
        prompt+='Reconstruct30raw decoded actions/30blockcells/6bootstrap+t/sign summaries and verify final claims. '
    def codex():
        out=Path(f'logs/s68_{a.stage}_codex{a.suffix}.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high','-o',str(out.resolve()),prompt+'Read '+', '.join(files)],f'/var/tmp/s68_{a.stage}_codex{a.suffix}_cli.log')
        if rc or not out.exists():out.write_text(f'UNAVAILABLE: exit{rc};CLI retained under /var/tmp.\n')
        return dict(critic='codex',exit=rc)
    def opus():
        chosen=['DESIGN_S68.md']
        if a.stage=='final':chosen+=['results/s68_summary.md','logs/s68_independent.json']
        else:
            chosen+=['scripts/s68_context_audit.py']
        context='\n\n'.join('FILE '+n+'\n'+Path(n).read_text() for n in chosen)
        if a.stage=='design':
            from scripts.s68_replay import select_cases,request
            c=select_cases()['cases'][0];context+='\nOutput tails:'+repr([request(c,v)['prompt'][-800:] for v in ['anchor','inverted']])
        context+='\nScope:supplied text only,no filesystem/raw/bootstrap enumeration audit claimed.'
        out=Path(f'logs/s68_{a.stage}_opus{a.suffix}.md')
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],out,prompt+context)
        return dict(critic='opus_supplied_text',exit=rc)
    with ThreadPoolExecutor(max_workers=2) as pool:result=list(pool.map(lambda f:f(),[codex,opus]))
    Path(f'logs/s68_{a.stage}_review_exits{a.suffix}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
