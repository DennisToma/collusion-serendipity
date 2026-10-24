"""Independent S25 critics with explicit availability records."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);a=p.parse_args()
    files=['DESIGN_S25.md','scripts/s25_replay.py','scripts/s25_analyze.py','scripts/s25_independent.py',
           'scripts/test_s25.py','data/s25_cases.json']
    instruction=('Independent adversarial S25 review. No edits or live model calls. Check assigned output-order contrast at fixed source histories, source selection, '
                 'information visibility, parser, one-shot guards, provenance, inference and scope. '
                 'Separate concrete remaining bugs from explicitly acknowledged limitations. '
                 'Give concise actionable review within500 words; finish within4 minutes if possible. ')
    if a.stage=='final':
        files+=['REPORT.md','results/s25_order.json','results/s25_summary.md','logs/s25_independent.json','data/s25_order/config.json','data/s25_order/responses.jsonl','logs/s25_review_disposition.md']
        instruction+='Independently recompute twenty target approvals/actual top-level field orders, all six five-block summaries and frozen verdict using raw responses. Opus sees these raw responses only as supplied text, not via filesystem or code execution; state actual verification scope. This is a requested output-format contrast, not hidden reasoning or collusion identification. '
    def codex():
        path=Path(f'logs/s25_{a.stage}_codex.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol',
                        '-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],
                       f'/var/tmp/s25_{a.stage}_codex_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE: Codex exit{rc}; CLI output retained in /var/tmp.\n')
        print(f'Codex {a.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s25_{a.stage}_opus.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+context)
        if rc:
            with path.open('a') as f:f.write(f'\nUNAVAILABLE: Opus exit{rc}.\n')
        print(f'Opus {a.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))

if __name__=='__main__':main()
