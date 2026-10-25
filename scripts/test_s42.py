"""S42 entry protocol, economic edge cases and end-to-end corruption checks."""
import contextlib,io,itertools,json,sys,tempfile,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch,Mock
import sim.entry as m
from scripts.s42_analyze import analyze,metrics,exact_summary,exact_signflip,classify,validate_game
from scripts.s42_independent import verify,expected_prompts,accepted

class EntryTests(unittest.TestCase):
    def setUp(self):
        clock=patch('sim.entry.now',return_value='2026-10-25T02:59:00+00:00')
        clock.start();self.addCleanup(clock.stop)
    def test_population_and_economics(self):
        from scripts.s42_economics import check
        self.assertTrue(check()['passed'])
        for seed in m.SEEDS:
            for turn in range(10):
                self.assertEqual(m.active_agents(seed,'control',turn),m.active_agents(seed,'entry',min(turn,4)))
                self.assertEqual(len(m.active_agents(seed,'entry',turn)),2 if turn<5 else 3)
        self.assertEqual(m.outcome([10,10,10],[20]*3),(10,[F(1,3)]*3,[F(10,3)]*3))
        self.assertEqual(m.outcome([8,19,19],[20]*3),(19,[F(0),F(1,2),F(1,2)],[F(0),F(1,2),F(1,2)]))
    def test_strict_parsers(self):
        good='{"rate":20,"reasoning":"","note":""}'
        self.assertEqual(m.parse_action(good),accepted(good))
        for bad in ['{"rate":true,"reasoning":"","note":""}','{"rate":21,"reasoning":"","note":""}','{"rate":1,"rate":2,"reasoning":"","note":""}','{"rate":2,"reasoning":"","note":NaN}','[]']:
            self.assertIsNone(m.parse_action(bad));self.assertIsNone(accepted(bad))
    def test_screen_boundaries(self):
        for diffs,verdict in [([4]*5,'HIT'),([0,5,5,5,5],'ODD'),([1]*5,'DUD'),([0]*5,'DUD'),([3]*5,'DUD')]:
            ns=[d*720 for d in diffs];sm=exact_summary(diffs);sm.update(exact_signflip(ns))
            self.assertEqual(classify(ns,sm),verdict)
    def test_prompts_visibility_and_no_advance_notice(self):
        seed=m.SEEDS[0];chat=[dict(round=1,author=a,text=a+' secret') for a in 'ABC']
        for turn in [0,4,5,9]:
            rows=[] if turn==0 else [dict(round=i,market=dict(resource_payment=10),agents=[dict(id=a,price=10,quantity=.5,profit=5) for a in m.active_agents(seed,'control',i)]) for i in range(turn)]
            for c in m.CONDITIONS:
                active=m.active_agents(seed,c,turn);values=m.productivity(seed,c,turn)
                for agent in active:
                    rivals=[a for a in active if a!=agent]
                    s,u=m.prompts(agent,rivals,rows,chat,c,values)
                    self.assertEqual((s,u),expected_prompts(agent,rivals,rows,chat,c,values))
                    self.assertEqual(json.loads(u.split('Notes file snapshot: ')[1].split('\n')[0]),[x for x in chat if x['author']==agent])
                    self.assertNotIn('round 6',s);self.assertNotIn('round 10',s)
            if turn<5:
                active=m.active_agents(seed,'control',turn);agent=active[0];rivals=active[1:]
                self.assertEqual(m.prompts(agent,rivals,rows,chat,'control',m.productivity(seed,'control',turn)),m.prompts(agent,rivals,rows,chat,'entry',m.productivity(seed,'entry',turn)))
    def test_rational_metrics(self):
        rows=[dict(agents=[dict(price=10)]*3,market=dict(resource_payment=10)) for _ in range(10)]
        r=metrics(dict(rows=rows))
        self.assertEqual(r['resource_payment'],10);self.assertEqual(r['firm_profit'],10)
        self.assertEqual(r['stage_regret'],F(17,3)) # dev11 earns9 versus10/3
        self.assertTrue(all((v*720).denominator==1 for v in r.values()))
    def test_abort_cutoff_and_cache_only(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            cache=m.TenderCache(Path(td)/'responses.jsonl',False)
            with patch('sim.entry.now',return_value='2099-01-01T00:00:00+00:00'),patch('sim.resource_cache.llm.chat') as chat:
                with self.assertRaisesRegex(RuntimeError,'deadline'):cache.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
                chat.assert_not_called();self.assertTrue(cache.abort.is_set())
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            cache=m.TenderCache(Path(td)/'responses.jsonl',True);cache.cache_only=True
            with self.assertRaisesRegex(RuntimeError,'Archived'):cache.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
    def test_transport_failure_not_retried(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            cache=m.TenderCache(Path(td)/'responses.jsonl',False)
            with patch('sim.resource_cache.llm.chat',side_effect=RuntimeError('down')) as chat:
                with self.assertRaisesRegex(RuntimeError,'down'):cache.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
                with self.assertRaisesRegex(RuntimeError,'Terminal'):cache.call('s','u','cheap','codex','r',0,'B',0,'gpt-6-luna')
                self.assertEqual(chat.call_count,1)
            self.assertTrue((Path(td)/'transport_failures.jsonl').exists())
    def test_runtime_drift(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            guard=m.make_dispatch_guard(Path(td),{}, {'old':1})
            with patch('scripts.s42_runtime.fingerprint',return_value={'new':1}):
                with self.assertRaisesRegex(RuntimeError,'Known CLI inputs changed'):guard()
    def test_full_dry_entry_replay_independent_tamper(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);data=root/'dry'
            with patch.object(sys,'argv',['sim.entry','--dry','--out',str(data)]),contextlib.redirect_stdout(io.StringIO()):m.main()
            r=analyze(data,allow_dry=True);out=root/'result.json';out.write_text(json.dumps(r))
            self.assertEqual(r['cached_responses'],225);self.assertTrue(verify(data,out)['passed'])
            for p in data.glob('game_*.json'):
                g=json.loads(p.read_text());c=g['ground_truth']['condition']
                self.assertEqual([len(row['agents']) for row in g['rows']],[2]*10 if c=='control' else [2]*5+[3]*5)
                notes=[]
                for turn,row in enumerate(g['rows']):
                    for a in row['agents']:
                        requests=[json.loads(l) for l in (data/'raw/requests.jsonl').read_text().splitlines()]
                        q=next(q for q in requests if q['payload'][5:8]==[g['ground_truth']['run_id'],turn,a['id']])
                        snap=json.loads(q['payload'][1].split('Notes file snapshot: ')[1].split('\n')[0])
                        self.assertTrue(all(n['author']==a['id'] and n['round']<=turn for n in snap))
                        if c=='entry' and turn==5 and a['id'] not in g['ground_truth']['assigned_pair']:self.assertEqual(snap,[])
            p=next(data.glob('game_*_entry.json'));original=p.read_bytes();g=json.loads(original)
            g['rows'][5]['agents'].pop();p.write_text(json.dumps(g))
            with self.assertRaises(AssertionError):analyze(data,allow_dry=True)
            with self.assertRaises(AssertionError):verify(data,out)
            p.write_bytes(original)
            with patch('sim.resource_cache.llm.chat',side_effect=AssertionError('No calls')),patch.object(sys,'argv',['sim.entry','--dry','--out',str(data)]),contextlib.redirect_stdout(io.StringIO()):m.main()
            self.assertEqual(p.read_bytes(),original)
    def test_mocked_live_end_to_end(self):
        """Run the full LIVE branch against synthetic paid-route responses in a temp git repo."""
        import contextlib,io,os,shutil,subprocess,sys,threading
        from datetime import datetime,timezone,timedelta
        from scripts.s42_launch import launch
        from scripts.s42_analyze import analyze
        from scripts.s42_independent import verify
        from scripts.s42_present import render
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
            seen=set();seen_lock=threading.Lock()
            def response(*args,**kwargs):
                self.assertEqual(kwargs['retries'],1)
                with seen_lock:
                    name=threading.current_thread().name;first=name not in seen;seen.add(name)
                if first:barrier.wait(timeout=30)
                return dict(text=json.dumps(dict(rate=10,reasoning='synthetic private',note='synthetic own note')),model='gpt-6-luna',backend='codex')
            try:
                os.chdir(root)
                with patch('sim.entry.now',side_effect=lambda:tick().isoformat()),patch('sim.resource_cache.datetime',FixtureDatetime),patch('scripts.s42_launch.datetime',FixtureDatetime),patch('scripts.s42_runtime.fingerprint',return_value={'fixture':True}),patch('scripts.s42_runtime.launch_observation',return_value={'fingerprint':{'fixture':True},'version':'fixture'}),patch('sim.resource_cache.llm.chat',side_effect=response) as transport,patch.object(sys,'argv',['s42_launch']),contextlib.redirect_stdout(io.StringIO()):
                    launch()
                    self.assertEqual(transport.call_count,225)
                    result=analyze(root/'data/s42_entry')
                    self.assertFalse(result['dry']);self.assertEqual(result['verdict'],'DUD')
                    out=root/'results/s42_entry.json';out.write_text(json.dumps(result,indent=2)+'\n')
                    self.assertTrue(verify(root/'data/s42_entry',out)['passed'])
                    render(str(out),str(root/'results/s42_summary.md'),str(root/'figures/s42_entry.png'))
                    # Direct rendering must enforce the complete scientific eligibility gate.
                    def rerender():render(str(out),str(root/'results/s42_summary.md'),str(root/'figures/s42_entry.png'))
                    original_result=out.read_bytes();bad_result=dict(result,cached_responses=-999)
                    out.write_text(json.dumps(bad_result))
                    with self.assertRaisesRegex(ValueError,'full archive validation'):rerender()
                    with self.assertRaises(AssertionError):verify(root/'data/s42_entry',out)
                    out.write_bytes(original_result)
                    failure=root/'data/s42_entry/failure_presentation.json';failure.write_text('{}')
                    with self.assertRaisesRegex(AssertionError,'Failed dataset'):rerender()
                    failure.unlink()
                    journal=root/'data/s42_entry/raw/execution.jsonl';original_journal=journal.read_bytes()
                    journal.write_bytes(original_journal.splitlines(keepends=True)[0])
                    with self.assertRaisesRegex(AssertionError,'Interrupted invocation'):rerender()
                    journal.write_bytes(original_journal)
                    request_path=root/'data/s42_entry/raw/requests.jsonl';original_requests=request_path.read_bytes()
                    qs=[json.loads(line) for line in original_requests.splitlines()];qs[0]['admitted_utc']='2099-01-01T00:00:00+00:00'
                    request_path.write_text(''.join(json.dumps(q)+'\n' for q in qs))
                    with self.assertRaises(AssertionError):rerender()
                    request_path.write_bytes(original_requests)
                    source=root/'DESIGN_S42.md';original_source=source.read_bytes();source.write_bytes(original_source+b'changed')
                    with self.assertRaisesRegex(AssertionError,'Source drift'):rerender()
                    source.write_bytes(original_source)

                    with patch('sim.resource_cache.llm.chat',side_effect=AssertionError('Resume cannot call provider')),patch.object(sys,'argv',['sim.entry']):m.main()
                    journal=root/'data/s42_entry/raw/execution.jsonl';original=journal.read_bytes()
                    journal.write_bytes(original.splitlines(keepends=True)[0])
                    with self.assertRaisesRegex(RuntimeError,'Interrupted invocation'):m.main()
                    journal.write_bytes(original)
                    failure=root/'data/s42_entry/failure_fixture.json';failure.write_text('{}')
                    with self.assertRaisesRegex(AssertionError,'Failed dataset'):analyze(root/'data/s42_entry')
            finally:os.chdir(origin)
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
    def test_referenced_file_contents_are_guarded(self):
        import os
        from scripts.s42_runtime import referenced_inputs
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            f=Path(td)/'config';f.write_text('alpha')
            with patch.dict(os.environ,{'CODEX_MANAGED_CONFIG_FILE':str(f),'NODE_OPTIONS':''}):
                first=referenced_inputs();f.write_text('beta')
                self.assertNotEqual(first,referenced_inputs())
                f.unlink()
                with self.assertRaisesRegex(RuntimeError,'unavailable'):referenced_inputs()
        with patch.dict(os.environ,{'NODE_OPTIONS':'--require /tmp/example.js'}):
            with self.assertRaisesRegex(RuntimeError,'NODE_OPTIONS'):referenced_inputs()

    def test_admission_survives_transport_interruption(self):
        from sim.entry import TenderCache
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            path=Path(td)/'responses.jsonl';cache=TenderCache(path,False)
            with patch('sim.resource_cache.llm.chat',side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):cache.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
            admissions=[json.loads(x) for x in path.with_name('admissions.jsonl').read_text().splitlines()]
            self.assertEqual(len(admissions),1);self.assertEqual(admissions[0]['payload'][0:2],['s','u'])
            self.assertTrue(cache.abort.is_set())
            with self.assertRaisesRegex(ValueError,'Unfinished admission'):TenderCache(path,False)

if __name__=='__main__':unittest.main()
