"""Independent methodology/claim critics, no edits, record failures honestly."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess


def main():
    p=argparse.ArgumentParser()
    p.add_argument('stage',choices=['design','final'])
    args=p.parse_args()
    instruction=('Adversarial independent research review. Do not edit files. Check design, code, '
                 'economics, cache/provenance, leakage, inference, exact decision rules and scope of claims. '
                 'Identify concrete bugs with severity and remedies; distinguish limitations from bugs. '
                 'Do not run live models. Review S03 only. ')
    files=['DESIGN_S03.md','sim/calculator.py','scripts/s03_analyze.py','scripts/test_s03.py']
    if args.stage=='final':
        files+=['REPORT.md','results/s03_calculator.json','logs/s03_verification.json',
                'logs/s03_review_disposition.md','logs/s03_design_codex.md','logs/s03_design_opus.md',
                'scripts/s03_verify.py','sim/advisor.py','sim/cournot.py','sim/common.py',
                'scripts/s02_analyze.py','data/s03_calculator/config.json','logs/s03_tests.log']
        instruction+='Independently recalculate claims and check every S03 numerical statement and verdict. '
    def codex():
        path=Path(f'logs/s03_{args.stage}_codex.md')
        with Path(f'/var/tmp/s03_{args.stage}_codex_cli.log').open('w') as log:
            proc=subprocess.run(['codex','exec','--skip-git-repo-check','-s','read-only',
                '-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high',
                '-o',str(path.resolve()),instruction+'Read these files: '+', '.join(files)],
                stdout=log,stderr=subprocess.STDOUT,timeout=480)
        if proc.returncode:
            path.write_text(f'UNAVAILABLE: Codex review exit {proc.returncode}; see /var/tmp CLI log.\n')
        return f'Codex {args.stage}: exit {proc.returncode}'
    def opus():
        path=Path(f'logs/s03_{args.stage}_opus.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        if args.stage=='final':
            context+='\nS03 report detail\n'+Path('REPORT_DETAILS.md').read_text().split('# S03 —')[1]
        proc=subprocess.run(['claude','-p',instruction+context,'--model','claude-opus-5-5',
                             '--output-format','text','--tools',''],capture_output=True,text=True,timeout=480)
        path.write_text(f'Exit code: {proc.returncode}\n'+proc.stdout+proc.stderr)
        return f'Opus {args.stage}: exit {proc.returncode}'
    with ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(lambda f:f(),[codex,opus]):
            print(result,flush=True)


if __name__=='__main__':
    main()
