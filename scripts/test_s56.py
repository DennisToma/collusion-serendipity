"""Meaningful synthetic invariant and corruption checks for S56."""
from fractions import Fraction as F
import copy
import json
import tempfile
import hashlib
import random
from pathlib import Path
import unittest
from unittest.mock import patch
from scripts import s56_coalitions as p
from scripts import s56_independent as independent

class S56Tests(unittest.TestCase):
    def test_conservation(self):
        for bids in [(6,6,6),(7,7,7),(20,20,20),(8,15,8),(9,10,11)]:
            self.assertEqual(sum(p.profits(bids)),min(bids)-6)

    def test_high_tie_undercut(self):
        d=p.decompose((20,20,20));self.assertEqual(d['outsider_regret'],F(25,3));self.assertGreater(d['pair_joint_regret'],0);self.assertEqual(d['coalition_stable'],0)

    def test_joint_gain_can_sacrifice_member(self):
        d=p.decompose((18,20,20));self.assertGreater(d['pair_joint_regret'],0);self.assertEqual(d['strict_pair_improvement'],0)

    def test_both_can_gain_without_transfers(self):
        d=p.decompose((20,20,10));self.assertEqual(d['pair_profit'],0);self.assertEqual(d['strict_pair_improvement'],1)

    def test_zero_profit_grid_equilibrium(self):
        d=p.decompose((6,6,6));self.assertEqual(d['pair_joint_regret'],0);self.assertEqual(d['outsider_regret'],0);self.assertEqual(d['coalition_stable'],1)

    def test_nonunique_nash(self):
        for bs in [(6,6,20),(7,7,7)]:self.assertFalse(any(p.decompose(bs)['individual_regrets']))

    def test_above_nash_not_negative(self):
        self.assertEqual(p.decompose((6,20,20))['payment_excess'],0);self.assertEqual(p.decompose((8,8,8))['payment_excess'],1)

    def test_pair_swap_invariance(self):
        a=p.decompose((10,15,13));b=p.decompose((15,10,13))
        self.assertEqual({k:a[k] for k in p.METRICS},{k:b[k] for k in p.METRICS})

    def test_invalid_action(self):
        for bs in [(True,7,8),(5,7,8),(21,7,8),(7.,7,8),(7,8)]:
            with self.assertRaises(ValueError):p.profits(bs)
            with self.assertRaises(ValueError):p.decompose(bs)

    def test_exact_bootstrap(self):
        v=[F(-1,3),F(0),F(1,3),F(2,3),F(1)];s=p.summary(v);independent.validate_summary(v,s)
        self.assertEqual(s['mean_exact'],'1/3')

    def test_degenerate_interval(self):
        s=p.summary([0]*5);self.assertEqual(s['ci95'],[0.,0.]);self.assertEqual(s['t95'],[0.,0.])

    def test_summary_corruption(self):
        s=p.summary([0,1,2,3,4]);s['ci95_exact'][0]='999'
        with self.assertRaises(ValueError):independent.validate_summary(list(map(F,range(5))),s)

    def test_summary_wrong_block_count(self):
        with self.assertRaises(ValueError):p.summary([1,2,3])

    def manifest_fixture(self,changes):
        from contextlib import ExitStack
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td, ExitStack() as stack:
            source=Path(td)/'source';source.write_text('frozen source')
            source_paths=[str(source)]
            m=dict(registered_utc='2026-10-25T00:00:00+00:00',input_and_source_sha256={str(source):p.digest(source)})
            manifest=Path(td)/'manifest.json';p.write(manifest,m)
            receipt=Path(td)/'receipt.json';p.write(receipt,dict(commit='abc',remote_main='abc',observed_utc='2026-10-25T01:00:00+00:00'))
            manifest_bytes=manifest.read_bytes()
            changes(source,source_paths)
            stack.enter_context(patch.object(p,'MANIFEST',str(manifest)))
            stack.enter_context(patch.object(p,'RECEIPT',str(receipt)))
            stack.enter_context(patch.object(p,'required_files',return_value=source_paths))
            stack.enter_context(patch.object(p.subprocess,'run'))
            stack.enter_context(patch.object(p.subprocess,'check_output',side_effect=lambda cmd:manifest_bytes if cmd[-1].endswith(str(manifest)) else b'frozen source'))
            return p.checked_manifest()

    def test_manifest_changed_source(self):
        with self.assertRaisesRegex(ValueError,'Registered file changed'):
            self.manifest_fixture(lambda source,paths:source.write_text('changed'))

    def test_manifest_missing_source(self):
        with self.assertRaises(FileNotFoundError):self.manifest_fixture(lambda source,paths:source.unlink())

    def test_manifest_incomplete_coverage(self):
        with self.assertRaisesRegex(ValueError,'Incomplete manifest'):self.manifest_fixture(lambda source,paths:paths.append('omitted'))

    def test_manifest_unchanged(self):
        self.assertIn('input_and_source_sha256',self.manifest_fixture(lambda source,paths:None))

    def test_production_vs_independent_profiles(self):
        for bs in [(6,6,6),(20,20,20),(7,7,20),(20,20,10),(10,15,13),(19,18,17)]:
            values,profits,regrets=independent.cell(*bs);d=p.decompose(bs)
            self.assertEqual(values,{k:d[k] for k in p.METRICS});self.assertEqual(profits,list(d['profits']));self.assertEqual(regrets,d['individual_regrets'])

