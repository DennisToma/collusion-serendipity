"""Reproduce the archived reader handoff using newly installed dependencies.

The target is fixed, so later editorial updates cannot change this experiment.
Downloads require network access; scientific replays retain the existing call
guard. The host OS, system libraries/fonts, Python and uv are reused.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
TARGET = 'e6b0c02bb189923b3fd039fe67db153826ee3aff'
RECEIPT = 'logs/iteration57_fresh_install.json'
EXPORT_LOCK = 'requirements-export.lock'
ARTIFACTS = ['BRIEF.html', 'BRIEF.pdf', 'REPORT.html', 'REPORT.pdf',
             'figures/explorer_handoff.png', 'logs/iteration56_exports.json',
             'REPORT.md', 'README.md']


def require(value, message):
    if not value:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def check(record=None):
    record = record or json.loads((ROOT / RECEIPT).read_text())
    require(record['passed'], 'Fresh installation did not pass')
    require(record['target_revision'] == git('rev-parse', TARGET).decode().strip(), 'Wrong target revision')
    require(record['runner_sha256'] == sha(Path(__file__).read_bytes()), 'Runner changed')
    require(record['initial_empty_paths'] == ['uv-cache', 'browsers', 'project-env', 'export-env'], 'Missing isolation')
    require(record['clone_clean'], 'Reproduction clone dirty')
    require(record['project_lock_sha256'] == sha(git('show', TARGET + ':uv.lock')), 'Wrong project lock')
    require(record['export_lock_sha256'] == sha((ROOT / EXPORT_LOCK).read_bytes()), 'Export lock changed')
    require(record['uv_config_disabled'] and record['default_index'] == 'https://pypi.org/simple', 'Index/config drift')
    require(record['actual_clone_revision'] == TARGET, 'Actual clone revision differs')
    stages = ['clone', 'checkout', 'project-install', 'project-inventory', 'selected-replay',
              'canonical-tests', 'export-venv', 'export-install', 'export-inventory',
              'browser-install', 'export-build']
    require([s['stage'] for s in record['commands']] == stages, 'Incomplete stage list')
    require(all(s['exit'] == 0 for s in record['commands']), 'A stage failed')
    for name, value in record['byte_identical_artifacts'].items():
        require(value == sha(git('show', TARGET + ':' + name)), 'Artifact hash differs: ' + name)
    require(set(record['byte_identical_artifacts']) == set(ARTIFACTS), 'Artifact coverage differs')
    require(record['selected_replay']['selected_replays'] == 5, 'Replay count differs')
    require(record['selected_replay']['passed'], 'Selected replay failed')
    require(record['canonical_tests']['passed'] and record['canonical_tests']['tests'] == 926
            and record['canonical_tests']['failures'] == record['canonical_tests']['errors'] == 0,
            'Canonical test suite did not pass')
    require(record['export_check']['pdf_coverage_reextracted'] and record['export_check']['passed'], 'PDF check missing')
    for key in ['project', 'export']:
        info = record['environments'][key]
        require(info['prefix'] != info['base_prefix'] and not info['external_site_paths'], 'Environment leakage')
        require(info['packages'] and all(p['inside_prefix'] for p in info['packages']), 'External installed package')
        actual = {p['name'].lower().replace('_', '-'): p['version'] for p in info['packages']}
        if key == 'project':
            lock = tomllib.loads(git('show', TARGET + ':uv.lock').decode())
            expected = {p['name']: p['version'] for p in lock['package'] if 'virtual' not in p['source']}
        else:
            expected = dict(re.findall(r'^([\w.-]+)==([^\s\\]+)', (ROOT / EXPORT_LOCK).read_text(), re.M))
        require(actual == expected, 'Installed versions differ from complete ' + key + ' lock')
    return {'passed': True, 'target_revision': record['target_revision'],
            'selected_replays': 5, 'canonical_tests': 926, 'byte_identical_artifacts': len(ARTIFACTS)}


INVENTORY = '''import importlib.metadata as m,json,sys
from pathlib import Path
p=Path(sys.prefix).resolve()
def inside(x):return Path(x).resolve().is_relative_to(p)
print(json.dumps(dict(prefix=str(p),base_prefix=sys.base_prefix,python=sys.version,
 external_site_paths=[s for s in sys.path if ('site-packages' in s or 'dist-packages' in s) and not inside(s)],
 packages=sorted([dict(name=d.metadata['Name'],version=d.version,inside_prefix=inside(d.locate_file(''))) for d in m.distributions()],key=lambda d:d['name'].lower()))))
'''


def run(output):
    record = {'passed': False, 'target_revision': TARGET, 'clone_source': 'origin',
              'started_utc': datetime.now(timezone.utc).isoformat(),
              'runner_sha256': sha(Path(__file__).read_bytes()),
              'commands': [], 'environments': {},
              'scope': 'Fresh Python package environments, initially empty uv/browser caches; selected scientific replay and canonical historical synthetic fixtures. Reuses host OS, system libraries/fonts, uv and base Python. Not network-isolated, cross-platform or full-portfolio raw replication.'}
    try:
        revision = git('rev-parse', TARGET).decode().strip()
        remote = git('remote', 'get-url', 'origin').decode().strip()
        record['project_lock_sha256'] = sha(git('show', TARGET + ':uv.lock'))
        record['export_lock_sha256'] = sha((ROOT / EXPORT_LOCK).read_bytes())
        record['uv_config_disabled'] = True
        record['default_index'] = 'https://pypi.org/simple'
        with tempfile.TemporaryDirectory(prefix='iteration57_fresh_', dir='/var/tmp') as tmp:
            scratch = Path(tmp)
            clone = scratch / 'repo'
            paths = {name: scratch / name for name in ['uv-cache', 'browsers', 'project-env', 'export-env']}
            require(not any(p.exists() for p in paths.values()), 'Scratch not empty')
            record['initial_empty_paths'] = list(paths)
            env = {k: v for k, v in os.environ.items() if not k.startswith(('UV_', 'PIP_'))}
            env.update(TMPDIR='/var/tmp', PYTHONDONTWRITEBYTECODE='1', UV_NO_CONFIG='1',
                       UV_CACHE_DIR=str(paths['uv-cache']), PLAYWRIGHT_BROWSERS_PATH=str(paths['browsers']),
                       UV_PROJECT_ENVIRONMENT=str(paths['project-env']), MPLCONFIGDIR=str(scratch / 'mpl'),
                       UV_DEFAULT_INDEX='https://pypi.org/simple')
            for key in ['VIRTUAL_ENV', 'PYTHONPATH', 'PYTHONHOME', 'UV_PYTHON', 'UV_NO_SYNC', 'UV_OFFLINE']:
                env.pop(key, None)
            # The uv executable and base interpreter are host prerequisites.
            base_python = sys._base_executable
            record['host'] = {'base_python': base_python, 'python': sys.version,
                              'uv': subprocess.check_output(['uv', '--version'], text=True).strip(),
                              'platform': sys.platform}

            def command(stage, args, cwd=clone, timeout=600):
                print(stage, flush=True)
                proc = subprocess.run(args, cwd=cwd, env=env, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True, timeout=timeout)
                record['commands'].append({'stage': stage, 'command': args, 'exit': proc.returncode,
                                          'stdout': proc.stdout, 'stderr': proc.stderr})
                require(proc.returncode == 0, stage + ' failed:\n' + proc.stdout + proc.stderr)
                return proc.stdout

            command('clone', ['git', 'clone', '--quiet', remote, str(clone)], cwd=scratch, timeout=120)
            command('checkout', ['git', 'checkout', '--quiet', '--detach', revision], timeout=60)
            record['actual_clone_revision'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=clone, text=True).strip()
            require(not (clone / '.venv').exists(), 'Clone unexpectedly has installed environment')
            command('project-install', ['uv', 'sync', '--frozen', '--python', base_python])
            project_python = str(paths['project-env'] / 'bin/python')
            record['environments']['project'] = json.loads(command('project-inventory', [project_python, '-c', INVENTORY]))
            record['selected_replay'] = json.loads(command('selected-replay',
                ['uv', 'run', '--frozen', 'python', 'scripts/export_report.py', '--check', '--replay-selected']))
            tests = scratch / 'canonical.json'
            command('canonical-tests', ['uv', 'run', '--frozen', 'python', 'scripts/s65_tests.py', '--out', str(tests)])
            record['canonical_tests'] = json.loads(tests.read_text())
            command('export-venv', ['uv', 'venv', '--python', base_python, str(paths['export-env'])])
            export_python = str(paths['export-env'] / 'bin/python')
            command('export-install', ['uv', 'pip', 'install', '--python', export_python,
                                      '--require-hashes', '-r', str(ROOT / EXPORT_LOCK)])
            record['environments']['export'] = json.loads(command('export-inventory', [export_python, '-c', INVENTORY]))
            command('browser-install', [export_python, '-m', 'playwright', 'install', 'chromium'])
            record['export_check'] = json.loads(command('export-build',
                [export_python, 'scripts/export_report.py', '--build', '--check-pdf']))
            hashes = {}
            for name in ARTIFACTS:
                content = (clone / name).read_bytes()
                require(content == git('show', revision + ':' + name), 'Rebuilt artifact differs: ' + name)
                hashes[name] = sha(content)
            record['byte_identical_artifacts'] = hashes
            status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=clone, text=True)
            require(not status, 'Clone became dirty: ' + status)
            record['clone_clean'] = True
            record['passed'] = True
            check(record)
    except Exception as error:
        record['passed'] = False
        record['error'] = str(error)
        raise
    finally:
        record['finished_utc'] = datetime.now(timezone.utc).isoformat()
        output.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(check(record)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['run', 'check'])
    parser.add_argument('--out', type=Path,
                        help='Required for run; use /var/tmp to retain the committed receipt')
    args = parser.parse_args()
    if args.mode == 'run':
        if args.out is None:
            parser.error('run requires --out; use /var/tmp/explorer-fresh-receipt.json to preserve the committed receipt')
        run(args.out)
    else:
        print(json.dumps(check()))
