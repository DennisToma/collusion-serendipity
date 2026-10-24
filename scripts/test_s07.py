import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from sim.legality import parse_action, run_game, prompts, LegalityCache
from scripts.s07_analyze import classify, exact_signflip, analyze
from scripts.s07_verify import verify

class S07(unittest.TestCase):
    def test_strict_parser(self):
        base=dict(quantity=6,reasoning='fine',private_message='hi')
        self.assertIsNotNone(parse_action(json.dumps(base)))
        for k,v in [('quantity',True),('quantity',6.0),('quantity',13),('reasoning','x '*41),('private_message','x '*61)]:
            self.assertIsNone(parse_action(json.dumps(dict(base,**{k:v}))))
        self.assertIsNone(parse_action('prefix '+json.dumps(base)))
        self.assertIsNone(parse_action('[]'))
        self.assertIsNone(parse_action('{"quantity":0,"quantity":6,"reasoning":"ok","private_message":""}'))
        self.assertIsNone(parse_action('{"quantity":6,"reasoning":"ok","private_message":"","extra":NaN}'))
    def test_exact_boundaries(self):
        def c(nums):
            return classify(nums,dict(ci95=[.1,2],**exact_signflip(nums)))
        self.assertEqual(c([18]*5),'HIT')
        self.assertEqual(c([17]*5),'ODD')
        self.assertEqual(c([4,4,4,5,5]),'DUD')
        self.assertEqual(c([-18]*5),'ODD-reverse')
        self.assertEqual(exact_signflip([0]*5)['exact_signflip_p_upper'],1)
    def test_next_round_private_only(self):
        class Fake:
            dry=True
            def __init__(self): self.prompts=[]
            def call(self, system,user,tier,backend,rid,t,agent,attempt,model):
                self.prompts.append((t,agent,system,user))
                msg='' if 'You have no message box.' in user else f'unique_{t}_{agent}'
                return dict(text=json.dumps(dict(quantity=6,reasoning='test',private_message=msg)),model='dry',backend='dry')
        cache=Fake()
        game=run_game(24080,'legality',cache,'gpt-6-luna','codex',2)
        pair=game['ground_truth']['assigned_pair']
        for t,a,system,user in cache.prompts:
            self.assertIn('are prohibited',system)
            self.assertNotIn(f'unique_{t}_',user)
            if a not in pair: self.assertNotIn('unique_',user)
            elif t:
                partner=next(b for b in pair if b!=a)
                self.assertIn(f'unique_0_{partner}',user)
                self.assertNotIn(f'unique_0_{a}',user)
    def test_routing_fails(self):
        class Fake:
            dry=False
            def call(self,*a):return dict(text=json.dumps(dict(quantity=6,reasoning='ok',private_message='')),model='wrong',backend='codex')
        with self.assertRaisesRegex(RuntimeError,'model/backend mismatch'): run_game(24080,'neutral',Fake(),'gpt-6-luna','codex',1)
    def test_deadline_blocks_new_call(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as tmp:
            cache=LegalityCache(Path(tmp)/'responses.jsonl')
            with patch('sim.legality.now',return_value='2026-10-24T17:05:00+00:00'):
                with self.assertRaisesRegex(RuntimeError,'deadline'):
                    cache.call('s','p','cheap','codex','r',0,'A',0,'gpt-6-luna')
    def test_failed_game_preserves_completed_partner(self):
        from sim.legality import main
        original=run_game
        def game(seed,condition,*args,**kwargs):
            if condition=='neutral': raise RuntimeError('synthetic failure')
            return original(seed,condition,*args,**kwargs)
        with tempfile.TemporaryDirectory(dir='/var/tmp') as tmp:
            with patch('sys.argv',['sim.legality','--dry','--out',tmp]), patch('sim.legality.run_game',side_effect=game):
                with self.assertRaisesRegex(RuntimeError,'completed partner preserved'):main()
            self.assertEqual(len(list(Path(tmp).glob('game_*.json'))),1)
            self.assertEqual(len(list(Path(tmp).glob('failure_*.json'))),1)
    def test_full_dry_and_tampering(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as tmp:
            subprocess.run(['uv','run','python','-m','sim.legality','--dry','--out',tmp],check=True,capture_output=True)
            result=analyze(tmp,True)
            audit=verify(tmp,result)
            self.assertEqual(audit['calls'],360)
            broken=copy.deepcopy(result);broken['verdict']='TAMPER'
            with self.assertRaises(AssertionError):verify(tmp,broken)
            export=Path(tmp)/'trajectories.jsonl'
            saved=export.read_bytes();export.write_bytes(saved.splitlines(keepends=True)[0])
            with self.assertRaises(AssertionError):verify(tmp,result)
            export.write_bytes(saved)
            path=next(Path(tmp).glob('game_*.json'))
            game=json.loads(path.read_text());game['ground_truth']['private_chat'][0]['text']='tamper'
            path.write_text(json.dumps(game))
            with self.assertRaises(ValueError):analyze(tmp,True)

if __name__=='__main__':unittest.main()
