"""Verify the committed handoff from a fresh, full-history origin clone.

Reuses the installed pinned venv; does not claim a clean dependency install.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    root = Path.cwd()
    revision = subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip()
    remote = subprocess.check_output(['git','remote','get-url','origin'], text=True).strip()
    remote_revision = subprocess.check_output(['git','ls-remote','origin','refs/heads/main'], text=True).split()[0]
    assert remote_revision == revision, 'Push the result revision before origin reproduction'
    receipt = json.loads(Path('logs/iteration54_handoff_check.json').read_text())
    names = [*receipt['presentation_hashes'], 'logs/iteration54_handoff_check.json']
    with tempfile.TemporaryDirectory(prefix='iteration54_origin_', dir='/var/tmp') as tmp:
        clone = Path(tmp)/'repo'
        subprocess.run(['git','clone','--quiet',remote,str(clone)], check=True, timeout=120)
        subprocess.run(['git','checkout','--quiet','--detach',revision], cwd=clone, check=True, timeout=60)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR='/var/tmp')
        command = [sys.executable,'scripts/iteration54_handoff.py','verify']
        run = subprocess.run(command, cwd=clone, env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
        assert run.returncode == 0, run.stdout
        hashes = {}
        for name in names:
            assert (clone/name).read_bytes() == (root/name).read_bytes(), name
            hashes[name] = hashlib.sha256((clone/name).read_bytes()).hexdigest()
        status = subprocess.check_output(['git','status','--porcelain'], cwd=clone, text=True)
        assert status == '', status
    record = dict(passed=True, result_revision=revision, clone_source='origin', full_history=True,
        installed_venv_reused=True, fresh_dependency_install=False, clone_clean=True,
        command=command, command_exit=run.returncode, command_output=run.stdout,
        byte_identical_artifacts=hashes)
    Path('logs/iteration54_remote_clean_clone.json').write_text(json.dumps(record, indent=2)+'\n')
    print('PASS: origin reproduction at ' + revision)


if __name__ == '__main__':
    main()
