"""Check the pushed current export overlay; fresh installs target the archive.

This separate closure check reuses installed project/export dependencies.
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
    export_python = '/var/tmp/explorer-export57/bin/python'
    commands = [
        [export_python, 'scripts/export_report.py', '--build', '--check-pdf'],
        [sys.executable, 'scripts/export_report.py', '--check', '--replay-selected'],
        [sys.executable, 'scripts/iteration57_fresh_install.py', 'check'],
        [sys.executable, 'scripts/iteration57_release.py'],
    ]
    names = ['BRIEF.html', 'BRIEF.pdf', 'REPORT.html', 'REPORT.pdf', 'figures/explorer_handoff.png',
             'logs/iteration57_exports.json', 'REPORT.md', 'README.md',
             'logs/iteration57_release.json', 'logs/iteration57_fresh_install.json']
    records = []
    with tempfile.TemporaryDirectory(prefix='iteration57_current_origin_', dir='/var/tmp') as tmp:
        clone = Path(tmp) / 'repo'
        subprocess.run(['git', 'clone', '--quiet', remote, str(clone)], check=True, timeout=120)
        subprocess.run(['git', 'checkout', '--quiet', '--detach', revision], cwd=clone, check=True, timeout=60)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR='/var/tmp')
        for command in commands:
            proc = subprocess.run(command, cwd=clone, env=env, text=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, timeout=300)
            records.append({'command': command, 'exit': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr})
            if proc.returncode:
                raise RuntimeError(proc.stdout + proc.stderr)
        hashes = {}
        for name in names:
            content = (clone / name).read_bytes()
            if content != (root / name).read_bytes():
                raise RuntimeError('Current-clone bytes differ: ' + name)
            hashes[name] = hashlib.sha256(content).hexdigest()
        status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=clone, text=True)
        if status:
            raise RuntimeError('Current clone became dirty: ' + status)
    record = {'passed': True, 'result_revision': revision, 'clone_source': 'origin', 'full_history': True,
              'scope': 'Current editorial overlay and receipt consistency; reuses installed environments and Chromium. Separate fresh-install receipt targets the archived handoff.',
              'clone_clean': True, 'commands': records, 'byte_identical_artifacts': hashes}
    (root / 'logs/iteration57_remote_clean_clone.json').write_text(json.dumps(record, indent=2) + '\n')
    print('PASS current export and receipt closure at ' + revision)


if __name__ == '__main__':
    main()
