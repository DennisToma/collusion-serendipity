"""Call-forbidden replay and preservation checks. No writes to canonical artifacts."""
import contextlib,hashlib,io,json,re,shutil,sys,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s66_analyze import analyze
from scripts.s66_independent import verify
from scripts.s66_present import documents

def check():
    root=Path('data/s66_payoff_order')
    prior=json.loads(Path('logs/s66_prior_artifacts.json').read_text())
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in prior.items() if p!='data/SPLITS.md'),'Older science changed'
    split=json.loads(Path('logs/s66_split_append.json').read_text())
    import subprocess
    old=subprocess.check_output(['git','show',split['baseline_commit']+':data/SPLITS.md'])
    assert hashlib.sha256(old).hexdigest()==split['baseline_sha256']==prior['data/SPLITS.md']
    assert Path('data/SPLITS.md').read_bytes()==old+split['appended'].encode(),'Split-index drift'
    names=['results/s66_payoff_order.json','results/s66_summary.md','figures/s66_payoff_order.png','logs/s66_independent.json','REPORT.md','REPORT_DETAILS.md','HITS.md','README.md']
    before={p:Path(p).read_bytes() for p in names}
    raw={p:p.read_bytes() for p in root.rglob('*') if p.is_file() and p.name!='.writer.lock'}
    with patch('llm.chat',side_effect=AssertionError('Model calls forbidden')):
        with contextlib.redirect_stdout(io.StringIO()):r=analyze(root)
        assert json.dumps(r,indent=2)+'\n'==before[names[0]].decode(),'Scientific result mismatch'
        independent=verify(root,names[0]);assert json.dumps(independent,indent=2)+'\n'==before['logs/s66_independent.json'].decode()
        from sim.payoff_order import main
        with patch.object(sys,'argv',['sim.payoff_order']),contextlib.redirect_stdout(io.StringIO()):main()
        with tempfile.TemporaryDirectory(dir='/var/tmp',prefix='s66_release_') as td:
            temp=Path(td);(temp/'results').mkdir();(temp/'figures').mkdir();(temp/'data').mkdir()
            (temp/'data/s66_payoff_order').symlink_to(root.resolve(),target_is_directory=True)
            shutil.copyfile(names[0],temp/names[0])
            with contextlib.chdir(temp):documents(isolated=True)
            for n in ['results/s66_summary.md','figures/s66_payoff_order.png','REPORT.md','REPORT_DETAILS.md','HITS.md','README.md']:
                assert (temp/n).read_bytes()==before[n],'Presentation mismatch: '+n
    assert all(Path(p).read_bytes()==b for p,b in before.items())
    assert all(p.read_bytes()==b for p,b in raw.items())
    links=0
    for n in ['REPORT.md','REPORT_DETAILS.md','HITS.md','README.md','results/s66_summary.md']:
        for href in re.findall(r'\]\(([^)]+)\)',Path(n).read_text()):
            href=href.strip('<>').split('#')[0]
            if not href or '://' in href:continue
            assert (Path(n).parent/href).exists(),(n,href)
            links+=1
    receipt=dict(passed=True,calls_forbidden=True,raw_unchanged=True,independent=independent,
        older_science_paths_unchanged=len(prior)-1,prospective_split_append_verified=True,local_links=links,
        checked_sha256={p:hashlib.sha256(b).hexdigest() for p,b in before.items()})
    Path('logs/s66_release.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));return receipt
if __name__=='__main__':check()
