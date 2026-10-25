"""In-memory probes for the actual export-review findings; archives untouched."""
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import export_report as export
from pypdf import PdfReader
from pypdf.generic import NameObject, TextStringObject


def main():
    checks = []
    material = export.sources()
    def reject(name, action, expected):
        try:
            action()
        except ValueError as error:
            if expected not in str(error):
                raise
            checks.append({'probe': name, 'rejected': True, 'reason': str(error)})
        else:
            raise RuntimeError('Probe accepted: ' + name)
    reject('missing_figure_marker', lambda: export.page('BRIEF', material['BRIEF'].replace(
        '**Why none is promoted:**', '**Promotion caveat:**', 1)), 'figure insertion marker')
    lines = material['BRIEF'].splitlines()
    first = next(i for i, line in enumerate(lines) if line.startswith('| [S29:'))
    second = next(i for i, line in enumerate(lines) if line.startswith('| [S62:'))
    lines[first], lines[second] = lines[second], lines[first]
    reject('reordered_complete_rows_with_same_fragments', lambda: export.pdf_checks('BRIEF', '\n'.join(lines)),
           'missing or reordered complete table row')
    reader = PdfReader(export.ROOT / 'REPORT.pdf')
    changed = False
    for page in reader.pages:
        for annotation in page.get('/Annots', []):
            action = annotation.get_object().get('/A', {})
            if action.get('/URI') == 'BRIEF.pdf':
                action[NameObject('/URI')] = TextStringObject('file:///var/tmp/other-machine/BRIEF.pdf')
                changed = True
    export.require(changed, 'Expected portable link absent')
    with patch('pypdf.PdfReader', return_value=reader):
        reject('machine_local_pdf_link', lambda: export.pdf_checks('REPORT', material['REPORT']), 'Machine-local PDF link')
    export.verify_sources()
    record = {'passed': True, 'archive_writes': False, 'probes': checks,
              'export_source_sha256': export.sha((export.ROOT / 'scripts/export_report.py').read_bytes()),
              'probe_source_sha256': export.sha(Path(__file__).read_bytes()),
              'command_argv': sys.argv,
              'scope': 'In-memory checks of missing-figure, row-order and PDF-link regressions; scientific archives unchanged.'}
    (export.ROOT / 'logs/iteration56_negative_checks.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record))


if __name__ == '__main__':
    main()
