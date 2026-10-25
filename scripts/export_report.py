"""Render the frozen explorer evidence for judges; no scientific re-estimation.

Verification: uv run --frozen python scripts/export_report.py --check
Rendering needs the separate pinned export environment documented in README.
Existing scientific files and the dependency lock are never rewritten.
"""
import argparse
import base64
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import iteration55_claims as audit

BASELINE = '573f97310771f76fefb67e8d57f666539ad919cb'
REPO_URL = 'https://github.com/DennisToma/collusion-serendipity'
COMMAND = 'uv run --frozen python scripts/export_report.py --check --replay-selected'
EXPORT_RECEIPT = 'logs/iteration58_exports.json'
REPLAY_SOURCE_REVISION = 'cd3505ce141d190d92ecda420430ff74caccf70d'
EXPORT_FILES = ['BRIEF.html', 'BRIEF.pdf', 'REPORT.html', 'REPORT.pdf', 'figures/explorer_handoff.png']
EXPORT_SOURCES = ['scripts/export_report.py', 'REPORT.md', 'README.md', 'results/iteration54_brief.md',
    'scripts/iteration57_fresh_install.py', 'logs/iteration57_fresh_install.json', 'requirements-export.lock',
    'results/iteration57_reproduction.md', 'scripts/portfolio_replay.py',
    'logs/iteration58_portfolio_replay.json', 'results/iteration58_reproduction.md']
EXPORT_ENV = {'markdown-it-py': '4.2.0', 'playwright': '1.64.1', 'pypdf': '6.21.2', 'matplotlib': '3.11.2'}
NOTICE = ('**Reader exports — iteration 58:** [Concise brief (PDF)](BRIEF.pdf) · '
          '[Brief (HTML)](BRIEF.html) · [Complete log (PDF)](REPORT.pdf) · [Complete log (HTML)](REPORT.html). '
          'Exports preserve the saved evidence and original pilot rows. Current verification: '
          f'`{COMMAND}`. The iteration-54/55 full-document commands require their archived revisions.\n\n')
FRESH_NOTICE = ('**Fresh dependency reproduction — iteration 57:** Archived handoff `e6b0c02` reproduced '
    'from new project/export environments and initially empty uv/browser caches: five selected scientific replays, '
    '926 canonical checks (including historical synthetic fixtures) and eight byte-identical artifacts. '
    'Host Python, uv, OS libraries and fonts were reused. '
    'This is selected same-host reproduction, not cross-platform or full-portfolio validation. '
    'Iteration-57 exports were built separately; the current exports use the current export check. '
    'Receipt consistency: `uv run --frozen python scripts/iteration57_fresh_install.py check`. '
    'Instructions and scope: `results/iteration57_reproduction.md`.\n\n')
PORTFOLIO_NOTICE = ('**Primary-result replay — iteration 58:** All **54 primary result objects** '
    'reproduce at pinned revisions: 52 completed analyses and two failure audits; '
    '**50 existing checkers** also run. Fifty-one entries use the frozen baseline and three use '
    'their historical result revisions. Validation depth varies by pilot. '
    '[Coverage, limits and run commands](results/iteration58_reproduction.md).\n\n')
