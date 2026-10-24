"""Tests for feedback leakage, strict responses, exact arithmetic and integrity."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from sim.delay import DelayCache, conditional_table, market_system, parse_action, prompt, visible_rows
from scripts.s11_analyze import classify, exact_signflip, metrics


def rows():
    return [dict(round=t,market=dict(price=30-3*q),agents=[dict(id=a,quantity=q,profit=(24-3*q)*q) for a in 'ABC'])
            for t,q in enumerate([4,8,4,8])]


class Tests(unittest.TestCase):
    def test_information_delay(self):
        history=rows()
        for t in range(5):
            for c,lag in [('immediate',1),('delayed',2)]:
                view=visible_rows(history[:t],c)
                self.assertEqual(len(view),max(0,t-lag+1))
                text,table=prompt('A',c,history[:t])
                self.assertIn(f'Round {t+1}.',text)
                if view:self.assertEqual(table,conditional_table(2*view[-1]['agents'][0]['quantity']))
                else:self.assertIsNone(table)
                # Hidden most recent action is not referenced in the available-history JSON.
                encoded=text.split('Available completed public rounds: ')[1].split('\n')[0]
                self.assertEqual([r['round'] for r in json.loads(encoded)],list(range(1,len(view)+1)))
        self.assertNotIn('revealed after each round',market_system('A','delayed'))

    def test_counterfactual_hidden_row(self):
        h=rows();before=prompt('A','delayed',h)
        h[-1]['agents'][0]['quantity']=11
        self.assertEqual(before,prompt('A','delayed',h))
        self.assertNotEqual(prompt('A','immediate',rows()),prompt('A','immediate',h))

    def test_strict_parser(self):
        obj=dict(quantity=6,reasoning='ok',private_message='')
        self.assertIsNotNone(parse_action(json.dumps(obj)))
        for bad in [True,6.0,-1,13]:
            self.assertIsNone(parse_action(json.dumps(dict(obj,quantity=bad))))
        for bad in [dict(obj,reasoning='word '*41),dict(obj,private_message='x')]:
            self.assertIsNone(parse_action(json.dumps(bad)))
        self.assertIsNone(parse_action('{"quantity":4,"quantity":6,"reasoning":"","private_message":""}'))
        self.assertIsNone(parse_action('{"quantity":NaN,"reasoning":"","private_message":""}'))

    def test_all_tables(self):
        for r in range(25):
            self.assertEqual(conditional_table(r),[dict(quantity=q,own_profit=(max(0,30-r-q)-6)*q) for q in range(13)])

    def test_metric_and_boundaries(self):
        h=rows()*3
        self.assertEqual(metrics(dict(rows=h))['absolute_change'],4)
        p=exact_signflip([27]*5);self.assertEqual(p['exact_signflip_p_upper'],1/32)
        self.assertEqual(classify([27]*5,dict(ci95=[1,1],**p)),'HIT')
        self.assertEqual(classify([0]*5,dict(ci95=[0,0],**exact_signflip([0]*5))),'DUD')
        self.assertEqual(classify([-27]*5,dict(ci95=[-1,-1],**exact_signflip([-27]*5))),'ODD-reverse')

    def test_cache_damage(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td)/'responses.jsonl';p.write_text('{')
            with self.assertRaises(ValueError):DelayCache(p,True)
            self.assertEqual(p.read_text(),'{')
            p.write_text('{"key":"x","response":{}}\n'*2)
            with self.assertRaises(ValueError):DelayCache(p,True)

    def test_deadline(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            cache=DelayCache(Path(td)/'responses.jsonl')
            with patch('sim.delay.now',return_value='2099'),patch('sim.common.llm.chat',side_effect=AssertionError):
                with self.assertRaisesRegex(RuntimeError,'deadline'):cache.call('s','u','cheap','codex','test',0,'A',0,'gpt-6-luna')

    def test_missing_provenance_rejected(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td)/'responses.jsonl';c=DelayCache(p,True)
            c.call('s','u','cheap','codex','test',0,'A',0,'gpt-6-luna')
            p.with_name('requests.jsonl').unlink()
            with self.assertRaisesRegex(ValueError,'provenance mismatch'):DelayCache(p,True)
            self.assertFalse(p.with_name('requests.jsonl').exists())

    def test_corrupt_provenance_rejected(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td)/'responses.jsonl';c=DelayCache(p,True)
            c.call('s','u','cheap','codex','test',0,'A',0,'gpt-6-luna')
            row=json.loads(p.read_text());row['response']['text']='changed'
            p.write_text(json.dumps(row)+'\n')
            with self.assertRaisesRegex(ValueError,'provenance corrupted'):DelayCache(p,True)

    def test_abort(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            cache=DelayCache(Path(td)/'responses.jsonl',True);cache.abort.set()
            with self.assertRaisesRegex(RuntimeError,'Terminal failure'):
                cache.call('s','u','cheap','codex','test',0,'A',0,'gpt-6-luna')

    def test_empty_directory_transport(self):
        import llm
        observed=[]
        def fake_run(cmd,**kwargs):
            cwd=Path(cmd[cmd.index('-C')+1]);observed.append(cwd)
            self.assertNotEqual(cwd,Path.cwd());self.assertEqual(list(cwd.iterdir()),[])
            self.assertEqual(cmd[cmd.index('-s')+1],'read-only')
            self.assertIn('Do not run commands',cmd[-1])
            Path(cmd[cmd.index('-o')+1]).write_text('mock')
        with patch('llm.subprocess.run',side_effect=fake_run):
            self.assertEqual(llm._codex([dict(role='user',content='test')],'gpt-6-luna',1,512),('mock','gpt-6-luna'))
        self.assertFalse(observed[0].exists())

    def test_dry_replay_tamper(self):
        import contextlib,io
        from sim.delay import run_game,assert_cached_replay
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            d=Path(td);cache=DelayCache(d/'raw/responses.jsonl',True)
            with contextlib.redirect_stdout(io.StringIO()):
                g=run_game(24110,'delayed',cache,'gpt-6-luna','codex')
            cfg=dict(dry=True,model='gpt-6-luna',backend='codex')
            before=(d/'raw/responses.jsonl').read_bytes()
            assert_cached_replay(d,[g],cfg)
            self.assertEqual(before,(d/'raw/responses.jsonl').read_bytes())
            g['rows'][1]['agents'][0]['quantity']=(g['rows'][1]['agents'][0]['quantity']+1)%13
            with self.assertRaises(ValueError):assert_cached_replay(d,[g],cfg)

    def test_no_same_round_leak(self):
        from sim.delay import run_game
        seen=[]
        class Fake:
            dry=True
            def call(self,system,user,tier,backend,run_id,t,agent,attempt,model):
                encoded=user.split('Available completed public rounds: ')[1].split('\n')[0]
                seen.append((t,agent,json.loads(encoded)))
                return dict(text=json.dumps(dict(quantity=6,reasoning='',private_message='')),model='dry',backend='dry')
        import contextlib,io
        with contextlib.redirect_stdout(io.StringIO()):run_game(24110,'delayed',Fake(),'gpt-6-luna','codex',3)
        for t,agent,h in seen:
            self.assertEqual(len(h),max(0,t-1))
            self.assertEqual([v['round'] for v in h],list(range(1,max(0,t-1)+1)))

class PublicationTests(unittest.TestCase):
    def test_full_pipeline_and_tamper(self):
        import contextlib,io,sys
        from sim.delay import main
        from scripts.s11_analyze import analyze
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            d=Path(td)
            with contextlib.redirect_stdout(io.StringIO()),patch.object(sys,'argv',['sim.delay','--dry','--out',td]):main()
            with patch('sim.common.llm.chat',side_effect=AssertionError('Must stay offline')):
                result=analyze(d,True)
                self.assertEqual(result['n_games'],10)
                with self.assertRaises(AssertionError):analyze(d)
                targets=[('source',d/'config.json'),('version',d/'config.json'),
                         ('export',d/'trajectories.jsonl'),('game',next(d.glob('game_*.json')))]
                for kind,path in targets:
                    with self.subTest(kind=kind):
                        old=path.read_bytes()
                        if kind=='export':path.write_text('')
                        else:
                            obj=json.loads(old)
                            if kind=='source':obj['sources']['sim/delay.py']='0'*64
                            elif kind=='version':obj['version']='wrong'
                            else:obj['rows'][0]['agents'][0]['quantity']=99
                            path.write_text(json.dumps(obj)+'\n')
                        with self.assertRaises((AssertionError,ValueError)):analyze(d,True)
                        path.write_bytes(old)
                marker=d/'failure_test.json';marker.write_text('{}')
                with self.assertRaises(AssertionError):analyze(d,True)
                marker.unlink()
                raw=d/'raw/responses.jsonl';old=raw.read_bytes()
                raw.write_bytes(b'\n'.join(old.splitlines()[:-1])+b'\n')
                with self.assertRaises((AssertionError,ValueError)):analyze(d,True)
                raw.write_bytes(old)
                self.assertEqual(result,analyze(d,True))

    def test_dry_generation_cannot_touch_live_destination(self):
        import sys
        from sim.delay import main
        with patch.object(sys,'argv',['sim.delay','--dry']):
            with self.assertRaisesRegex(ValueError,'Dry destination'):main()

if __name__=='__main__':unittest.main()


