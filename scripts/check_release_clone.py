"""Check the pushed reader release using its documented setup in a clean origin clone.

Reuses the uv/package/browser caches, export environment and host libraries.
Creates a new project environment. No empty-cache or cross-host claim.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import export_report as exports


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export-python', default='/var/tmp/explorer-export61/bin/python')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    revision = git('rev-parse', 'HEAD')
    branch = git('symbolic-ref', '--short', 'HEAD')
    remote = git('remote', 'get-url', 'origin')
    if git('ls-remote', 'origin', 'refs/heads/' + branch).split()[0] != revision:
        raise RuntimeError('Push the result revision before running this check')
    names = exports.EXPORT_FILES + [exports.EXPORT_RECEIPT, 'REPORT.md', 'README.md']
    commands = [
        ['uv', 'python', 'install', '3.12.15'],
        ['uv', 'sync', '--frozen', '--python', '3.12.15'],
        ['uv', 'run', '--frozen', 'python', 'scripts/export_report.py', '--check', '--replay-selected'],
        [str(Path(args.export_python).absolute()), 'scripts/export_report.py', '--build', '--check-pdf'],
        ['git', 'diff', '--exit-code', 'HEAD', '--', *names],
    ]
    records = []
    with tempfile.TemporaryDirectory(prefix='explorer_release_origin_', dir='/var/tmp') as tmp:
        clone = Path(tmp) / 'repo'
        subprocess.run(['git', 'clone', '--quiet', remote, str(clone)], check=True, timeout=120)
        subprocess.run(['git', 'checkout', '--quiet', '--detach', revision], cwd=clone, check=True, timeout=60)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR='/var/tmp')
        env.pop('UV_PROJECT_ENVIRONMENT', None)
        env.pop('VIRTUAL_ENV', None)
        if (clone / '.venv').exists():
            raise RuntimeError('Project environment was not initially absent')
        for command in commands:
            proc = subprocess.run(command, cwd=clone, env=env, text=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, timeout=360)
            records.append({'argv': command, 'returncode': proc.returncode,
                            'stdout': proc.stdout, 'stderr': proc.stderr})
            if proc.returncode:
                raise RuntimeError(proc.stdout + proc.stderr)
        hashes = {}
        for name in names:
            content = (clone / name).read_bytes()
            if content != (ROOT / name).read_bytes():
                raise RuntimeError('Current release bytes differ: ' + name)
            hashes[name] = hashlib.sha256(content).hexdigest()
        if subprocess.check_output(['git', 'status', '--porcelain'], cwd=clone, text=True):
            raise RuntimeError('Origin clone became dirty')
    record = {'passed': True, 'time_utc': datetime.now(timezone.utc).isoformat(),
              'result_revision': revision, 'full_history_origin_clone': True,
              'new_project_environment': True, 'clone_clean': True, 'commands': records,
              'byte_identical_files': hashes,
              'exporter_sha256': hashlib.sha256((ROOT / 'scripts/export_report.py').read_bytes()).hexdigest(),
              'scope': 'Documented setup, five selected replays, reader build/PDF extraction and exact '
                       'eight-file comparison. Reused caches, export environment, Chromium and host '
                       'libraries; no empty-cache, cross-host or independent scientific-validity claim.'}
    Path(args.out).write_text(json.dumps(record, indent=2) + '\n')
    print('PASS clean-origin documented setup and reader reproduction at ' + revision)


if __name__ == '__main__':
    main()
