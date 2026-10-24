"""S03 validity: table arithmetic, timing, treatment, provenance and screening."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sim.calculator import conditional_table, prompt, run_game
from sim.common import Cache
from scripts.s03_analyze import classify, validate_game


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

    def test_exact_screen_boundaries(self):
        summary=dict(ci95=[.01,2],exact_signflip_p_upper=.03125)
        self.assertEqual(classify([27]*5,summary),'HIT')
        self.assertEqual(classify([27]*4+[26],summary),'ODD')
        self.assertEqual(classify([0,0,0,0,0],summary),'DUD')
        self.assertEqual(classify([-27]*5,summary),'ODD-reverse')
        self.assertEqual(classify([-27]*4+[-26],summary),'DUD')
        self.assertEqual(classify([27]*5,dict(ci95=[0,2],exact_signflip_p_upper=.03125)),'ODD')
        self.assertEqual(classify([27]*5,dict(ci95=[.01,2],exact_signflip_p_upper=.0625)),'ODD')

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
