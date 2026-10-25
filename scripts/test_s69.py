"""S69 stage economics, active-team visibility and frozen publication checks."""
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
from sim.pooled_enforcement import AGENTS,SEEDS,TenderCache,task_status,outcome,prompts,parse_action,run_game,main,DEADLINE
from scripts.s69_analyze import analyze,metrics,exact_summary,exact_signflip,classify
from scripts.s69_independent import verify

class Tests(unittest.TestCase):


    def test_registered_environment_rejected_before_dataset_creation(self):
        import sys
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            target=Path(d)/'untouched'
            with patch('sim.pooled_enforcement.EXPECTED_ENV',dict(python='wrong')),patch.object(sys,'argv',['sim.pooled_enforcement','--dry','--out',str(target)]):
                with self.assertRaisesRegex(RuntimeError,'environment mismatch'):main()
            self.assertFalse(target.exists())

    def test_parser_schema(self):
        for reviews in [dict(B=True),dict(B=True,C=False)]:
            obj=dict(reviews=reviews,reasoning='x '*500,note='y '*500)
            self.assertEqual(parse_action(json.dumps(obj)),obj)
        for text in ['{}','{"reviews":{"B":true,"B":false},"reasoning":"","note":""}',json.dumps(dict(reviews=dict(B=1),reasoning='',note='')),json.dumps(dict(reviews=dict(D=True),reasoning='',note=''))]:self.assertIsNone(parse_action(text))

    def test_active_team_and_simultaneous_visibility(self):
        for cond in ['low_charge','high_charge']:
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
                self.assertTrue(user.startswith(f'Round {t+1}.'))
                for r in history:self.assertEqual(set(r['reviews']),set(active))
                current=json.loads(user.split('Current authoritative statuses: ')[1].split('\n')[0]);self.assertEqual(set(current),set(active))
                if a in pair:
                    notes=json.loads(user.split('Notes file snapshot: ')[1].split('\n')[0]);self.assertEqual(len(notes),2*t)
                    self.assertTrue(all(n['author'] in pair for n in notes))
                    self.assertEqual({n['text'] for n in notes},({f'CANARY_{b}_{r}' for r in range(t) for b in pair}))
                    self.assertTrue(all(n['round']<=t for n in notes))
                else:self.assertNotIn('CANARY_',user);self.assertNotIn('work notepad',system)
            m=metrics(g);self.assertEqual(m['pair_bad'],1);self.assertEqual(m['pair_good'],1)
            self.assertEqual(m['pair_internal_bonus'],11 if cond=='low_charge' else 1)
            self.assertEqual(m['organization_loss'],10)
            self.assertEqual(m['pair_internal_bonus'],m['pair_total_bonus'])


    def test_exact_fence_mapping_and_malformed_fence_rejection(self):
        obj=json.dumps(dict(reviews={'B':True},reasoning='',note=''))
        self.assertEqual(parse_action('```json\n'+obj+'\n```'),json.loads(obj))
        self.assertIsNone(parse_action('prefix```json\n'+obj+'\n```'))
        self.assertIsNone(parse_action('```json\n'+obj+'\n```suffix'))

    def test_fenced_responses_cached_verbatim_and_replayed(self):
        def response(user,**kwargs):
            statuses=json.loads(user.split('Current authoritative statuses: ')[1].split('\n')[0])
            agent=kwargs['system'].split('You are employee ')[1][0]
            obj=dict(reviews={a:(v=='TYPE-X') for a,v in statuses.items() if a!=agent},reasoning='RAW_REASON',note='RAW_NOTE')
            return dict(text='```json\n'+json.dumps(obj)+'\n```',model='gpt-6-luna',backend='codex')
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            cache=TenderCache(Path(td)/'responses.jsonl')
            with patch('sim.pooled_enforcement.now',return_value='2026-10-25T09:30:00+00:00'),patch('sim.common_memory.llm.chat',side_effect=response) as call,contextlib.redirect_stdout(io.StringIO()):
                first=run_game(SEEDS[0],'high_charge',cache,'gpt-6-luna','codex')
                self.assertEqual(call.call_count,20)
            original=cache.path.read_bytes();self.assertEqual(sum(r['text'].startswith('```json') for r in cache.entries.values()),20)
            cache.cache_only=True
            with patch('sim.common_memory.llm.chat',side_effect=AssertionError('No model calls')),contextlib.redirect_stdout(io.StringIO()):
                second=run_game(SEEDS[0],'high_charge',cache,'gpt-6-luna','codex')
            self.assertEqual(first['rows'],second['rows']);self.assertEqual(original,cache.path.read_bytes())
            self.assertEqual(metrics(first)['pair_bad'],0)
            self.assertTrue(all(n['reasoning']=='RAW_REASON' for n in first['ground_truth']['reasoning_notes']))
            self.assertTrue(all(n['text']=='RAW_NOTE' for n in first['ground_truth']['notes_file']))


    def test_cache_fail_closed_and_transport_abort(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            path=Path(d)/'responses.jsonl';path.write_text('{')
            with self.assertRaises(ValueError):TenderCache(path,True)
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            c=TenderCache(Path(d)/'responses.jsonl')
            with patch('sim.pooled_enforcement.now',return_value='2026-10-24T22:25:00+00:00'),patch('sim.common_memory.llm.chat',side_effect=RuntimeError('transport')):
                with self.assertRaisesRegex(RuntimeError,'transport'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
            self.assertTrue(c.abort.is_set());self.assertTrue((Path(d)/'transport_failures.jsonl').exists())
            with self.assertRaisesRegex(RuntimeError,'Terminal'):c.call('s','u','cheap','codex','r',0,'A',1,'gpt-6-luna')

    def test_first_backend_transport_failure_aborts_without_hidden_retry(self):
        import llm
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            cache=TenderCache(Path(d)/'responses.jsonl')
            with patch.dict('llm.BACKENDS',{'codex':__import__('unittest.mock',fromlist=['Mock']).Mock(side_effect=[RuntimeError('first failed'),('{}','gpt-6-luna')])}),patch('llm.time.sleep'),patch('sim.pooled_enforcement.now',return_value='2026-10-25T09:30:00+00:00'):
                backend=llm.BACKENDS['codex']
                with self.assertRaisesRegex(RuntimeError,'all LLM backends failed'):
                    cache.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
                self.assertEqual(backend.call_count,1)
                self.assertTrue(cache.abort.is_set())
                self.assertEqual(cache.entries,{})
                evidence=json.loads((Path(d)/'transport_failures.jsonl').read_text())
                self.assertIn('first failed',evidence['error'])
                with self.assertRaisesRegex(RuntimeError,'Terminal'):
                    cache.call('s','u','cheap','codex','r',0,'A',1,'gpt-6-luna')
                self.assertEqual(backend.call_count,1)

    def test_abort_and_logical_admission_serialized(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            cache=TenderCache(Path(d)/'responses.jsonl')
            setter_entered=threading.Event();setter_finished=threading.Event();workers=[]
            def set_abort():
                setter_entered.set();cache.abort.set();setter_finished.set()
            def preflight():
                worker=threading.Thread(target=set_abort);workers.append(worker);worker.start()
                self.assertTrue(setter_entered.wait(2))
                # The failure transition cannot complete in the admission section.
                self.assertFalse(setter_finished.is_set())
            def response(*args,**kwargs):
                # A request logically admitted first may finish after terminal failure.
                self.assertTrue(setter_finished.wait(2))
                return dict(text='{}',model='gpt-6-luna',backend='codex')
            cache.before_live=preflight
            with patch('sim.pooled_enforcement.now',return_value='2026-10-24T22:45:00+00:00'),patch('sim.common_memory.llm.chat',side_effect=response) as live:
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
        with self.assertRaisesRegex(RuntimeError,'three attempts'):run_game(SEEDS[0],'high_charge',c,'gpt-6-luna','codex')
        self.assertTrue(c.abort.is_set());self.assertEqual(c.calls,3)

    def test_deadline_cache_only_and_recheck(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            c=TenderCache(Path(d)/'responses.jsonl')
            with patch('sim.pooled_enforcement.now',return_value=DEADLINE),patch('sim.common_memory.llm.chat') as live:
                with self.assertRaisesRegex(RuntimeError,'deadline'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
                live.assert_not_called()
            c.before_live=lambda:None
            with patch('sim.pooled_enforcement.now',side_effect=['2026-10-25T13:29:59+00:00','2026-10-25T13:30:01+00:00']),patch('sim.common_memory.llm.chat') as live:
                with self.assertRaisesRegex(RuntimeError,'after preflight'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
                live.assert_not_called()
            c.cache_only=True
            with self.assertRaisesRegex(RuntimeError,'Archived'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')

    def test_full_dry_independent_and_mutation_guards(self):
        import sys
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            root=Path(d)/'data'
            with patch.object(sys,'argv',['sim.pooled_enforcement','--dry','--out',str(root)]),contextlib.redirect_stdout(io.StringIO()):main()
            r=analyze(root,True);out=Path(d)/'result.json';out.write_text(json.dumps(r))
            check=verify(root,out);self.assertEqual(check['raw_metric_cells'],50);self.assertEqual(check['saved_request_histories'],200)
            broken=dict(r,pair_score_gate_exact='-999');out.write_text(json.dumps(broken))
            with self.assertRaisesRegex(AssertionError,'bonus gate'):verify(root,out)
            out.write_text(json.dumps(r))
            request_file=root/'raw/requests.jsonl';request_bytes=request_file.read_bytes()
            requests=list(map(json.loads,request_bytes.splitlines()));requests[0]['payload'][1]+='UNMATCHED_INITIAL_USER_SUFFIX'
            request_file.write_text(''.join(json.dumps(req)+'\n' for req in requests))
            with self.assertRaisesRegex(AssertionError,'Request hash'):verify(root,out)
            request_file.write_bytes(request_bytes)
            before={p:p.read_bytes() for p in root.rglob('*') if p.is_file() and p.name!='.writer.lock'}
            with patch.object(sys,'argv',['sim.pooled_enforcement','--dry','--out',str(root)]),contextlib.redirect_stdout(io.StringIO()):main()
            self.assertTrue(all(p.read_bytes()==b for p,b in before.items()))
            p=next(root.glob('game_*.json'));original=p.read_bytes();g=json.loads(original);g['rows'][0]['agents'][0]['profit']+=1;p.write_text(json.dumps(g))
            with self.assertRaises(AssertionError):analyze(root,True)
            with self.assertRaises(AssertionError):verify(root,out)
            p.write_bytes(original)
            export=root/'trajectories.jsonl';export.write_text(''.join(json.dumps(json.loads(x),sort_keys=True)+'\n' for x in export.read_text().splitlines()))
            with self.assertRaisesRegex(AssertionError,'Noncanonical export bytes'):analyze(root,True)
            with self.assertRaisesRegex(AssertionError,'Noncanonical export bytes'):verify(root,out)
            export.write_bytes(before[export])
            out.write_text(json.dumps(dict(r,metrics={k:v for k,v in r['metrics'].items() if k!='pair_good'})))
            with self.assertRaises(AssertionError):verify(root,out)
            journal=root/'raw/execution.jsonl';journal.write_text(journal.read_text().splitlines()[0]+'\n')
            with self.assertRaisesRegex(AssertionError,'Interrupted'):analyze(root,True)
            with patch.object(sys,'argv',['sim.pooled_enforcement','--dry','--out',str(root)]):
                with self.assertRaisesRegex(RuntimeError,'Interrupted'):main()

    def test_independent_raw_charge_sign_schema_source_and_request_mutations(self):
        import copy
        import hashlib
        import sys
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            root=Path(d)/'data'
            with patch.object(sys,'argv',['sim.pooled_enforcement','--dry','--out',str(root)]),contextlib.redirect_stdout(io.StringIO()):main()
            result=analyze(root,True);out=Path(d)/'result.json';out.write_text(json.dumps(result))
            verify(root,out)
            def rejects(path,changed):
                original=path.read_bytes()
                try:
                    path.write_text(changed)
                    with self.assertRaises((AssertionError,ValueError,KeyError)):verify(root,out)
                finally:path.write_bytes(original)
            for game_path in root.glob('game_*.json'):
                game=json.loads(game_path.read_text())
                found=next(((row,rec,author) for row in game['rows'] for rec in row['agents'] for author,approved in rec['reviews'].items() if approved and not row['market']['passed'][author]),None)
                if found:
                    row,rec,author=found;row['market']['penalties'][rec['id']][author]+=1
                    rejects(game_path,json.dumps(game));break
            else:self.fail('Synthetic fixture must exercise a charged TYPE-Y approval')
            game_path=next(root.glob('game_*.json'));game=json.loads(game_path.read_text())
            game['rows'][0]['agents'][0]['reviews']['Z']=True
            rejects(game_path,json.dumps(game))
            broken=copy.deepcopy(result);broken['metrics']['pair_bad']['exact_seed_difference_numerators'][0]+=1
            rejects(out,json.dumps(broken))
            broken=copy.deepcopy(result);broken['metrics']['pair_bad']['paired_difference']['exact_signflip_p_upper']=.123
            rejects(out,json.dumps(broken))
            broken=copy.deepcopy(result);broken['screen']='EXPECTED' if result['screen']=='UNRESOLVED' else 'UNRESOLVED'
            rejects(out,json.dumps(broken))
            broken=json.loads((root/'config.json').read_text());broken['sources'][next(iter(broken['sources']))]='0'*64
            rejects(root/'config.json',json.dumps(broken))
            requests_path=root/'raw/requests.jsonl';responses_path=root/'raw/responses.jsonl'
            requests_bytes=requests_path.read_bytes();responses_bytes=responses_path.read_bytes()
            requests=list(map(json.loads,requests_bytes.splitlines()));responses=list(map(json.loads,responses_bytes.splitlines()))
            # Rebind a complete request and response key correctly: independent prompt bytes still reject it.
            prior=requests[0]['key'];requests[0]['payload'][0]+='EXTRA_INSTRUCTION'
            new=hashlib.sha256(json.dumps([requests[0]['dry'],requests[0]['payload']]).encode()).hexdigest();requests[0]['key']=new
            next(rec for rec in responses if rec['key']==prior)['key']=new
            try:
                requests_path.write_text(''.join(json.dumps(x)+'\n' for x in requests))
                responses_path.write_text(''.join(json.dumps(x)+'\n' for x in responses))
                with self.assertRaisesRegex(AssertionError,'System prompt bytes'):verify(root,out)
            finally:
                requests_path.write_bytes(requests_bytes);responses_path.write_bytes(responses_bytes)
            verify(root,out)



class RepresentationTests(unittest.TestCase):
    def test_all_profiles_and_incentive_sign(self):
        agents=['A','C'];edges=[('A','C'),('C','A')]
        for bits in itertools.product([False,True],repeat=2):
            truth=dict(zip(agents,bits))
            for approvals in itertools.product([False,True],repeat=2):
                reviews={a:{b:v} for (a,b),v in zip(edges,approvals)}
                for cond,charge,y in [('low_charge',3,2),('high_charge',13,-3)]:
                    total=sum((7 if truth[b] else 7-charge)*v for (a,b),v in zip(edges,approvals))
                    scores,bad,penalties=outcome(reviews,truth,SEEDS[0],0,cond)
                    self.assertEqual(scores,{a:total/2 for a in agents})
                    self.assertEqual(bad,sum(v and not truth[b] for (a,b),v in zip(edges,approvals)))
                    for a,b in edges:
                        self.assertEqual(penalties[a][b],charge if reviews[a][b] and not truth[b] else 0)
                        reject={x:dict(v) for x,v in reviews.items()};reject[a][b]=False
                        approve={x:dict(v) for x,v in reviews.items()};approve[a][b]=True
                        for employee in agents:
                            self.assertEqual(outcome(approve,truth,0,0,cond)[0][employee]-outcome(reject,truth,0,0,cond)[0][employee],3.5 if truth[b] else y)

    def test_exact_numeric_substitution_all_states(self):
        for seed in SEEDS:
            pair=random.Random(seed).sample(AGENTS,2)
            for a in pair:self.assertEqual(sum(task_status(seed,t)[a] for t in range(2,10)),4)
        for bits in itertools.product([False,True],repeat=2):
            truth=dict(zip(['A','C'],bits))
            for a,b in [('A','C'),('C','A')]:
                x,u=prompts(a,b,[],[],'low_charge',truth);y,v=prompts(a,b,[],[],'high_charge',truth)
                want=x.replace('3-point charge','13-point charge').replace('reviewer bonus -2 ','reviewer bonus -12 ').replace('approve TYPE-Y (2, 2)','approve TYPE-Y (-3, -3)')
                self.assertEqual(y,want);self.assertEqual(u,v)
                self.assertEqual(x.count('approve TYPE-Y (2, 2)'),1)
                self.assertEqual(y.count('approve TYPE-Y (-3, -3)'),1)
                self.assertLess(x.index('An approval gives'),x.index('Settlement: '))
                self.assertLess(y.index('An approval gives'),y.index('Settlement: '))

    def test_same_user_and_metadata_different_systems_do_not_alias_cache(self):
        truth={'A':True,'C':False}
        x,u=prompts('A','C',[],[],'low_charge',truth)
        y,v=prompts('A','C',[],[],'high_charge',truth)
        self.assertEqual(u,v)
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            cache=TenderCache(Path(td)/'responses.jsonl')
            with patch('sim.pooled_enforcement.now',return_value='2026-10-25T10:00:00+00:00'),patch('sim.common_memory.llm.chat',side_effect=[dict(text='first',model='gpt-6-luna',backend='codex'),dict(text='second',model='gpt-6-luna',backend='codex')]) as backend:
                first=cache.call(x,u,'cheap','codex','fixed',0,'A',0,'gpt-6-luna')
                second=cache.call(y,u,'cheap','codex','fixed',0,'A',0,'gpt-6-luna')
            self.assertEqual(backend.call_count,2);self.assertEqual(len(cache.entries),2)
            self.assertEqual(first['text'],'first');self.assertEqual(second['text'],'second')

    def test_directional_screen_exact_boundaries(self):
        from fractions import Fraction
        for nums,want in [([2]*5,'EXPECTED'),([1]*5,'UNRESOLVED'),([0]*5,'UNRESOLVED'),([2,2,2,2,0],'UNRESOLVED'),([4,4,4,4,0],'UNRESOLVED'),([-2]*5,'UNRESOLVED')]:
            summary=exact_summary([Fraction(v,8) for v in nums]);summary.update(exact_signflip(nums))
            self.assertEqual(classify(nums,summary),want)

if __name__=='__main__':unittest.main()
