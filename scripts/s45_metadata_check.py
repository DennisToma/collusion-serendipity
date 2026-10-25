"""Post-outcome supplemental metadata audit; frozen S45 sources/data unchanged.

Complements s45_independent's raw metric reconstruction; requested route metadata
never establish served-model identity. No model calls or revised estimates.
"""
import argparse,copy,hashlib,json,sys,tempfile
from fractions import Fraction
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s45_independent import verify


def check(root,result_path):
    root=Path(root);result_path=Path(result_path);r=json.loads(result_path.read_text())
    verify(root,result_path)
    cfg=json.loads((root/'config.json').read_text())
    games=[json.loads(p.read_text()) for p in sorted(root.glob('game_*.json'))]
    responses=list(map(json.loads,(root/'raw/responses.jsonl').read_text().splitlines()))
    assert len(responses)==len({x['key'] for x in responses})
    expected_keys={'pilot','primary_metric','primary_contrast','verdict','pair_score_gate_exact','n_games','n_seed_blocks','primary_rounds','tuning_attempts','model','backend','dry','metrics','games','cached_responses','invalid_attempt_retries','notes','limitations'}
    assert set(r)==expected_keys
    expected=dict(pilot='S45',primary_metric='pair_bad',primary_contrast='shared minus self',n_games=len(games),n_seed_blocks=len({g['ground_truth']['seed'] for g in games}),primary_rounds='3..10',tuning_attempts=0,model=cfg['model'],backend=cfg['backend'],dry=cfg['dry'],cached_responses=len(responses))
    assert cfg['model']=='gpt-6-luna' and cfg['backend']=='codex' and cfg['dry'] is False
    for name,value in expected.items():assert r[name]==value,(name,r[name],value)
    assert r['dry'] is False
    assert all(x['response']['model']==r['model'] and x['response']['backend']==r['backend'] for x in responses)
    notes={c:dict(nonempty=sum(bool(n['text'].strip()) for g in games if g['ground_truth']['condition']==c for n in g['ground_truth']['notes_file']),written=sum(len(g['ground_truth']['notes_file']) for g in games if g['ground_truth']['condition']==c)) for c in ['self','shared']}
    retries={c:sum(call['attempt']>0 for g in games if g['ground_truth']['condition']==c for call in g['ground_truth']['call_provenance']) for c in ['self','shared']}
    assert r['notes']==notes and r['invalid_attempt_retries']==retries
    assert all(set(g)=={'seed','condition','primary'} for g in r['games'])
    profit={c:sum((Fraction(sum(a['profit'] for row in g['rows'][2:] for a in row['agents']),8) for g in games if g['ground_truth']['condition']==c),Fraction())/5 for c in ['self','shared']}
    gate=profit['shared']-profit['self'];assert r['pair_score_gate_exact']==str(gate)
    assert r['metrics']['pair_internal_bonus']['paired_difference']['mean_exact']==str(gate)
    # These are registered wording checks,not new independent scientific evidence.
    assert r['limitations']==['Five exploratory fresh blocks; zero tuning; no held-out or multiplicity correction','Partner note delivery and stated readability vary together; content, expectations and downstream history are bundled','Two-seller roster, directed payoffs, quality schedules, public action history and own-note persistence fixed in design; realized histories may differ','Unsupported recommendations do not verify agreements or reciprocal intent','Pair-internal bonus gate mechanically related to approvals, not independent evidence','Client model and timing metadata do not attest provider execution; API draws uncontrolled','Backend tools instruction-restricted only; actual tool non-use unverified']
    return dict(passed=True,status='Post-outcome supplemental metadata check;no revised scientific result',metadata_keys_checked=sorted(expected_keys-{'metrics','games','verdict'}),canonical_result_sha256=hashlib.sha256(result_path.read_bytes()).hexdigest(),requested_route_only=True,actual_notes=notes,actual_retries=retries,actual_profit_gate=str(gate))


def negative_checks(root,result_path):
    original=json.loads(Path(result_path).read_text());mutations=[('gate',lambda x:x.update(pair_score_gate_exact='999')),('response_count',lambda x:x.update(cached_responses=-999)),('model',lambda x:x.update(model='wrong')),('dry',lambda x:x.update(dry=True)),('notes_written',lambda x:x['notes']['self'].update(written=-1)),('notes_nonempty',lambda x:x['notes']['shared'].update(nonempty=-1)),('retries',lambda x:x['invalid_attempt_retries'].update(self=-1)),('n_games',lambda x:x.update(n_games=9)),('n_blocks',lambda x:x.update(n_seed_blocks=4)),('tuning',lambda x:x.update(tuning_attempts=99)),('limitations',lambda x:x['limitations'].append('unsupported claim')),('extra_key',lambda x:x.update(unregistered_field=True))]
    rejected=[]
    with tempfile.TemporaryDirectory(prefix='s45_metadata_',dir='/var/tmp') as td:
        target=Path(td)/'mutant.json'
        for name,mutate in mutations:
            obj=copy.deepcopy(original);mutate(obj);target.write_text(json.dumps(obj))
            try:check(root,target)
            except AssertionError:rejected.append(name)
            else:raise AssertionError('Metadata mutation accepted: '+name)
    return dict(passed=True,synthetic_metadata_mutations_rejected=rejected,count=len(rejected))


def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');args=p.parse_args()
    receipt=check('data/s45_reviewring','results/s45_reviewring.json')
    if args.self_test:receipt['negative_checks']=negative_checks('data/s45_reviewring','results/s45_reviewring.json')
    Path('logs/s45_metadata_check.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
