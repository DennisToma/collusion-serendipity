"""Protocol and economic checks for fresh labor world."""
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fractions import Fraction as F
from sim import grossnet as m
from scripts.s36_analyze import exact_summary, exact_signflip, classify

class Resource(unittest.TestCase):
    def setUp(self):
        self.clock=patch('sim.grossnet.now',return_value='2026-10-24T23:50:00+00:00')
        self.clock.start();self.addCleanup(self.clock.stop)
    def test_exhaustive_economics(self):
        equilibria=[]
        for ws in itertools.product(range(21),repeat=2):
            paid,sh,p=m.outcome(list(ws))
            self.assertEqual(sum(sh),1);self.assertEqual(sum(p)+paid,20)
            for i in range(2):self.assertEqual(p[i],(20-ws[i])*sh[i])
            if all(max(m.outcome([w if j!=i else q for j,w in enumerate(ws)])[2][i] for q in range(21))==p[i] for i in range(2)):equilibria.append(ws)
        self.assertEqual(equilibria,[(18,18),(19,19),(20,20)])
        self.assertEqual(m.outcome([0,0])[2],[10,10]);self.assertEqual(m.outcome([1,0])[2],[19,0])
    def test_deep_json_is_a_parser_rejection(self):
        from scripts.s36_independent import accepted
        text='['*10000+']'*10000
        self.assertIsNone(m.parse_action(text));self.assertIsNone(accepted(text))
    def test_mocked_live_end_to_end(self):
        """Run the full LIVE branch against synthetic paid-route responses in a temp git repo."""
        import contextlib,io,os,shutil,subprocess,sys,threading
        from datetime import datetime,timezone,timedelta
        from scripts.s36_launch import launch
        from scripts.s36_analyze import analyze
        from scripts.s36_independent import verify
        from scripts.s36_exact_check import check
        from scripts.s36_present import render
        origin=Path.cwd()
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td)
            for name in m.SOURCES:
                dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(origin/name,dest)
            shutil.copytree(origin/'data/s19_labels',root/'data/s19_labels')
            for name in ['logs','results','figures']:(root/name).mkdir(exist_ok=True)
            subprocess.run(['git','init','-q','-b','main',str(root)],check=True)
            subprocess.run(['git','add','.'],cwd=root,check=True)
            subprocess.run(['git','-c','user.name=Synthetic Fixture','-c','user.email=fixture@example.invalid','commit','-qm','Synthetic source freeze'],cwd=root,env=dict(os.environ,GIT_AUTHOR_DATE='2026-10-25T01:09:00+00:00',GIT_COMMITTER_DATE='2026-10-25T01:09:00+00:00'),check=True)
            subprocess.run(['git','remote','add','origin',str(root)],cwd=root,check=True)
            mutex=threading.Lock();elapsed=0
            base=datetime.fromisoformat('2026-10-25T01:10:00+00:00')
            def tick():
                nonlocal elapsed
                with mutex:elapsed+=1;return base+timedelta(milliseconds=elapsed)
            class FixtureDatetime(datetime):
                @classmethod
                def now(cls,tz=None):return tick()
            barrier=threading.Barrier(2)
            def response(*args,**kwargs):
                self.assertEqual(kwargs['retries'],1)
                barrier.wait(timeout=30)
                return dict(text=json.dumps(dict(rate=20 if 'Post a GROSS' in kwargs['system'] else 10,reasoning='synthetic private',note='synthetic own note')),model='gpt-6-luna',backend='codex')
            try:
                os.chdir(root)
                with patch('sim.grossnet.now',side_effect=lambda:tick().isoformat()),patch('sim.resource_cache.datetime',FixtureDatetime),patch('scripts.s36_launch.datetime',FixtureDatetime),patch('scripts.s36_runtime.fingerprint',return_value={'fixture':True}),patch('scripts.s36_runtime.launch_observation',return_value={'fingerprint':{'fixture':True},'version':'fixture'}),patch('sim.resource_cache.llm.chat',side_effect=response) as transport,patch.object(sys,'argv',['s36_launch']),contextlib.redirect_stdout(io.StringIO()):
                    launch()
                    self.assertEqual(transport.call_count,200)
                    result=analyze(root/'data/s36_grossnet')
                    self.assertFalse(result['dry']);self.assertEqual(result['verdict'],'DUD')
                    out=root/'results/s36_grossnet.json';out.write_text(json.dumps(result,indent=2)+'\n')
                    self.assertTrue(verify(root/'data/s36_grossnet',out)['passed'])
                    self.assertEqual(check(root/'data/s36_grossnet',out)['exact_summaries'],15)
                    render(str(out),str(root/'results/s36_summary.md'),str(root/'figures/s36_grossnet.png'))
                    with patch('sim.resource_cache.llm.chat',side_effect=AssertionError('Resume cannot call provider')),patch.object(sys,'argv',['sim.grossnet']):m.main()
                    journal=root/'data/s36_grossnet/raw/execution.jsonl';original=journal.read_bytes()
                    journal.write_bytes(original.splitlines(keepends=True)[0])
                    with self.assertRaisesRegex(RuntimeError,'Interrupted invocation'):m.main()
                    journal.write_bytes(original)
                    failure=root/'data/s36_grossnet/failure_fixture.json';failure.write_text('{}')
                    with self.assertRaisesRegex(AssertionError,'Failed dataset'):analyze(root/'data/s36_grossnet')
            finally:os.chdir(origin)
    def test_translation_exhaustive(self):
        equilibria=[]
        for ws in itertools.product(range(21),repeat=2):
            net=m.outcome(list(ws));gross=m.outcome([w+10 for w in ws],offset=10)
            self.assertEqual(net,gross)
            for i in range(2):
                for q in range(21):
                    ns=[w if j!=i else q for j,w in enumerate(ws)]
                    self.assertEqual(m.outcome(ns),m.outcome([w+10 for w in ns],offset=10))
            if all(max(m.outcome([w if j!=i else q for j,w in enumerate(ws)])[2][i] for q in range(21))==net[2][i] for i in range(2)):equilibria.append(ws)
        self.assertEqual(equilibria,[(18,18),(19,19),(20,20)])
    def test_productivity_assignment(self):
        for seed in m.SEEDS:
            self.assertEqual(m.productivity(seed,'net'),m.productivity(seed,'gross'))
            self.assertEqual(set(m.productivity(seed,'net').values()),{20})
    def test_guard_baseline_cannot_follow_mutable_config(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            baseline={'old':'value'};d=Path(td)
            guard=m.make_dispatch_guard(d,{},baseline)
            baseline.clear();baseline['new']='value'
            (d/'config.json').write_text(json.dumps({'cli_fingerprint':baseline}))
            with patch('scripts.s36_runtime.fingerprint',return_value=baseline):
                with self.assertRaisesRegex(RuntimeError,'Known CLI inputs changed'):guard()
    def test_zero_actual_overlap_rejected(self):
        from scripts.s36_analyze import verify_transport_and_preflight
        # The preflight chronology itself is exercised by a full live archive check;
        # actual strict overlap is checked here by the same independent validator.
        from scripts.s36_analyze import validate_call_overlap
        def gt(start,end):return dict(call_provenance=[dict(call_started_utc='2026-10-25T'+start+'+00:00',call_completed_utc='2026-10-25T'+end+'+00:00')])
        with self.assertRaisesRegex(AssertionError,'do not overlap'):validate_call_overlap([gt('01:01:00','01:02:00'),gt('01:02:00','01:03:00')])
    def test_parser(self):
        good='{"rate":0,"reasoning":"","note":""}'
        self.assertIsNotNone(m.parse_action(good))
        for value in ['true','0.0','-1','21','NaN']:
            self.assertIsNone(m.parse_action(good.replace('"rate":0','"rate":'+value)))
        self.assertIsNone(m.parse_action(good.replace('"rate":0','"rate":0,"rate":1')))
        self.assertIsNotNone(m.parse_action(json.dumps(dict(rate=20,reasoning='x '*1000,note='x '*1000))))
    def test_visibility_and_prompt_contrast(self):
        chat=[dict(round=1,author=a,text=a+' note') for a in ['A','B']]
        for c in m.CONDITIONS:
            system,user=m.prompts('A','B',[],chat,c,{'A':20,'B':20})
            snapshot=json.loads(user.split('Notes file snapshot: ')[1].split('\n')[0])
            self.assertEqual(snapshot,chat[:1])
            self.assertIn('0..20' if c=='net' else '10..30',user)
            self.assertIn('NET' if c=='net' else 'GROSS',system)
    def test_condition_specific_parser(self):
        from scripts.s36_independent import accepted
        for offset in (0,10):
            for q in range(-1,32):
                text=json.dumps(dict(rate=q,reasoning='',note=''))
                self.assertEqual(m.parse_action(text,offset) is not None,offset<=q<=offset+20)
                self.assertEqual(accepted(text,offset) is not None,offset<=q<=offset+20)
    def test_dry_simultaneity(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            cache=m.TenderCache(Path(td)/'responses.jsonl',True)
            g=m.run_game(24760,'gross',cache,'gpt-6-luna','codex')
            req=list(cache.requests.values());self.assertEqual(len(req),20)
            for q in req:
                turn=q['payload'][6]
                snapshot=json.loads(q['payload'][1].split('Notes file snapshot: ')[1].split('\n')[0])
                self.assertEqual(len(snapshot),turn)
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
        from scripts.s36_independent import accepted
        self.assertIsNotNone(accepted('{"rate":20,"reasoning":"","note":""}'))
        for bad in ['{"rate":true,"reasoning":"","note":""}','{"rate":1,"rate":2,"reasoning":"","note":""}','{"rate":2,"reasoning":"","note":NaN}']:
            self.assertIsNone(accepted(bad))
    def test_live_admission_cutoff_and_preflight(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            c=m.TenderCache(Path(td)/'responses.jsonl',False)
            with patch('sim.grossnet.now',return_value='2099-01-01T00:00:00+00:00'),patch('sim.resource_cache.llm.chat') as chat:
                with self.assertRaisesRegex(RuntimeError,'deadline'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
                chat.assert_not_called()
            self.assertTrue(c.abort.is_set())
            c=m.TenderCache(Path(td)/'responses.jsonl',False)
            def bad_source():raise RuntimeError('Source mismatch')
            c.before_live=bad_source
            with patch('sim.resource_cache.llm.chat') as chat:
                with self.assertRaisesRegex(RuntimeError,'Source mismatch'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
                chat.assert_not_called()
    def test_corruption_rejected(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td)/'responses.jsonl';p.write_text('{')
            with self.assertRaisesRegex(ValueError,'Torn'):m.TenderCache(p,True)
    def test_exact_screen(self):
        nums=[64]*5;sm=exact_summary([F(x,32) for x in nums]);sm.update(exact_signflip(nums))
        self.assertEqual(classify(nums,sm),'HIT')
        nums=[0,80,80,80,80];sm=exact_summary([F(x,32) for x in nums]);sm.update(exact_signflip(nums))
        self.assertEqual(sm['exact_signflip_p_upper'],.0625);self.assertEqual(classify(nums,sm),'ODD')
        nums=[0]*5;sm=exact_summary([F(0)]*5);sm.update(exact_signflip(nums));self.assertEqual(classify(nums,sm),'DUD')
    def test_negative_summaries(self):
        s=exact_summary([F(-2)]*5);self.assertEqual(s['ci95'],[-2,-2]);self.assertEqual(s['paired_t_ci95'],[-2,-2])
    def test_cli_drift_blocks_admission(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            d=Path(td);(d/'config.json').write_text(json.dumps({'cli_fingerprint':{'old':'value'}}))
            guard=m.make_dispatch_guard(d,{}, {'old':'value'})
            with patch('scripts.s36_runtime.fingerprint',return_value={'new':'value'}):
                with self.assertRaisesRegex(RuntimeError,'Known CLI inputs changed'):guard()
    def test_independent_identity_history_contract(self):
        from scripts.s36_independent import expected_prompts
        for c in m.CONDITIONS:
            notes=[dict(round=1,author='A',text='alpha'),dict(round=1,author='B',text='beta')]
            rows=[dict(round=0,market=dict(resource_payment=8),agents=[dict(id='A',price=8,quantity=1.,profit=12.),dict(id='B',price=7,quantity=0.,profit=0.)])]
            self.assertEqual(m.prompts('A','B',rows,notes,c,{'A':20,'B':20}),expected_prompts('A','B',rows,notes,c,{'A':20,'B':20}))
    def test_completion_freeze_preserves_response_and_aborts(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            c=m.TenderCache(Path(td)/'responses.jsonl',False)
            c.before_live=unittest.mock.Mock(side_effect=[None,RuntimeError('completion drift')]);c.first_admission_checked=True
            response=dict(text='{"rate":10,"reasoning":"","note":""}',model='gpt-6-luna',backend='codex')
            with patch('sim.resource_cache.llm.chat',return_value=response):
                with self.assertRaisesRegex(RuntimeError,'completion drift'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
            self.assertEqual(len(c.entries),1);self.assertEqual(len(c.requests),1);self.assertTrue(c.abort.is_set())
    def test_call_overlap_not_function_lifetimes(self):
        from scripts.s36_analyze import validate_call_overlap
        def gt(start,end):return dict(call_provenance=[dict(call_started_utc='2026-10-24T'+start+'+00:00',call_completed_utc='2026-10-24T'+end+'+00:00')])
        validate_call_overlap([gt('23:01:00','23:02:00'),gt('23:01:30','23:03:00')])
        with self.assertRaisesRegex(AssertionError,'do not overlap'):validate_call_overlap([gt('23:01:00','23:01:10'),gt('23:01:30','23:03:00')])
        with self.assertRaisesRegex(AssertionError,'more than60s'):validate_call_overlap([gt('23:01:00','23:04:00'),gt('23:02:01','23:03:00')])
    def test_resolved_dry_publication_guard(self):
        from scripts.s36_present import render
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td)/'result.json';p.write_text(json.dumps(dict(dry=True,metrics={'resource_payment':{'paired_difference':{}}})))
            for out,fig in [(str(Path('results/s36_summary.md').resolve()),str(Path(td)/'figure.png')),('./results/s36_summary.md',str(Path(td)/'figure.png')),(str(Path(td)/'summary.md'),str(Path('figures/s36_grossnet.png').resolve()))]:
                with self.assertRaisesRegex(ValueError,'dry publication'):render(str(p),out,fig)
    def test_raw_quote_and_normalization_tamper_rejected(self):
        import contextlib,io,sys
        from scripts.s36_analyze import analyze
        from scripts.s36_independent import verify
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);data=root/'dry'
            with patch.object(sys,'argv',['sim.grossnet','--dry','--out',str(data)]),contextlib.redirect_stdout(io.StringIO()):m.main()
            result=analyze(data,allow_dry=True);out=root/'result.json';out.write_text(json.dumps(result))
            self.assertTrue(verify(data,out)['passed'])
            game_path=next(data.glob('game_*_gross.json'));original=game_path.read_bytes()
            game=json.loads(original);game['rows'][2]['market']['resource_payment']+=10
            game_path.write_text(json.dumps(game))
            with self.assertRaises(AssertionError):analyze(data,allow_dry=True)
            with self.assertRaises(AssertionError):verify(data,out)
            game_path.write_bytes(original)
            game=json.loads(original);game['rows'][2]['agents'][0]['price']-=10
            game_path.write_text(json.dumps(game))
            with self.assertRaises((AssertionError,ValueError)):analyze(data,allow_dry=True)
            with self.assertRaises(AssertionError):verify(data,out)
    def test_admission_failure_atomically_stops_waiting_partner(self):
        import threading
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            cache=m.TenderCache(Path(td)/'responses.jsonl',False)
            entered=threading.Event();partner_started=threading.Event();errors={};guard_calls=[]
            def guard():
                guard_calls.append(1);entered.set()
                self.assertTrue(partner_started.wait(5))
                raise RuntimeError('transient preflight failure')
            cache.before_live=guard
            def call(name):
                if name=='B':partner_started.set()
                try:cache.call('s','u','cheap','codex','r',0,name,0,'gpt-6-luna')
                except BaseException as exc:errors[name]=str(exc)
            with patch('sim.resource_cache.llm.chat') as transport:
                first=threading.Thread(target=call,args=('A',));first.start()
                self.assertTrue(entered.wait(5))
                second=threading.Thread(target=call,args=('B',));second.start()
                first.join(5);second.join(5)
                self.assertFalse(first.is_alive());self.assertFalse(second.is_alive())
                self.assertTrue(cache.abort.is_set());self.assertEqual(len(guard_calls),1)
                self.assertIn('preflight failure',errors['A']);self.assertIn('Terminal failure',errors['B'])
                transport.assert_not_called()
    def test_preflight_chronology_mutations(self):
        from copy import deepcopy
        from datetime import datetime
        from scripts.s36_analyze import verify_transport_and_preflight
        stamp=lambda text:'2026-10-25T'+text+'+00:00'
        def receipt(checked,observed):
            return dict(observed_utc=stamp(observed),runtime_precheck=dict(checked_utc=stamp(checked),required_seconds=10,remaining_seconds=(datetime.fromisoformat(m.DEADLINE)-datetime.fromisoformat(stamp(checked))).total_seconds()))
        launch=receipt('00:59:58','00:59:59');dispatch=receipt('01:00:01','01:00:02')
        events=[dict(utc=stamp('01:00:00'))];requests=[dict(admitted_utc=stamp('01:00:03'))]
        games=[]
        for seed in m.SEEDS:
            for condition,second in [('net',4),('gross',5)]:
                games.append(dict(ground_truth=dict(seed=seed,condition=condition,call_provenance=[dict(call_started_utc=stamp('01:00:0'+str(second)),call_completed_utc=stamp('01:00:10'))])))
        verify_transport_and_preflight(games,requests,launch,dispatch,events)
        bad=deepcopy(dispatch);bad['observed_utc']=stamp('01:00:04')
        with self.assertRaises(AssertionError):verify_transport_and_preflight(games,requests,launch,bad,events)
        bad=deepcopy(launch);bad['observed_utc']=stamp('01:00:01')
        with self.assertRaises(AssertionError):verify_transport_and_preflight(games,requests,bad,dispatch,events)
    def test_utc(self):
        with self.assertRaises(ValueError):m.utc('2026-10-24T00:00:00')
        with self.assertRaises(ValueError):m.utc('2026-10-24T00:00:00+01:00')

if __name__=='__main__':unittest.main()
