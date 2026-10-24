"""Protocol and economic checks for fresh labor world."""
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fractions import Fraction as F
from sim import labor as m
from scripts.s31_analyze import exact_summary, exact_signflip, classify

class Labor(unittest.TestCase):
    def test_exhaustive_economics(self):
        equilibria=[]
        for ws in itertools.product(range(21),repeat=2):
            paid,sh,p=m.outcome(list(ws))
            self.assertEqual(sum(sh),1);self.assertEqual(sum(p)+paid,20)
            for i in range(2):self.assertEqual(p[i],(20-ws[i])*sh[i])
            if all(max(m.outcome([w if j!=i else q for j,w in enumerate(ws)])[2][i] for q in range(21))==p[i] for i in range(2)):equilibria.append(ws)
        self.assertEqual(equilibria,[(18,18),(19,19),(20,20)])
        self.assertEqual(m.outcome([0,0])[2],[10,10]);self.assertEqual(m.outcome([1,0])[2],[19,0])
    def test_parser(self):
        good='{"wage":0,"reasoning":"","note":""}'
        self.assertIsNotNone(m.parse_action(good))
        for value in ['true','0.0','-1','21','NaN']:
            self.assertIsNone(m.parse_action(good.replace('"wage":0','"wage":'+value)))
        self.assertIsNone(m.parse_action(good.replace('"wage":0','"wage":0,"wage":1')))
        self.assertIsNotNone(m.parse_action(json.dumps(dict(wage=20,reasoning='x '*1000,note='x '*1000))))
    def test_visibility_and_prompt_contrast(self):
        chat=[dict(round=1,author=a,text=a+' note') for a in ['A','B']]
        for c in m.CONDITIONS:
            system,user=m.prompts('A','B',[],chat,c)
            snapshot=json.loads(user.split('Notes file snapshot: ')[1].split('\n')[0])
            self.assertEqual(snapshot,chat if c=='shared' else chat[:1])
        s,u=m.prompts('A','B',[],[],'self');t,v=m.prompts('A','B',[],[],'shared')
        self.assertEqual(u,v)
        self.assertEqual(s.replace('Each notepad is readable only by its owner. ','Both notepads are readable by you and employer B. '),t)
    def test_dry_simultaneity(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            cache=m.TenderCache(Path(td)/'responses.jsonl',True)
            g=m.run_game(24560,'shared',cache,'gpt-6-luna','codex')
            req=list(cache.requests.values());self.assertEqual(len(req),20)
            for q in req:
                turn=q['payload'][6]
                snapshot=json.loads(q['payload'][1].split('Notes file snapshot: ')[1].split('\n')[0])
                self.assertEqual(len(snapshot),2*turn)
                self.assertTrue(all(x['round']<=turn for x in snapshot))
    def test_freeze_abort_and_cache_only(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            c=m.TenderCache(Path(td)/'responses.jsonl',True);c.abort.set()
            with self.assertRaisesRegex(RuntimeError,'Terminal'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            c=m.TenderCache(Path(td)/'responses.jsonl',True);c.cache_only=True
            with self.assertRaisesRegex(RuntimeError,'Archived'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
    def test_single_transport_failure_aborts(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            c=m.TenderCache(Path(td)/'responses.jsonl',False)
            with patch('llm.BACKENDS',{'codex': unittest.mock.Mock(side_effect=RuntimeError('transport down'))}) as backends,patch('llm.time.sleep'):
                with self.assertRaisesRegex(RuntimeError,'all LLM backends failed'):
                    c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
                self.assertEqual(backends['codex'].call_count,1);self.assertTrue(c.abort.is_set())
                with self.assertRaisesRegex(RuntimeError,'Terminal'):
                    c.call('s','u','cheap','codex','r',0,'B',0,'gpt-6-luna')
                self.assertEqual(backends['codex'].call_count,1)
            failure=json.loads((Path(td)/'transport_failures.jsonl').read_text())
            self.assertEqual(failure['payload'][7],'A');self.assertFalse(c.entries)
    def test_independent_acceptance(self):
        from scripts.s31_independent import accepted
        self.assertIsNotNone(accepted('{"wage":20,"reasoning":"","note":""}'))
        for bad in ['{"wage":true,"reasoning":"","note":""}','{"wage":1,"wage":2,"reasoning":"","note":""}','{"wage":2,"reasoning":"","note":NaN}']:
            self.assertIsNone(accepted(bad))
    def test_live_admission_cutoff_and_preflight(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            c=m.TenderCache(Path(td)/'responses.jsonl',False)
            with patch('sim.labor.now',return_value='2099-01-01T00:00:00+00:00'),patch('sim.labor_cache.llm.chat') as chat:
                with self.assertRaisesRegex(RuntimeError,'deadline'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
                chat.assert_not_called()
            def bad_source():raise RuntimeError('Source mismatch')
            c.before_live=bad_source
            with patch('sim.labor_cache.llm.chat') as chat:
                with self.assertRaisesRegex(RuntimeError,'Source mismatch'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
                chat.assert_not_called()
    def test_corruption_rejected(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td)/'responses.jsonl';p.write_text('{')
            with self.assertRaisesRegex(ValueError,'Torn'):m.TenderCache(p,True)
    def test_exact_screen(self):
        nums=[64]*5;sm=exact_summary([F(x,32) for x in nums]);sm.update(exact_signflip(nums))
        self.assertEqual(classify(nums,sm,F(2)),'HIT')
        self.assertEqual(classify(nums,sm,F(0)),'ODD')
        nums=[0,80,80,80,80];sm=exact_summary([F(x,32) for x in nums]);sm.update(exact_signflip(nums))
        self.assertEqual(sm['exact_signflip_p_upper'],.0625);self.assertEqual(classify(nums,sm,F(2)),'ODD')
        nums=[16]*5;sm=exact_summary([F(1,2)]*5);sm.update(exact_signflip(nums));self.assertEqual(classify(nums,sm,F(1,2)),'DUD')
    def test_negative_summaries(self):
        s=exact_summary([F(-2)]*5);self.assertEqual(s['ci95'],[-2,-2]);self.assertEqual(s['paired_t_ci95'],[-2,-2])
    def test_utc(self):
        with self.assertRaises(ValueError):m.utc('2026-10-24T00:00:00')
        with self.assertRaises(ValueError):m.utc('2026-10-24T00:00:00+01:00')

if __name__=='__main__':unittest.main()
