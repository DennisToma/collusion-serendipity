"""Rebuild reader exports and replay selected evidence in a full origin clone.

Reuses installed project/export dependencies and Chromium; not a fresh install.
Run from the project environment after pushing the result commit.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    root = Path(__file__).resolve().parents[1]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    remote = subprocess.check_output(['git', 'remote', 'get-url', 'origin'], cwd=root, text=True).strip()
    pushed = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'], cwd=root, text=True).split()[0]
    if revision != pushed:
        raise RuntimeError('Push this result revision first')
    names = ['BRIEF.html', 'BRIEF.pdf', 'REPORT.html', 'REPORT.pdf', 'figures/explorer_handoff.png',
             'logs/iteration56_exports.json', 'REPORT.md', 'README.md']
    commands = [
        ['uv', 'run', '--no-project', '--with', 'markdown-it-py==4.2.0', '--with', 'playwright==1.64.1',
         '--with', 'pypdf==6.21.2', '--with', 'matplotlib==3.11.2', 'python', 'scripts/export_report.py', '--build', '--check-pdf'],
        [sys.executable, 'scripts/export_report.py', '--check', '--replay-selected'],
    ]
    records = []
    with tempfile.TemporaryDirectory(prefix='iteration56_origin_', dir='/var/tmp') as tmp:
        clone = Path(tmp) / 'repo'
        subprocess.run(['git', 'clone', '--quiet', remote, str(clone)], check=True, timeout=120)
        subprocess.run(['git', 'checkout', '--quiet', '--detach', revision], cwd=clone, check=True, timeout=60)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR='/var/tmp')
        for command in commands:
            proc = subprocess.run(command, cwd=clone, env=env, text=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, timeout=300)
            records.append({'command': command, 'exit': proc.returncode, 'output': proc.stdout})
            if proc.returncode:
                raise RuntimeError(proc.stdout)
        hashes = {}
        for name in names:
            content = (clone / name).read_bytes()
            if content != (root / name).read_bytes():
                raise RuntimeError('Clone bytes differ: ' + name)
            hashes[name] = hashlib.sha256(content).hexdigest()
        status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=clone, text=True)
        if status:
            raise RuntimeError('Clone became dirty: ' + status)
    record = {'passed': True, 'result_revision': revision, 'clone_source': 'origin', 'full_history': True,
              'export_source_sha256': hashlib.sha256((root / 'scripts/export_report.py').read_bytes()).hexdigest(),
              'installed_dependencies_and_chromium_reused': True, 'fresh_install_claimed': False,
              'clone_clean': True, 'commands': records, 'byte_identical_artifacts': hashes,
              'scope': 'Reader exports, full-table saved-field checks and five selected scientific replays/checkers.'}
    (root / 'logs/iteration56_remote_clean_clone.json').write_text(json.dumps(record, indent=2) + '\n')
    print('PASS: reader export and selected replay reproduction at ' + revision)


if __name__ == '__main__':
    main()
