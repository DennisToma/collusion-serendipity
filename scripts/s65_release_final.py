"""Corrected editorial S65 release; registered sources and estimates unchanged."""
import contextlib,hashlib,io,json,re,sys,tempfile,shutil,subprocess
from pathlib import Path
if not __debug__:raise RuntimeError('S65 release requires Python without optimization')
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s65_analyze import analyze
from scripts.s65_independent import verify
from scripts.s65_publication_final import render,DOCUMENTS

def check():
    root=Path('data/s65_bonus_pooling')
    raw={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and p.name!='.writer.lock'}
    names=['results/s65_bonus_pooling.json','results/s65_summary.md','figures/s65_pooling.png','results/s65_action_text.json','results/s65_action_text.md','results/s65_all_y_decisions.json','results/s65_all_y_decisions.md','logs/s65_independent.json',*DOCUMENTS]
    original={p:Path(p).read_bytes() for p in names}
    with patch('llm.chat',side_effect=AssertionError('Release forbids model calls')):
        with contextlib.redirect_stdout(io.StringIO()):r=analyze(root)
        assert json.dumps(r,indent=2)+'\n'==original['results/s65_bonus_pooling.json'].decode()
        independent=verify(root,'results/s65_bonus_pooling.json')
        assert json.dumps(independent,indent=2)+'\n'==original['logs/s65_independent.json'].decode()
        from sim.bonus_pooling import main as resume
        from scripts.s65_action_text import main as action_text
        from scripts.s65_decisions import render as all_decisions
        with contextlib.redirect_stdout(io.StringIO()),patch.object(sys,'argv',['sim.bonus_pooling']):resume()
        with tempfile.TemporaryDirectory(prefix='s65_render_',dir='/var/tmp') as td:
            temp=Path(td);(temp/'results').mkdir();(temp/'figures').mkdir();(temp/'data').mkdir()
            shutil.copytree(root,temp/'data/s65_bonus_pooling',ignore=shutil.ignore_patterns('.writer.lock'))
            shutil.copyfile('results/s65_bonus_pooling.json',temp/'results/s65_bonus_pooling.json')
            with contextlib.chdir(temp),contextlib.redirect_stdout(io.StringIO()):
                action_text();all_decisions();render()
            for n in ['results/s65_summary.md','figures/s65_pooling.png','results/s65_action_text.json','results/s65_action_text.md','results/s65_all_y_decisions.json','results/s65_all_y_decisions.md',*DOCUMENTS]:
                assert (temp/n).read_bytes()==original[n],'Rendered document/asset mismatch: '+n
    assert all(Path(p).read_bytes()==b for p,b in original.items()),'Rendered document/asset changed'
    assert {p:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and p.name!='.writer.lock'}==raw, 'Archive file inventory changed'
    prior=json.loads(Path('logs/s65_prior_artifacts.json').read_text())
    split='data/SPLITS.md'
    cfg=json.loads((root/'config.json').read_text());reg=cfg['registration_commit']
    old_split=subprocess.check_output(['git','show',f'{reg}^:{split}'])
    registered_split=subprocess.check_output(['git','show',f'{reg}:{split}'])
    assert hashlib.sha256(old_split).hexdigest()==prior[split]
    assert registered_split.startswith(old_split) and Path(split).read_bytes()==registered_split,'Prospective split index drift'
    locks={p for p in prior if Path(p).name=='.writer.lock'}
    assert all(prior[p]==hashlib.sha256(b'').hexdigest() for p in locks),'Unexpected nonempty process lock'
    published=set(subprocess.check_output(['git','ls-tree','-r','--name-only',reg],text=True).splitlines())
    protected={p:h for p,h in prior.items() if p!=split and p not in locks}
    assert set(protected)<=published,'Unpublished scientific evidence in preservation inventory'
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in protected.items()),'Older scientific artifact changed'
    links=0
    for n in [*DOCUMENTS,'results/s65_summary.md','results/s65_action_text.md','results/s65_all_y_decisions.md']:
        for href in re.findall(r'\]\(([^)]+)\)',Path(n).read_text()):
            href=href.strip('<>').split('#')[0]
            if not href or '://' in href:continue
            assert (Path(n).parent/href).exists(),(n,href)
            links+=1
    receipt=dict(passed=True,scientific_calls_forbidden=True,raw_archive_unchanged=True,result_byte_identical=True,
                 independent=independent,older_science_artifacts_unchanged=len(protected),unpublished_empty_writer_locks_excluded=len(locks),split_index_prospective_append_verified=True,local_links=links,
                 checked_sha256={n:hashlib.sha256(b).hexdigest() for n,b in original.items()})
    Path('logs/s65_release_final.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));return receipt

if __name__=='__main__':check()