class S56FullSyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(dir='/var/tmp');cls.root=Path(cls.temp.name);data=cls.root/'data/s14_tender';data.mkdir(parents=True)
        rows=[];games=[];by={};requests=[];responses=[]
        for seed in range(24200,24205):
            for cond in ['none','private']:
                pair=random.Random(seed).sample(list('ABC'),2);outside=next(a for a in 'ABC' if a not in pair);order=pair+[outside];raw=[];provenance=[];run_id=f'synthetic_{seed}_{cond}';total={k:F(0) for k in p.METRICS}
                for turn in range(12):
                    bids=tuple(6+(seed+turn*(i+1)+(cond=='private')*i)%15 for i in range(3));vals=p.decompose(bids)
                    raw.append(dict(round=turn,agents=[dict(id=a,price=bids[order.index(a)],profit=float(vals['profits'][order.index(a)])) for a in 'ABC']))
                    for agent in 'ABC':
                        payload=['synthetic system','synthetic user','cheap','codex',1,run_id,turn,agent,0,'synthetic-model']
                        key=hashlib.sha256(json.dumps([False,payload]).encode()).hexdigest()
                        response=dict(text=json.dumps(dict(bid=bids[order.index(agent)],reasoning='',private_message='')),model='synthetic-model',backend='codex',call_started_utc='synthetic_start',call_completed_utc='synthetic_end')
                        requests.append(dict(key=key,dry=False,payload=payload,response_sha256=hashlib.sha256(json.dumps(response,sort_keys=True).encode()).hexdigest()))
                        responses.append(dict(key=key,response=response))
                        provenance.append(dict(round=turn,agent=agent,attempt=0,model=response['model'],backend=response['backend'],call_started_utc=response['call_started_utc'],call_completed_utc=response['call_completed_utc']))
                    if turn>=3:
                        rows.append(dict(seed=seed,condition=cond,round=turn+1,agent_order=order,bids=list(bids),metrics={k:str(vals[k]) for k in p.METRICS},profits=list(map(str,vals['profits'])),individual_regrets=list(map(str,vals['individual_regrets']))))
                        for k in p.METRICS:total[k]+=vals[k]
                p.write(data/f'game_{seed}_{cond}.json',dict(ground_truth=dict(seed=seed,condition=cond,assigned_pair=pair,run_id=run_id,call_provenance=provenance),rows=raw))
                games.append(dict(seed=seed,condition=cond,totals_exact={k:str(v) for k,v in total.items()},means_exact={k:str(v/9) for k,v in total.items()}));by[seed,cond]={k:v/9 for k,v in total.items()}
        (data/'raw').mkdir()
        for name,items in [('requests',requests),('responses',responses)]:
            (data/f'raw/{name}.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in items))
        metrics={}
        for k in p.METRICS:
            a=[by[s,'none'][k] for s in range(24200,24205)];b=[by[s,'private'][k] for s in range(24200,24205)]
            metrics[k]=dict(none=p.summary(a),private=p.summary(b),difference=p.summary([y-x for x,y in zip(a,b)]))
        totals={c:{k:str(sum(F(g['totals_exact'][k]) for g in games if g['condition']==c)) for k in p.METRICS} for c in ['none','private']}
        cls.result=dict(id='S56',posthoc=True,verdict='ODD/context-only',new_games=0,scientific_model_calls=0,tuning_attempts=0,n_blocks=5,primary_rounds='4..12',metrics=metrics,games=games,rounds=rows,totals=totals,census=p.census())

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def checked(self,r):
        real_path=Path
        def redirect(value):return real_path(self.root)/value
        with patch.object(independent,'Path',side_effect=redirect):
            return independent.verify(r)

    def test_full_synthetic_reconstruction(self):self.assertTrue(self.checked(self.result)['passed'])

    def test_wrong_pair_order_rejected(self):
        r=copy.deepcopy(self.result);r['rounds'][0]['agent_order'].reverse()
        with self.assertRaises(AssertionError):self.checked(r)

    def test_round_metric_tamper_rejected(self):
        r=copy.deepcopy(self.result);r['rounds'][0]['metrics']['pair_joint_regret']='999'
        with self.assertRaises(AssertionError):self.checked(r)

    def test_game_metric_tamper_rejected(self):
        r=copy.deepcopy(self.result);r['games'][0]['totals_exact']['pair_joint_regret']='999'
        with self.assertRaises(AssertionError):self.checked(r)

    def test_duplicate_round_rejected(self):
        r=copy.deepcopy(self.result);r['rounds'][-1]=r['rounds'][0]
        with self.assertRaises(AssertionError):self.checked(r)

    def test_missing_metric_rejected(self):
        r=copy.deepcopy(self.result);del r['metrics']['strict_pair_improvement']
        with self.assertRaises(AssertionError):self.checked(r)

    def test_summary_tamper_rejected(self):
        r=copy.deepcopy(self.result);r['metrics']['outsider_regret']['difference']['mean_exact']='999'
        with self.assertRaises(ValueError):self.checked(r)

    def test_census_tamper_rejected(self):
        r=copy.deepcopy(self.result);r['census']['stable_payments']=[20]
        with self.assertRaises(AssertionError):self.checked(r)

    def corrupt_raw(self,kind):
        data=self.root/'data/s14_tender/raw';paths=[data/'requests.jsonl',data/'responses.jsonl'];before=[x.read_bytes() for x in paths]
        requests=[json.loads(x) for x in paths[0].read_text().splitlines()];responses=[json.loads(x) for x in paths[1].read_text().splitlines()]
        try:
            if kind=='duplicate':requests.append(requests[0])
            else:
                r=responses[0]['response']
                if kind=='bid':
                    action=json.loads(r['text']);action['bid']=6+(action['bid']-5)%15;r['text']=json.dumps(action)
                else:r['call_completed_utc']='tampered'
                requests[0]['response_sha256']=hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest()
            for path,items in zip(paths,[requests,responses]):path.write_text(''.join(json.dumps(x)+'\n' for x in items))
            with self.assertRaises(AssertionError):self.checked(self.result)
        finally:
            for path,content in zip(paths,before):path.write_bytes(content)

    def test_raw_bid_tamper_rejected(self):self.corrupt_raw('bid')
    def test_raw_time_tamper_rejected(self):self.corrupt_raw('time')
    def test_raw_duplicate_rejected(self):self.corrupt_raw('duplicate')

if __name__=='__main__':unittest.main()
