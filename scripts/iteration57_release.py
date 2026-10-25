"""Current-tree preservation and fresh-install receipt rejection probes."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import iteration57_fresh_install as fresh


def main():
    mutable = {'REPORT.md', 'README.md', 'STATUS.md', 'scripts/export_report.py',
               'BRIEF.html', 'BRIEF.pdf', 'REPORT.html', 'REPORT.pdf'}
    count = 0
    for row in fresh.git('ls-tree', '-r', fresh.TARGET).decode().splitlines():
        meta, name = row.split('\t', 1)
        if name in mutable:
            continue
        data = (ROOT / name).read_bytes()
        actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        fresh.require(actual == meta.split()[2], 'Previous file changed: ' + name)
        count += 1
    previous = fresh.git('show', fresh.TARGET + ':STATUS.md').decode().split('## Log\n', 1)[1]
    fresh.require((ROOT / 'STATUS.md').read_text().split('## Log\n', 1)[1].startswith(previous), 'Historical log changed')
    old_rows = [r for r in fresh.git('show', fresh.TARGET + ':REPORT.md').decode().splitlines() if r.startswith('| S')]
    fresh.require(old_rows == [r for r in (ROOT / 'REPORT.md').read_text().splitlines() if r.startswith('| S')], 'Pilot rows changed')
    receipt = json.loads((ROOT / fresh.RECEIPT).read_text())
    checked = fresh.check(receipt)
    probes = {}
    cases = {
        'failed_run': lambda r: r.update(passed=False),
        'target_revision': lambda r: r.update(target_revision='0' * 40),
        'artifact_hash': lambda r: r['byte_identical_artifacts'].update({'BRIEF.pdf': '0' * 64}),
        'failed_stage': lambda r: r['commands'][4].update(exit=1),
        'missing_stage': lambda r: r['commands'].pop(),
        'installed_version': lambda r: r['environments']['export']['packages'][0].update(version='0.0'),
        'canonical_count': lambda r: r['canonical_tests'].update(tests=925),
        'external_site': lambda r: r['environments']['project'].update(external_site_paths=['/host/site-packages']),
        'external_package': lambda r: r['environments']['export']['packages'][0].update(inside_prefix=False),
        'dirty_clone': lambda r: r.update(clone_clean=False),
        'lock_hash': lambda r: r.update(export_lock_sha256='0' * 64),
        'replay_count': lambda r: r['selected_replay'].update(selected_replays=4),
        'checkout_arguments': lambda r: r['commands'][1]['command'].__setitem__(-1, '0' * 40),
        'contradictory_stdout': lambda r: r['commands'][4].update(stdout='{"passed": false}'),
        'missing_stdout': lambda r: r['commands'][4].pop('stdout'),
    }
    for name, mutate in cases.items():
        altered = deepcopy(receipt)
        mutate(altered)
        try:
            fresh.check(altered)
        except RuntimeError:
            probes[name] = 'rejected'
        else:
            raise RuntimeError('Corruption accepted: ' + name)
    from scripts import export_report
    export_record = json.loads((ROOT / export_report.EXPORT_RECEIPT).read_text())
    export_report.check_coverage(export_record)
    for group in ['files', 'source_hashes']:
        altered = deepcopy(export_record)
        altered[group].pop(next(iter(altered[group])))
        try:
            export_report.check_coverage(altered)
        except ValueError:
            probes['missing_export_' + group] = 'rejected'
        else:
            raise RuntimeError('Incomplete export receipt accepted: ' + group)
    record = {'passed': True, 'unchanged_prior_files': count, 'original_pilot_rows': len(old_rows),
              'fresh_receipt_check': checked, 'rejected_in_memory_probes': probes,
              'scope': 'Current-tree preservation and receipt consistency, not fresh execution or external attestation.'}
    (ROOT / 'logs/iteration57_release.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record))


if __name__ == '__main__':
    main()
