"""Run canonical checks after README compression, preserving historical test inputs.

Only three legacy S60 document tests read the pre-compression README. Frozen
tests, scientific validators, data and current presentation files stay intact.
Current presentation checks run separately against the actual current files.
"""
import argparse
from contextlib import ExitStack, contextmanager
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import s65_tests as legacy

README_REVISION = '73492a929c2245a033f1b1598a03703c3f6f6ee6'
NAMES = ['test_front_report_drift_is_rejected_without_rewriting',
         'test_readme_false_claim_is_rejected',
         'test_later_pilots_can_append_and_archive_the_front_summary']


@contextmanager
def archived_readme_fixture():
    archived = subprocess.check_output(['git', 'show', README_REVISION + ':README.md'], cwd=ROOT)
    readme_path = (ROOT / 'README.md').resolve()
    with ExitStack() as stack:
        for name in NAMES:
            original = getattr(legacy.test_s60_presentation.Tests, name)

            def scoped(self, original=original):
                # Capture inside the invocation, preserving the existing nested
                # split-index fixture installed by legacy.fixture().
                previous = Path.read_bytes

                def read(path, *args, **kwargs):
                    return archived if path.resolve() == readme_path else previous(path, *args, **kwargs)

                with patch.object(Path, 'read_bytes', new=read):
                    return original(self)

            stack.enter_context(patch.object(legacy.test_s60_presentation.Tests, name, new=scoped))
        yield {'readme_revision': README_REVISION,
               'archived_readme_sha256': hashlib.sha256(archived).hexdigest(),
               'named_tests': NAMES,
               'scope': 'Only these historical S60 tests read archived README bytes; '
                        'all other reads and actual scientific validation remain unchanged.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    checked = subprocess.run([sys.executable, 'scripts/export_report.py', '--check'], cwd=ROOT,
                             capture_output=True, text=True, check=True)
    with archived_readme_fixture() as presentation_fixture, legacy.fixture():
        from scripts.repository_tests import run
        run(args.out)
    path = Path(args.out)
    record = json.loads(path.read_text())
    record['legacy_readme_fixture'] = presentation_fixture
    record['actual_current_presentation_check'] = json.loads(checked.stdout)
    path.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
