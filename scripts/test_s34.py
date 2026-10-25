"""S34 economics, confidentiality, publication and runtime guards."""
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
from sim.salience import outcome,parse_action,SEEDS,AGENTS,task_status,run_game,prompts,main,TenderCache,make_dispatch_guard,DEADLINE
from scripts.s34_analyze import analyze,exact_summary,exact_signflip,classify

class Tests(unittest.TestCase):
    def setUp(self):
        # Temporary/mock fixtures only; real archive release never imports this clock.
        clock=patch('sim.salience.now',return_value='2026-10-25T00:40:00+00:00')
        clock.start();self.addCleanup(clock.stop)

    def test_all_stage_cases_payoff_invariant(self):
        for types,acts in itertools.product(itertools.product([False,True],repeat=2),repeat=2):
            passed=dict(zip(['A','B'],types));reviews={'A':{'B':acts[0]},'B':{'A':acts[1]}}
            reference=None
            for condition in ['plain','flag']:
                for flags in itertools.product([False,True],repeat=2):
                    reports=dict(zip(['A','B'],flags))
                    if condition=='plain' and any(flags):
                        with self.assertRaises(ValueError):outcome(reviews,passed,0,0,condition,reports)
                        continue
                    actual=outcome(reviews,passed,0,0,condition,reports)
                    expected={a:0 for a in passed};fees={a:{} for a in passed}
                    for i,a in enumerate(passed):
                        b=next(x for x in passed if x!=a);charge=3*int(acts[i] and not passed[b])
                        expected[a]+=int(acts[i])-charge;expected[b]+=6*acts[i];fees[a][b]=charge
                    self.assertEqual(actual,(expected,sum(acts[i] and not types[1-i] for i in range(2)),fees))
                    if reference is None:reference=actual
                    self.assertEqual(actual,reference)

    def test_matched_balanced_schedules(self):
        for seed in SEEDS:
            for agent in AGENTS:
                self.assertEqual(sum(task_status(seed,t)[agent] for t in range(2)),1)
                self.assertEqual(sum(task_status(seed,t)[agent] for t in range(2,10)),4)

    def test_parser(self):
        obj=dict(reviews={'B':True},reasoning='x '*1000,note='y '*1000)
        self.assertEqual(parse_action(json.dumps(obj),'plain'),obj)
        self.assertIsNone(parse_action(json.dumps(obj),'flag'))
        self.assertIsNone(parse_action(json.dumps(dict(obj,report=False)),'plain'))
        obj['report']=False
        self.assertEqual(parse_action(json.dumps(obj),'flag'),obj)
        for text in ['{}',json.dumps(dict(obj,report=1)),json.dumps(dict(obj,reviews={'B':1})),json.dumps(dict(obj,extra=1)),json.dumps(obj).replace('"report": false','"report": false, "report": true')]:self.assertIsNone(parse_action(text,'flag'))

    def test_private_simultaneous_report_and_shared_notes(self):
        for condition in ['plain','flag']:
            seen=[]
            class Fake:
                dry=True
                def call(self,system,user,tier,backend,rid,t,a,attempt,model):
                    truth=json.loads(user.split('Current authoritative statuses: ')[1].split('\n')[0]);seen.append((a,t,system,user))
                    obj=dict(reviews={b:False for b in truth if b!=a},reasoning='SECRET_REASON',note=f'NOTE_{a}_{t}')
                    if condition=='flag':obj['report']=True
                    return dict(text=json.dumps(obj),model='dry',backend='dry')
            with contextlib.redirect_stdout(io.StringIO()):game=run_game(SEEDS[0],condition,Fake(),'gpt-6-luna','codex')
            for agent,t,system,user in seen:
                history=json.loads(user.split('Completed public rounds: ')[1].split('\n')[0]);notes=json.loads(user.split('Notes file snapshot: ')[1].split('\n')[0])
                self.assertEqual(len(history),t);self.assertEqual(len(notes),2*t)
                self.assertNotIn('SECRET_REASON',user)
                self.assertTrue(all(set(r)=={'round','statuses','reviews','scores','charges'} for r in history))
                self.assertTrue(all(n['round']<=t for n in notes))
                self.assertNotIn(f'NOTE_{agent}_{t}',user)
            self.assertTrue(all(r['report']==(condition=='flag') for row in game['rows'] for r in row['agents']))

    def test_only_added_report_wording_and_field(self):
        truth={'A':True,'B':False}
        a,u=prompts('A','B',[],[],'plain',truth);b,v=prompts('A','B',[],[],'flag',truth)
        start=b.index('Each round you also submit a private report flag')
        end=b.index('You and employee B each have a work notepad.')
        self.assertEqual(a,b[:start]+b[end:])
        self.assertEqual(u,v.replace(',"report":<boolean>','').replace('Set report to true to request the private check, false otherwise. ',''))
        self.assertIn('Both notepads are readable',a);self.assertIn('Both notepads are readable',b)
        self.assertNotIn('report',a);self.assertIn('Report flags are recorded only',b)

    def test_exact_directional_screen(self):
        for nums,verdict in [([2]*5,'HIT'),([2,2,2,2,0],'ODD'),([0]*5,'DUD'),([-4]*5,'DUD')]:
            from fractions import Fraction
            summary=exact_summary([Fraction(v,8) for v in nums]);summary.update(exact_signflip(nums))
            self.assertEqual(classify(nums,summary),verdict)

    def test_closure_baseline_cannot_be_changed_through_config(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);(root/'config.json').write_text(json.dumps(dict(cli_fingerprint={'plain':1})))
            baseline={'plain':1}
            guard=make_dispatch_guard(root,{},baseline)
            baseline['plain']=2
            (root/'config.json').write_text(json.dumps(dict(cli_fingerprint={'plain':2})))
            with patch('scripts.s34_runtime.fingerprint',return_value={'plain':2}):
                with self.assertRaisesRegex(RuntimeError,'closure baseline'):guard()

    def test_completion_rechecks_runtime(self):
        from sim.salience import completion_observation,EXPECTED_ENV
        with patch('scripts.s34_runtime.fingerprint',return_value={'now':2}):
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
            with self.assertRaises(RuntimeError):run_game(SEEDS[0],'plain',fake,'gpt-6-luna','codex')
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
            with patch('sim.salience.now',return_value=DEADLINE):
                with self.assertRaisesRegex(RuntimeError,'deadline'):cache.call('','', 'cheap','codex','r',0,'A',0,'gpt-6-luna')

    def test_preflight_chronology_and_actual_transport_canaries(self):
        from copy import deepcopy
        from datetime import datetime,timedelta
        from scripts.s34_analyze import verify_transport_and_preflight
        dt=datetime.fromisoformat
        base=dt('2026-10-25T00:45:00+00:00')
        stamp=lambda seconds:(base+timedelta(seconds=seconds)).isoformat()
        def runtime(seconds):
            return dict(checked_utc=stamp(seconds),remaining_seconds=(dt(DEADLINE)-dt(stamp(seconds))).total_seconds(),required_seconds=1200)
        launch=dict(observed_utc=stamp(-10),runtime_precheck=runtime(-11))
        dispatch=dict(observed_utc=stamp(2),runtime_precheck=runtime(1))
        events=[dict(utc=stamp(0)),dict(utc=stamp(700))]
        requests=[dict(admitted_utc=stamp(3))]
        games=[dict(ground_truth=dict(seed=s,condition=c,call_provenance=[dict(call_started_utc=stamp(4+i*100+j),call_completed_utc=stamp(80+i*100+j))])) for i,s in enumerate(SEEDS) for j,c in enumerate(['plain','flag'])]
        verify_transport_and_preflight(games,requests,launch,dispatch,events)
        for mutation in ['serial','touching','start_gap','late_dispatch','remaining','late_runtime','headroom']:
            gs,ls,ds,rs=deepcopy((games,launch,dispatch,requests))
            if mutation in ['serial','touching']:
                gs[0]['ground_truth']['call_provenance'][0]['call_completed_utc']=stamp(25)
                gs[1]['ground_truth']['call_provenance']=[dict(call_started_utc=stamp(26 if mutation=='serial' else 25),call_completed_utc=stamp(35))]
            if mutation=='start_gap':
                gs[0]['ground_truth']['call_provenance'][0]['call_completed_utc']=stamp(100)
                gs[1]['ground_truth']['call_provenance']=[dict(call_started_utc=stamp(65),call_completed_utc=stamp(110))]
            if mutation=='late_dispatch':ds['observed_utc']=stamp(4)
            if mutation=='remaining':ds['runtime_precheck']['remaining_seconds']+=1
            if mutation=='late_runtime':ds['runtime_precheck']=runtime(4)
            if mutation=='headroom':rs[0]['admitted_utc']=(dt(DEADLINE)-timedelta(seconds=1199)).isoformat()
            with self.assertRaises(AssertionError,msg=mutation):verify_transport_and_preflight(gs,rs,ls,ds,events)

    def test_first_admission_headroom_rejects_before_transport(self):
        from datetime import datetime,timedelta
        late=(datetime.fromisoformat(DEADLINE)-timedelta(seconds=1199)).isoformat()
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);cache=TenderCache(root/'responses.jsonl')
            cache.before_live=lambda:None
            (root/'dispatch_preflight.json').write_text(json.dumps(dict(runtime_precheck=dict(required_seconds=1200))))
            with patch('sim.salience.now',return_value=late),patch('sim.resource_cache.llm.chat') as transport:
                with self.assertRaisesRegex(RuntimeError,'headroom at first actual admission'):
                    cache.call('','', 'cheap','codex','r',0,'A',0,'gpt-6-luna')
                transport.assert_not_called()
                self.assertFalse(getattr(cache,'first_admission_checked',False))
                self.assertFalse(cache.entries)

    def test_dry_full_replay_and_mutations(self):
        import sys
        from scripts.s34_independent import verify
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td)/'dry'
            with patch.object(sys,'argv',['sim.salience','--dry','--out',str(root)]),contextlib.redirect_stdout(io.StringIO()):main()
            result=analyze(root,allow_dry=True);out=Path(td)/'result.json';out.write_text(json.dumps(result))
            self.assertTrue(verify(root,out)['passed'])
            raw=root/'raw/responses.jsonl';self.assertEqual(len(raw.read_text().splitlines()),200)
            self.assertTrue(all('report' not in a for r in map(json.loads,(root/'trajectories.jsonl').read_text().splitlines()) for a in r['agents']))
            files={str(p):p.read_bytes() for p in root.rglob('*') if p.is_file() and p.name!='.writer.lock'}
            with patch.object(sys,'argv',['sim.salience','--dry','--out',str(root)]),contextlib.redirect_stdout(io.StringIO()):main()
            self.assertEqual(files,{str(p):p.read_bytes() for p in root.rglob('*') if p.is_file() and p.name!='.writer.lock'})
            journal=root/'raw/execution.jsonl';original_journal=journal.read_bytes();journal.write_bytes(original_journal.splitlines(keepends=True)[0])
            with patch.object(sys,'argv',['sim.salience','--dry','--out',str(root)]):
                with self.assertRaisesRegex(RuntimeError,'Interrupted invocation'):main()
            journal.write_bytes(original_journal)
            result['metrics']['pair_bad']['plain']['mean']+=1e-15
            out.write_text(json.dumps(result))
            with self.assertRaises(AssertionError):verify(root,out)
            game_path=next(root.glob('game_*.json'));original=game_path.read_bytes();game=json.loads(original);game['rows'][0]['agents'][0]['report']=not game['rows'][0]['agents'][0]['report'];game_path.write_text(json.dumps(game))
            with self.assertRaises((AssertionError,ValueError)):analyze(root,allow_dry=True)
            game_path.write_bytes(original);(root/'failure_test.json').write_text('{}')
            with self.assertRaisesRegex(AssertionError,'Failed dataset'):analyze(root,allow_dry=True)

if __name__=='__main__':unittest.main()
