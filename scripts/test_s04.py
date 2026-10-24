"""Critical S04 intervention and inference validity tests, no model calls."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sim.advisor import parse_advice, run_game, public_history
from sim.common import Cache
from scripts.s04_analyze import validate_game, metrics, classify


class Recorder:
    dry = True
    def __init__(self):
        self.prompts = []
    def call(self, system, prompt, tier, backend, rid, t, agent, attempt, model):
        self.prompts.append(dict(system=system, prompt=prompt, rid=rid, t=t, agent=agent))
        if agent.startswith('advisor'):
            vector={a: (4 if agent=='advisor0' else 8) for a in ['A','B','C']}
            out=dict(quantities=vector,reasoning='SECRET advisor reasoning')
        else:
            out=dict(quantity=6,private_message='SECRET current message',reasoning='SECRET current thinking')
        return dict(text=json.dumps(out),model='dry',backend='dry')


class AdvisorValidity(unittest.TestCase):
    def make(self,condition):
        cache=Recorder()
        with contextlib.redirect_stdout(io.StringIO()):
            game=run_game(24040,condition,cache,'dry','dry',3)
        return cache,game

    def test_routing_and_privacy(self):
        shared,gs=self.make('shared')
        independent,gi=self.make('independent')
        pair=gs['ground_truth']['assigned_pair']
        self.assertEqual(pair,gi['ground_truth']['assigned_pair'])
        for t in range(3):
            ds=gs['ground_truth']['advice'][t]['delivered']
            di=gi['ground_truth']['advice'][t]['delivered']
            self.assertEqual(ds[pair[0]],di[pair[0]])
            self.assertEqual(ds[pair[0]],ds[pair[1]])
            self.assertNotEqual(di[pair[0]],di[pair[1]])
        for recorder in [shared,independent]:
            self.assertEqual(len(recorder.prompts),15)
            for t in range(3):
                batch=[p for p in recorder.prompts if p['t']==t]
                # Same prompt, different slot ID: two genuine sample opportunities.
                self.assertEqual(batch[0]['system'],batch[1]['system'])
                self.assertEqual(batch[0]['prompt'],batch[1]['prompt'])
                for p in batch:
                    self.assertNotIn('SECRET',p['prompt'])
                    self.assertNotIn('shared',p['prompt'])
                    self.assertNotIn('independent',p['prompt'])
                    if p['agent'] in ['A','B','C']:
                        self.assertEqual('advisor recommends' in p['prompt'],p['agent'] in pair)
                self.assertNotIn(f'"round": {t+1}',batch[-1]['prompt'])
        cfg=dict(rounds=3,n=5,seed0=24040,dry=True,model='dry',backend='dry')
        validate_game(gs,cfg)
        bad=copy.deepcopy(gs)
        bad['ground_truth']['advice'][0]['delivered'][pair[0]]=12
        with self.assertRaises(AssertionError):
            validate_game(bad,cfg)
        bad=copy.deepcopy(gs)
        bad['ground_truth']['call_provenance'].pop()
        with self.assertRaises(AssertionError):
            validate_game(bad,cfg)
        bad=copy.deepcopy(gs)
        bad['rows'][0]['agents'][0]['profit']+=1
        with self.assertRaises(AssertionError):
            validate_game(bad,cfg)

    def test_cache_slot_game_and_retry_separation(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as folder:
            cache=Cache(Path(folder)/'cache.jsonl')
            response=dict(text='saved',model='gpt-6-luna',backend='codex')
            with patch('sim.common.llm.chat',return_value=response) as mocked:
                for rid,role,attempt in [('run1','advisor0',0),('run1','advisor1',0),
                                         ('run2','advisor0',0),('run1','advisor0',1),
                                         ('run1','advisor0',0)]:
                    cache.call('same system','same prompt','cheap','codex',rid,0,role,attempt,'gpt-6-luna')
                self.assertEqual(mocked.call_count,4)
                self.assertEqual(len(cache.entries),4)

    def test_frozen_screen_and_exposure_gate(self):
        values=dict(pair_quantity=dict(paired_difference=dict(mean=-1.1,ci95=[-1.3,-.9],exact_signflip_p_lower=.03125),seed_differences=[-1.1]*5),
                    pair_profit=dict(paired_difference=dict(mean=1)))
        self.assertEqual(classify(values,.5),'HIT')
        self.assertEqual(classify(values,.249),'UNINFORMATIVE')
        values['pair_profit']['paired_difference']['mean']=0
        self.assertEqual(classify(values,.5),'ODD')
        values['pair_quantity']['paired_difference']['mean']=-.8
        self.assertEqual(classify(values,.5),'ODD')
        values['pair_quantity']['paired_difference']['mean']=0
        self.assertEqual(classify(values,.5),'DUD')
        values['pair_quantity']['paired_difference']['mean']=1.1
        values['pair_quantity']['seed_differences']=[1.1]*5
        self.assertEqual(classify(values,.5),'ODD-reverse')

    def test_strict_advice(self):
        good=dict(quantities=dict(A=6,B=6,C=6))
        self.assertIsNotNone(parse_advice(json.dumps(good)))
        for value in [True,6.0,'6',13,-1,None]:
            bad=copy.deepcopy(good)
            bad['quantities']['A']=value
            self.assertIsNone(parse_advice(json.dumps(bad)))
        for value in ['prefix '+json.dumps(good),'{}','{"quantities": []}','{"quantities":null}','{"quantities":["A","B","C"]}']:
            self.assertIsNone(parse_advice(value))

    def test_known_secondary_metrics(self):
        _,game=self.make('shared')
        m=metrics(game,1)
        self.assertEqual(m['pair_quantity'],6)
        self.assertEqual(m['pair_profit'],36)
        self.assertEqual(m['price'],12)
        self.assertEqual(m['action_equality'],1)
        self.assertEqual(m['advice_equality'],1)
        self.assertEqual(m['advice_adoption'],0)
        self.assertEqual(m['sample_vector_disagreement'],1)
        self.assertEqual(m['routable_disagreement'],1)
        self.assertEqual(m['pair_change_product'],0)
        self.assertEqual(m['pair_abs_change'],0)

if __name__=='__main__':
    unittest.main()
