"""Post-outcome editorial correction; frozen S64 science remains byte-identical.

Fix lost historical anchors, stale next axis, and reproduction entry points.
No new endpoint, number, parser, source-manifest change or scientific calls.
"""
import contextlib,io,json,re,subprocess,tempfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s64_publish import managed

FOOTER=('\nPublication/reproduction correction: use `uv run python scripts/s64_release_final.py` and '
        '`uv run python scripts/s64_tests.py`. The original registered publication/release helpers are retained unchanged; '
        'the corrected entry preserves historical report anchors and scopes one frozen synthetic test to its registration baseline. '
        '[Correction record](../logs/s64_review_disposition.md).\n')
DOCUMENTS=['REPORT.md','REPORT_DETAILS.md','HITS.md','README.md']

def baseline(name):
    cfg=json.loads(Path('data/s64_memory_retention/config.json').read_text())
    return subprocess.check_output(['git','show',f"{cfg['registration_commit']}:{name}"],text=True)

def expected_documents():
    blocks,row=managed();r=json.loads(Path('results/s64_memory_retention.json').read_text());expected={}
    for name in DOCUMENTS:
        old=baseline(name);block=blocks[name]
        if name=='REPORT.md':
            old=re.sub(r'<!-- (S\d+) summary start -->.*?<!-- \1 summary end -->',lambda m:f'<!-- {m[1]} summary start --><!-- {m[1]} summary end -->',old,flags=re.S)
            old=old.replace('Iteration 45','Iteration 46')
            old=re.sub(r'\*\*Next:\*\*[^\n]*','**Next:** fresh different-axis A/B/E pilot;S63,S57,S52,S49 remain queued. No sibling headline change.',old)
            if r['verdict']=='HIT':old=old.replace('**No hits promoted.**','**S64 passes the exploratory HIT screen.**')
            at=old.index('| Pilot |');old=old[:at]+block+'\n\n'+old[at:]
            lines=old.splitlines();at=max(i for i,x in enumerate(lines) if x.startswith('| S'));lines.insert(at+1,row);old='\n'.join(lines)+'\n'
        else:
            if name=='README.md':
                block=block.replace('scripts/s64_release.py','scripts/s64_release_final.py').replace('python -m unittest scripts.test_s64','python scripts/s64_tests.py')
                block=block.replace(' runs focused checks.',' runs all17focused checks with one registration-baseline-only synthetic fixture. Registered scientific sources/raw results stay unchanged; the original direct unittest command is superseded for post-publication use.')
            if name=='REPORT_DETAILS.md':block=block.replace('logs/s64_release.json','logs/s64_release_final.json')
            if name=='HITS.md':old=old.replace('after iteration 45','after iteration 46')
            old=old.rstrip()+'\n\n'+block+'\n'
        expected[name]=old
    return expected

def render_expected():
    from scripts.s64_present import main as present
    from scripts.s64_action_text import main as actions
    archive=Path('data/s64_memory_retention').resolve();result=Path('results/s64_memory_retention.json').read_bytes()
    names=['results/s64_summary.md','figures/s64_memory.png','results/s64_action_text.json','results/s64_action_text.md']
    with tempfile.TemporaryDirectory(prefix='s64_final_render_',dir='/var/tmp') as td:
        root=Path(td);(root/'results').mkdir();(root/'figures').mkdir();(root/'data').mkdir()
        (root/'results/s64_memory_retention.json').write_bytes(result);(root/'data/s64_memory_retention').symlink_to(archive,target_is_directory=True)
        with contextlib.chdir(root),contextlib.redirect_stdout(io.StringIO()):present();actions()
        rendered={n:(root/n).read_bytes() for n in names}
    rendered['results/s64_summary.md']+=FOOTER.encode()
    return rendered

def check_documents():
    expected=expected_documents()
    for name,text in expected.items():assert Path(name).read_text()==text,'Corrected document mismatch: '+name
    report=expected['REPORT.md'];prior=[x for x in baseline('REPORT.md').splitlines() if x.startswith('| S')]
    assert all(report.count(x)==1 for x in prior)
    oldanchors=re.findall(r'<!-- (S\d+) summary start -->',baseline('REPORT.md'))
    assert all(report.count(f'<!-- {a} summary start -->')==1 for a in oldanchors)
    assert len([x for x in report.splitlines() if x.startswith('| S64 ')])==1
    return dict(passed=True,complete_documents_exact=4,older_pilot_rows=len(prior),historical_anchors=len(oldanchors),new_pilot_rows=1)

def publish():
    for name,text in expected_documents().items():Path(name).write_text(text)
    for name,data in render_expected().items():Path(name).write_bytes(data)
    return check_documents()

if __name__=='__main__':print(json.dumps(publish(),indent=2))
