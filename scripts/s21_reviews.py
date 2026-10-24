"""Independent S21 critics with explicit availability records."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final']);a=p.parse_args()
    files=['DESIGN_S21.md','scripts/s21_audit.py','scripts/s21_analyze.py','scripts/s21_independent.py',
           'scripts/s21_present.py','scripts/test_s21.py','data/s21_cases.json']
    instruction=('Independent adversarial S21 review. No edits or live model calls. Check factual task, source selection, '
                 'information visibility, parser, one-shot guards, provenance, inference and scope. '
                 'Separate concrete remaining bugs from explicitly acknowledged limitations. '
                 'Give concise actionable review within500 words; finish within4 minutes if possible. ')
    if a.stage=='final':
        files+=['REPORT.md','results/s21_audit.json','results/s21_summary.md','logs/s21_independent.json','data/s21_audit/config.json']
        instruction+='Independently recompute thirty predictions/counts, five-block contrasts/uncertainty and verdict using raw responses. '
    def codex():
        path=Path(f'logs/s21_{a.stage}_codex.md')
        rc=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only','-C',str(Path.cwd()),'-m','gpt-6.1-sol',
                        '-c','model_reasoning_effort=high','-o',str(path.resolve()),instruction+'Read '+', '.join(files)],
                       f'/var/tmp/s21_{a.stage}_codex_cli.log')
        if rc or not path.exists():path.write_text(f'UNAVAILABLE: Codex exit{rc}; CLI output retained in /var/tmp.\n')
        print(f'Codex {a.stage} exit{rc}',flush=True)
    def opus():
        path=Path(f'logs/s21_{a.stage}_opus.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,instruction+context)
        if rc:
            with path.open('a') as f:f.write(f'\nUNAVAILABLE: Opus exit{rc}.\n')
        print(f'Opus {a.stage} exit{rc}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[codex,opus]))

if __name__=='__main__':main()
