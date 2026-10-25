"""S64 stage economics, active-team visibility and frozen publication checks."""
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
from sim.memory_retention import AGENTS,SEEDS,TenderCache,task_status,outcome,prompts,parse_action,run_game,main,DEADLINE
from scripts.s64_analyze import analyze,metrics,exact_summary,exact_signflip,classify
from scripts.s64_independent import verify

class Tests(unittest.TestCase):
    def test_exhaustive_economics(self):
        agents=['A','C'];edges=[('A','C'),('C','A')]
        for cond in ['reset','persistent']:
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
            pair=random.Random(seed).sample(AGENTS,2)
            for a in pair:
                self.assertEqual(sum(task_status(seed,t)[a] for t in range(2)),1)
                self.assertEqual(sum(task_status(seed,t)[a] for t in range(2,10)),4)
            for t in range(10):
                truth={a:v for a,v in task_status(seed,t).items() if a in pair}
                for approvals in itertools.product([False,True],repeat=2):
                    reviews={a:{b:v} for (a,b),v in zip([(pair[0],pair[1]),(pair[1],pair[0])],approvals)}
                    self.assertEqual(outcome(reviews,truth,seed,t,'reset'),outcome(reviews,truth,seed,t,'persistent'))

    def test_registered_environment_rejected_before_dataset_creation(self):
        import sys
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            target=Path(d)/'untouched'
            with patch('sim.memory_retention.EXPECTED_ENV',dict(python='wrong')),patch.object(sys,'argv',['sim.memory_retention','--dry','--out',str(target)]):
                with self.assertRaisesRegex(RuntimeError,'environment mismatch'):main()
            self.assertFalse(target.exists())

    def test_parser_schema(self):
        for reviews in [dict(B=True),dict(B=True,C=False)]:
            obj=dict(reviews=reviews,reasoning='x '*500,note='y '*500)
            self.assertEqual(parse_action(json.dumps(obj)),obj)
        for text in ['{}','{"reviews":{"B":true,"B":false},"reasoning":"","note":""}',json.dumps(dict(reviews=dict(B=1),reasoning='',note='')),json.dumps(dict(reviews=dict(D=True),reasoning='',note=''))]:self.assertIsNone(parse_action(text))

    def test_active_team_and_simultaneous_visibility(self):
        for cond in ['reset','persistent']:
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
                history=json.loads(user.split('Completed public rounds: ')[1].split('\n')[0]);self.assertEqual(len(history),t if cond=='persistent' else 0)
                self.assertTrue(user.startswith(f'Round {t+1}.'))
                for r in history:self.assertEqual(set(r['reviews']),set(active))
                current=json.loads(user.split('Current authoritative statuses: ')[1].split('\n')[0]);self.assertEqual(set(current),set(active))
                if a in pair:
                    notes=json.loads(user.split('Notes file snapshot: ')[1].split('\n')[0]);self.assertEqual(len(notes),(2*t if cond=='persistent' else 0))
                    self.assertTrue(all(n['author'] in pair for n in notes))
                    self.assertEqual({n['text'] for n in notes},({f'CANARY_{b}_{r}' for r in range(t) for b in pair} if cond=='persistent' else set()))
                    self.assertTrue(all(n['round']<=t for n in notes))
                else:self.assertNotIn('CANARY_',user);self.assertNotIn('work notepad',system)
            m=metrics(g);self.assertEqual(m['pair_bad'],1);self.assertEqual(m['pair_good'],1)
            self.assertEqual(m['pair_internal_bonus'],11)
            self.assertEqual(m['organization_loss'],10)
            self.assertEqual(m['pair_internal_bonus'],m['pair_total_bonus'])

    def test_identical_system_and_initial_request(self):
        for seed in SEEDS:
            pair=random.Random(seed).sample(AGENTS,2)
            truth={a:v for a,v in task_status(seed,0).items() if a in pair}
            for agent in pair:
                partner=next(a for a in pair if a!=agent)
                a,u=prompts(agent,partner,[],[],'reset',truth)
                b,v=prompts(agent,partner,[],[],'persistent',truth)
                self.assertEqual(a,b)
                self.assertEqual(u,v)
                self.assertNotIn('human employees',a);self.assertNotIn('AI agents',a)

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
            with patch('sim.memory_retention.now',return_value='2026-10-25T09:30:00+00:00'),patch('sim.common_memory.llm.chat',side_effect=response) as call,contextlib.redirect_stdout(io.StringIO()):
                first=run_game(SEEDS[0],'persistent',cache,'gpt-6-luna','codex')
                self.assertEqual(call.call_count,20)
            original=cache.path.read_bytes();self.assertEqual(sum(r['text'].startswith('```json') for r in cache.entries.values()),20)
            cache.cache_only=True
            with patch('sim.common_memory.llm.chat',side_effect=AssertionError('No model calls')),contextlib.redirect_stdout(io.StringIO()):
                second=run_game(SEEDS[0],'persistent',cache,'gpt-6-luna','codex')
            self.assertEqual(first['rows'],second['rows']);self.assertEqual(original,cache.path.read_bytes())
            self.assertEqual(metrics(first)['pair_bad'],0)
            self.assertTrue(all(n['reasoning']=='RAW_REASON' for n in first['ground_truth']['reasoning_notes']))
            self.assertTrue(all(n['text']=='RAW_NOTE' for n in first['ground_truth']['notes_file']))

    def test_exact_screen(self):
        s=exact_summary([0]*5);s.update(exact_signflip([0]*5));self.assertEqual(classify([0]*5,s,1),'DUD')
        self.assertEqual(s['ci95'],[0,0]);self.assertEqual(s['paired_t_ci95'],[0,0])
        s=exact_summary([1]*5);s.update(exact_signflip([8]*5));self.assertEqual(s['exact_signflip_p_upper'],1/32)
        self.assertEqual(classify([8]*5,s,1),'HIT');self.assertEqual(classify([8]*5,s,0),'ODD')

    def test_cache_fail_closed_and_transport_abort(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            path=Path(d)/'responses.jsonl';path.write_text('{')
            with self.assertRaises(ValueError):TenderCache(path,True)
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            c=TenderCache(Path(d)/'responses.jsonl')
            with patch('sim.memory_retention.now',return_value='2026-10-24T22:25:00+00:00'),patch('sim.common_memory.llm.chat',side_effect=RuntimeError('transport')):
                with self.assertRaisesRegex(RuntimeError,'transport'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
            self.assertTrue(c.abort.is_set());self.assertTrue((Path(d)/'transport_failures.jsonl').exists())
            with self.assertRaisesRegex(RuntimeError,'Terminal'):c.call('s','u','cheap','codex','r',0,'A',1,'gpt-6-luna')

    def test_first_backend_transport_failure_aborts_without_hidden_retry(self):
        import llm
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            cache=TenderCache(Path(d)/'responses.jsonl')
            with patch.dict('llm.BACKENDS',{'codex':__import__('unittest.mock',fromlist=['Mock']).Mock(side_effect=[RuntimeError('first failed'),('{}','gpt-6-luna')])}),patch('llm.time.sleep'),patch('sim.memory_retention.now',return_value='2026-10-25T09:30:00+00:00'):
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
            with patch('sim.memory_retention.now',return_value='2026-10-24T22:45:00+00:00'),patch('sim.common_memory.llm.chat',side_effect=response) as live:
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
        with self.assertRaisesRegex(RuntimeError,'three attempts'):run_game(SEEDS[0],'persistent',c,'gpt-6-luna','codex')
        self.assertTrue(c.abort.is_set());self.assertEqual(c.calls,3)

    def test_deadline_cache_only_and_recheck(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            c=TenderCache(Path(d)/'responses.jsonl')
            with patch('sim.memory_retention.now',return_value=DEADLINE),patch('sim.common_memory.llm.chat') as live:
                with self.assertRaisesRegex(RuntimeError,'deadline'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
                live.assert_not_called()
            c.before_live=lambda:None
            with patch('sim.memory_retention.now',side_effect=['2026-10-25T10:59:59+00:00','2026-10-25T11:00:01+00:00']),patch('sim.common_memory.llm.chat') as live:
                with self.assertRaisesRegex(RuntimeError,'after preflight'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
                live.assert_not_called()
            c.cache_only=True
            with self.assertRaisesRegex(RuntimeError,'Archived'):c.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')

    def test_full_dry_independent_and_mutation_guards(self):
        import sys
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            root=Path(d)/'data'
            with patch.object(sys,'argv',['sim.memory_retention','--dry','--out',str(root)]),contextlib.redirect_stdout(io.StringIO()):main()
            r=analyze(root,True);out=Path(d)/'result.json';out.write_text(json.dumps(r))
            check=verify(root,out);self.assertEqual(check['raw_metric_cells'],50);self.assertEqual(check['saved_request_histories'],200)
            before={p:p.read_bytes() for p in root.rglob('*') if p.is_file() and p.name!='.writer.lock'}
            with patch.object(sys,'argv',['sim.memory_retention','--dry','--out',str(root)]),contextlib.redirect_stdout(io.StringIO()):main()
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
            with patch.object(sys,'argv',['sim.memory_retention','--dry','--out',str(root)]):
                with self.assertRaisesRegex(RuntimeError,'Interrupted'):main()

    def test_published_claim_and_older_row_mutations_rejected(self):
        import sys
        from scripts.s64_publish import apply
        names=['REPORT.md','REPORT_DETAILS.md','HITS.md','README.md']
        baseline={name:Path(name).read_text() for name in names}
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            root=Path(d);data=root/'data/s64_memory_retention'
            with patch.object(sys,'argv',['sim.memory_retention','--dry','--out',str(data)]),contextlib.redirect_stdout(io.StringIO()):main()
            r=analyze(data,True);r['dry']=False
            (root/'results').mkdir();(root/'results/s64_memory_retention.json').write_text(json.dumps(r))
            def git_show(cmd,**kwargs):
                self.assertEqual(cmd[:2],['git','show'])
                return baseline[cmd[2].split(':',1)[1]]
            with contextlib.chdir(root),patch('scripts.s64_publish.subprocess.check_output',side_effect=git_show):
                receipt=apply();self.assertEqual(receipt['managed_blocks'],4);self.assertEqual(receipt['older_pilot_rows'],46)
                report=Path('REPORT.md');good=report.read_text()
                report.write_text(good.replace('TYPE-Y approvals with full memory','FABRICATED approvals with full memory'))
                with self.assertRaisesRegex(AssertionError,'prose mismatch'):apply(True)
                report.write_text(good.replace('| S01 · C, price digits','| BROKEN · C, price digits'))
                with self.assertRaisesRegex(AssertionError,'Older pilot row'):apply(True)
                report.write_text('S64 is a fabricated HIT.\n'+good)
                with self.assertRaisesRegex(AssertionError,'prose mismatch'):apply(True)
                report.write_text(good+'\n| S64 · F, contradiction | bogus | HIT |\n')
                with self.assertRaisesRegex(AssertionError,'Extra or missing'):apply(True)
                report.write_text(good);self.assertEqual(receipt,apply(True))

    def test_renderer_idempotent_synthetic(self):
        import sys
        from scripts.s64_present import main as present
        report=Path('REPORT.md').read_text()
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            root=Path(d);data=root/'data'
            with patch.object(sys,'argv',['sim.memory_retention','--dry','--out',str(data)]),contextlib.redirect_stdout(io.StringIO()):main()
            r=analyze(data,True);r['dry']=False
            (root/'results').mkdir();(root/'figures').mkdir();(root/'REPORT.md').write_text(report);(root/'results/s64_memory_retention.json').write_text(json.dumps(r))
            with contextlib.chdir(root),contextlib.redirect_stdout(io.StringIO()):
                present();before={p:p.read_bytes() for p in [Path('REPORT.md'),Path('results/s64_summary.md'),Path('figures/s64_memory.png')]}
                present();self.assertTrue(all(p.read_bytes()==b for p,b in before.items()))

if __name__=='__main__':unittest.main()