CSS = """
:root { font-family: Arial, sans-serif; color: #192b3e; background: #fff }
body { margin: 0 } main { max-width: 1080px; margin: 32px auto; padding: 0 28px }
h1 { font-size: 28px; line-height: 1.2 } p, li { font-size: 15px; line-height: 1.45 }
a { color: #155a86 } .note { font-size: 12px; color: #52677a }
table { border-collapse: collapse; width: 100%; font-size: 12px; margin: 14px 0; font-variant-numeric: tabular-nums }
th, td { padding: 7px; border: 1px solid #d4dee5; text-align: left; vertical-align: top }
th { background: #edf3f7 } pre { background: #edf3f7; padding: 10px; white-space: pre-wrap }
code { font-size: .86em; overflow-wrap: anywhere } img { display: block; max-width: 100%; height: auto; margin: 18px auto }
.chart { break-inside: avoid } .chart p { font-size: 12px }
@media print {
  @page { size: A4 portrait; margin: 14mm 12mm }
  main { margin: 0; padding: 0; max-width: none }
  h1 { font-size: 19pt; break-after: avoid } p, li { font-size: 9.2pt; line-height: 1.32 }
  table { font-size: 7.3pt; } th, td { padding: 4px 5px } tr { break-inside: avoid }
  thead { display: table-header-group } pre { font-size: 8pt }
  .chart img { max-height: 86mm; margin: 8px auto } .chart p, .note { font-size: 8pt }
}
"""


def require(test, message):
    if not test:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check_coverage(record):
    require(set(record['files']) == set(EXPORT_FILES), 'Export receipt artifact coverage differs')
    require(set(record['source_hashes']) == set(EXPORT_SOURCES), 'Export receipt source coverage differs')


def old(name):
    return audit.git('show', BASELINE + ':' + name)


def replace_once(text, before, after):
    require(text.count(before) == 1, 'Editorial substitution target changed: ' + before[:80])
    return text.replace(before, after, 1)


def documents():
    report = replace_once(old('REPORT.md').decode(), '2026-10-25 · Iteration 55 ·', '2026-10-25 · Iteration 58 ·')
    report = replace_once(report, '**Reading guide — iteration 55:**', NOTICE + PORTFOLIO_NOTICE + FRESH_NOTICE + '**Reading guide — iteration 58:**')
    report = replace_once(report, 'Current offline command: `uv run --frozen python scripts/iteration55_claims.py --check --replay-selected`.',
                            f'Current offline command: `{COMMAND}`.')
    report = replace_once(report, '**Next:** different-axis pilot only if valuable before14:30UTC;then polish.',
                          '**Next:** preserve the frozen evidence and polish the final handoff.')
    readme = old('README.md').decode()
    entry = readme.split('\n\n')[1]
    require(entry.startswith('**Judge / handoff entry:**'), 'README entry moved')
    replacement = NOTICE + PORTFOLIO_NOTICE + FRESH_NOTICE + replace_once(entry,
        'uv run --frozen python scripts/iteration55_claims.py --check --replay-selected', COMMAND)
    replacement += ('\n\nRender with a separate pinned environment (project dependencies and `uv.lock` stay unchanged):\n\n'
        'The Git diff command below checks byte identity on the recording host. On another host, '
        'use the PDF content checks and report any byte differences.\n\n'
        '```bash\nuv venv --python 3.12.15 /var/tmp/explorer-export57\n'
        'uv pip install --python /var/tmp/explorer-export57/bin/python --require-hashes -r requirements-export.lock\n'
        '/var/tmp/explorer-export57/bin/python -m playwright install chromium\n'
        '/var/tmp/explorer-export57/bin/python scripts/export_report.py --build\n'
        '/var/tmp/explorer-export57/bin/python scripts/export_report.py --check-pdf\n'
        'git diff --exit-code -- BRIEF.html BRIEF.pdf REPORT.html REPORT.pdf figures/explorer_handoff.png logs/iteration58_exports.json\n```\n\n'
        'The build uses installed Chromium, embeds the interval figure, and blocks browser network requests. '
        'Source links in the exports point to the frozen evidence revision on GitHub; following them requires repository access. '
        'The archive checks and selected replay use the installed project dependencies and full Git history. '
        'For independent PDF-content checking use the pinned export command with `--check-pdf`. '
        'Plain `--check` verifies consistency with the source/export hashes in the committed receipt; '
        'it reports saved PDF-coverage counts without re-extracting text. '
        '`--check-pdf` re-extracts source text and checks complete table rows in order. '
        'Use the project-environment command above for the five selected scientific replays. '
        'The separate iteration-57 runner downloads and installs both environments and Chromium anew to reproduce '
        'the fixed iteration-56 handoff; its receipt-only check does not rerun installation or validate later checkout edits. '
        'It consumes the complete hash-locked export requirements. To rerun without replacing the committed receipt, use '
        '`uv run --frozen python scripts/iteration57_fresh_install.py run --out /var/tmp/explorer-fresh-receipt.json`. '
        'No full-portfolio raw replication is claimed.')
    return {'REPORT.md': report, 'README.md': replace_once(readme, entry, replacement)}


