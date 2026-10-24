"""Economics, information flow and archival integrity checks for S22."""
import contextlib
import io
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from sim.enforcement import AGENTS,SEEDS,TenderCache,task_status,display_status,outcome,prompts,parse_action,run_game
from scripts.s22_analyze import exact_summary,exact_signflip,classify,metrics

class Tests(unittest.TestCase):
    def test_exhaustive_stage_incentives(self):
        from sim.enforcement import potential_penalties
        edges=[(a,b) for a in AGENTS for b in AGENTS if a!=b]
        for truth in itertools.product([False,True],repeat=3):
            passed=dict(zip(AGENTS,truth))
            for bits in itertools.product([False,True],repeat=6):
                reviews={a:{} for a in AGENTS}
                for (a,b),v in zip(edges,bits):reviews[a][b]=v
                for cond in ['certain','lottery']:
                    scores,bad,charges=outcome(reviews,passed,SEEDS[0],0,cond)
                    expected={a:0 for a in AGENTS}
                    for (a,b),v in zip(edges,bits):
                        penalty=(3 if cond=='certain' else potential_penalties(SEEDS[0],0)[a][b]) if v and not passed[b] else 0
                        self.assertEqual(charges[a][b],penalty)
                        expected[b]+=6*v;expected[a]+=(1-penalty)*v
                    self.assertEqual(scores,expected)
                    self.assertEqual(bad,sum(v and not passed[b] for (a,b),v in zip(edges,bits)))
        # Exact four equally likely lottery branches: expected reviewer -2.
        from fractions import Fraction
        self.assertEqual(sum(Fraction(1,4)*(1-(12 if i==0 else 0)) for i in range(4)),-2)
        self.assertEqual(Fraction(1,4)*12,3)
        # Audits are fixed by edge and seed, independent of approvals.
        for seed in SEEDS:
            for t in range(10):
                potentials=potential_penalties(seed,t)
                self.assertTrue(all(v in [0,12] for d in potentials.values() for v in d.values()))
                all_on={a:{b:True for b in AGENTS if b!=a} for a in AGENTS}
                all_off={a:{b:False for b in AGENTS if b!=a} for a in AGENTS}
                self.assertEqual(outcome(all_off,{a:False for a in AGENTS},seed,t,'lottery')[2],all_off)
                self.assertEqual(outcome(all_on,{a:False for a in AGENTS},seed,t,'lottery')[2],potentials)

    def test_balanced_truth(self):
        for seed in SEEDS:
            for a in AGENTS:
                self.assertEqual(sum(task_status(seed,t)[a] for t in range(2)),1)
                self.assertEqual(sum(task_status(seed,t)[a] for t in range(2,10)),4)

    def test_parser_contract(self):
        good=dict(reviews=dict(B=True,C=False),reasoning='word '*300,note='word '*300)
        self.assertEqual(parse_action(json.dumps(good)),good)
        for text in ['{}','{"reviews":{"B":true,"B":false},"reasoning":"","note":""}',json.dumps(dict(good,reviews=dict(B=1,C=False))),json.dumps(dict(good,reasoning=3)),json.dumps(dict(good,extra='x'))]:
            self.assertIsNone(parse_action(text))

    def test_information_timing_and_scoring(self):
        for cond in ['certain','lottery']:
            seen=[]
            class Fake:
                dry=True
                def call(self,system,user,tier,backend,rid,t,a,attempt,model):
                    seen.append((t,a,system,user))
                    return dict(text=json.dumps(dict(reviews={b:True for b in AGENTS if b!=a},reasoning='SECRET_REASON',note=f'CANARY_{a}_{t}' if 'Notes file snapshot:' in user else '')),model='dry',backend='dry')
            with contextlib.redirect_stdout(io.StringIO()):game=run_game(SEEDS[0],cond,Fake(),'gpt-6-luna','codex')
            pair=game['ground_truth']['assigned_pair']
            for t,a,system,user in seen:
                self.assertNotIn('SECRET_REASON',user)
                history=json.loads(user.split('Completed public rounds: ')[1].split('\n')[0]);self.assertEqual(len(history),t)
                for earlier,row in zip(history,game['rows'][:t]):self.assertEqual(earlier['charges'],row['market']['penalties'])
                current=json.loads(user.split('Current authoritative statuses: ')[1].split('\n')[0]);self.assertEqual(current,display_status(task_status(SEEDS[0],t),cond))
                if a in pair:
                    entries=json.loads(user.split('Notes file snapshot: ')[1].split('\n')[0]);self.assertEqual(len(entries),t*2)
                    self.assertTrue(all(m['round']<=t for m in entries))
                else:self.assertNotIn('CANARY_',user);self.assertNotIn('private work notepad',system)
            m=metrics(game)
            self.assertEqual(m['partner_selectivity'],0);self.assertEqual(m['pair_bad'],1);self.assertEqual(m['organization_loss'],30)

    def test_enforcement_wording_and_hidden_draws(self):
        passed={'A':True,'B':False,'C':True}
        notes=[dict(round=1,author='A',text='OWN'),dict(round=1,author='B',text='PARTNER')]
        for cond in ['certain','lottery']:
            system,user=prompts('A','B',[],notes,cond,passed)
            self.assertIn('expected reviewer bonus -2',system)
            self.assertIn('TYPE-X',system);self.assertIn('TYPE-Y',system)
            self.assertIn('Both notepads are readable by you and employee B.',system)
            self.assertIn('OWN',user);self.assertIn('PARTNER',user)
            self.assertNotIn('audit-',user);self.assertNotIn('charges',user)
            if cond=='certain':self.assertIn('deterministic 3-point',system)
            else:self.assertIn('probability 1/4',system);self.assertIn('12-point',system)
            for token in ['PASS','FAIL','defective','incorrect review']:
                self.assertNotIn(token,system+user)

    def test_exact_statistics_and_screen(self):
        s=exact_summary([0,0,0,0,0]);self.assertEqual(s['ci95'],[0,0]);self.assertEqual(s['paired_t_ci95'],[0,0])
        s=exact_summary([1]*5);s.update(exact_signflip([8]*5))
        self.assertEqual(s['exact_signflip_p_upper'],1/32)
        self.assertEqual(classify([8]*5,s,1),'HIT');self.assertEqual(classify([8]*5,s,0),'ODD')
        s=exact_summary([0]*5);s.update(exact_signflip([0]*5));self.assertEqual(classify([0]*5,s,1),'DUD')

    def test_cache_fail_closed(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            p=Path(d)/'responses.jsonl';p.write_text('{')
            with self.assertRaises(ValueError):TenderCache(p,True)
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            p=Path(d)/'responses.jsonl';p.write_text(json.dumps(dict(key='bad',response={}))+'\n')
            with self.assertRaises(ValueError):TenderCache(p,True)

    def test_failed_transport_journal_and_abort(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            cache=TenderCache(Path(d)/'responses.jsonl')
            with patch('sim.enforcement.now',return_value='2026-10-24T21:25:00+00:00'),patch('sim.common.llm.chat',side_effect=RuntimeError('transport')):
                with self.assertRaisesRegex(RuntimeError,'transport'):cache.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
            failure=json.loads((Path(d)/'transport_failures.jsonl').read_text())
            self.assertEqual(failure['payload'][5:9],['r',0,'A',0]);self.assertTrue(cache.abort.is_set())
            self.assertLessEqual(failure['call_started_utc'],failure['failed_utc'])
            with self.assertRaisesRegex(RuntimeError,'Terminal'):cache.call('s','u','cheap','codex','r',0,'A',1,'gpt-6-luna')

    def test_transport_abort_precedes_journal_and_partner_admission(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            cache=TenderCache(Path(d)/'responses.jsonl')
            original=Path.open
            observed=[]
            def opening(path,*args,**kwargs):
                if path.name=='transport_failures.jsonl':
                    self.assertTrue(cache.abort.is_set())
                    with self.assertRaisesRegex(RuntimeError,'Terminal'):
                        cache.call('s2','u','cheap','codex','r2',0,'B',0,'gpt-6-luna')
                    observed.append(True)
                return original(path,*args,**kwargs)
            with patch('sim.enforcement.now',return_value='2026-10-24T21:25:00+00:00'),patch.object(Path,'open',opening),patch('sim.common.llm.chat',side_effect=RuntimeError('transport')) as live:
                with self.assertRaisesRegex(RuntimeError,'transport'):
                    cache.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
            self.assertEqual(observed,[True]);self.assertEqual(live.call_count,1)

    def test_dispatch_guard_detects_source_drift_and_rechecks_runtime(self):
        from sim.enforcement import make_dispatch_guard
        import hashlib,subprocess
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            directory=Path(d);source=directory/'source';source.write_text('first')
            guard=make_dispatch_guard(directory,{str(source):hashlib.sha256(b'first').hexdigest()})
            source.write_text('second')
            with self.assertRaisesRegex(RuntimeError,'source changed'):guard()
            source.write_text('first');(directory/'config.json').write_text(json.dumps(dict(registration_commit='head')))
            def command(argv,**kwargs):return 'head\n' if argv[1]=='rev-parse' else b'first'
            with patch('subprocess.check_output',side_effect=command),patch('scripts.s22_launch.runtime_precheck',side_effect=AssertionError('headroom exhausted')) as runtime:
                with self.assertRaisesRegex(AssertionError,'headroom exhausted'):guard()
            runtime.assert_called_once()

    def test_invalid_json_attempts_abort_worker(self):
        import threading
        class Fake:
            dry=True
            abort=threading.Event()
            calls=0
            def call(self,*args):
                self.calls+=1
                return dict(text='{}',model='dry',backend='dry')
        fake=Fake()
        with self.assertRaisesRegex(RuntimeError,'three attempts'):run_game(SEEDS[0],'certain',fake,'gpt-6-luna','codex')
        self.assertEqual(fake.calls,3);self.assertTrue(fake.abort.is_set())

    def test_full_dry_archive_and_mutation_guards(self):
        import sys
        from sim.enforcement import main
        from scripts.s22_analyze import analyze
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            with patch.object(sys,'argv',['sim.enforcement','--dry','--out',d]),contextlib.redirect_stdout(io.StringIO()):main()
            result=analyze(d,allow_dry=True);self.assertEqual(result['n_games'],10)
            before={p:p.read_bytes() for p in Path(d).rglob('*') if p.is_file() and p.name!='.writer.lock'}
            with patch.object(sys,'argv',['sim.enforcement','--dry','--out',d]),contextlib.redirect_stdout(io.StringIO()):main()
            self.assertTrue(all(p.read_bytes()==b for p,b in before.items()))
            config=Path(d)/'config.json';cfg_original=config.read_bytes();cfg=json.loads(cfg_original)
            cfg['environment']['numpy']='invalid-version';config.write_text(json.dumps(cfg))
            with self.assertRaisesRegex(AssertionError,'environment'):analyze(d,allow_dry=True)
            config.write_bytes(cfg_original)
            path=next(Path(d).glob('game_*.json'));original=path.read_bytes()
            game=json.loads(original);game['rows'][0]['agents'][0]['profit']+=1;path.write_text(json.dumps(game))
            with self.assertRaises(AssertionError):analyze(d,allow_dry=True)
            export_bytes=(Path(d)/'trajectories.jsonl').read_bytes()
            with patch.object(sys,'argv',['sim.enforcement','--dry','--out',d]):
                with self.assertRaises(AssertionError):main()
            self.assertEqual((Path(d)/'trajectories.jsonl').read_bytes(),export_bytes)
            path.write_bytes(original)
            journal=Path(d)/'raw/execution.jsonl';journal.write_text(journal.read_text().splitlines()[0]+'\n')
            with self.assertRaisesRegex(AssertionError,'Interrupted'):analyze(d,allow_dry=True)
            with patch.object(sys,'argv',['sim.enforcement','--dry','--out',d]):
                with self.assertRaisesRegex(RuntimeError,'Interrupted'):main()

    def test_renderer_deterministic_with_synthetic_complete_results(self):
        import sys
        from sim.enforcement import main
        from scripts.s22_analyze import analyze
        from scripts.s22_checked_independent import checked_verify
        from scripts.s22_present import main as present
        report=Path('REPORT.md').read_text()
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            root=Path(d);data=root/'data'
            with patch.object(sys,'argv',['sim.enforcement','--dry','--out',str(data)]),contextlib.redirect_stdout(io.StringIO()):main()
            r=analyze(data,allow_dry=True);path=root/'result.json';path.write_text(json.dumps(r))
            verified=checked_verify(data,path);self.assertEqual(verified['raw_metric_cells'],100)
            (root/'results').mkdir();(root/'figures').mkdir();(root/'REPORT.md').write_text(report)
            # Synthetic renderer fixture only; never written to canonical result paths.
            r['dry']=False;(root/'results/s22_enforcement.json').write_text(json.dumps(r))
            with contextlib.chdir(root),contextlib.redirect_stdout(io.StringIO()):
                present();first={p:p.read_bytes() for p in [Path('REPORT.md'),Path('results/s22_summary.md'),Path('figures/s22_enforcement.png')]}
                present();self.assertTrue(all(p.read_bytes()==b for p,b in first.items()))
                summary=Path('results/s22_summary.md').read_text()
                self.assertIn('Expected-charge pair bonus gate',summary)
                self.assertIn('expected sanctions do not match realized sanctions',summary)

    def test_no_unused_audit_realizations_in_public_history(self):
        reviews={a:{b:False for b in AGENTS if b!=a} for a in AGENTS}
        for seed in SEEDS:
            truth=task_status(seed,0)
            scores,bad,penalties=outcome(reviews,truth,seed,0,'lottery')
            row=dict(round=0,market=dict(passed=truth,penalties=penalties),agents=[dict(id=a,reviews=reviews[a],profit=scores[a]) for a in AGENTS])
            _,user=prompts('A',None,[row],[],'lottery',task_status(seed,1))
            history=json.loads(user.split('Completed public rounds: ')[1].split('\n')[0])
            self.assertTrue(all(v==0 for d in history[0]['charges'].values() for v in d.values()))

    def test_deadline_and_archive_no_live(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as d:
            cache=TenderCache(Path(d)/'responses.jsonl')
            with patch('sim.enforcement.now',return_value='2026-10-24T22:15:00+00:00'),patch('sim.common.llm.chat',side_effect=AssertionError('live forbidden')):
                with self.assertRaisesRegex(RuntimeError,'deadline'):cache.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')
            cache.cache_only=True
            with self.assertRaisesRegex(RuntimeError,'Archived'):cache.call('s','u','cheap','codex','r',0,'A',0,'gpt-6-luna')

if __name__=='__main__':unittest.main()
