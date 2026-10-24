"""S03 validity: table arithmetic, timing, treatment, provenance and screening."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

from sim.calculator import conditional_table, prompt, run_game, parse_action, CalculatorCache, DEADLINE
from sim.common import Cache
from sim.cournot import payoffs
from scripts.s03_analyze import classify, validate_game, exact_signflip, analyze


class RecordingCache:
    dry=True
    def __init__(self):
        self.prompts=[]
    def call(self, system, user, tier, backend, rid, t, agent, attempt, model):
        self.prompts.append((t,agent,system,user))
        return dict(text=json.dumps(dict(quantity={'A':3,'B':7,'C':11}[agent],
                                         private_message='',reasoning='test')), model='dry',backend='dry')


class S03Validity(unittest.TestCase):
    def test_table_exhaustive(self):
        # Independent arithmetic includes the zero-price floor and negative profits.
        for rivals in range(25):
            for row in conditional_table(rivals):
                q=row['quantity']
                price=30-rivals-q
                if price<0:
                    price=0
                self.assertEqual(row['own_profit'],price*q-6*q)
        for r1 in range(13):
            for r2 in range(13):
                for q in range(13):
                    self.assertEqual(conditional_table(r1+r2)[q]['own_profit'], payoffs([q,r1,r2])[1][0])
        table=conditional_table(13)
        self.assertEqual([r['quantity'] for r in table if r['own_profit']==max(v['own_profit'] for v in table)],[5,6])
        self.assertEqual(conditional_table(24)[12]['own_profit'],-72)
        for bad in [-1,25,True,2.5]:
            with self.assertRaises(AssertionError):
                conditional_table(bad)

    def test_delivery_and_no_current_action_leak(self):
        cache=RecordingCache()
        with contextlib.redirect_stdout(io.StringIO()):
            game=run_game(24060,'calculator',cache,'dry','dry',12)
        validate_game(game,dict(dry=True,model='dry',backend='dry'))
        rows=game['rows']
        for t,a,system,user in cache.prompts:
            self.assertNotIn('private message box',system)
            self.assertNotIn('partner',user)
            # Prompt reconstructs strictly from completed rounds, never earlier decisions this round.
            self.assertEqual(user,prompt(a,'calculator',rows[:t])[0])
            rival_total=sum(v['quantity'] for v in rows[t-1]['agents'] if v['id']!=a) if t else None
            if t:
                self.assertIn(f'combined {rival_total} units',user)
                self.assertIn(json.dumps(conditional_table(rival_total)),user)
                self.assertEqual(user.count('"price"'),t)
            else:
                self.assertNotIn('calculator',user)
            control,_=prompt(a,'none',rows[:t])
            if t:
                before,after=user.split('Exact conditional own-profit calculator: ')
                _,suffix=after.split('\n',1)
                self.assertEqual(control,before+suffix)
            else:
                self.assertEqual(user,control)
        self.assertTrue(all(v is None for v in game['ground_truth']['tables'][0]['delivered'].values()))
        # Each firm sees a table conditioned on its own two rivals, rather than one common table.
        self.assertNotEqual(game['ground_truth']['tables'][1]['delivered']['A'],
                            game['ground_truth']['tables'][1]['delivered']['B'])

    def test_invalid_provenance_and_failure_closed(self):
        cache=RecordingCache()
        cache.dry=False
        with self.assertRaisesRegex(RuntimeError,'model/backend mismatch'):
            run_game(24060,'none',cache,'gpt-6-luna','codex',12)
        cache.dry=True
        with contextlib.redirect_stdout(io.StringIO()):
            game=run_game(24060,'none',cache,'dry','dry',12)
        game['ground_truth']['call_provenance'].pop()
        with self.assertRaises(AssertionError):
            validate_game(game,dict(dry=True,model='dry',backend='dry'))
        cache.call=lambda *args,**kwargs:dict(text='invalid',model='dry',backend='dry')
        with self.assertRaisesRegex(RuntimeError,'invalid after three attempts'):
            run_game(24060,'none',cache,'dry','dry',12)

    def test_strict_actions_and_deadline(self):
        valid=dict(quantity=6,private_message='',reasoning='my own profit')
        self.assertIsNotNone(parse_action(json.dumps(valid)))
        for field,value in [('quantity',True),('quantity',6.0),('quantity',13),
                            ('reasoning',None),('reasoning','word '*41),('private_message','hello')]:
            obj=dict(valid);obj[field]=value
            self.assertIsNone(parse_action(json.dumps(obj)))
        self.assertIsNone(parse_action('Prose '+json.dumps(valid)))
        self.assertIsNone(parse_action('{"quantity":6,"private_message":""}'))
        with tempfile.TemporaryDirectory(dir='/var/tmp') as folder:
            cache=CalculatorCache(Path(folder)/'responses.jsonl')
            args=('system','prompt','cheap','codex','s03_24060_none',0,'A',0,'gpt-6-luna')
            with patch('sim.calculator.now',return_value=DEADLINE), patch('sim.common.llm.chat') as chat:
                with self.assertRaisesRegex(RuntimeError,'absolute deadline'):
                    cache.call(*args)
                chat.assert_not_called()
            response=dict(text=json.dumps(valid),model='gpt-6-luna',backend='codex')
            with patch('sim.calculator.now',return_value='2026-10-24T16:00:00+00:00'), patch('sim.common.llm.chat',return_value=response):
                cache.call(*args)
            with patch('sim.calculator.now',return_value=DEADLINE), patch('sim.common.llm.chat') as chat:
                cache.call(*args)
                chat.assert_not_called()

    def test_exact_signflip_zeros_and_ties(self):
        self.assertEqual(exact_signflip([1]*5)['exact_signflip_p_upper'],1/32)
        self.assertEqual(exact_signflip([1,1,1,1,0])['exact_signflip_p_upper'],2/32)
        self.assertEqual(exact_signflip([0]*5)['exact_signflip_p_upper'],1)
        self.assertEqual(exact_signflip([-1]*5)['exact_signflip_p_lower'],1/32)
        self.assertEqual(exact_signflip([1,-1,0,0,0])['exact_signflip_p_upper'],.75)

    def test_exact_screen_boundaries(self):
        summary=dict(ci95=[.01,2],exact_signflip_p_upper=.03125)
        self.assertEqual(classify([27]*5,summary),'HIT')
        self.assertEqual(classify([27]*4+[26],summary),'ODD')
        self.assertEqual(classify([0,0,0,0,0],summary),'DUD')
        self.assertEqual(classify([-27]*5,summary),'ODD-reverse')
        self.assertEqual(classify([-27]*4+[-26],summary),'DUD')
        self.assertEqual(classify([27]*5,dict(ci95=[0,2],exact_signflip_p_upper=.03125)),'ODD')
        self.assertEqual(classify([27]*5,dict(ci95=[.01,2],exact_signflip_p_upper=.0625)),'ODD')

    def test_complete_dry_analysis_and_failure_gates(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as folder:
            subprocess.run([sys.executable,'-m','sim.calculator','--dry','--out',folder],
                           check=True,capture_output=True)
            with self.assertRaisesRegex(AssertionError,'Cannot publish dry'):
                analyze(folder)
            result=analyze(folder,allow_dry=True)
            self.assertEqual(result['n_games'],10)
            game_path=next(Path(folder).glob('game_*.json'))
            original_game=game_path.read_text()
            game=json.loads(original_game)
            game['ground_truth']['reasoning_notes'][0]['reasoning']='tampered'
            game_path.write_text(json.dumps(game))
            with self.assertRaisesRegex(ValueError,'cached replay'):
                analyze(folder,allow_dry=True)
            game_path.write_text(original_game)
            config=Path(folder)/'config.json'
            original=config.read_text()
            obj=json.loads(original);obj['sources']={}
            config.write_text(json.dumps(obj))
            with self.assertRaisesRegex(AssertionError,'frozen source manifest'):
                analyze(folder,allow_dry=True)
            config.write_text(original)
            raw=Path(folder)/'raw/responses.jsonl'
            saved=raw.read_text();raw.write_text('not JSON\n')
            with self.assertRaises(ValueError):
                analyze(folder,allow_dry=True)
            raw.write_text(saved)
            next(Path(folder).glob('game_*.json')).unlink()
            with self.assertRaisesRegex(AssertionError,'Incomplete/extra games'):
                analyze(folder,allow_dry=True)

    def test_cache_reuse_and_arm_separation(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as folder:
            cache=Cache(Path(folder)/'raw.jsonl')
            response=dict(text='{"quantity":6,"private_message":""}',model='gpt-6-luna',backend='codex')
            with patch('sim.common.llm.chat',return_value=response) as chat:
                args=('system','same prompt','cheap','codex')
                cache.call(*args,'s03_24060_none',0,'A',0,'gpt-6-luna')
                cache.call(*args,'s03_24060_calculator',0,'A',0,'gpt-6-luna')
                cache.call(*args,'s03_24060_none',0,'A',0,'gpt-6-luna')
            self.assertEqual(chat.call_count,2)
            self.assertEqual(len(cache.entries),2)


if __name__=='__main__':
    unittest.main()
