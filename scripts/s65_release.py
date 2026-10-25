"""Call-forbidden S65 release with deterministic raw/result/presentation checks."""
import contextlib,hashlib,io,json,re,sys,tempfile,shutil
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s65_analyze import analyze
from scripts.s65_independent import verify
from scripts.s65_present import render,DOCUMENTS

def check():
    root=Path('data/s65_bonus_pooling')
    raw={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and p.name!='.writer.lock'}
    names=['results/s65_bonus_pooling.json','results/s65_summary.md','figures/s65_pooling.png','results/s65_action_text.json','results/s65_action_text.md','logs/s65_independent.json',*DOCUMENTS]
    original={p:Path(p).read_bytes() for p in names}
    with patch('llm.chat',side_effect=AssertionError('Release forbids model calls')):
        with contextlib.redirect_stdout(io.StringIO()):r=analyze(root)
        assert json.dumps(r,indent=2)+'\n'==original['results/s65_bonus_pooling.json'].decode()
        independent=verify(root,'results/s65_bonus_pooling.json')
        assert json.dumps(independent,indent=2)+'\n'==original['logs/s65_independent.json'].decode()
        from sim.bonus_pooling import main as resume
        from scripts.s65_action_text import main as action_text
        with contextlib.redirect_stdout(io.StringIO()),patch.object(sys,'argv',['sim.bonus_pooling']):resume()
        with tempfile.TemporaryDirectory(prefix='s65_render_',dir='/var/tmp') as td:
            temp=Path(td);(temp/'results').mkdir();(temp/'figures').mkdir();(temp/'data').mkdir()
            (temp/'data/s65_bonus_pooling').symlink_to(root.resolve(),target_is_directory=True)
            shutil.copyfile('results/s65_bonus_pooling.json',temp/'results/s65_bonus_pooling.json')
            with contextlib.chdir(temp),contextlib.redirect_stdout(io.StringIO()):
                action_text();render()
            for n in ['results/s65_summary.md','figures/s65_pooling.png','results/s65_action_text.json','results/s65_action_text.md',*DOCUMENTS]:
                assert (temp/n).read_bytes()==original[n],'Rendered document/asset mismatch: '+n
    assert all(Path(p).read_bytes()==b for p,b in original.items()),'Rendered document/asset changed'
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in raw.items())
    prior=json.loads(Path('logs/s65_prior_artifacts.json').read_text())
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in prior.items()),'Older scientific artifact changed'
    links=0
    for n in [*DOCUMENTS,'results/s65_summary.md','results/s65_action_text.md']:
        for href in re.findall(r'\]\(([^)]+)\)',Path(n).read_text()):
            href=href.strip('<>').split('#')[0]
            if not href or '://' in href:continue
            assert (Path(n).parent/href).exists(),(n,href)
            links+=1
    receipt=dict(passed=True,scientific_calls_forbidden=True,raw_archive_unchanged=True,result_byte_identical=True,
                 independent=independent,older_science_artifacts_unchanged=len(prior),local_links=links,
                 checked_sha256={n:hashlib.sha256(b).hexdigest() for n,b in original.items()})
    Path('logs/s65_release.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));return receipt

if __name__=='__main__':check()
