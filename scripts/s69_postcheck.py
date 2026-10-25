"""Post-run corruption probes and archival preservation; no new scientific endpoints."""
import copy,contextlib,hashlib,json,shutil,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s69_independent import verify
from scripts.s69_present import render,ASSETS,DOCS

def main():
    root=Path('data/s69_pooled_enforcement');path=Path('results/s69_pooled_enforcement.json');result=json.loads(path.read_text())
    assert verify(root,path)['passed']
    mutations={
      'mean':lambda r:r['metrics']['pair_bad']['paired_difference'].__setitem__('mean',999),
      'bootstrap_endpoint':lambda r:r['metrics']['pair_bad']['paired_difference']['ci95'].__setitem__(0,999),
      'exact_bootstrap_endpoint':lambda r:r['metrics']['pair_bad']['paired_difference']['ci95_exact'].__setitem__(0,'999'),
      'sign_probability':lambda r:r['metrics']['pair_bad']['paired_difference'].__setitem__('exact_signflip_p_upper',999),
      't_endpoint':lambda r:r['metrics']['pair_bad']['paired_difference']['paired_t_ci95'].__setitem__(0,999),
      'calibration':lambda r:r.__setitem__('screen','BAD'),
      'verdict':lambda r:r.__setitem__('verdict','HIT'),
      'forbidden_bonus_gate':lambda r:r.__setitem__('pair_score_gate_exact','1'),
      'missing_metric':lambda r:r['metrics'].pop('pair_good'),
      'notes':lambda r:r['notes']['high_charge'].__setitem__('nonempty',999),
    }
    rejected=[];guards=[]
    with tempfile.TemporaryDirectory(dir='/var/tmp',prefix='s69_mutations_') as td:
        p=Path(td)/'mutated.json'
        for name,mutate in mutations.items():
            broken=copy.deepcopy(result);mutate(broken);p.write_text(json.dumps(broken))
            try:verify(root,p)
            except AssertionError:rejected.append(name)
            else:raise AssertionError('Accepted mutation '+name)
        temp=Path(td)/'publication';temp.mkdir();(temp/'results').mkdir();(temp/'figures').mkdir();(temp/'data').mkdir()
        (temp/'data/s69_pooled_enforcement').symlink_to(root.resolve(),target_is_directory=True)
        shutil.copyfile(path,temp/path)
        for n in [*ASSETS,*DOCS]:shutil.copyfile(n,temp/n)
        for target in ['REPORT.md','HITS.md','README.md']:
            original=(temp/target).read_bytes();(temp/target).write_bytes(original+b'\nUNEXPECTED EDIT\n')
            before={n:(temp/n).read_bytes() for n in [*ASSETS,*DOCS]}
            with contextlib.chdir(temp):
                try:render()
                except RuntimeError as exc:assert 'Intervening document change' in str(exc);guards.append(target)
                else:raise AssertionError('Accepted intervening edit '+target)
            assert before=={n:(temp/n).read_bytes() for n in [*ASSETS,*DOCS]}
            (temp/target).write_bytes(original)
    receipt=dict(passed=True,verifier_mutations_rejected=rejected,prewrite_document_mutations_rejected=guards,
                 scope='Isolated nonconcurrent corruption tests only;no atomic transaction or concurrent-writer safety claim')
    Path('logs/s69_postcheck.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
