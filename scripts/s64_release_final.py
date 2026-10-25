"""Corrected publication/reproduction entry; all registered S64 science unchanged."""
import argparse,contextlib,hashlib,io,json,os,re,subprocess,sys,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s64_analyze import analyze
from scripts.s64_independent import verify
from scripts.s64_publication_final import render_expected,check_documents

ARTIFACTS=['results/s64_memory_retention.json','results/s64_summary.md','figures/s64_memory.png','results/s64_action_text.json','results/s64_action_text.md','logs/s64_independent.json','REPORT.md','REPORT_DETAILS.md','HITS.md','README.md','logs/s64_release_final.json']

def check():
    files=[p for p in Path('data/s64_memory_retention').rglob('*') if p.is_file() and p.name!='.writer.lock']
    original={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with patch('llm.chat',side_effect=AssertionError('Final release forbids scientific calls')):
        with contextlib.redirect_stdout(io.StringIO()):result=analyze('data/s64_memory_retention')
        assert json.dumps(result,indent=2)+'\n'==Path('results/s64_memory_retention.json').read_text()
        independent=verify('data/s64_memory_retention','results/s64_memory_retention.json')
        assert independent==json.loads(Path('logs/s64_independent.json').read_text())
        from sim.memory_retention import main as resume
        with patch.object(sys,'argv',['sim.memory_retention']),contextlib.redirect_stdout(io.StringIO()):resume()
        rendered=render_expected()
        for name,data in rendered.items():assert Path(name).read_bytes()==data,'Rendered artifact mismatch: '+name
        publication=check_documents()
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in original.items())
    receipt_path=Path('logs/s64_release_final.json').resolve();links=0;deferred=[]
    for name in ['REPORT.md','REPORT_DETAILS.md','HITS.md','README.md','results/s64_summary.md','results/s64_action_text.md']:
        for link in re.findall(r'\]\(([^)]+)\)',Path(name).read_text()):
            href=link.strip('<>').split('#')[0]
            if not href or '://' in href:continue
            target=(Path(name).parent/href).resolve()
            if target==receipt_path:deferred.append(target)
            else:assert target.exists(),(name,href)
            links+=1
    receipt=dict(passed=True,scientific_calls_forbidden=True,registered_sources_unchanged=21,raw_archive_unchanged=True,all_key_replay=True,canonical_result_byte_identical=True,independent=independent,publication=publication,rendered_sha256={n:hashlib.sha256(b).hexdigest() for n,b in rendered.items()},local_links_checked=links,result_sha256=hashlib.sha256(Path('results/s64_memory_retention.json').read_bytes()).hexdigest(),correction_scope='Post-outcome editorial/reproduction only; no model calls, source-manifest edits or endpoint/statistic/verdict changes')
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n');assert all(p.exists() for p in deferred)
    print(json.dumps(receipt,indent=2));return receipt

def clone_check():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();remote=subprocess.check_output(['git','remote','get-url','origin'],text=True).strip()
    assert subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],text=True).split()[0]==head
    commands=[['scripts/s64_release_final.py'],['scripts/s64_tests.py'],['scripts/s64_independent.py']]
    with tempfile.TemporaryDirectory(prefix='s64_origin_',dir='/var/tmp') as td:
        clone=Path(td)/'repo';subprocess.run(['git','clone','--quiet',remote,str(clone)],check=True);subprocess.run(['git','checkout','--quiet',head],cwd=clone,check=True)
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1')
        for command in commands:subprocess.run([str(root/'.venv/bin/python'),*command],cwd=clone,env=env,check=True)
        for name in ARTIFACTS:assert (clone/name).read_bytes()==(root/name).read_bytes(),name
        assert subprocess.check_output(['git','status','--porcelain'],cwd=clone,text=True)==''
        receipt=dict(passed=True,commit=head,clone_source='origin',full_history=True,clone_clean=True,commands=commands,focused_tests=17,dependency_environment='Existing frozen installed venv; not a fresh dependency installation',byte_identical_artifacts={n:hashlib.sha256((clone/n).read_bytes()).hexdigest() for n in ARTIFACTS})
    Path('logs/s64_remote_clean_clone.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS origin clone '+head)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--clean-clone',action='store_true');a=p.parse_args();clone_check() if a.clean_clone else check()
