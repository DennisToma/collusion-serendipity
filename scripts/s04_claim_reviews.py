"""Independent strong-model reviews of complete S04 claims, with saved outputs."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))


def main():
    result=json.loads(Path('results/s04_advisor.json').read_text())
    assert result['n_games']==10 and result['n_seeds']==5
    checks=json.loads(Path('logs/s04_verification.json').read_text())
    assert checks['cache_only_replay_all_games'] and checks['independent_primary_matches']
    instruction=(
        'Adversarial final-claims review for exploratory S04. Do not edit files or run live model calls. '
        'Independently check numerical claims against the frozen JSON, exposure-gated verdict, '
        'and exact-integer rule. Evaluate whether the report overstates evidence, a null effect, '
        'absence of collusion, intentional coordination, advice causality, model identity, '
        'or detector performance. Check controls, n5 uncertainty and sign-flip assumptions. '
        'Flag material errors, give required corrections, or say no material errors. '
        'No new experiments or tuning; concise review. ')
    def codex():
        path=Path('logs/s04_final_codex.md')
        if path.exists():
            return 'Codex: existing review retained'
        prompt=instruction+('Read REPORT.md, the S04 section of REPORT_DETAILS.md, DESIGN_S04.md, '
            'results/s04_advisor.json, scripts/s04_analyze.py, logs/s04_verification.json, '
            'logs/s04_review_disposition.md. Review these independently; do not read the other final review.')
        proc=subprocess.run(['codex','exec','-m','gpt-6.1-sol','-c','model_reasoning_effort=high',
             '-s','read-only','-C',str(Path.cwd()),'-o',str(path),prompt],
             capture_output=True,text=True,timeout=480)
        Path('/var/tmp/s04_final_codex_cli.log').write_text(proc.stdout+proc.stderr)
        if proc.returncode:
            path.write_text(f'UNAVAILABLE: exit {proc.returncode}\n'+proc.stderr)
        return f'Codex review exit {proc.returncode}'
    def opus():
        path=Path('logs/s04_final_opus.md')
        if path.exists():
            return 'Opus: existing review retained'
        files=['REPORT.md','DESIGN_S04.md','results/s04_advisor.json','logs/s04_verification.json']
        context='\n\n'.join(f'FILE {p}\n{Path(p).read_text()}' for p in files)
        detail=Path('REPORT_DETAILS.md').read_text().split('# S04 — shared public-information advisor')[1]
        context+='\n\nS04 details\n'+detail
        proc=subprocess.run(['claude','-p',instruction+context,'--model','claude-opus-5-5',
                             '--output-format','text','--tools',''],capture_output=True,text=True,timeout=480)
        path.write_text(f'Exit code: {proc.returncode}\n'+proc.stdout+proc.stderr)
        return f'Opus review exit {proc.returncode}'
    with ThreadPoolExecutor(max_workers=2) as pool:
        for status in pool.map(lambda f:f(),[codex,opus]):
            print(status,flush=True)

if __name__=='__main__':
    main()
