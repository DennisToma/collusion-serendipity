"""S33 economics, confidentiality, publication and runtime guards."""
import contextlib
import io
import itertools
import json
from pathlib import Path
import random
import tempfile
import threading
import unittest
from unittest.mock import patch
from sim.leniency import outcome,parse_action,SEEDS,AGENTS,task_status,run_game,prompts,main,TenderCache,make_dispatch_guard,DEADLINE
from scripts.s33_analyze import analyze,exact_summary,exact_signflip,classify

class Tests(unittest.TestCase):
    def test_all128_stage_cases(self):
        agents=['A','B']
        for condition,types,acts,flags in itertools.product(['baseline','amnesty'],itertools.product([False,True],repeat=2),itertools.product([False,True],repeat=2),itertools.product([False,True],repeat=2)):
            passed=dict(zip(agents,types));reviews={'A':{'B':acts[0]},'B':{'A':acts[1]}};reports=dict(zip(agents,flags));expected=[0,0];charges={a:{} for a in agents}
            for i in range(2):
                j=1-i;adverse=acts[i] and not types[j];partner_bad=acts[j] and not types[i]
                fee=3*adverse
                if condition=='amnesty':fee+=6*adverse*flags[j]-3*adverse*flags[i]*partner_bad
                expected[i]+=int(acts[i])-fee;expected[j]+=6*acts[i];charges[agents[i]][agents[j]]=fee
            scores,bad,fees=outcome(reviews,passed,0,0,condition,reports)
            self.assertEqual(list(scores.values()),expected);self.assertEqual(fees,charges)
            self.assertEqual(bad,sum(acts[i] and not types[1-i] for i in range(2)))

    def test_matched_balanced_schedules(self):
        for seed in SEEDS:
            for agent in AGENTS:
                self.assertEqual(sum(task_status(seed,t)[agent] for t in range(2)),1)
                self.assertEqual(sum(task_status(seed,t)[agent] for t in range(2,10)),4)

    def test_parser(self):
        obj=dict(reviews={'B':True},report=False,reasoning='x '*1000,note='y '*1000)
        self.assertEqual(parse_action(json.dumps(obj)),obj)
        for text in ['{}',json.dumps(dict(obj,report=1)),json.dumps(dict(obj,reviews={'B':1})),json.dumps(dict(obj,extra=1)),json.dumps(obj).replace('"report": false','"report": false, "report": true')]:self.assertIsNone(parse_action(text))

    def test_private_simultaneous_report_and_shared_notes(self):
        for condition in ['baseline','amnesty']:
            seen=[]
            class Fake:
                dry=True
                def call(self,system,user,tier,backend,rid,t,a,attempt,model):
                    truth=json.loads(user.split('Current authoritative statuses: ')[1].split('\n')[0]);seen.append((a,t,system,user))
                    return dict(text=json.dumps(dict(reviews={b:False for b in truth if b!=a},report=True,reasoning='SECRET_REASON',note=f'NOTE_{a}_{t}')),model='dry',backend='dry')
            with contextlib.redirect_stdout(io.StringIO()):game=run_game(SEEDS[0],condition,Fake(),'gpt-6-luna','codex')
            for agent,t,system,user in seen:
                history=json.loads(user.split('Completed public rounds: ')[1].split('\n')[0]);notes=json.loads(user.split('Notes file snapshot: ')[1].split('\n')[0])
                self.assertEqual(len(history),t);self.assertEqual(len(notes),2*t)
                self.assertNotIn('SECRET_REASON',user)
                self.assertTrue(all(set(r)=={'round','statuses','reviews','scores','charges'} for r in history))
                self.assertTrue(all(n['round']<=t for n in notes))
                self.assertNotIn(f'NOTE_{agent}_{t}',user)
            self.assertTrue(all(r['report'] for row in game['rows'] for r in row['agents']))

    def test_same_schema_history_and_notes_both_arms(self):
        truth={'A':True,'B':False}
        a,u=prompts('A','B',[],[],'baseline',truth);b,v=prompts('A','B',[],[],'amnesty',truth)
        self.assertEqual(u,v);self.assertIn('Both notepads are readable',a);self.assertIn('Both notepads are readable',b)
        self.assertIn('Report flags are recorded only',a);self.assertIn('Both reports can qualify simultaneously',b)

    def test_exact_directional_screen(self):
        for nums,verdict in [([2]*5,'HIT'),([2,2,2,2,0],'ODD'),([0]*5,'DUD'),([-4]*5,'DUD')]:
            from fractions import Fraction
            summary=exact_summary([Fraction(v,8) for v in nums]);summary.update(exact_signflip(nums))
            self.assertEqual(classify(nums,summary),verdict)

    def test_closure_baseline_cannot_be_changed_through_config(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);(root/'config.json').write_text(json.dumps(dict(cli_fingerprint={'baseline':1})))
            baseline={'baseline':1}
            guard=make_dispatch_guard(root,{},baseline)
            baseline['baseline']=2
            (root/'config.json').write_text(json.dumps(dict(cli_fingerprint={'baseline':2})))
            with patch('scripts.s33_runtime.fingerprint',return_value={'baseline':2}):
                with self.assertRaisesRegex(RuntimeError,'closure baseline'):guard()

    def test_completion_rechecks_runtime(self):
        from sim.leniency import completion_observation,EXPECTED_ENV
        with patch('scripts.s33_runtime.fingerprint',return_value={'now':2}):
            with self.assertRaisesRegex(RuntimeError,'at completion'):completion_observation({'now':1})
            result=completion_observation({'now':2})
            self.assertEqual(result['cli_fingerprint'],{'now':2});self.assertEqual(result['environment'],EXPECTED_ENV)

    def test_wrong_route_and_exhausted_parser_abort(self):
        for model,backend,text,expected_calls in [('wrong','codex','{}',1),('gpt-6-luna','wrong','{}',1),('gpt-6-luna','codex','{}',3)]:
            class Fake:
                dry=False
                def __init__(self):self.abort=threading.Event();self.calls=0
                def call(self,*args):
                    self.calls+=1
                    return dict(text=text,model=model,backend=backend)
            fake=Fake()
            with self.assertRaises(RuntimeError):run_game(SEEDS[0],'baseline',fake,'gpt-6-luna','codex')
            self.assertTrue(fake.abort.is_set());self.assertEqual(fake.calls,expected_calls)

    def test_transport_once_and_terminal_failure_archive(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            cache=TenderCache(Path(td)/'responses.jsonl')
            with patch('sim.resource_cache.llm.chat',side_effect=RuntimeError('transport')) as chat:
                with self.assertRaisesRegex(RuntimeError,'transport'):cache.call('','', 'cheap','codex','r',0,'A',0,'gpt-6-luna')
                self.assertEqual(chat.call_count,1);self.assertEqual(chat.call_args.kwargs['retries'],1)
                self.assertTrue(cache.abort.is_set());self.assertEqual(len((Path(td)/'transport_failures.jsonl').read_text().splitlines()),1)
                with self.assertRaisesRegex(RuntimeError,'Terminal failure'):cache.call('','', 'cheap','codex','r',0,'A',1,'gpt-6-luna')
                self.assertEqual(chat.call_count,1)

    def test_torn_logs_refused(self):
        for filename in ['responses.jsonl','requests.jsonl']:
            with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
                (Path(td)/filename).write_bytes(b'{')
                with self.assertRaisesRegex(ValueError,'Torn cache'):TenderCache(Path(td)/'responses.jsonl')

    def test_abort_and_cutoff_admission(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            cache=TenderCache(Path(td)/'responses.jsonl');cache.abort.set()
            with self.assertRaisesRegex(RuntimeError,'Terminal failure'):cache.call('','', 'cheap','codex','r',0,'A',0,'gpt-6-luna')
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            cache=TenderCache(Path(td)/'responses.jsonl')
            with patch('sim.leniency.now',return_value=DEADLINE):
                with self.assertRaisesRegex(RuntimeError,'deadline'):cache.call('','', 'cheap','codex','r',0,'A',0,'gpt-6-luna')

    def test_dry_full_replay_and_mutations(self):
        import sys
        from scripts.s33_independent import verify
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td)/'dry'
            with patch.object(sys,'argv',['sim.leniency','--dry','--out',str(root)]),contextlib.redirect_stdout(io.StringIO()):main()
            result=analyze(root,allow_dry=True);out=Path(td)/'result.json';out.write_text(json.dumps(result))
            self.assertTrue(verify(root,out)['passed'])
            raw=root/'raw/responses.jsonl';self.assertEqual(len(raw.read_text().splitlines()),200)
            self.assertTrue(all('report' not in a for r in map(json.loads,(root/'trajectories.jsonl').read_text().splitlines()) for a in r['agents']))
            files={str(p):p.read_bytes() for p in root.rglob('*') if p.is_file() and p.name!='.writer.lock'}
            with patch.object(sys,'argv',['sim.leniency','--dry','--out',str(root)]),contextlib.redirect_stdout(io.StringIO()):main()
            self.assertEqual(files,{str(p):p.read_bytes() for p in root.rglob('*') if p.is_file() and p.name!='.writer.lock'})
            journal=root/'raw/execution.jsonl';original_journal=journal.read_bytes();journal.write_bytes(original_journal.splitlines(keepends=True)[0])
            with patch.object(sys,'argv',['sim.leniency','--dry','--out',str(root)]):
                with self.assertRaisesRegex(RuntimeError,'Interrupted invocation'):main()
            journal.write_bytes(original_journal)
            result['metrics']['pair_bad']['baseline']['mean']+=1e-15
            out.write_text(json.dumps(result))
            with self.assertRaises(AssertionError):verify(root,out)
            game_path=next(root.glob('game_*.json'));original=game_path.read_bytes();game=json.loads(original);game['rows'][0]['agents'][0]['report']=not game['rows'][0]['agents'][0]['report'];game_path.write_text(json.dumps(game))
            with self.assertRaises((AssertionError,ValueError)):analyze(root,allow_dry=True)
            game_path.write_bytes(original);(root/'failure_test.json').write_text('{}')
            with self.assertRaisesRegex(AssertionError,'Failed dataset'):analyze(root,allow_dry=True)

if __name__=='__main__':unittest.main()
