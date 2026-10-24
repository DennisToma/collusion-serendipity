"""S06 scaling invariance, visibility, fail-closed provenance and analysis checks."""
import contextlib
import io
import itertools
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from sim.denomination import (DenominationCache, conditional_table, market_system,
    parse_action, prompt, run_game, assert_cached_replay, main, scale)
from scripts.s06_analyze import analyze, exact_signflip, classify


def rows():
    return [dict(round=t,market=dict(price=max(0,30-sum(qs))),agents=[
        dict(id=a,quantity=q,profit=(max(0,30-sum(qs))-6)*q) for a,q in zip('ABC',qs)])
        for t,qs in enumerate([[4,6,8],[12,10,11],[0,1,2]])]


class Tests(unittest.TestCase):
    def test_exhaustive_real_payoff_and_argmax_invariance(self):
        for qs in itertools.product(range(13),repeat=3):
            p=max(0,30-sum(qs));pc=max(0,3000-100*sum(qs))
            self.assertEqual(pc,100*p)
            self.assertEqual([(pc-600)*q for q in qs],[100*(p-6)*q for q in qs])
        for rivals in range(25):
            u=conditional_table(rivals);c=conditional_table(rivals,100)
            self.assertEqual([v['own_profit'] for v in c],[100*v['own_profit'] for v in u])
            best=lambda v:[r['quantity'] for r in v if r['own_profit']==max(r['own_profit'] for r in v)]
            self.assertEqual(best(u),best(c))

    def test_all_displayed_money_scaled(self):
        h=rows();saved=json.dumps(h)
        for t in range(4):
            for a in 'ABC':
                user,table=prompt(a,'cent',h[:t]);unit,ut=prompt(a,'unit',h[:t])
                history=json.loads(user.split('Available completed public rounds: ')[1].split('\n')[0])
                uh=json.loads(unit.split('Available completed public rounds: ')[1].split('\n')[0])
                for r,u in zip(history,uh):
                    self.assertEqual(r['price'],100*u['price'])
                    self.assertEqual(r['profits'],{a:100*v for a,v in u['profits'].items()})
                    self.assertEqual(r['quantities'],u['quantities']);self.assertEqual(r['round'],u['round'])
                if t:self.assertEqual(table,[dict(quantity=v['quantity'],own_profit=100*v['own_profit']) for v in ut])
                else:self.assertIsNone(table)
        self.assertEqual(saved,json.dumps(h))
        for c,k in [('unit',1),('cent',100)]:
            system=market_system('A',c)
            self.assertIn(f'{30*k} - {k} *',system);self.assertIn(f'cost is {6*k} accounting units per unit of product',system)
            self.assertIn(f'conversion rate is {k} accounting units per common currency unit',system)

    def test_no_current_round_or_reasoning_leak(self):
        seen=[]
        class Fake:
            dry=True
            def call(self,system,user,tier,backend,run_id,t,agent,attempt,model):
                seen.append((t,json.loads(user.split('Available completed public rounds: ')[1].split('\n')[0]),user))
                return dict(text=json.dumps(dict(quantity=6,reasoning='SECRET_CANARY',private_message='')),model='dry',backend='dry')
        with contextlib.redirect_stdout(io.StringIO()):run_game(24160,'cent',Fake(),'gpt-6-luna','codex',3)
        for t,history,user in seen:
            self.assertEqual(len(history),t);self.assertNotIn('SECRET_CANARY',user)

    def test_strict_action_and_route(self):
        good=dict(quantity=6,reasoning='ok',private_message='')
        for value in [True,6.0,-1,13]:self.assertIsNone(parse_action(json.dumps(dict(good,quantity=value))))
        for obj in [dict(good,reasoning='word '*41),dict(good,private_message='x')]:self.assertIsNone(parse_action(json.dumps(obj)))
        self.assertIsNone(parse_action('{"quantity":1,"quantity":6,"reasoning":"","private_message":""}'))
        self.assertIsNone(parse_action('{"quantity":NaN,"reasoning":"","private_message":""}'))
        class Bad:
            dry=False
            import threading
            abort=threading.Event()
            def call(self,*args):return dict(text=json.dumps(good),model='WRONG',backend='codex')
        cache=Bad()
        with self.assertRaisesRegex(RuntimeError,'mismatch'):run_game(24160,'unit',cache,'gpt-6-luna','codex')
        self.assertTrue(cache.abort.is_set())

    def test_deadline_and_worker_abort(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            c=DenominationCache(Path(td)/'responses.jsonl')
            with patch('sim.denomination.now',return_value='2099'),patch('sim.common.llm.chat',side_effect=AssertionError):
                with self.assertRaisesRegex(RuntimeError,'deadline'):run_game(24160,'unit',c,'gpt-6-luna','codex')
                self.assertTrue(c.abort.is_set())
                with self.assertRaisesRegex(RuntimeError,'Terminal failure'):c.call('s','u','cheap','codex','x',0,'A',0,'gpt-6-luna')

    def test_torn_missing_and_changed_cache(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td)/'responses.jsonl';p.write_text('{')
            with self.assertRaisesRegex(ValueError,'Torn'):DenominationCache(p,True)
            self.assertEqual(p.read_text(),'{');p.unlink()
            c=DenominationCache(p,True);c.call('s','u','cheap','codex','test',0,'A',0,'gpt-6-luna')
            req=p.with_name('requests.jsonl');old=req.read_bytes();req.unlink()
            with self.assertRaisesRegex(ValueError,'provenance mismatch'):DenominationCache(p,True)
            req.write_bytes(old);response=json.loads(p.read_text());response['response']['text']='changed';p.write_text(json.dumps(response)+'\n')
            with self.assertRaisesRegex(ValueError,'provenance corrupted'):DenominationCache(p,True)

    def test_two_sided_screen(self):
        for nums,ci,verdict in [([27]*5,[1,1],'HIT'),([-27]*5,[-1,-1],'HIT'),([0]*5,[0,0],'DUD'),([54,-27,54,54,54],[-1,2],'ODD')]:
            s=dict(ci95=ci,**exact_signflip(nums));self.assertEqual(classify(nums,s),verdict)
        self.assertEqual(exact_signflip([27]*5)['exact_signflip_p_two_sided'],.0625)
        self.assertGreaterEqual(exact_signflip([0,27,27,27,27])['exact_signflip_p_two_sided'],.125)

    def test_dry_full_pipeline_and_tamper(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            d=Path(td)
            with contextlib.redirect_stdout(io.StringIO()),patch.object(sys,'argv',['sim.denomination','--dry','--out',td]):main()
            with patch('sim.common.llm.chat',side_effect=AssertionError('Must stay offline')):
                r=analyze(d,True);self.assertEqual(r['n_games'],10)
                from scripts.s06_independent import check
                rp=d/'result.json';rp.write_text(json.dumps(r))
                with contextlib.redirect_stdout(io.StringIO()):check(d,rp,d/'ind.json')
                broken=json.loads(rp.read_text());del broken['metrics']['all_equal'];rp.write_text(json.dumps(broken))
                with self.assertRaises(AssertionError):check(d,rp,d/'ind.json')
                with self.assertRaises(AssertionError):analyze(d)
                for name in ['config.json','trajectories.jsonl','raw/requests.jsonl','raw/responses.jsonl']:
                    p=d/name;old=p.read_bytes()
                    if name=='config.json':
                        obj=json.loads(old);obj['sources']['sim/denomination.py']='0'*64;p.write_text(json.dumps(obj))
                    else:p.write_bytes(b'\n'.join(old.splitlines()[:-1])+b'\n')
                    with self.assertRaises((ValueError,AssertionError)):analyze(d,True)
                    p.write_bytes(old)
                marker=d/'failure_x.json';marker.write_text('{}')
                with self.assertRaises(AssertionError):analyze(d,True)
                marker.unlink();self.assertEqual(r,analyze(d,True))
                p=d/'raw/responses.jsonl';old=p.read_bytes();c=DenominationCache(p,True)
                c.call('s','u','cheap','codex','orphan',0,'A',0,'gpt-6-luna')
                with self.assertRaisesRegex(ValueError,'every key'):analyze(d,True)

    def test_resume_preserves_earliest_call_and_sequential_validation(self):
        from scripts.s06_analyze import validate_game
        class Cached:
            dry=False
            def call(self,system,user,tier,backend,rid,t,a,attempt,model):
                i=t*3+'ABC'.index(a)
                return dict(text=json.dumps(dict(quantity=6,reasoning='',private_message='')),
                            model=model,backend=backend,call_started_utc=f'2026-10-24T18:00:{i:02d}+00:00',
                            call_completed_utc=f'2026-10-24T18:00:{i:02d}+00:00')
        with contextlib.redirect_stdout(io.StringIO()):g=run_game(24160,'unit',Cached(),'gpt-6-luna','codex')
        self.assertEqual(g['ground_truth']['started_utc'],'2026-10-24T18:00:00+00:00')
        cfg=dict(dry=False,model='gpt-6-luna',backend='codex')
        validate_game(g,cfg)
        g['ground_truth']['call_provenance'][1]['call_started_utc']='2026-10-24T17:59:59+00:00'
        with self.assertRaises(AssertionError):validate_game(g,cfg)

    def test_dry_destination(self):
        with patch.object(sys,'argv',['sim.denomination','--dry']):
            with self.assertRaisesRegex(ValueError,'Dry destination'):main()

if __name__=='__main__':unittest.main()
