"""Isolated corruption probes; no extra scientific endpoint or model call."""
import contextlib,copy,json,tempfile
from pathlib import Path
from scripts.s68_independent import verify
from scripts.s68_publish import expected_documents,guard_documents,DOCS

def check():
    result=json.loads(Path('results/s68_polarity.json').read_text())
    cfg=json.loads(Path('data/s68_polarity/config.json').read_text())
    expected,old=expected_documents(result,cfg['registration']['commit'])
    mutations={
        'mean':lambda r:r['contrast'].__setitem__('mean',999),
        'exact_mean':lambda r:r['contrast'].__setitem__('mean_exact','999'),
        'bootstrap':lambda r:r['contrast']['ci95'].__setitem__(0,999),
        'exact_bootstrap':lambda r:r['contrast']['ci95_exact'].__setitem__(0,'999'),
        't':lambda r:r['contrast']['t95'].__setitem__(0,999),
        'sign':lambda r:r['contrast'].__setitem__('upper_signflip_p',999),
        'verdict':lambda r:r.__setitem__('verdict','FORGED'),
        'decoded_action':lambda r:r['cases'][0]['approvals'].__setitem__('inverted',not r['cases'][0]['approvals']['inverted']),
        'missing_case':lambda r:r['cases'].pop(),
    };rejected=[];guards=[]
    with tempfile.TemporaryDirectory(dir='/var/tmp',prefix='s68_corruption_') as td:
        root=Path(td);p=root/'result.json'
        for name,mutate in mutations.items():
            altered=copy.deepcopy(result);mutate(altered);p.write_text(json.dumps(altered))
            try:verify('data/s68_polarity',p)
            except AssertionError:rejected.append(name)
            else:raise AssertionError('Accepted mutation '+name)
        for name,text in expected.items():(root/name).write_text(text)
        with contextlib.chdir(root):
            guard_documents(expected,old)
            for target in DOCS:
                Path(target).write_text(expected[target]+'\nFORGED EDIT\n')
                before={n:Path(n).read_bytes() for n in DOCS}
                try:guard_documents(expected,old)
                except RuntimeError:guards.append(target)
                else:raise AssertionError('Accepted unexpected document edit '+target)
                assert before=={n:Path(n).read_bytes() for n in DOCS}
                Path(target).write_text(expected[target])
    return dict(passed=True,verifier_mutations_rejected=rejected,prewrite_document_mutations_rejected=guards,scope='Isolated nonconcurrent probes;no atomicity/concurrent-writer guarantee')
if __name__=='__main__':
    r=check();Path('logs/s68_postcheck.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
