"""Reproduce the table audit and selected replays from a full-history origin clone.

The existing installed pinned venv is reused; no fresh-install claim.
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
    remote_revision = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'], cwd=root, text=True).split()[0]
    if revision != remote_revision:
        raise RuntimeError('Push the result revision before origin reproduction')
    names = ['results/iteration55_claim_audit.json', 'logs/iteration55_selected_replay.json', 'REPORT.md', 'README.md']
    with tempfile.TemporaryDirectory(prefix='iteration55_origin_', dir='/var/tmp') as tmp:
        clone = Path(tmp) / 'repo'
        subprocess.run(['git', 'clone', '--quiet', remote, str(clone)], check=True, timeout=120)
        subprocess.run(['git', 'checkout', '--quiet', '--detach', revision], cwd=clone, check=True, timeout=60)
        command = [sys.executable, 'scripts/iteration55_claims.py', '--replay-selected']
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR='/var/tmp')
        run = subprocess.run(command, cwd=clone, env=env, text=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=300)
        if run.returncode:
            raise RuntimeError(run.stdout)
        hashes = {}
        for name in names:
            data = (clone / name).read_bytes()
            if data != (root / name).read_bytes():
                raise RuntimeError('Clone bytes differ: ' + name)
            hashes[name] = hashlib.sha256(data).hexdigest()
        status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=clone, text=True)
        if status:
            raise RuntimeError('Clone became dirty: ' + status)
    record = dict(passed=True, result_revision=revision, clone_source='origin', full_history=True,
                  installed_venv_reused=True, fresh_dependency_install=False, clone_clean=True,
                  command=command, command_exit=run.returncode, command_output=run.stdout,
                  byte_identical_artifacts=hashes,
                  scope='Complete table saved-artifact audit plus five selected scientific reanalyses/checkers; no full-portfolio raw reproduction.')
    (root / 'logs/iteration55_remote_clean_clone.json').write_text(json.dumps(record, indent=2) + '\n')
    print('PASS: full-history origin reproduction at ' + revision)


if __name__ == '__main__':
    main()
