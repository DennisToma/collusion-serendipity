"""Independent S16 critics. Bounded process groups; preserve unavailable reviews."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import signal
import subprocess


def run_bounded(cmd,log_path,prompt=None):
    with Path(log_path).open('w') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE if prompt else subprocess.DEVNULL,
                              stdout=log,stderr=subprocess.STDOUT,text=True,start_new_session=True)
        try:
            proc.communicate(prompt,timeout=360)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            log.write('\nUNAVAILABLE: review timed out after360s; process group terminated.\n')
            return 124
        return proc.returncode


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['design','final'])
    p.add_argument('--critic',choices=['both','codex','opus'],default='both')
    p.add_argument('--suffix',default='')
    args=p.parse_args()
    instruction=('Give a concise adversarial independent research review, no edits or live model calls. '
                 'Review S16 only. Check treatment timing, provenance, inference, decision rules, '
                 'and scope of claims. Report concrete remaining bugs and separate acknowledged limitations. '
                 'Earlier reviews prompted guards now in the current code; do not report resolved issues as remaining. ')
    files=['DESIGN_S16.md','sim/notes.py','scripts/s16_analyze.py','scripts/test_s16.py',
           'sim/legality.py','sim/common.py','sim/advisor.py','sim/cournot.py','scripts/s16_independent.py']
    if args.stage=='final':
        files+=['results/s16_summary.md','REPORT.md','results/s16_tender.json',
                'logs/s16_independent.json','data/s16_tender/config.json',
                'logs/s16_review_disposition.md','logs/s16_launch_preflight.json',
                'logs/s16_request_audit.json','scripts/s16_request_audit.py','scripts/s16_release.py',
                'logs/s16_release.json','logs/s16_economics.json']
        instruction+='Independently recalculate S16 numerical claims, using raw games if useful. '
    def codex():
        path=Path(f'logs/s16_{args.stage}_codex{args.suffix}.md')
        code=run_bounded(['codex','exec','--skip-git-repo-check','-s','read-only',
                         '-C',str(Path.cwd()),'-m','gpt-6.1-sol','-c','model_reasoning_effort=high',
                         '-o',str(path.resolve()),instruction+'Read these files: '+', '.join(files)],
                         f'/var/tmp/s16_{args.stage}_codex{args.suffix}_cli.log')
        if code or not path.exists():path.write_text(f'UNAVAILABLE: Codex review exit {code}; see retained CLI log.\n')
        print(f'Codex {args.stage}: exit{code}',flush=True)
    def opus():
        path=Path(f'logs/s16_{args.stage}_opus{args.suffix}.md')
        context='\n\n'.join(f'FILE {f}\n{Path(f).read_text()}' for f in files)
        code=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],
                         path,instruction+context)
        print(f'Opus {args.stage}: exit{code}',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda f:f(),{'both':[codex,opus],'codex':[codex],'opus':[opus]}[args.critic]))

if __name__=='__main__':main()
