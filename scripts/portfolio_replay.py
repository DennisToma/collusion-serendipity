"""Replay archived results in disposable, revision-pinned local clones.

No new decisions, tuning, outcome pooling, or archive repairs. The llm.chat
guard is installed before importing scientific modules; it is not a network
sandbox. Existing project dependencies and host libraries are reused.
"""
import argparse
import contextlib
from functools import lru_cache
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BASELINE = 'a9b3c47654c1f694b253a4b8ab70477a2731aa5d'
OUT = 'logs/iteration58_portfolio_replay.json'
SPECIAL_REVISIONS = {
    'S67': '15b318959aa08eccd2b7d0b19768f6dde539352f',
    'S68': '043d3577e614e7858c9a97843fa1d05143315510',
    'S72': '793a6411f6d7b646b1897d964b531cbaa7116cc0',
}
REPLAY_IDS = {40, 43, 44, 47, 48, 50, 51, 55, 58, 59, 61}
POSTHOC = {53: 'payoffs', 56: 'coalitions', 67: 'audit', 72: 'temporal'}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def packed(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def canonical(value):
    """Ignore object-key order; retain JSON numeric/boolean types and values."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':'))


def preserved():
    mutable = {'STATUS.md', 'REPORT.md', 'README.md', 'scripts/export_report.py',
               'BRIEF.html', 'BRIEF.pdf', 'REPORT.html', 'REPORT.pdf'}
    count = 0
    for line in git(ROOT, 'ls-tree', '-r', BASELINE).decode().splitlines():
        meta, name = line.split('\t', 1)
        if name in mutable:
            continue
        data = (ROOT / name).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == meta.split()[2], 'Baseline evidence changed: ' + name)
        count += 1
    old_report = git(ROOT, 'show', BASELINE + ':REPORT.md').decode()
    require([r for r in old_report.splitlines() if r.startswith('| S')] ==
            [r for r in (ROOT / 'REPORT.md').read_text().splitlines() if r.startswith('| S')], 'Original pilot rows changed')
    old_log = git(ROOT, 'show', BASELINE + ':STATUS.md').decode().split('## Log\n', 1)[1]
    require((ROOT / 'STATUS.md').read_text().split('## Log\n', 1)[1].startswith(old_log), 'Historical STATUS log changed')
    return count


def output_path(out):
    path = Path(out).resolve()
    if path.is_relative_to(ROOT):
        require(path.parent == ROOT / 'logs' and path.name.startswith('iteration58_')
                and path.suffix == '.json', 'Repository output must be logs/iteration58_*.json')
    return path


def specs(root):
    # Use the existing explicit table-source map, never infer a result from a
    # file glob. The complete inventory fixes the exact set and ordering.
    sys.path.insert(0, str(root))
    from scripts.iteration55_claims import SOURCES
    inventory = json.loads((root / 'results/iteration54_portfolio.json').read_text())
    rows = []
    for pilot in inventory['pilots']:
        pid = pilot['id']
        n = int(pid[1:])
        result = SOURCES[pid]
        stem = Path(result).stem
        data = 'data/' + stem
        if n == 1:
            data = 'data/s01_prices'
        if n == 2:
            data = 'data/s02_cournot_luna'
        if n in POSTHOC:
            data = {53: 'data/s29_notepad', 56: 'data/s14_tender',
                    67: 'data/s65_bonus_pooling', 72: 'data/s29_notepad'}[n]
        if n in POSTHOC:
            module = f'scripts.s{n:02d}_' + POSTHOC[n]
        elif n in REPLAY_IDS:
            module = f'scripts.s{n:02d}_replay'
        else:
            module = f'scripts.s{n:02d}_analyze'
        if n == 1:
            module = 'scripts.s01_digits'
        if n == 16:
            module, data = 'scripts.s16_failure_audit', 'data/s16_tender'
        if n == 68:
            module, data = 'scripts.s68_failure_audit', 'data/s68_polarity'
        checker = None
        if n in {3, 4}:
            checker = [f'scripts.s{n:02d}_verify', 'main']
        elif n == 7:
            checker = ['scripts.s07_independent', 'main']
        elif n in {6, 11, 14}:
            checker = [f'scripts.s{n:02d}_' + ('checked_independent' if n == 6 else 'independent'), 'check_out']
        elif n in {18, 19, 22, 24}:
            checker = [f'scripts.s{n:02d}_checked_independent', 'checked_verify']
        elif n in {21, 25}:
            checker = [f'scripts.s{n:02d}_independent', 'check']
        elif n not in {1, 2, 16, 68}:
            checker = [f'scripts.s{n:02d}_independent', 'verify_result' if n in POSTHOC else 'verify']
        require((root / data).is_dir(), 'Missing main/source data root: ' + pid)
        if pid in SPECIAL_REVISIONS:
            references = [r['commit'] for r in pilot['experiment_records'] if r['id'] == pid + '-result']
            require(references == [SPECIAL_REVISIONS[pid]], 'Historical revision differs from result ledger')
            subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', SPECIAL_REVISIONS[pid], BASELINE], check=True)
        rows.append(dict(pilot=pid, category=pilot['category'], result=result,
                         data=data, analyzer=module, checker=checker,
                         analyzer_input=('fixed dataset names' if n == 1 else 'fixed source paths' if n in POSTHOC else 'data directory argument'),
                         checker_log=(f'logs/s{n:02d}_' + ('verification' if n in {3, 4} else 'independent') + '.json') if checker else None,
                         revision=SPECIAL_REVISIONS.get(pid, git(root, 'rev-parse', BASELINE).decode().strip())))
    require(len(rows) == 54 and len({r['pilot'] for r in rows}) == 54, 'Incomplete portfolio')
    return rows


def evidence_snapshot(root):
    paths = git(root, 'ls-files', '-z').decode().split('\0')[:-1]
    hashes = {name: sha((root / name).read_bytes()) for name in paths}
    # Also cover ignored caches/outputs under data, except regenerable locks.
    for path in (root / 'data').rglob('*'):
        if path.is_file() and path.name != '.writer.lock':
            hashes[str(path.relative_to(root))] = sha(path.read_bytes())
    return hashes


@lru_cache(maxsize=4)
def pinned_evidence(revision):
    """Bind recorded before/after manifests to the actual immutable Git tree."""
    with tempfile.TemporaryDirectory(dir='/var/tmp', prefix='portfolio_manifest_') as tmp:
        clone = Path(tmp)/'repo'
        subprocess.run(['git', 'clone', '-q', '--shared', '--no-checkout', str(ROOT), str(clone)], check=True, timeout=90)
        subprocess.run(['git', 'checkout', '-q', '--detach', revision], cwd=clone, check=True, timeout=60)
        return evidence_snapshot(clone)


def worker(root, spec):
    os.chdir(root)
    sys.path.insert(0, str(root))
    sys.path.insert(1, str(root / 'scripts'))
    require(__debug__, 'Do not use Python -O')
    before = evidence_snapshot(root)
    capture = io.StringIO()
    checked = None
    # Import transport before scientific modules, including their aliases.
    with patch('llm.chat', side_effect=RuntimeError('Portfolio replay forbids scientific model calls')) as guard:
        with contextlib.redirect_stdout(capture):
            mod = importlib.import_module(spec['analyzer'])
            n = int(spec['pilot'][1:])
            if n == 1:
                actual = {name: mod.analyze(name) for name in ['llm_v1', 'llm_ds_p2']}
            elif n == 16:
                actual = mod.audit(spec['data'])
            elif n == 68:
                actual = mod.verify(spec['data'])
            elif n in POSTHOC:
                actual = mod.analyze()
            else:
                actual = mod.analyze(Path(spec['data']))
            saved = json.loads(Path(spec['result']).read_text())
            # Ignore key ordering/tuple representation, but preserve bool/int/
            # float distinctions, full finite numbers and every result field.
            require(canonical(actual) == canonical(saved), 'Archived result differs: ' + spec['pilot'])
            if spec['checker']:
                name, function = spec['checker']
                independent = importlib.import_module(name)
                if function == 'main':
                    log = f'logs/s{n:02d}_' + ('independent' if n == 7 else 'verification') + '.json'
                    # Observe the current invocation's actual write, so a
                    # committed checker log cannot stand in for fresh output.
                    target = Path(log).resolve()
                    writes = []
                    write_text = Path.write_text
                    def observed(path, text, *args, **kwargs):
                        if path.resolve() == target:
                            writes.append(json.loads(text))
                        return write_text(path, text, *args, **kwargs)
                    with patch.object(Path, 'write_text', new=observed):
                        independent.main()
                    require(len(writes) == 1, 'Checker did not freshly write its output')
                    checked = writes[0]
                    require(checked == json.loads(Path(log).read_text()), 'Checker write/read differs')
                elif function == 'check_out':
                    with tempfile.TemporaryDirectory(dir='/var/tmp', prefix='portfolio_checker_') as tmp:
                        output = str(Path(tmp) / 'checker.json')
                        independent.check(spec['data'], spec['result'], output)
                        checked = json.loads(Path(output).read_text())
                elif function == 'verify_result':
                    checked = independent.verify(actual)
                else:
                    checked = getattr(independent, function)(spec['data'], spec['result'])
                require(isinstance(checked, dict) and checked and checked.get('passed', True), 'Independent checker failed')
                require(canonical(checked) == canonical(json.loads(Path(spec['checker_log']).read_text())),
                        'Fresh checker receipt differs from archive')
    require(guard.call_count == 0, 'Attempted scientific model call')
    require(before == evidence_snapshot(root), 'Replay changed evidence or tracked files')
    require(git(root, 'status', '--porcelain') == b'', 'Replay changed checkout')
    ignored = git(root, 'ls-files', '--others', '--ignored', '--exclude-standard', '-z').decode().split('\0')
    require(all(not p or Path(p).name == '.writer.lock' for p in ignored),
            'Replay left ignored output/cache outside the permitted writer locks')
    modules = {}
    for name, mod in list(sys.modules.items()):
        path = getattr(mod, '__file__', None)
        if path:
            path = Path(path).resolve()
            original = os.environ.get('PORTFOLIO_SOURCE_ROOT')
            require(not original or not path.is_relative_to(Path(original).resolve())
                    or path.is_relative_to(Path(sys.prefix).resolve()),
                    'Imported a module from the source checkout: ' + str(path))
            if path.is_relative_to(root) and path.suffix == '.py':
                modules[str(path.relative_to(root))] = sha(path.read_bytes())
    return dict(passed=True, specification=spec, exact_complete_result_match=True,
                result_sha256=sha(Path(spec['result']).read_bytes()),
                evidence_files_unchanged=len(before), evidence_manifest_sha256=sha(packed(before)),
                clone_clean=True, llm_chat_attempts=guard.call_count,
                independent_checker=checked,
                checker_success_basis=('not available' if checked is None else
                    'explicit passed=true and no exception' if checked.get('passed') is True else
                    'completed without exception; nonempty returned/freshly written receipt'),
                checker_scope=('No additional independent checker in this runner' if checked is None else 'Existing archived checker; coverage is pilot-specific'),
                imported_repo_sources=modules, captured_stdout_sha256=sha(capture.getvalue().encode()))


def run(out):
    require(__debug__, 'Do not use Python -O')
    target = git(ROOT, 'rev-parse', BASELINE).decode().strip()
    require(git(ROOT, 'rev-parse', '--is-shallow-repository') == b'false\n', 'Use full Git history')
    output = output_path(out)
    plan = specs(ROOT)
    protected = preserved()
    before = evidence_snapshot(ROOT)
    records = []
    script_hash = sha(Path(__file__).read_bytes())
    with tempfile.TemporaryDirectory(dir='/var/tmp', prefix='portfolio_replay_') as tmp:
        runner = Path(tmp) / 'worker.py'
        runner.write_bytes(Path(__file__).read_bytes())
        clone = Path(tmp) / 'repo'
        subprocess.run(['git', 'clone', '--quiet', '--shared', '--no-checkout', str(ROOT), str(clone)], check=True, timeout=90)
        revision = None
        for spec in plan:
            if revision != spec['revision']:
                subprocess.run(['git', 'checkout', '--quiet', '--detach', spec['revision']], cwd=clone, check=True, timeout=60)
                revision = spec['revision']
            require(sha((clone / spec['result']).read_bytes()) == sha((ROOT / spec['result']).read_bytes()), 'Historical/current artifact differs')
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(clone),
                       OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                       PYTHONHASHSEED='0', PORTFOLIO_SOURCE_ROOT=str(ROOT))
            env.pop('PYTHONOPTIMIZE', None)
            command = [sys.executable, str(runner), 'worker', '--root', str(clone), '--spec', json.dumps(spec)]
            proc = subprocess.run(command, cwd=clone, env=env, text=True, capture_output=True, timeout=240)
            if proc.returncode:
                records.append(dict(passed=False, specification=spec, exit=proc.returncode, stdout=proc.stdout, stderr=proc.stderr))
                print(spec['pilot'] + ' FAILED', flush=True)
            else:
                records.append(json.loads(proc.stdout))
                print(spec['pilot'] + ' PASS', flush=True)
        require(sha(runner.read_bytes()) == script_hash, 'Copied worker changed during replay')
    unchanged = before == evidence_snapshot(ROOT)
    source_unchanged = script_hash == sha(Path(__file__).read_bytes())
    result = dict(passed=all(r['passed'] for r in records) and unchanged and source_unchanged, baseline_commit=target,
                  runner_sha256=script_hash, records=records,
                  special_revisions=SPECIAL_REVISIONS, protected_baseline_files=protected,
                  scope='All 54 archived result objects (52 completed analyses, two failure audits); exact result equality plus available existing checkers. Validation depth varies by pilot. Not an independent scientific validity audit, a new experiment, network isolation, fresh installation, or cross-platform reproduction.',
                  project_python=sys.version,
                  llm_chat_attempts_in_passing_workers=sum(r.get('llm_chat_attempts', 0) for r in records if r['passed']),
                  full_history_local_clone=True, existing_installed_dependencies_reused=True,
                  origin_clone=False, source_checkout_preserved=unchanged, runner_unchanged=source_unchanged)
    temporary = output.with_name(output.name + '.tmp')
    temporary.write_bytes(packed(result))
    temporary.replace(output)
    require(result['passed'], 'Some portfolio replays failed; see ' + str(out))


def check(receipt):
    """Check Git-committed receipt consistency, without asserting execution anew."""
    require(receipt['passed'] is True, 'Replay did not pass')
    require(receipt['baseline_commit'] == BASELINE, 'Wrong baseline')
    require(receipt['runner_sha256'] == sha(Path(__file__).read_bytes()), 'Runner differs from receipt')
    require(receipt['source_checkout_preserved'] is True and receipt['runner_unchanged'] is True, 'Source changed')
    require(receipt['llm_chat_attempts_in_passing_workers'] == 0, 'Unexpected model call attempts')
    require(receipt['special_revisions'] == SPECIAL_REVISIONS, 'Historical revision exceptions differ')
    require(receipt['protected_baseline_files'] == preserved(), 'Preserved baseline coverage differs')
    require(receipt['full_history_local_clone'] is True and receipt['origin_clone'] is False,
            'Incorrect clone scope')
    require(receipt['existing_installed_dependencies_reused'] is True, 'Incorrect install scope')
    plan = specs(ROOT)
    require([r['specification'] for r in receipt['records']] == plan, 'Portfolio/specification coverage differs')
    source_cache = {}
    for record, spec in zip(receipt['records'], plan):
        require(record['passed'] is True and record['exact_complete_result_match'] is True, 'Result did not match')
        require(record['llm_chat_attempts'] == 0 and record['clone_clean'] is True, 'Replay guard/checkout failure')
        require(record['result_sha256'] == sha((ROOT / spec['result']).read_bytes()), 'Current result hash differs')
        require(record['result_sha256'] == sha(git(ROOT, 'show', spec['revision'] + ':' + spec['result'])), 'Pinned result differs')
        require(bool(record['independent_checker']) == bool(spec['checker']), 'Checker coverage differs')
        require(record['independent_checker'] is None or record['independent_checker'].get('passed', True), 'Checker failed')
        if spec['checker']:
            require(canonical(record['independent_checker']) == canonical(json.loads(
                git(ROOT, 'show', spec['revision'] + ':' + spec['checker_log']))), 'Checker receipt differs from pinned Git')
        manifest = pinned_evidence(spec['revision'])
        require(record['evidence_files_unchanged'] == len(manifest), 'Evidence file count differs')
        require(record['evidence_manifest_sha256'] == sha(packed(manifest)), 'Evidence manifest differs from pinned Git')
        modules = record['imported_repo_sources']
        require('llm.py' in modules and spec['analyzer'].replace('.', '/') + '.py' in modules, 'Core imported source missing')
        if spec['checker']:
            require(spec['checker'][0].replace('.', '/') + '.py' in modules, 'Checker source missing')
        for name, digest in modules.items():
            key = (spec['revision'], name)
            if key not in source_cache:
                source_cache[key] = sha(git(ROOT, 'show', spec['revision'] + ':' + name))
            require(digest == source_cache[key], 'Imported source differs from Git: ' + name)
            require(digest == sha((ROOT / name).read_bytes()), 'Current scientific source changed: ' + name)
    failures = sum(p['category'] == 'FAILED' for p in plan)
    return dict(passed=True, archived_result_objects=len(plan), completed_analyses=len(plan)-failures, failure_audits=failures,
                existing_independent_checkers=sum(bool(p['checker']) for p in plan),
                imported_revision_source_bindings=sum(len(r['imported_repo_sources']) for r in receipt['records']),
                scope='Receipt consistency with pinned Git objects and current scientific sources; no new execution attestation')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['run', 'worker', 'check'])
    parser.add_argument('--out', default=OUT)
    parser.add_argument('--root', type=Path)
    parser.add_argument('--spec')
    args = parser.parse_args()
    if args.mode == 'worker':
        try:
            print(json.dumps(worker(args.root.resolve(), json.loads(args.spec))))
        except Exception:
            traceback.print_exc()
            raise SystemExit(1)
    elif args.mode == 'check':
        require(__debug__, 'Do not use Python -O')
        print(json.dumps(check(json.loads(Path(args.out).read_text())), indent=2))
    else:
        run(args.out)


if __name__ == '__main__':
    main()