def preservation():
    mutable = {'REPORT.md', 'README.md', 'STATUS.md'}
    count = 0
    for line in audit.git('ls-tree', '-r', BASELINE).decode().splitlines():
        metadata, name = line.split('\t', 1)
        if name in mutable:
            continue
        data = (ROOT / name).read_bytes()
        require(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == metadata.split()[2],
                'Preexisting file changed: ' + name)
        count += 1
    require((ROOT / 'STATUS.md').read_text().split('## Log\n', 1)[1].startswith(
        old('STATUS.md').decode().split('## Log\n', 1)[1]), 'Historical STATUS log changed')
    return count


def verify_sources():
    protected = preservation()
    result = audit.run()
    saved = json.loads((ROOT / audit.OUT).read_text())
    # preservation() binds the complete historical receipt (including its probe
    # list) to Git. Recompute field checks here; do not claim to rerun old probes.
    del saved['rejected_corruption_probes']
    require(saved == result, 'Saved table receipt differs from current field audit')
    for name, expected in documents().items():
        require((ROOT / name).read_text() == expected, 'Presentation overlay drift: ' + name)
    from scripts.iteration54_handoff import products
    reconstructed = products()
    require(reconstructed['results/iteration54_brief.md'] == (ROOT / 'results/iteration54_brief.md').read_bytes(),
            'Archived brief differs from saved-field/raw-opportunity reconstruction')
    from scripts.iteration57_fresh_install import check
    check()
    from scripts.portfolio_replay import check as check_portfolio
    portfolio = check_portfolio(json.loads((ROOT / 'logs/iteration58_portfolio_replay.json').read_text()))
    return {'protected_files': protected, 'pilot_rows': result['pilot_entries'],
            'numeric_bindings': result['numeric_tokens_checked'], 'metadata_checks': result['metadata_checks'],
            'saved_primary_replay_objects': portfolio['archived_result_objects'],
            'saved_existing_checkers': portfolio['existing_independent_checkers']}


def sources():
    brief = (ROOT / 'results/iteration54_brief.md').read_text()
    brief = replace_once(brief, 'Iteration 54 ·', 'Reader edition · Iteration 58 ·')
    require(brief.count('**Offline verification of this handoff:**') == 1, 'Brief verification block moved')
    brief = brief.split('**Offline verification of this handoff:**', 1)[0]
    brief += ('**Current offline verification:**\n\n```bash\n' + COMMAND + '\n```\n\n'
        'Checks all original report rows and saved numerical bindings, preserves prior evidence, '
        'and replays five selected scientific analyses and separate checkers. '
        'S72 uses its historical revision. This is selected reproduction with a scientific call guard, '
        'not full-portfolio raw validation or network isolation. Use full Git history and the installed pinned project dependencies. '
        'Archived presentation commands require their own revisions.\n')
    # The brief lives at the repository root in the export, unlike its source.
    brief = re.sub(r'\]\(([^)]+)\)', lambda m: '](' + (
        m[1][3:] if m[1].startswith('../') else 'results/' + m[1]) + ')', brief)
    brief += '\n' + PORTFOLIO_NOTICE
    return {'BRIEF': brief, 'REPORT': documents()['REPORT.md']}


