"""Read-only canonical-artifact audit plus isolated publication corruption probes."""
import contextlib,json,shutil,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s66_publication_final import ARTIFACTS,documents
from scripts.s66_release_final import check

def main():
    receipt=check();root=Path.cwd();before={n:Path(n).read_bytes() for n in ARTIFACTS}
    with tempfile.TemporaryDirectory(dir='/var/tmp',prefix='s66_editorial_check_') as td:
        temp=Path(td);(temp/'data').mkdir();(temp/'results').mkdir();(temp/'figures').mkdir()
        (temp/'data/s66_payoff_order').symlink_to(root/'data/s66_payoff_order',target_is_directory=True)
        shutil.copyfile(root/'results/s66_payoff_order.json',temp/'results/s66_payoff_order.json')
        for n,b in before.items():(temp/n).write_bytes(b)
        rejected=[]
        with contextlib.chdir(temp):
            documents();assert all(Path(n).read_bytes()==b for n,b in before.items())
            for name in ['README.md','results/s66_summary.md','figures/s66_payoff_order.png']:
                Path(name).write_bytes(before[name]+b'UNEXPECTED_INTERVENING_EDIT')
                corrupted={n:Path(n).read_bytes() for n in ARTIFACTS}
                try:documents()
                except RuntimeError as exc:assert 'Intervening S66 publication changes' in str(exc);rejected.append(name)
                else:raise AssertionError('Publication accepted mutation '+name)
                assert all(Path(n).read_bytes()==b for n,b in corrupted.items()),'Publication wrote before rejecting'
                Path(name).write_bytes(before[name])
    assert all(Path(n).read_bytes()==b for n,b in before.items())
    summary=Path('results/s66_summary.md').read_text()
    assert 'upper sign-flip p=0.93750' in summary and 'Upper sign-flip p |' in summary
    assert 'near-ceiling controls in some blocks' in summary
    assert 'scripts/s66_release_final.py' in summary
    out=dict(passed=True,release_passed=receipt['passed'],canonical_artifacts_unchanged=True,editorial_render_idempotent=True,
        isolated_intervening_edit_mutations_rejected=rejected,all_guard_failures_before_writes=True,science_unchanged=True)
    Path('logs/s66_editorial_check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
