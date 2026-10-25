"""Read-only negative controls plus link verification; no scientific byte writes."""
import contextlib
import copy
from fractions import Fraction
import io
import json
from pathlib import Path
import re
import sys
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    from scripts.s72_temporal import ARTIFACTS, checked_manifest, digest, release, write
    from scripts.s72_independent import verify
    from scripts.s72_present import documents
    m = checked_manifest()
    before = {p: digest(p) for p in ARTIFACTS}
    result = json.loads(Path(ARTIFACTS[0]).read_text())
    verify(result)
    probes = []
    def corrupt(label, change):
        r = copy.deepcopy(result)
        change(r)
        try:
            verify(r)
        except (AssertionError, ValueError, KeyError):
            probes.append(label)
        else:
            raise AssertionError('Corruption accepted: '+label)
    corrupt('individual window gain', lambda r: r['games'][0]['excess'].__setitem__(next(iter(r['games'][0]['excess'])), 123456))
    corrupt('window boundary', lambda r: r['two_round_windows'][0].__setitem__('rounds', [4, 5]))
    corrupt('raw decoded action', lambda r: r['rounds'][0]['actions'].__setitem__(next(iter(r['rounds'][0]['actions'])), not next(iter(r['rounds'][0]['actions'].values()))))
    corrupt('missing metric', lambda r: r['metrics'].pop('stage_both_gain'))
    corrupt('exact rational endpoint', lambda r: r['metrics']['stage_both_gain']['difference']['ci95_exact'].__setitem__(0,
        str(Fraction(r['metrics']['stage_both_gain']['difference']['ci95_exact'][0])+Fraction(1, 10**13))))
    corrupt('embedded provenance', lambda r: r['registration_receipt'].__setitem__('commit', '0'*40))
    corrupt('opportunity denominator', lambda r: r['games'][0]['opportunities'].__setitem__('y', 16))
    original_bytes = Path.read_bytes
    raw_path = Path('data/s29_notepad/raw/responses.jsonl').resolve()
    def changed_bytes(path, *a, **kw):
        data = original_bytes(path, *a, **kw)
        return data+b'\n' if path.resolve() == raw_path else data
    with patch.object(Path, 'read_bytes', new=changed_bytes):
        try:
            checked_manifest()
        except ValueError as e:
            assert 'file changed' in str(e)
            probes.append('source raw bytes')
        else:
            raise AssertionError('Source raw mutation accepted')
    original_text = Path.read_text
    editorial = []
    for target in ['REPORT.md', 'REPORT_DETAILS.md', 'HITS.md', 'README.md']:
        absolute = Path(target).resolve()
        def changed_text(path, *a, **kw):
            data = original_text(path, *a, **kw)
            return data+'\nEDITORIAL CANARY\n' if path.resolve() == absolute else data
        with patch.object(Path, 'read_text', new=changed_text), patch.object(Path, 'write_text', side_effect=AssertionError('Write before all validations')):
            try:
                documents()
            except ValueError as e:
                assert 'Unexpected document edit' in str(e)
                editorial.append(target)
            else:
                raise AssertionError('Editorial mutation accepted: '+target)
    with contextlib.redirect_stdout(io.StringIO()):
        release()
        docs = documents(check=True)
    assert before == {p: digest(p) for p in ARTIFACTS}
    links = 0
    for document in [*map(Path, ['REPORT.md', 'REPORT_DETAILS.md', 'HITS.md', 'README.md']), Path('results/s72_summary.md')]:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', document.read_text()):
            target = target.split('#')[0]
            if not target or '://' in target or target.startswith('mailto:'):
                continue
            path = document.parent/target
            assert path.exists(), (str(document), target)
            links += 1
    checked = dict(passed=True, result_or_source_corruptions_rejected=probes,
        prewrite_document_corruptions_rejected=editorial, mutations='in memory/read interception only; archive bytes untouched',
        older_scientific_paths=len(m['older_science_sha256']), source_and_input_paths=len(m['input_and_source_sha256']),
        artifact_sha256=before, documents=docs, local_links=links)
    write('logs/s72_postcheck.json', checked)
    print(json.dumps(checked, indent=2))


if __name__ == '__main__':
    main()
