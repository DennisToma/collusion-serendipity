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
    parser.add_argument('--full-validation', action='store_true',
                        help='Also run the canonical suite and all archived primary replays/checkers')
    args = parser.parse_args()
    Path(args.out).write_text(json.dumps({'passed': False, 'status': 'started; no completed acceptance',
        'time_utc': datetime.now(timezone.utc).isoformat()}, indent=2) + '\n')
    revision = git('rev-parse', 'HEAD')
    runner_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    committed_runner = subprocess.check_output(
        ['git', 'show', revision + ':scripts/check_release_clone.py'], cwd=ROOT)
    if Path(__file__).read_bytes() != committed_runner:
        raise RuntimeError('Commit and push the acceptance runner before running this check')
    branch = git('symbolic-ref', '--short', 'HEAD')
    remote = git('remote', 'get-url', 'origin')
    if git('ls-remote', 'origin', 'refs/heads/' + branch).split()[0] != revision:
        raise RuntimeError('Push the result revision before running this check')
    names = exports.EXPORT_FILES + [exports.EXPORT_RECEIPT, 'REPORT.md', 'README.md']
    commands = [
        ['uv', 'python', 'install', '3.12.15'],
        ['uv', 'sync', '--frozen', '--python', '3.12.15'],
        ['uv', 'run', '--frozen', 'python', '-c',
         'import json,sys; print(json.dumps(dict(executable=sys.executable,version=sys.version)))'],
        ['uv', 'run', '--frozen', 'python', 'scripts/export_report.py', '--check', '--replay-selected'],
        [str(Path(args.export_python).absolute()), 'scripts/export_report.py', '--build', '--check-pdf'],
        ['git', 'diff', '--exit-code', 'HEAD', '--', *names],
    ]
    records = []
    full_validation = None
    with tempfile.TemporaryDirectory(prefix='explorer_release_origin_', dir='/var/tmp') as tmp:
        clone = Path(tmp) / 'repo'
        subprocess.run(['git', 'clone', '--quiet', remote, str(clone)], check=True, timeout=120)
        subprocess.run(['git', 'checkout', '--quiet', '--detach', revision], cwd=clone, check=True, timeout=60)
        env = {key: value for key, value in os.environ.items()
               if key not in {'VIRTUAL_ENV', 'PYTHONPATH', 'PYTHONHOME', 'PYTHONOPTIMIZE'}
               and (not key.startswith('UV_') or key == 'UV_CACHE_DIR')}
        env.update(PYTHONDONTWRITEBYTECODE='1', TMPDIR='/var/tmp', UV_NO_CONFIG='1',
                   UV_DEFAULT_INDEX='https://pypi.org/simple')
        exporter_hash = hashlib.sha256((clone / 'scripts/export_report.py').read_bytes()).hexdigest()
        if (clone / '.venv').exists():
            raise RuntimeError('Project environment was not initially absent')
        if args.full_validation:
            # Keep outputs outside the clone: the portfolio runner checks every
            # tracked source byte before/after its own historical checkouts.
            canonical = Path(tmp) / 'canonical.json'
            portfolio = Path(tmp) / 'portfolio.json'
            commands[4:4] = [
                ['uv', 'run', '--frozen', 'python', 'scripts/release_tests.py', '--out', str(canonical)],
                ['uv', 'run', '--frozen', 'python', 'scripts/portfolio_replay.py', 'run', '--out', str(portfolio)],
                ['uv', 'run', '--frozen', 'python', 'scripts/portfolio_replay.py', 'check', '--out', str(portfolio)],
            ]
        for command in commands:
            proc = subprocess.run(command, cwd=clone, env=env, text=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, timeout=1200 if args.full_validation else 360)
            records.append({'argv': command, 'returncode': proc.returncode,
                            'stdout': proc.stdout, 'stderr': proc.stderr})
            if proc.returncode:
                Path(args.out).write_text(json.dumps({
                    'passed': False, 'result_revision': revision, 'commands': records,
                    'scope': 'Incomplete clean-origin acceptance; see failed command. No success claim.'
                }, indent=2) + '\n')
                raise RuntimeError(proc.stdout + proc.stderr)
        if args.full_validation:
            tests = json.loads(canonical.read_text())
            replay = json.loads(portfolio.read_text())
            checked = json.loads(next(row['stdout'] for row in records
                if 'scripts/portfolio_replay.py' in row['argv'] and 'check' in row['argv']))
            if not (tests['passed'] is True and tests['tests'] == 926
                    and tests['failures'] == tests['errors'] == 0
                    and replay['passed'] is True
                    and replay['llm_chat_attempts_in_passing_workers'] == 0
                    and checked['passed'] is True
                    and checked['archived_result_objects'] == 54
                    and checked['completed_analyses'] == 52
                    and checked['failure_audits'] == 2
                    and checked['existing_independent_checkers'] == 50):
                raise RuntimeError('Full acceptance coverage differs from frozen release')
            full_validation = {'canonical_tests': tests, 'primary_replays': replay,
                               'primary_replay_receipt_check': checked}
        interpreter = json.loads(records[2]['stdout'])
        if Path(interpreter['executable']).absolute() != clone / '.venv/bin/python':
            raise RuntimeError('Commands did not use the new clone project environment')
        if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != runner_hash:
            raise RuntimeError('Acceptance runner changed during execution')
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
              'exporter_sha256': exporter_hash,
              'acceptance_runner_sha256': runner_hash, 'acceptance_runner_revision': revision,
              'project_interpreter': interpreter,
              'environment_scope': 'Removed inherited Python path/home/optimization and UV settings except '
                                   'cache directory; config disabled, public default index. Host, network and '
                                   'cache state reused; not a network sandbox.',
              'full_validation': full_validation,
              'scope': 'Documented setup, five selected replays, reader build/PDF extraction and exact '
                       'eight-file comparison. Reused caches, export environment, Chromium and host '
                       'libraries; no empty-cache, cross-host or independent scientific-validity claim. '
                       + ('Also executed 926 canonical tests with zero recorded failures/errors and the documented historical fixtures, '
                          '52 primary analyses, two failure audits and 50 existing checkers in this '
                          'origin clone. Inner historical replay checkouts are local clones; checker '
                          'depth varies. No new scientific decisions or independent replication.'
                          if args.full_validation else 'Full validation was not requested.')}
    Path(args.out).write_text(json.dumps(record, indent=2) + '\n')
    print('PASS clean-origin documented setup and reader reproduction at ' + revision)


if __name__ == '__main__':
    main()
