"""Reproduce S72 from a fresh full-history origin clone; installed venv reused."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    root = Path(__file__).resolve().parents[1]
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    origin = subprocess.check_output(['git', 'remote', 'get-url', 'origin'], text=True).strip()
    paths = ['results/s72_temporal.json', 'results/s72_summary.md', 'figures/s72_temporal.png',
        'logs/s72_independent.json', 'logs/s72_release.json', 'data/s72_registration.json',
        'data/s72_registration_receipt.json', 'logs/s72_postcheck.json',
        'REPORT.md', 'REPORT_DETAILS.md', 'HITS.md', 'README.md']
    records = []
    with tempfile.TemporaryDirectory(prefix='s72_origin_', dir='/var/tmp') as tmp:
        clone = Path(tmp)/'repo'
        subprocess.run(['git', 'clone', '--quiet', origin, str(clone)], check=True, timeout=90)
        if subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=clone, text=True).strip() != head:
            raise ValueError('Origin HEAD differs from results commit')
        commands = [[sys.executable, 'scripts/s72_temporal.py', 'release'],
            [sys.executable, 'scripts/s72_independent.py'],
            [sys.executable, 'scripts/s72_present.py'],
            [sys.executable, 'scripts/s72_present.py', '--check-documents'],
            [sys.executable, 'scripts/s72_postcheck.py'],
            [sys.executable, '-m', 'unittest', 'scripts.test_s72']]
        for command in commands:
            run = subprocess.run(command, cwd=clone, text=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, timeout=180)
            records.append(dict(command=command, returncode=run.returncode, output=run.stdout))
            if run.returncode:
                raise RuntimeError(run.stdout)
        hashes = {}
        for p in paths:
            if (clone/p).read_bytes() != (root/p).read_bytes():
                raise ValueError('Clone bytes differ: '+p)
            hashes[p] = hashlib.sha256((clone/p).read_bytes()).hexdigest()
        status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=clone, text=True)
        if status:
            raise ValueError('Clone changed: '+status)
    receipt = dict(passed=True, results_commit=head, origin=origin, full_history_origin_clone=True,
        installed_frozen_venv_reused=True, fresh_dependency_install=False,
        commands=records, byte_identical_artifacts=hashes, clone_git_status=status)
    Path('logs/s72_remote_clean_clone.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'commands'}, indent=2))


if __name__ == '__main__':
    main()
