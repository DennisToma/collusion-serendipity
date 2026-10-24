"""S16 economically meaningful checks, timing, fail-closed archives and statistics."""
import contextlib
from fractions import Fraction as F
import io
import itertools
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from sim.notes import TenderCache, outcome, prompts, parse_action, run_game, main
from scripts.s16_analyze import analyze, exact_signflip, classify


def equilibrium_check():
    equilibria=[]
    for bs in itertools.product(range(6,21),repeat=3):
        p,sh,pf=outcome(list(bs))
        assert sum(sh)==1 and sum(pf)==p-6
        assert pf==[(b-6)*s for b,s in zip(bs,sh)]
        if all(max(outcome(list(bs[:i])+[q]+list(bs[i+1:]))[2][i] for q in range(6,21))==pf[i] for i in range(3)):
            equilibria.append(bs)
    assert set(min(b) for b in equilibria)=={6,7}
    assert (6,6,6) in equilibria and (7,7,7) in equilibria
    return equilibria


class Tests(unittest.TestCase):
    def test_exhaustive_economics_and_nash(self):
        eq=equilibrium_check();self.assertTrue(eq)
        self.assertEqual(outcome([10,10,20]),(10,[F(1,2),F(1,2),F(0)],[F(2),F(2),F(0)]))
        self.assertEqual(outcome([20,20,20])[2],[F(14,3)]*3)

    def test_note_timing_visibility_no_reasoning_or_current_bid_leak(self):
        for cond in ['self','shared']:
            seen=[]
            class Fake:
                dry=True
                def call(self,system,user,tier,backend,rid,t,a,attempt,model):
                    seen.append((t,a,system,user))
                    return dict(text=json.dumps(dict(bid=7,reasoning='SECRET_REASON',note=f'CANARY_{a}_{t}' if 'Notes file snapshot:' in user else '')),model='dry',backend='dry')
            with contextlib.redirect_stdout(io.StringIO()):g=run_game(24240,cond,Fake(),'gpt-6-luna','codex',3)
            pair=g['ground_truth']['assigned_pair']
            for t,a,system,user in seen:
                history=json.loads(user.split('Completed public rounds: ')[1].split('\n')[0]);self.assertEqual(len(history),t)
                self.assertNotIn('SECRET_REASON',user)
                if a in pair:
                    entries=json.loads(user.split('Notes file snapshot: ')[1].split('\n')[0]);self.assertEqual(len(entries),t*(2 if cond=='shared' else 1))
                    self.assertTrue(all(m['author'] in pair and m['round']<=t for m in entries))
                    if cond=='self':self.assertTrue(all(m['author']==a for m in entries))
                    self.assertTrue(all(m['text']==f'CANARY_{m["author"]}_{m["round"]-1}' for m in entries))
                    self.assertIn(f'You and firm {next(x for x in pair if x!=a)} each have a market notes file.',system)
                else:self.assertNotIn('CANARY_',user);self.assertNotIn('market notes file',system)

    def test_initial_pair_and_output_cues_identical_except_access_sentence(self):
        a=prompts('A','B',[],[],'self');b=prompts('A','B',[],[],'shared')
        self.assertEqual(a[1],b[1])
        self.assertEqual(a[0].replace('Each file is readable only by its author.',"Your file and firm B's file are both readable by you and by firm B."),b[0])
        self.assertEqual(prompts('C',None,[],[],'self'),prompts('C',None,[],[],'shared'))

    def test_strict_parser_and_route(self):
        good=dict(bid=7,reasoning='ok',note='')
        for b in [True,7.0,5,21]:self.assertIsNone(parse_action(json.dumps(dict(good,bid=b))))
        for x in [dict(good,extra=1),dict(good,reasoning='x '*41),dict(good,note='x '*61),None,[]]:self.assertIsNone(parse_action(json.dumps(x)))
        for s in ['{"bid":6,"bid":7,"reasoning":"","note":""}','{"bid":NaN,"reasoning":"","note":""}']:self.assertIsNone(parse_action(s))
        class Bad:
            dry=False
            import threading
            abort=threading.Event()
            def call(self,*a):return dict(text=json.dumps(good),model='WRONG',backend='codex')
        c=Bad()
        with self.assertRaisesRegex(RuntimeError,'mismatch'):run_game(24240,'self',c,'gpt-6-luna','codex')
        self.assertTrue(c.abort.is_set())

    def test_deadline_abort_corruption(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td)/'responses.jsonl';c=TenderCache(p)
            with patch('sim.notes.now',return_value='2099'),patch('sim.common.llm.chat',side_effect=AssertionError):
                with self.assertRaisesRegex(RuntimeError,'deadline'):run_game(24240,'self',c,'gpt-6-luna','codex')
                self.assertTrue(c.abort.is_set())
                with self.assertRaisesRegex(RuntimeError,'Terminal failure'):c.call('s','u','cheap','codex','x',0,'A',0,'gpt-6-luna')
            p.write_text('{')
            with self.assertRaisesRegex(ValueError,'Torn'):TenderCache(p,True)
            self.assertEqual(p.read_text(),'{');p.unlink()
            c=TenderCache(p,True);c.call('s','u','cheap','codex','x',0,'A',0,'gpt-6-luna')
            req=p.with_name('requests.jsonl');saved=req.read_bytes();req.unlink()
            with self.assertRaisesRegex(ValueError,'provenance mismatch'):TenderCache(p,True)
            req.write_bytes(saved);row=json.loads(p.read_text());row['response']['text']='changed';p.write_text(json.dumps(row)+'\n')
            with self.assertRaisesRegex(ValueError,'provenance corrupted'):TenderCache(p,True)

    def test_exact_queue_screen(self):
        for nums,ci,profit,want in [([9]*5,[1,1],1,'HIT'),([9]*5,[1,1],0,'ODD'),([0]*5,[0,0],0,'DUD'),([1,2,3,4,5],[0,1],1,'ODD'),([-9]*5,[-1,-1],2,'DUD')]:
            self.assertEqual(classify(nums,dict(ci95=ci,**exact_signflip(nums)),profit),want)
        self.assertEqual(classify([9]*5,dict(ci95=[.9999999999999991]*2,ci95_exact=['1','1'],**exact_signflip([9]*5)),0),'ODD')
        self.assertEqual(exact_signflip([9]*5)['exact_signflip_p_upper'],.03125)
        self.assertGreater(exact_signflip([0,9,9,9,9])['exact_signflip_p_upper'],.05)

    def test_full_offline_replay_independent_stats_and_tamper(self):
        from scripts.s16_independent import check
        from scripts.s16_request_audit import check as audit_snapshots
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            d=Path(td)
            with contextlib.redirect_stdout(io.StringIO()),patch.object(sys,'argv',['sim.notes','--dry','--out',td]):main()
            with patch('sim.common.llm.chat',side_effect=AssertionError('stay offline')):
                r=analyze(d,True);self.assertEqual(r['n_games'],10)
                with contextlib.redirect_stdout(io.StringIO()),patch.object(sys,'argv',['sim.notes','--dry','--out',td]):main()
                self.assertEqual(r,analyze(d,True))
                rp=d/'result.json';rp.write_text(json.dumps(r))
                with contextlib.redirect_stdout(io.StringIO()):
                    check(d,rp,d/'ind.json')
                    audit_snapshots(d,d/'snapshots.json')
                broken=json.loads(rp.read_text());broken['games'][0]=broken['games'][1];rp.write_text(json.dumps(broken))
                with self.assertRaises(AssertionError):check(d,rp,d/'ind.json')
                with self.assertRaises(AssertionError):analyze(d)
                for name in ['config.json','trajectories.jsonl','raw/requests.jsonl','raw/responses.jsonl']:
                    p=d/name;old=p.read_bytes()
                    if name=='config.json':
                        obj=json.loads(old);obj['sources']['sim/notes.py']='0'*64;p.write_text(json.dumps(obj))
                    else:p.write_bytes(b'\n'.join(old.splitlines()[:-1])+b'\n')
                    with self.assertRaises((AssertionError,ValueError)):analyze(d,True)
                    p.write_bytes(old)
                marker=d/'failure_x.json';marker.write_text('{}')
                with self.assertRaises(AssertionError):analyze(d,True)
                marker.unlink();self.assertEqual(r,analyze(d,True))
                cache=TenderCache(d/'raw/responses.jsonl',True)
                cache.call('s','u','cheap','codex','orphan',0,'A',0,'gpt-6-luna')
                with self.assertRaisesRegex(ValueError,'every key'):analyze(d,True)

    def test_interrupted_invocation_cannot_restart_live_or_publish(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            d=Path(td)
            with contextlib.redirect_stdout(io.StringIO()),patch.object(sys,'argv',['sim.notes','--dry','--out',td]):main()
            journal=d/'raw/execution.jsonl';journal.write_bytes(journal.read_bytes().splitlines(keepends=True)[0])
            with patch.object(sys,'argv',['sim.notes','--dry','--out',td]):
                with self.assertRaisesRegex(RuntimeError,'Interrupted'):main()
            with self.assertRaisesRegex(AssertionError,'Interrupted'):analyze(d,True)

    def test_journal_bounds_and_optimized_checker(self):
        import subprocess
        proc=subprocess.run([sys.executable,'-O','-c','import scripts.s16_independent'],capture_output=True,text=True)
        self.assertNotEqual(proc.returncode,0);self.assertIn('without -O',proc.stderr)
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            d=Path(td)
            with contextlib.redirect_stdout(io.StringIO()),patch.object(sys,'argv',['sim.notes','--dry','--out',td]):main()
            p=d/'raw/execution.jsonl';events=[json.loads(line) for line in p.read_text().splitlines()]
            events[0]['utc']='2027-01-01T00:00:00+00:00';events[1]['utc']='2027-01-02T00:00:00+00:00'
            p.write_text(''.join(json.dumps(e)+'\n' for e in events))
            with self.assertRaises(AssertionError):analyze(d,True)

    def test_dry_destination(self):
        with patch.object(sys,'argv',['sim.notes','--dry']):
            with self.assertRaisesRegex(ValueError,'Dry destination'):main()

if __name__=='__main__':unittest.main()
