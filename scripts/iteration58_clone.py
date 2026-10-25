"""Fresh-origin execution of the committed portfolio/reader handoff.

Reuses installed project/export dependencies; no fresh-install claim. The inner
portfolio runner still uses its explicitly described local shared clones.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    remote = subprocess.check_output(['git', 'remote', 'get-url', 'origin'], text=True).strip()
    assert subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'], text=True).split()[0] == head
    export_python = Path('/var/tmp/explorer-export57/bin/python')
    assert export_python.exists(), 'Install the documented pinned export environment first'
    files = ['REPORT.md', 'README.md', 'BRIEF.html', 'BRIEF.pdf', 'REPORT.html', 'REPORT.pdf',
             'figures/explorer_handoff.png', 'logs/iteration58_exports.json',
             'logs/iteration58_portfolio_replay.json', 'results/iteration58_reproduction.md']
    expected = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}
    commands = []
    with tempfile.TemporaryDirectory(dir='/var/tmp', prefix='iteration58_origin_') as tmp:
        clone = Path(tmp)/'repo'
        subprocess.run(['git', 'clone', '-q', remote, str(clone)], check=True, timeout=120)
        subprocess.run(['git', 'checkout', '-q', '--detach', head], cwd=clone, check=True, timeout=60)
        assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=clone, text=True).strip() == head
        receipt = str(Path(tmp)/'portfolio.json')
        probes = str(Path(tmp)/'probes.json')
        stages = [
            [sys.executable, 'scripts/portfolio_replay.py', 'run', '--out', receipt],
            [sys.executable, 'scripts/portfolio_replay.py', 'check', '--out', receipt],
            [sys.executable, 'scripts/iteration58_verify.py', '--receipt', receipt, '--out', probes],
            [str(export_python), 'scripts/export_report.py', '--build'],
            [str(export_python), 'scripts/export_report.py', '--check-pdf'],
            [sys.executable, 'scripts/export_report.py', '--check', '--replay-selected'],
        ]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR='/var/tmp')
        env.pop('PYTHONPATH', None)
        for index, command in enumerate(stages, 1):
            print(f'Origin stage {index}/{len(stages)}', flush=True)
            run = subprocess.run(command, cwd=clone, env=env, text=True,
                                 capture_output=True, timeout=900)
            commands.append(dict(command=command, returncode=run.returncode,
                                 stdout=run.stdout, stderr=run.stderr))
            assert run.returncode == 0, run.stdout + run.stderr
        assert Path(receipt).read_bytes() == (ROOT/'logs/iteration58_portfolio_replay.json').read_bytes()
        probe_result = json.loads(Path(probes).read_text())
        assert probe_result['passed'] and len(probe_result['probes']) == 25
        for name, digest in expected.items():
            assert hashlib.sha256((clone/name).read_bytes()).hexdigest() == digest, name
        status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=clone, text=True)
        assert status == '', status
    result = dict(passed=True, result_revision=head, full_history_origin_clone=True,
                  commands=commands, byte_identical_artifacts=expected,
                  portfolio_replay_receipt_recomputed_byte_identically=True,
                  corruption_probes=25, clone_git_status=status,
                  installed_project_export_dependencies_reused=True,
                  fresh_install=False, cross_platform=False,
                  clone_runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Actual fresh-origin selected-host replay of all archived result objects and reader rebuild. Pilot-specific validation depth and inner local/shared clone scopes remain unchanged.')
    Path('logs/iteration58_remote_clean_clone.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'commands'}, indent=2))


if __name__ == '__main__':
    main()