def chart():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 3.7), layout='constrained')
    labels = ['S29 · shared − self\ngpt-6-luna', 'S62 · shared − self\nQwen-3.6',
              'S69 · low − high charge\nexpected calibration', 'S70 · endowed − baseline\nfixed income']
    rows = []
    directions = ['shared minus self', 'shared minus self', 'low_charge minus high_charge', 'endowed minus baseline']
    for y, stem in enumerate(['s29_notepad', 's62_notepad_qwen', 's69_pooled_enforcement', 's70_bonus_endowment']):
        obj = json.loads((ROOT / ('results/' + stem + '.json')).read_text())
        require(obj['primary_contrast'] == directions[y], 'Chart direction differs from source')
        d = obj['metrics']['pair_bad']['paired_difference']
        rows.append({'source': 'results/' + stem + '.json', 'mean': d['mean'],
                     'bootstrap95': d['ci95'], 'paired_t95': d['paired_t_ci95']})
        for offset, key, color, label in [(-.09, 'paired_t_ci95', '#9ba8b2', 'Paired t 95%'),
                                         (.09, 'ci95', '#176283', 'Block bootstrap 95%')]:
            lo, hi = d[key]
            ax.plot([lo, hi], [y + offset] * 2, color=color, linewidth=2.5, label=label if y == 0 else None)
            ax.plot(d['mean'], y + offset, 'o', color=color, markersize=4)
    ax.axvline(0, color='#8493a1', linewidth=.8, linestyle='--')
    ax.set(yticks=range(4), yticklabels=labels, xlabel='Difference in TYPE-Y approval rate (named direction per row)',
           title='Selected workplace contrasts · five paired blocks each')
    ax.invert_yaxis()
    ax.set_xlim(-.2, 1.08)
    ax.legend(loc='lower right', fontsize=8)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    fig.savefig(ROOT / 'figures/explorer_handoff.png', dpi=160, metadata={'Software': 'Explorer reader export'})
    plt.close(fig)
    return rows


def markdown():
    from markdown_it import MarkdownIt
    return MarkdownIt('commonmark', {'html': True}).enable('table')


def body(source):
    return markdown().render(source)


def page(name, source):
    markup = body(source)
    def link(match):
        path = match[1]
        if urlsplit(path).scheme or path.startswith('#'):
            return match[0]
        require('..' not in Path(path).parts, 'Unresolved source link: ' + path)
        if path in ['BRIEF.pdf', 'REPORT.pdf', 'BRIEF.html', 'REPORT.html']:
            return match[0]
        require((ROOT / path).is_file(), 'Missing source link: ' + path)
        if path == 'REPORT.md':
            return 'href="REPORT.pdf"'
        revision = REPLAY_SOURCE_REVISION if path == 'results/iteration58_reproduction.md' else BASELINE
        audit.git('cat-file', '-e', revision + ':' + path)
        if path == 'results/iteration58_reproduction.md':
            require(audit.git('show', revision + ':' + path) == (ROOT/path).read_bytes(), 'Pinned source link changed: ' + path)
        return 'href="' + html.escape(REPO_URL + '/blob/' + revision + '/' + path) + '"'
    markup = re.sub(r'href="([^"]+)"', link, markup)
    if name == 'BRIEF':
        data = base64.b64encode((ROOT / 'figures/explorer_handoff.png').read_bytes()).decode()
        figure = ('<div class="chart"><img alt="Four selected contrasts with bootstrap and paired t intervals" '
            'src="data:image/png;base64,' + data + '"><p>Post hoc selection; no pooling. Intervals are descriptive '
            'and may disagree. S69 changes incentives; S70 holds marginal incentives fixed. Neither interval style '
            'establishes collusion, agreement or equivalence.</p></div>')
        marker = '<p><strong>Why none is promoted:'
        require(markup.count(marker) == 1, 'Brief figure insertion marker changed')
        markup = markup.replace(marker, figure + marker, 1)
    note = ('<p class="note">Reader export · frozen scientific evidence · no new experiments. '
            'Source links require repository access. Export checks: scripts/export_report.py.</p>')
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>' + name + \
        '</title><style>' + CSS + '</style></head><body><main>' + note + markup + '</main></body></html>\n'


