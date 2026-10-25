"""Call-forbidden S69 reanalysis, full raw replay and deterministic publication check."""
import contextlib,hashlib,io,json,re,shutil,subprocess,sys,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s69_analyze import analyze
from scripts.s69_independent import verify
from scripts.s69_present import ASSETS,DOCS,render

def check():
    root=Path('data/s69_pooled_enforcement')
    prior=json.loads(Path('logs/s69_prior_artifacts.json').read_text())
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in prior.items()),'Older scientific artifact changed'
    split=json.loads(Path('logs/s69_split_append.json').read_text())
    old=subprocess.check_output(['git','show',split['baseline_commit']+':data/SPLITS.md'])
    assert hashlib.sha256(old).hexdigest()==split['baseline_sha256']
    assert Path('data/SPLITS.md').read_bytes()==old+split['appended'].encode()
    names=['results/s69_pooled_enforcement.json','logs/s69_independent.json',*ASSETS,*DOCS]
    before={p:Path(p).read_bytes() for p in names}
    raw={p:p.read_bytes() for p in root.rglob('*') if p.is_file() and p.name!='.writer.lock'}
    with patch('llm.chat',side_effect=AssertionError('Model calls forbidden')):
        with contextlib.redirect_stdout(io.StringIO()):result=analyze(root)
        assert json.dumps(result,indent=2)+'\n'==before[names[0]].decode()
        independent=verify(root,names[0])
        assert json.dumps(independent,indent=2)+'\n'==before[names[1]].decode()
        from sim.pooled_enforcement import main
        with patch.object(sys,'argv',['sim.pooled_enforcement']),contextlib.redirect_stdout(io.StringIO()):main()
        with tempfile.TemporaryDirectory(dir='/var/tmp',prefix='s69_release_') as td:
            temp=Path(td);(temp/'results').mkdir();(temp/'figures').mkdir();(temp/'data').mkdir()
            (temp/'data/s69_pooled_enforcement').symlink_to(root.resolve(),target_is_directory=True)
            shutil.copyfile(names[0],temp/names[0])
            with contextlib.chdir(temp):render(isolated=True)
            for name in [*ASSETS,*DOCS]:assert (temp/name).read_bytes()==before[name],name
    assert all(Path(p).read_bytes()==b for p,b in before.items())
    assert all(p.read_bytes()==b for p,b in raw.items())
    cfg=json.loads((root/'config.json').read_text())
    baseline_report=subprocess.check_output(['git','show',cfg['registration_commit']+':REPORT.md'],text=True)
    older=[l for l in baseline_report.splitlines() if l.startswith('| S')]
    now=[l for l in Path('REPORT.md').read_text().splitlines() if l.startswith('| S')]
    assert now[:-1]==older and now[-1].startswith('| S69 · D,')
    ids=[i for i,l in enumerate(Path('REPORT.md').read_text().splitlines()) if l.startswith('| S')]
    assert ids==list(range(ids[0],ids[0]+len(ids)))
    links=0
    for name in [*DOCS,'results/s69_summary.md']:
        for target in re.findall(r'\]\(([^)]+)\)',Path(name).read_text()):
            if target.startswith(('https:','http:','#')):continue
            assert (Path(name).parent/target.split('#')[0]).exists(),(name,target)
            links+=1
    return dict(passed=True,independent=independent,prior_scientific_artifacts=len(prior),prospective_split_append=True,
                prior_report_rows=len(older),current_report_rows=len(now),contiguous_table=True,local_links=links,
                source_hashes=len(cfg['sources']),raw_archive_unchanged=True,model_calls_forbidden=True,
                checked_sha256={n:hashlib.sha256(b).hexdigest() for n,b in before.items()},
                scope='Exclusive-writer validation;document guard is not an atomic concurrent-write transaction;existing pinned venv reused')
if __name__=='__main__':
    receipt=check();Path('logs/s69_release.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
