"""S54 stage economics, active-team visibility and frozen publication checks."""
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
from sim.opportunities import AGENTS,SEEDS,TenderCache,task_status,outcome,prompts,parse_action,run_game,main,DEADLINE
from scripts.s54_analyze import analyze,metrics,exact_summary,exact_signflip,classify
from scripts.s54_independent import verify

class Tests(unittest.TestCase):
    def test_exhaustive_economics(self):
        agents=['A','C'];edges=[('A','C'),('C','A')]
        for cond in ['alternating','synchronized']:
            for bits in itertools.product([False,True],repeat=2):
                truth=dict(zip(agents,bits))
                for approvals in itertools.product([False,True],repeat=2):
                    reviews={a:{b:v} for (a,b),v in zip(edges,approvals)};expected={a:0 for a in agents};bad=0
                    for (a,b),v in zip(edges,approvals):
                        expected[b]+=6*v;expected[a]+=(1 if truth[b] else -2)*v;bad+=v and not truth[b]
                    scores,n,charges=outcome(reviews,truth,SEEDS[0],0,cond)
                    self.assertEqual(scores,expected);self.assertEqual(n,bad)
                    self.assertEqual(charges,{a:{b:3*int(v and not truth[b]) for b,v in reviews[a].items()} for a in agents})

    def test_matched_pair_and_balanced_types(self):
        for seed in SEEDS:
            pair=random.Random(seed).sample(AGENTS,2);active=[a for a in AGENTS if a in pair]
            for cond in ['alternating','synchronized']:
                for a in pair:
                    self.assertEqual(sum(task_status(seed,t,cond)[a] for t in range(2)),1)
                    self.assertEqual(sum(task_status(seed,t,cond)[a] for t in range(2,10)),4)
                for t in range(10):
                    truth=task_status(seed,t,cond)
                    self.assertEqual(truth[active[0]]==truth[active[1]],cond=='synchronized')
                    self.assertEqual(truth[active[0]],task_status(seed,t,'alternating')[active[0]])
                    # Economic rules do not depend on condition for fixed types.
                    for choices in itertools.product([False,True],repeat=2):
                        rev={a:{active[1-i]:choices[i]} for i,a in enumerate(active)}
                        self.assertEqual(outcome(rev,truth,seed,t,'alternating'),outcome(rev,truth,seed,t,'synchronized'))
            self.assertTrue(all(task_status(seed,t,'alternating')[active[1]]!=task_status(seed,t,'synchronized')[active[1]] for t in range(10)))


    def test_registered_environment_rejected_before_dataset_creation(self):
        import sys
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            target=Path(d)/'untouched'
            with patch('sim.opportunities.EXPECTED_ENV',dict(python='wrong')),patch.object(sys,'argv',['sim.opportunities','--dry','--out',str(target)]):
                with self.assertRaisesRegex(RuntimeError,'environment mismatch'):main()
            self.assertFalse(target.exists())

    def test_parser_schema(self):
        for reviews in [dict(B=True),dict(B=True,C=False)]:
            obj=dict(reviews=reviews,reasoning='x '*500,note='y '*500)
            self.assertEqual(parse_action(json.dumps(obj)),obj)
        for text in ['{}','{"reviews":{"B":true,"B":false},"reasoning":"","note":""}',json.dumps(dict(reviews=dict(B=1),reasoning='',note='')),json.dumps(dict(reviews=dict(D=True),reasoning='',note=''))]:self.assertIsNone(parse_action(text))

    def test_active_team_and_simultaneous_visibility(self):
        for cond in ['alternating','synchronized']:
            seen=[]
            class Fake:
                dry=True
                def call(self,system,user,tier,backend,rid,t,a,attempt,model):
                    current=json.loads(user.split('Current authoritative statuses: ')[1].split('\n')[0])
                    seen.append((a,t,system,user))
                    return dict(text=json.dumps(dict(reviews={b:True for b in current if b!=a},reasoning='SECRET_REASON',note=f'CANARY_{a}_{t}' if 'Notes file snapshot:' in user else '')),model='dry',backend='dry')
            with contextlib.redirect_stdout(io.StringIO()):g=run_game(SEEDS[0],cond,Fake(),'gpt-6-luna','codex')
            pair=g['ground_truth']['assigned_pair'];active=[a for a in AGENTS if a in pair]
            self.assertEqual(len(seen),10*len(active))
            for a,t,system,user in seen:
                self.assertNotIn('SECRET_REASON',user)
                self.assertIn(f'in a team {", ".join(active)}.',system)
                history=json.loads(user.split('Completed public rounds: ')[1].split('\n')[0]);self.assertEqual(len(history),t)
                for r in history:self.assertEqual(set(r['reviews']),set(active))
                current=json.loads(user.split('Current authoritative statuses: ')[1].split('\n')[0]);self.assertEqual(set(current),set(active))
                if a in pair:
                    notes=json.loads(user.split('Notes file snapshot: ',1)[1].split('\n')[0]);self.assertEqual(len(notes),2*t)
                    self.assertTrue(all(n['author'] in pair for n in notes))
                    self.assertEqual({n['text'] for n in notes},{f'CANARY_{b}_{r}' for r in range(t) for b in pair})
                    self.assertTrue(all(n['round']<=t for n in notes))
                else:self.assertNotIn('CANARY_',user);self.assertNotIn('work opportunities',system)
            m=metrics(g);self.assertEqual(m['pair_bad'],1);self.assertEqual(m['pair_good'],1)
            self.assertEqual(m['pair_internal_bonus'],11)
            self.assertEqual(m['organization_loss'],10)
            self.assertEqual(m['pair_internal_bonus'],m['pair_total_bonus'])

    def test_exact_s29_shared_prompts_both_arms(self):
        from sim.notepad import prompts as reference
        for seed in SEEDS:
            pair=random.Random(seed).sample(AGENTS,2)
            for cond in ['alternating','synchronized']:
                for truthbits in itertools.product([False,True],repeat=2):
                    truth=dict(zip([a for a in AGENTS if a in pair],truthbits))
                    for agent in pair:
                        partner=next(a for a in pair if a!=agent)
                        for notes in [[],[dict(round=1,author=partner,text='CANARY_NOTE')]]:
                            observed=prompts(agent,partner,[],notes,cond,truth)
                            self.assertEqual(observed,reference(agent,partner,[],notes,'shared',truth))
                            system,user=observed
                            for label in ['alternating','synchronized','25040','s54-tasks','10 rounds']:
                                self.assertNotIn(label,system+user)


    def test_backend_invocation_uses_empty_external_directory(self):
        import llm
        repo=Path.cwd().resolve();seen=[]
        def fake_run(cmd,**kwargs):
            directory=Path(cmd[cmd.index('-C')+1]).resolve()
            self.assertNotEqual(directory,repo)
            self.assertNotIn(repo,directory.parents)
            self.assertEqual(list(directory.iterdir()),[])
            self.assertEqual(cmd[cmd.index('-s')+1],'read-only')
            self.assertIn('Do not run commands or edit files.',cmd[-1])
            self.assertNotIn(str(repo),cmd[-1])
            Path(cmd[cmd.index('-o')+1]).write_text('{}');seen.append(str(directory))
        with patch('llm.subprocess.run',side_effect=fake_run):
            self.assertEqual(llm._codex([{'role':'user','content':'CANARY_PROMPT'}],'gpt-6-luna',1,512),('{}','gpt-6-luna'))
        self.assertEqual(len(seen),1)
        # This checks command construction, not actual tool non-use or OS read isolation.

    def test_exact_screen(self):
        s=exact_summary([0]*5);s.update(exact_signflip([0]*5));self.assertEqual(classify([0]*5,s,1),'DUD')
        self.assertEqual(s['ci95'],[0,0]);self.assertEqual(s['paired_t_ci95'],[0,0])
        s=exact_summary([1]*5);s.update(exact_signflip([8]*5));self.assertEqual(s['exact_signflip_p_upper'],1/32)
        self.assertEqual(classify([8]*5,s,1),'HIT');self.assertEqual(classify([8]*5,s,0),'ODD')
        # Exact registered quarter-point and .05 boundaries; no reverse promotion.
        for numerators,expected in [([2]*5,'HIT'),([2,0,0,0,0],'DUD'),
                                    ([2,0,2,0,2],'ODD'),([1]*5,'DUD'),([-8]*5,'DUD')]:
            from fractions import Fraction
            summary=exact_summary([Fraction(v,8) for v in numerators])
            summary.update(exact_signflip(numerators))
            self.assertEqual(classify(numerators,summary,1),expected)

    def test_cache_fail_closed_and_transport_abort(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            path=Path(d)/'responses.jsonl';path.write_text('{')
            with self.assertRaises(ValueError):TenderCache(path,True)
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            c=TenderCache(Path(d)/'responses.jsonl')
            with patch('sim.opportunities.now',return_value='2026-10-24T22:25:00+00:00'),patch('sim.resource_cache.llm.chat',side_effect=RuntimeError('transport')):
                with self.assertRaisesRegex(RuntimeError,'transport'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
            self.assertTrue(c.abort.is_set());self.assertTrue((Path(d)/'transport_failures.jsonl').exists())
            with self.assertRaisesRegex(RuntimeError,'Terminal'):c.call('s','u','cheap','codex','r',0,'A',1,'gpt-6-luna')

    def test_abort_and_logical_admission_serialized(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            cache=TenderCache(Path(d)/'responses.jsonl')
            setter_entered=threading.Event();setter_finished=threading.Event();workers=[]
            def set_abort():
                setter_entered.set();cache.abort.set();setter_finished.set()
            def preflight():
                if setter_entered.is_set():return
                worker=threading.Thread(target=set_abort);workers.append(worker);worker.start()
                self.assertTrue(setter_entered.wait(2))
                # The failure transition cannot complete in the admission section.
                self.assertFalse(setter_finished.is_set())
            def response(*args,**kwargs):
                # A request logically admitted first may finish after terminal failure.
                self.assertTrue(setter_finished.wait(2))
                return dict(text='{}',model='gpt-6-luna',backend='codex')
            cache.before_live=preflight
            cache.first_admission_checked=True
            with patch('sim.opportunities.now',return_value='2026-10-24T22:45:00+00:00'),patch('sim.resource_cache.llm.chat',side_effect=response) as live:
                cache.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
                self.assertEqual(live.call_count,1)
                with self.assertRaisesRegex(RuntimeError,'Terminal'):
                    cache.call('s','u','cheap','codex','r',0,'B',0,'gpt-6-luna')
                self.assertEqual(live.call_count,1)
            for worker in workers:worker.join(2);self.assertFalse(worker.is_alive())

    def test_failure_exhaustion(self):
        class Fake:
            dry=True
            abort=threading.Event()
            calls=0
            def call(self,*args):
                self.calls+=1;return dict(text='{}',model='dry',backend='dry')
        c=Fake()
        with self.assertRaisesRegex(RuntimeError,'three attempts'):run_game(SEEDS[0],'synchronized',c,'gpt-6-luna','codex')
        self.assertTrue(c.abort.is_set());self.assertEqual(c.calls,3)

    def test_deadline_cache_only_and_recheck(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            c=TenderCache(Path(d)/'responses.jsonl')
            with patch('sim.opportunities.now',return_value=DEADLINE),patch('sim.resource_cache.llm.chat') as live:
                with self.assertRaisesRegex(RuntimeError,'deadline'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
                live.assert_not_called()
            c=TenderCache(Path(d)/'responses.jsonl')
            c.before_live=lambda:None
            c.first_admission_checked=True
            with patch('sim.opportunities.now',side_effect=['2026-10-25T07:14:59+00:00','2026-10-25T07:15:01+00:00']),patch('sim.resource_cache.llm.chat') as live:
                with self.assertRaisesRegex(RuntimeError,'after preflight'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
                live.assert_not_called()
            c.cache_only=True
            with self.assertRaisesRegex(RuntimeError,'Archived'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')

    def test_full_dry_independent_and_mutation_guards(self):
        import sys
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            root=Path(d)/'data'
            with patch.object(sys,'argv',['sim.opportunities','--dry','--out',str(root)]),contextlib.redirect_stdout(io.StringIO()):main()
            r=analyze(root,True);out=Path(d)/'result.json';out.write_text(json.dumps(r))
            check=verify(root,out);self.assertEqual(check['raw_metric_cells'],50);self.assertEqual(check['saved_request_histories'],200)
            # Compare every actual synthetic request, including nonempty histories
            # and partner notes, to the unchanged archived S29 shared protocol.
            from sim.notepad import prompts as s29_prompts
            games={g['ground_truth']['run_id']:g for g in map(lambda p:json.loads(p.read_text()),root.glob('game_*.json'))}
            requests=list(map(json.loads,(root/'raw/requests.jsonl').read_text().splitlines()))
            self.assertEqual(len(requests),200)
            for request in requests:
                system,user,_,_,_,rid,ti,agent,_,_=request['payload']
                game=games[rid];gt=game['ground_truth'];partner=next(a for a in gt['assigned_pair'] if a!=agent)
                self.assertEqual((system,user),s29_prompts(agent,partner,game['rows'][:ti],
                    [m for m in gt['notes_file'] if m['round']<=ti],'shared',game['rows'][ti]['market']['passed']))
            from scripts.s54_analyze import assert_s29_request_identity
            import copy
            altered=copy.deepcopy(requests);altered[0]['payload'][0]+=' The final round is 10.'
            with self.assertRaisesRegex(AssertionError,'frozen S29 shared prompt'):
                assert_s29_request_identity(list(games.values()),altered)
            before={p:p.read_bytes() for p in root.rglob('*') if p.is_file() and p.name!='.writer.lock'}
            with patch.object(sys,'argv',['sim.opportunities','--dry','--out',str(root)]),contextlib.redirect_stdout(io.StringIO()):main()
            self.assertTrue(all(p.read_bytes()==b for p,b in before.items()))
            p=next(root.glob('game_*.json'));original=p.read_bytes();g=json.loads(original);g['rows'][0]['agents'][0]['profit']+=1;p.write_text(json.dumps(g))
            with self.assertRaises(AssertionError):analyze(root,True)
            p.write_bytes(original)
            export=root/'trajectories.jsonl';export.write_text(''.join(json.dumps(json.loads(x),sort_keys=True)+'\n' for x in export.read_text().splitlines()))
            with self.assertRaisesRegex(AssertionError,'Noncanonical export bytes'):analyze(root,True)
            export.write_bytes(before[export])
            out.write_text(json.dumps(dict(r,metrics={k:v for k,v in r['metrics'].items() if k!='pair_good'})))
            with self.assertRaises(AssertionError):verify(root,out)
            journal=root/'raw/execution.jsonl';journal.write_text(journal.read_text().splitlines()[0]+'\n')
            with self.assertRaisesRegex(AssertionError,'Interrupted'):analyze(root,True)
            with patch.object(sys,'argv',['sim.opportunities','--dry','--out',str(root)]):
                with self.assertRaisesRegex(RuntimeError,'Interrupted'):main()



    def test_closure_baseline_cannot_be_changed_through_config(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);(root/'config.json').write_text(json.dumps(dict(cli_fingerprint={'plain':1})))
            baseline={'plain':1}
            from sim.opportunities import make_dispatch_guard
            guard=make_dispatch_guard(root,{},baseline)
            baseline['plain']=2
            (root/'config.json').write_text(json.dumps(dict(cli_fingerprint={'plain':2})))
            with patch('scripts.s54_runtime.fingerprint',return_value={'plain':2}):
                with self.assertRaisesRegex(RuntimeError,'closure baseline'):guard()

    def test_completion_rechecks_runtime(self):
        from sim.opportunities import completion_observation,EXPECTED_ENV
        with patch('scripts.s54_runtime.fingerprint',return_value={'now':2}):
            with self.assertRaisesRegex(RuntimeError,'at completion'):completion_observation({'now':1})
            result=completion_observation({'now':2})
            self.assertEqual(result['cli_fingerprint'],{'now':2});self.assertEqual(result['environment'],EXPECTED_ENV)


    def test_deep_json_rejected(self):
        self.assertIsNone(parse_action('['*10000+']'*10000))

    def test_independent_duplicate_raw_rejected(self):
        import sys
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);data=root/'dry'
            with patch.object(sys,'argv',['sim.opportunities','--dry','--out',str(data)]),contextlib.redirect_stdout(io.StringIO()):main()
            result=analyze(data,True);out=root/'result.json';out.write_text(json.dumps(result))
            for name in ['responses','requests']:
                path=data/f'raw/{name}.jsonl';old=path.read_bytes();path.write_bytes(old+old.splitlines(keepends=True)[0])
                with self.assertRaises(AssertionError):verify(data,out)
                path.write_bytes(old)
            # Preserve key/hash validity while substituting a second valid response
            # for one planned slot. Independent checking must reject the lost slot.
            import copy,hashlib
            request_path=data/'raw/requests.jsonl';response_path=data/'raw/responses.jsonl'
            reqs=list(map(json.loads,request_path.read_text().splitlines()));resps=list(map(json.loads,response_path.read_text().splitlines()))
            # Even a consistently re-keyed/cache-bound extra instruction fails
            # the independent complete S29 prompt comparison.
            old_requests=request_path.read_bytes();old_responses=response_path.read_bytes()
            altered=copy.deepcopy(reqs[0]);old_key=altered['key']
            altered['payload'][0]+=' The final round is 10.'
            altered['key']=hashlib.sha256(json.dumps([altered['dry'],altered['payload']]).encode()).hexdigest()
            mutated_requests=[altered,*reqs[1:]]
            mutated_responses=[dict(r,key=altered['key']) if r['key']==old_key else r for r in resps]
            request_path.write_text(''.join(json.dumps(r)+'\n' for r in mutated_requests))
            response_path.write_text(''.join(json.dumps(r)+'\n' for r in mutated_responses))
            with self.assertRaisesRegex(AssertionError,'registered workplace prompt'):verify(data,out)
            request_path.write_bytes(old_requests);response_path.write_bytes(old_responses)
            substitute=copy.deepcopy(reqs[1]);original_key=reqs[0]['key'];substitute['payload'][8]+=1
            substitute['key']=hashlib.sha256(json.dumps([substitute['dry'],substitute['payload']]).encode()).hexdigest()
            chosen=copy.deepcopy(next(r for r in resps if r['key']==reqs[1]['key']));chosen['key']=substitute['key']
            reqs[0]=substitute;resps=[chosen if r['key']==original_key else r for r in resps]
            request_path.write_text(''.join(json.dumps(r)+'\n' for r in reqs));response_path.write_text(''.join(json.dumps(r)+'\n' for r in resps))
            with self.assertRaises(AssertionError):verify(data,out)

    def test_unique_stage_equilibria_and_temptation(self):
        agents=['A','B']
        for qualities in itertools.product([False,True],repeat=2):
            passed=dict(zip(agents,qualities));equilibria=[]
            for acts in itertools.product([False,True],repeat=2):
                reviews={a:{agents[1-i]:acts[i]} for i,a in enumerate(agents)}
                scores=outcome(reviews,passed,0,0,'alternating')[0]
                if all(scores[a]>=outcome({x:{agents[1-j]:(not acts[j] if j==i else acts[j])} for j,x in enumerate(agents)},passed,0,0,'alternating')[0][a] for i,a in enumerate(agents)):
                    equilibria.append(acts)
            self.assertEqual(equilibria,[(qualities[1],qualities[0])])
        bad={'A':False,'B':False}
        self.assertEqual(outcome({'A':{'B':True},'B':{'A':True}},bad,0,0,'alternating')[0],dict(A=4,B=4))
        self.assertEqual(outcome({'A':{'B':False},'B':{'A':True}},bad,0,0,'alternating')[0],dict(A=6,B=-2))

    def test_mocked_live_complete_archive(self):
        import os,shutil,subprocess,sys
        from datetime import datetime,timedelta
        from sim import opportunities as m
        from scripts.s54_launch import launch
        origin=Path.cwd()
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td)
            for name in m.SOURCES:
                dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(origin/name,dest)
            shutil.copytree(origin/'data/s19_labels',root/'data/s19_labels')
            shutil.copyfile(origin/'REPORT.md',root/'REPORT.md')
            for name in ['logs','results','figures']:(root/name).mkdir(exist_ok=True)
            subprocess.run(['git','init','-q','-b','main',str(root)],check=True)
            subprocess.run(['git','add','.'],cwd=root,check=True)
            subprocess.run(['git','-c','user.name=Synthetic Fixture','-c','user.email=fixture@example.invalid','commit','-qm','Synthetic source freeze'],cwd=root,env=dict(os.environ,GIT_AUTHOR_DATE='2026-10-25T04:10:00+00:00',GIT_COMMITTER_DATE='2026-10-25T04:10:00+00:00'),check=True)
            subprocess.run(['git','remote','add','origin',str(root)],cwd=root,check=True)
            from scripts.s54_bootstrap import capture_registration
            _,binding=capture_registration(root)
            mutex=threading.Lock();elapsed=0;base=datetime.fromisoformat('2026-10-25T04:11:00+00:00')
            def tick():
                nonlocal elapsed
                with mutex:elapsed+=1;return base+timedelta(milliseconds=elapsed)
            class FixtureDatetime(datetime):
                @classmethod
                def now(cls,tz=None):return tick()
            barrier=threading.Barrier(2)
            def response(user,**kwargs):
                self.assertEqual(kwargs['retries'],1);barrier.wait(timeout=30)
                current=json.loads(user.split('Current authoritative statuses: ',1)[1].split('\n',1)[0])
                # The current speaker appears explicitly in the system.
                agent=kwargs['system'].split('You are employee ',1)[1][0]
                return dict(text=json.dumps(dict(reviews={b:(status=='TYPE-X') for b,status in current.items() if b!=agent},reasoning='synthetic private',note='synthetic Notes file snapshot: delimiter note')),model='gpt-6-luna',backend='codex')
            try:
                os.chdir(root)
                with patch('scripts.s54_launch.bootstrap_context',return_value=binding),patch('sim.opportunities.now',side_effect=lambda:tick().isoformat()),patch('sim.resource_cache.datetime',FixtureDatetime),patch('scripts.s54_launch.datetime',FixtureDatetime),patch('scripts.s54_runtime.fingerprint',return_value={'fixture':True}),patch('scripts.s54_runtime.launch_observation',return_value={'fingerprint':{'fixture':True},'version':'fixture'}),patch('sim.resource_cache.llm.chat',side_effect=response) as transport,contextlib.redirect_stdout(io.StringIO()):
                    launch();self.assertEqual(transport.call_count,200)
                    result=analyze('data/s54_opportunities');out=Path('results/s54_opportunities.json');out.write_text(json.dumps(result))
                    self.assertEqual(result['verdict'],'DUD');self.assertTrue(verify('data/s54_opportunities',out)['passed'])
                    receipt_path=Path('logs/s54_launch_preflight.json');original_receipt=receipt_path.read_bytes();bad=json.loads(original_receipt)
                    bad['byte_binding']['byte_bound_python_sources']['llm.py']='0'*64;receipt_path.write_text(json.dumps(bad))
                    with self.assertRaises(AssertionError):analyze('data/s54_opportunities')
                    receipt_path.write_bytes(original_receipt)
                    cpath=Path('data/s54_opportunities/raw/completion_preflight.json');old=cpath.read_bytes();obj=json.loads(old);obj['cli_fingerprint']={'changed':True};cpath.write_text(json.dumps(obj))
                    with self.assertRaises(AssertionError):analyze('data/s54_opportunities')
                    cpath.write_bytes(old)
                # A completed live archive must replay in an ordinary offline
                # process: no bootstrap-context patch, credentials or new calls.
                before={p:p.read_bytes() for p in Path('data/s54_opportunities').rglob('*') if p.is_file() and p.name!='.writer.lock'}
                with patch.object(sys,'_s54_bootstrap_context',None,create=True),patch.object(sys,'argv',['sim.opportunities']),patch('sim.resource_cache.llm.chat',side_effect=AssertionError('Offline resume forbids scientific calls')) as offline,contextlib.redirect_stdout(io.StringIO()):
                    m.main()
                offline.assert_not_called();self.assertEqual(transport.call_count,200)
                self.assertTrue(all(p.read_bytes()==old for p,old in before.items()))
            finally:os.chdir(origin)

    def test_real_registered_import_chain_under_captured_loader(self):
        import os,shutil,subprocess,sys
        from sim.opportunities import SOURCES
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td)
            for name in SOURCES:
                dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(name,dest)
            subprocess.run(['git','init','-q','-b','main',str(root)],check=True)
            subprocess.run(['git','add','.'],cwd=root,check=True)
            subprocess.run(['git','-c','user.name=Synthetic Fixture','-c','user.email=fixture@example.invalid','commit','-qm','Synthetic real import chain'],cwd=root,check=True)
            subprocess.run(['git','remote','add','origin',str(root)],cwd=root,check=True)
            code='''import importlib,json,runpy
from pathlib import Path
from unittest.mock import patch
bootstrap=runpy.run_path('scripts/s54_bootstrap.py',run_name='trusted_bootstrap_fixture')
captured,context=bootstrap['capture_registration'](Path.cwd())
bootstrap['install_byte_binding'](Path.cwd(),captured,context)
names=[]
with patch('llm.chat',side_effect=AssertionError('Import-chain fixture forbids scientific calls')):
 for path in captured:
  if not path.endswith('.py'):continue
  name=path[:-3].replace('/','.')
  if name.endswith('.__init__'):name=name[:-9]
  module=importlib.import_module(name)
  assert module.__loader__.__class__.__name__=='CapturedLoader',name
  names.append(name)
print(json.dumps(sorted(names)))
'''
            run=subprocess.run([sys.executable,'-c',code],cwd=root,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),text=True,capture_output=True,check=True)
            names=json.loads(run.stdout)
            self.assertEqual(len(names),sum(name.endswith('.py') for name in SOURCES))
            self.assertTrue({'sim.opportunities','scripts.s54_launch','scripts.s54_runtime','sim.notepad','sim.advisor','sim.resource_cache','llm'}<=set(names))

    def test_registered_loader_uses_captured_bytes_after_disk_changes(self):
        import importlib,py_compile,shutil,subprocess,sys
        from scripts.s54_bootstrap import capture_registration,CapturedSourceFinder,install_byte_binding
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);(root/'sim').mkdir();(root/'scripts').mkdir()
            sources=['sim/opportunities.py','scripts/s54_bootstrap.py','scripts/s54_launch.py','s54_loader_fixture.py']
            (root/'sim/opportunities.py').write_text('SOURCES = '+repr(sources)+'\n')
            shutil.copyfile('scripts/s54_bootstrap.py',root/'scripts/s54_bootstrap.py')
            (root/'scripts/s54_launch.py').write_text('import s54_loader_fixture\nassert s54_loader_fixture.VALUE == "captured"\nprint("captured launch executed")\n')
            toy=root/'s54_loader_fixture.py';toy.write_text('VALUE = "captured"\n')
            subprocess.run(['git','init','-q','-b','main',str(root)],check=True)
            subprocess.run(['git','add','.'],cwd=root,check=True)
            subprocess.run(['git','-c','user.name=Synthetic Fixture','-c','user.email=fixture@example.invalid','commit','-qm','Synthetic captured loader'],cwd=root,check=True)
            subprocess.run(['git','remote','add','origin',str(root)],cwd=root,check=True)
            # The actual stdlib bootstrap can bind and execute a fresh process;
            # this synthetic entry has no model calls or research side effects.
            launched=subprocess.run([sys.executable,'scripts/s54_bootstrap.py'],cwd=root,text=True,capture_output=True,check=True)
            self.assertEqual(launched.stdout.strip(),'captured launch executed')
            captured,binding=capture_registration(root)
            toy.write_text('VALUE = "wrong pyc"\n');py_compile.compile(str(toy),doraise=True)
            toy.write_text('raise AssertionError("changed disk executed")\n')
            finder=CapturedSourceFinder(root,captured);sys.meta_path.insert(0,finder)
            try:
                module=importlib.import_module('s54_loader_fixture')
                self.assertEqual(module.VALUE,'captured')
                self.assertEqual(module.__file__,str(toy))
                with self.assertRaisesRegex(ImportError,'Unregistered local scientific module'):
                    finder.find_spec('sim.unregistered')
            finally:
                sys.meta_path.remove(finder);sys.modules.pop('s54_loader_fixture',None)
            with self.assertRaisesRegex(RuntimeError,'differs from captured Git bytes'):capture_registration(root)
            # Imported scientific modules bypass loaders via sys.modules, so a
            # live bootstrap refuses this already-imported test process.
            with self.assertRaisesRegex(RuntimeError,'source context mismatch'):
                install_byte_binding(root,captured,dict(binding,sources={}))
            with self.assertRaisesRegex(RuntimeError,'loaded before byte binding'):install_byte_binding(root,captured,binding)

    def test_direct_live_entries_rejected_without_bootstrap(self):
        import runpy,sys
        with patch.object(sys,'_s54_bootstrap_context',None,create=True),patch('sim.resource_cache.llm.chat') as transport:
            with self.assertRaisesRegex(RuntimeError,'byte-bound entry'):runpy.run_path('scripts/s54_launch.py',run_name='__main__')
            with patch.object(sys,'argv',['sim.opportunities']):
                with self.assertRaisesRegex(RuntimeError,'byte-bound entry'):main()
            transport.assert_not_called()

    def test_alternating_calls_fail_overlap_gate(self):
        from scripts.s54_analyze import verify_transport_and_preflight
        from datetime import datetime,timedelta
        base=datetime.fromisoformat('2026-10-25T04:00:00+00:00');stamp=lambda seconds:(base+timedelta(seconds=seconds)).isoformat()
        def runtime(seconds):return dict(checked_utc=stamp(seconds),remaining_seconds=(datetime.fromisoformat(DEADLINE)-datetime.fromisoformat(stamp(seconds))).total_seconds(),required_seconds=100)
        launch=dict(observed_utc=stamp(-1),runtime_precheck=runtime(-2));dispatch=dict(observed_utc=stamp(1),runtime_precheck=runtime(.5));events=[dict(utc=stamp(0))];requests=[dict(admitted_utc=stamp(2))]
        games=[dict(ground_truth=dict(seed=seed,condition=condition,call_provenance=[dict(call_started_utc=stamp(s),call_completed_utc=stamp(e)) for s,e in ([(3,4),(6,7)] if condition=='alternating' else [(4,5),(7,8)])])) for seed in SEEDS for condition in ['alternating','synchronized']]
        with self.assertRaisesRegex(AssertionError,'call intervals'):verify_transport_and_preflight(games,requests,launch,dispatch,events)
        for g in games:
            if g['ground_truth']['condition']=='synchronized':g['ground_truth']['call_provenance'][0]['call_started_utc']=stamp(3.5)
        verify_transport_and_preflight(games,requests,launch,dispatch,events)

if __name__=='__main__':unittest.main()