def normalize(value):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', value)).replace('−', '-').replace('–', '-').replace('\u00ad', '')


def fragments(source):
    tokens = markdown().parse(source)
    # Inline tokens correspond to paragraphs/headings/table cells, preserving
    # links' visible text while dropping Markdown formatting markers.
    return [''.join(t.content for t in token.children if t.type in ['text', 'code_inline'])
            for token in tokens if token.type == 'inline'] + [token.content for token in tokens if token.type == 'fence']


def pdf_checks(name, source):
    from pypdf import PdfReader
    reader = PdfReader(ROOT / (name + '.pdf'))
    text = normalize(''.join(p.extract_text() or '' for p in reader.pages))
    needles = fragments(source)
    missing = [v for v in needles if normalize(v) and normalize(v) not in text]
    require(not missing, name + ' PDF lost source text: ' + repr(missing[:4]))
    rows, row = [], None
    for token in markdown().parse(source):
        if token.type == 'tr_open':
            row = []
        elif token.type == 'inline' and row is not None:
            row.append(''.join(t.content for t in token.children if t.type in ['text', 'code_inline']))
        elif token.type == 'tr_close':
            rows.append(normalize(''.join(row)))
            row = None
    position = 0
    for row in rows:
        location = text.find(row, position)
        require(location >= 0, name + ' PDF missing or reordered complete table row: ' + row[:80])
        position = location + len(row)
    portable_links = 0
    pdf_links = set()
    for page in reader.pages:
        for annotation in page.get('/Annots', []):
            action = annotation.get_object().get('/A', {})
            uri = str(action.get('/URI', ''))
            if uri:
                pdf_links.add(uri)
            require(not uri.startswith('file:'), 'Machine-local PDF link: ' + uri)
            if uri and not urlsplit(uri).scheme:
                require(uri in ['BRIEF.html', 'BRIEF.pdf', 'REPORT.html', 'REPORT.pdf'], 'Unexpected relative PDF link')
                portable_links += 1
    expected_links = {html.unescape(uri) for uri in re.findall(r'href="([^"]+)"', page_markup(name, source))}
    require(pdf_links == expected_links, name + ' PDF link targets differ from pinned HTML')
    for phrase in [('No promoted hits.' if name == 'BRIEF' else 'No hits promoted.'),
                   'Neither has an effect estimate.' if name == 'BRIEF' else 'No effect estimated.']:
        require(normalize(phrase) in text, name + ' PDF missing key caveat: ' + phrase)
    return {'pages': len(reader.pages), 'source_fragments_checked': len(needles), 'missing_fragments': len(missing),
            'complete_table_rows_in_order': len(rows), 'portable_relative_links': portable_links}


def page_markup(name, source):
    # Alias avoids shadowing page() in PDF iteration loops.
    return page(name, source)


