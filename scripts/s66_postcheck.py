"""Post-run verifier mutations and historical-row continuity; no new scientific metrics."""
import copy,hashlib,json,re,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s66_independent import verify

def main():
    root=Path('data/s66_payoff_order');result=json.loads(Path('results/s66_payoff_order.json').read_text())
    assert verify(root,'results/s66_payoff_order.json')['passed']
    mutations={
        'primary_mean':lambda r:r['metrics']['pair_bad']['paired_difference'].__setitem__('mean',999),
        'bootstrap_numeric_endpoint':lambda r:r['metrics']['pair_bad']['paired_difference']['ci95'].__setitem__(0,999),
        'bootstrap_exact_endpoint':lambda r:r['metrics']['pair_bad']['paired_difference']['ci95_exact'].__setitem__(0,'999'),
        'sign_probability':lambda r:r['metrics']['pair_bad']['paired_difference'].__setitem__('exact_signflip_p_upper',999),
        't_endpoint':lambda r:r['metrics']['pair_bad']['paired_difference']['paired_t_ci95'].__setitem__(0,999),
        'verdict':lambda r:r.__setitem__('verdict','MUTATION'),
        'bonus_gate':lambda r:r.__setitem__('pair_score_gate_exact','999'),
        'missing_metric':lambda r:r['metrics'].pop('pair_good'),
        'note_bindings':lambda r:r['notes']['final_first'].__setitem__('nonempty',999),
    }
    rejected=[]
    with tempfile.TemporaryDirectory(dir='/var/tmp',prefix='s66_mutations_') as td:
        path=Path(td)/'mutated.json'
        for name,mutate in mutations.items():
            broken=copy.deepcopy(result);mutate(broken);path.write_text(json.dumps(broken))
            try:verify(root,path)
            except AssertionError:rejected.append(name)
            else:raise AssertionError('Verifier accepted mutation '+name)
    reg=json.loads((root/'config.json').read_text())['registration_commit']
    before=subprocess.check_output(['git','show',reg+':REPORT.md'],text=True)
    after=Path('REPORT.md').read_text()
    older=[line for line in before.splitlines() if line.startswith('| S')]
    rows=[line for line in after.splitlines() if line.startswith('| S')]
    assert rows[:-1]==older and rows[-1].startswith('| S66 · own,')
    ids=[i for i,line in enumerate(after.splitlines()) if line.startswith('| S')]
    assert ids==list(range(ids[0],ids[0]+len(ids))),'Pilot table is not contiguous'
    cfg=json.loads((root/'config.json').read_text())
    assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==digest for n,digest in cfg['sources'].items())
    receipt=dict(passed=True,verifier_mutations_rejected=rejected,prior_rows_preserved=len(older),current_rows=len(rows),
        contiguous_pilot_table=True,registered_source_hashes_checked=len(cfg['sources']),new_scientific_calls=0,
        scope='Post-outcome validation only; no statistic,scientific source or verdict changes')
    Path('logs/s66_postcheck.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