def render():
    from importlib.metadata import version
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import NameObject, TextStringObject
    require({k: version(k) for k in EXPORT_ENV} == EXPORT_ENV, 'Use the pinned export environment')
    rows = chart()
    material = sources()
    checks = {}
    blocked = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        pg = browser.new_page()
        def route(request):
            if urlsplit(request.request.url).scheme in ['file', 'data', 'about']:
                request.continue_()
            else:
                blocked.append(request.request.url)
                request.abort()
        pg.route('**/*', route)
        for name, source in material.items():
            (ROOT / (name + '.html')).write_text(page(name, source))
            pg.goto((ROOT / (name + '.html')).as_uri(), wait_until='load')
            require(pg.locator('img').count() == (1 if name == 'BRIEF' else 0), 'Export image count differs')
            require(pg.locator('img').evaluate_all('(xs) => xs.every(x => x.complete && x.naturalWidth > 0)'), 'Image failed to load')
            require(pg.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'HTML horizontal overflow')
            pg.pdf(path=str(ROOT / (name + '.pdf')), prefer_css_page_size=True, print_background=True)
            # Remove wall-clock metadata so rerenders can reproduce exact bytes.
            reader = PdfReader(ROOT / (name + '.pdf'))
            writer = PdfWriter()
            writer.clone_document_from_reader(reader)
            writer.add_metadata({'/CreationDate': 'D:20261025130000Z', '/ModDate': 'D:20261025130000Z'})
            for pdf_page in writer.pages:
                for annotation in pdf_page.get('/Annots', []):
                    action = annotation.get_object().get('/A', {})
                    uri = str(action.get('/URI', ''))
                    if urlsplit(uri).scheme == 'file':
                        target = Path(unquote(urlsplit(uri).path)).name
                        require(target in ['BRIEF.html', 'BRIEF.pdf', 'REPORT.html', 'REPORT.pdf'], 'Unexpected local PDF link')
                        action[NameObject('/URI')] = TextStringObject(target)
            with (ROOT / (name + '.pdf')).open('wb') as file:
                writer.write(file)
            checks[name] = pdf_checks(name, source)
        browser_version = browser.version
        browser.close()
    require(not blocked, 'Unexpected browser network request')
    record = {'scope': 'Presentation only; source-fragment coverage is not raw scientific validation.',
        'reader_iteration': 58, 'primary_replay_revision': REPLAY_SOURCE_REVISION,
        'fresh_install_target_revision': 'e6b0c02bb189923b3fd039fe67db153826ee3aff',
        'source_revision': BASELINE, 'export_environment': EXPORT_ENV, 'chromium_version': browser_version,
        'network_requests_blocked': blocked, 'chart_rows': rows, 'pdf_text_coverage': checks,
        'files': {n: sha((ROOT / n).read_bytes()) for n in EXPORT_FILES},
        'source_hashes': {n: sha((ROOT / n).read_bytes()) for n in EXPORT_SOURCES}}
    (ROOT / EXPORT_RECEIPT).write_text(json.dumps(record, indent=2) + '\n')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--check-pdf', action='store_true')
    parser.add_argument('--replay-selected', action='store_true')
    args = parser.parse_args()
    require(args.build or args.check or args.check_pdf, 'Choose --build, --check or --check-pdf')
    if args.build:
        preservation()
        for name, value in documents().items():
            require((ROOT / name).read_bytes() in [old(name), audit.git('show', 'e6b0c02:' + name), audit.git('show', REPLAY_SOURCE_REVISION + ':' + name), value.encode()], 'Intervening editorial change: ' + name)
        for name, value in documents().items():
            (ROOT / name).write_text(value)
        checked = verify_sources()
        render()
    else:
        checked = verify_sources()
    record = json.loads((ROOT / EXPORT_RECEIPT).read_text())
    check_coverage(record)
    for name, expected in {**record['files'], **record['source_hashes']}.items():
        require(sha((ROOT / name).read_bytes()) == expected, 'Export/source hash differs: ' + name)
    if args.check_pdf:
        for name, source in sources().items():
            require(page(name, source) == (ROOT / (name + '.html')).read_text(), 'HTML differs from source: ' + name)
            require(pdf_checks(name, source) == record['pdf_text_coverage'][name], 'PDF coverage differs: ' + name)
    if args.replay_selected:
        replay = audit.selected_replay()
        require(replay == json.loads((ROOT / 'logs/iteration55_selected_replay.json').read_text()), 'Selected scientific replay differs')
        checked['selected_replays'] = len(replay['replays'])
    print(json.dumps(dict(checked, pdf_coverage_reextracted=args.check_pdf,
                         saved_pdf_coverage=record['pdf_text_coverage'], passed=True)))


if __name__ == '__main__':
    main()
