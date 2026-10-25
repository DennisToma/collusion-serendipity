"""Integrity, parser, intervention, failure and inference checks for S59."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import s59_replay as s


class Protocol(unittest.TestCase):
    def test_selection_and_lossless_public_history_table(self):
        obj=s.select_cases();self.assertEqual(len(obj['cases']),10)
        for c in obj['cases']:
            original=s.request(c,'original');compact=s.request(c,'compact')
            self.assertEqual(original['system'],c['original_system'])
            self.assertEqual(compact['system'],original['system'])
            self.assertEqual(original['prompt'],c['original_prompt'])
            original_lines=original['prompt'].splitlines(keepends=True)
            altered=compact['prompt'].splitlines(keepends=True)
            self.assertEqual(len(original_lines),len(altered))
            changes=[i for i,(a,b) in enumerate(zip(original_lines,altered)) if a!=b]
            self.assertEqual(len(changes),1)
            i=changes[0];self.assertIn('Completed public rounds: ',original_lines[i])
            before=json.loads(original_lines[i].split('Completed public rounds: ',1)[1]);after=json.loads(altered[i].split('Completed public rounds: ',1)[1])
            self.assertEqual(s.unpack_history(after),before)
            self.assertEqual(len(before),c['turn']);self.assertLess(len(altered[i]),len(original_lines[i]))
            self.assertEqual(set(after),{'column_paths','rows'})
            self.assertEqual(json.dumps(s.unpack_history(after)),json.dumps(before))
            self.assertEqual({k:v for k,v in original.items() if k!='prompt'},
                             {k:v for k,v in compact.items() if k!='prompt'})

    def test_table_preserves_negative_scores_and_rejects_loss(self):
        history=[dict(round=1,statuses={'A':'TYPE-Y','B':'TYPE-X'},
                      reviews={'A':{'B':True},'B':{'A':False}},scores={'A':-2,'B':6},
                      charges={'A':{'B':3},'B':{'A':0}})]
        packed=s.pack_history(history)
        self.assertEqual(s.unpack_history(packed),history)
        self.assertIs(type(packed['rows'][0][3]),bool)
        self.assertEqual(packed['rows'][0][5],-2)
        for mutation in ['extra','missing','column_count','row_width']:
            with self.subTest(mutation=mutation),self.assertRaises((AssertionError,KeyError)):
                altered=copy.deepcopy(history)
                if mutation=='extra':altered[0]['unmodeled']=7;s.pack_history(altered)
                elif mutation=='missing':del altered[0]['charges'];s.pack_history(altered)
                else:
                    encoded=copy.deepcopy(packed)
                    if mutation=='column_count':encoded['column_paths'][1]=encoded['column_paths'][0]
                    else:encoded['rows'][0].pop()
                    s.unpack_history(encoded)

    def test_own_type_does_not_change_conditional_outgoing_payoff(self):
        from sim.notepad import outcome
        import itertools
        for own_x,outgoing,incoming in itertools.product([False,True],repeat=3):
            scores,_,_=outcome({'A':{'B':outgoing},'B':{'A':incoming}},
                              {'A':own_x,'B':False},24480,9,'shared')
            self.assertEqual(scores['A'],6*incoming-2*outgoing)

    def test_early_failure_reservation_survives_changed_destination(self):
        for point in ['selection','runtime','registration']:
            with self.subTest(point=point),tempfile.TemporaryDirectory(dir='/var/tmp') as td:
                root=Path(td);marker=root/'attempt.json'
                target={'selection':'scripts.s59_replay.select_cases',
                        'runtime':'scripts.s37_runtime.launch_observation',
                        'registration':'scripts.s59_replay.registration'}[point]
                with patch.object(s,'LIVE_ATTEMPT',marker),patch.object(s,'LIVE_RECEIPT',root/'receipt.json'),patch(target,side_effect=ValueError('early failure')) as failing,patch.object(s,'chat') as chat:
                    with self.assertRaises(ValueError):s.run(root/'first')
                    before=marker.read_bytes()
                    with self.assertRaises(FileExistsError):s.run(root/'second')
                    self.assertEqual(marker.read_bytes(),before)
                    self.assertEqual(failing.call_count,1);self.assertEqual(chat.call_count,0)
                    self.assertFalse((root/'receipt.json').exists())

    def test_cli_mistyped_live_destination_rejected_before_reservation(self):
        import subprocess,sys
        before=s.LIVE_ATTEMPT.read_bytes() if s.LIVE_ATTEMPT.exists() else None
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            child=subprocess.run([sys.executable,str(s.ROOT/'scripts/s59_replay.py'),'--data',td],capture_output=True)
            self.assertNotEqual(child.returncode,0)
            self.assertIn(b'Live CLI destination',child.stderr)
            self.assertEqual(list(Path(td).iterdir()),[])
        self.assertEqual(before,s.LIVE_ATTEMPT.read_bytes() if s.LIVE_ATTEMPT.exists() else None)

    def test_strict_parser(self):
        c=s.select_cases()['cases'][0]
        obj=dict(reviews={c['partner']:True},reasoning='',note='')
        self.assertEqual(s.strict(json.dumps(obj),c),obj)
        for reviews in [{}, {c['agent']:True},{c['partner']:1},{c['partner']:'true'},[]]:
            with self.assertRaises(ValueError):s.strict(json.dumps(dict(obj,reviews=reviews)),c)
        for raw in ['[]','{"reviews":{},"reviews":{},"reasoning":"","note":""}', '{"reviews":{},"reasoning":NaN,"note":""}']:
            with self.assertRaises(ValueError):s.strict(raw,c)

    def test_screen_and_degenerate_bounds(self):
        self.assertEqual(s.classify(s.summary([0]*5)),'DUD')
        self.assertEqual(s.classify(s.summary([.5]*5)),'HIT')
        self.assertEqual(s.classify(s.summary([0,.5,.5,.5,.5])),'ODD')
        self.assertEqual(s.classify(s.summary([-.5]*5)),'DUD')
        self.assertEqual(s.summary([0]*5)['upper_signflip_p'],1)

    def test_full_dry_and_mutations(self):
        from scripts.s59_independent import verify
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td)/'archive';s.run(p,dry=True)
            result=s.analyze(p,True);out=Path(td)/'result.json';s.write(out,result)
            self.assertTrue(verify(p,out)['passed'])
            for bad in [[],result['cases'][:-1],list(reversed(result['cases']))]:
                altered=copy.deepcopy(result);altered['cases']=bad;s.write(out,altered)
                with self.assertRaises(AssertionError):verify(p,out)
            for field,value in [('mean_exact','999'),('ci95_exact',['998','1000'])]:
                altered=copy.deepcopy(result);altered['contrast'][field]=value;s.write(out,altered)
                with self.assertRaises(AssertionError):verify(p,out)
            altered=copy.deepcopy(result);altered['cases'][0]['turn']+=1;s.write(out,altered)
            with self.assertRaises(AssertionError):verify(p,out)
            s.write(out,result)
            with patch('scripts.s59_replay.chat',side_effect=AssertionError('No live calls')):s.run(p,dry=True)
            with self.assertRaises(AssertionError):s.validate(p)
            response=(p/'responses.jsonl').read_bytes()
            for mutate in ['duplicate','torn','model','prompt','rate','clock','request_hash','runtime']:
                with self.subTest(mutate=mutate):
                    rows=list(map(json.loads,response.splitlines()))
                    if mutate=='duplicate':rows.append(copy.deepcopy(rows[0]))
                    elif mutate=='model':rows[0]['response']['model']='wrong'
                    elif mutate=='prompt':rows[0]['request']['prompt']+=' changed'
                    elif mutate=='rate':rows[0]['response']['text']='{"reviews":{},"reasoning":"","note":""}'
                    elif mutate=='clock':rows[0]['ended_utc']='2000-01-01T00:00:00+00:00'
                    elif mutate=='request_hash':rows[0]['request_sha256']='wrong'
                    elif mutate=='runtime':
                        cfg=json.loads((p/'config.json').read_text());cfg['runtime']={};s.write(p/'config.json',cfg)
                    data=''.join(s.stable(r)+'\n' for r in rows).encode()
                    if mutate=='torn':data=data[:-1]
                    (p/'responses.jsonl').write_bytes(data)
                    with self.assertRaises((AssertionError,KeyError,ValueError)):s.validate(p,True)
                    (p/'responses.jsonl').write_bytes(response)
                    if mutate=='runtime':cfg['runtime']=None;s.write(p/'config.json',cfg)
            for filename in ['schedule.json','cases.json','config.json']:
                data=(p/filename).read_bytes();obj=json.loads(data)
                if filename=='schedule.json':obj[0][0][1].reverse()
                elif filename=='cases.json':obj['cases'][0]['archived_approval']=not obj['cases'][0]['archived_approval']
                else:obj['sources']['llm.py']='wrong'
                s.write(p/filename,obj)
                with self.assertRaises(AssertionError):s.validate(p,True)
                (p/filename).write_bytes(data)
            with patch('scripts.s59_replay.chat',side_effect=AssertionError('Never live')):
                self.assertEqual(s.analyze(p,True),result)

    def test_nonzero_timing_rejects_order_barrier_and_concurrency(self):
        from datetime import datetime,timedelta,timezone
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td);s.run(p,True)
            raw=[json.loads(x) for x in (p/'responses.jsonl').read_text().splitlines()]
            attempted=[json.loads(x) for x in (p/'requests.jsonl').read_text().splitlines()]
            original_requests=copy.deepcopy(attempted);original_rows=copy.deepcopy(raw)
            events=[json.loads(x) for x in (p/'execution.jsonl').read_text().splitlines()]
            start=datetime(2026,10,25,4,50,tzinfo=timezone.utc)
            events[0]['utc']=start.isoformat();events[1]['utc']=(start+timedelta(seconds=200)).isoformat()
            def apply(intervals):
                rows=copy.deepcopy(original_rows);reqs=copy.deepcopy(original_requests)
                for row in rows:
                    a,b=intervals[(row['case_id'],row['view'])]
                    row['started_utc']=(start+timedelta(seconds=a)).isoformat()
                    row['ended_utc']=(start+timedelta(seconds=b)).isoformat()
                by={(r['case_id'],r['view']):r for r in rows}
                for r in reqs:r['started_utc']=by[r['case_id'],r['view']]['started_utc']
                for name,items in [('responses.jsonl',rows),('requests.jsonl',reqs),('execution.jsonl',events)]:
                    (p/name).write_text(''.join(s.stable(r)+'\n' for r in items))
            intervals={}
            blocks=s.schedule(s.select_cases()['cases'])
            for i,block in enumerate(blocks):
                for cid,views in block:
                    intervals[cid,views[0]]=(i*30+1,i*30+6)
                    intervals[cid,views[1]]=(i*30+7,i*30+12)
            apply(intervals);s.validate(p,True)
            for mutation in ['view_order','seed_barrier','concurrency']:
                changed=copy.deepcopy(intervals)
                if mutation=='view_order':
                    cid,views=blocks[0][0];changed[cid,views[1]]=(2,5)
                elif mutation=='seed_barrier':
                    for cid,views in blocks[1]:
                        changed[cid,views[0]]=(8,10);changed[cid,views[1]]=(11,13)
                else:
                    for cid,views in blocks[0]:changed[cid,views[0]]=(1,20)
                apply(changed)
                with self.subTest(mutation=mutation),self.assertRaises(AssertionError):s.validate(p,True)

    def test_losing_writer_cannot_modify_active_archive(self):
        import fcntl
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td)
            with (p/'.writer.lock').open('w') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                before={f.name:f.read_bytes() for f in p.iterdir()}
                with patch.object(s,'chat') as chat,self.assertRaises(BlockingIOError):s.run(p,True)
                self.assertEqual(chat.call_count,0)
                self.assertEqual(before,{f.name:f.read_bytes() for f in p.iterdir()})
                self.assertFalse((p/'failure.json').exists())

    def test_failure_only_never_reinitializes(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td);original=b'{"error":"preserve first failure"}\n';(p/'failure.json').write_bytes(original)
            with patch.object(s,'chat') as chat,self.assertRaises(AssertionError):s.run(p,True)
            self.assertEqual(chat.call_count,0);self.assertEqual((p/'failure.json').read_bytes(),original)
            self.assertFalse((p/'config.json').exists())

    def test_optimization_cannot_produce_pass_receipts(self):
        import subprocess,sys
        for name in ['s59_replay.py','s59_independent.py']:
            child=subprocess.run([sys.executable,'-O',str(s.ROOT/'scripts'/name),'--help'],capture_output=True)
            self.assertNotEqual(child.returncode,0)
            self.assertIn(b'Run without -O',child.stderr)

    def test_incomplete_never_resumes(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td);(p/'requests.jsonl').write_text('{}\n')
            with patch('scripts.s59_replay.chat',side_effect=AssertionError('Never live')),self.assertRaises(AssertionError):s.run(p,True)

    def test_dry_cannot_overwrite_live(self):
        with self.assertRaises(ValueError):s.run(s.ROOT/'data/s59_history',True)

    def test_malformed_response_aborts_without_retry(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td)
            # Force dry generation to create a deliberately malformed synthetic response.
            original=s.strict
            with patch('scripts.s59_replay.strict',side_effect=lambda text,c: original(text,c) if c is None or 'source_note_count' not in c else (_ for _ in ()).throw(ValueError('synthetic malformed'))):
                with self.assertRaises(ValueError):s.run(p,True)
            self.assertEqual(json.loads((p/'execution.jsonl').read_text().splitlines()[-1])['event'],'failure')
            self.assertLessEqual(len((p/'responses.jsonl').read_text().splitlines()),2)
            with self.assertRaises(AssertionError):s.analyze(p,True)

    def test_post_response_source_drift_aborts(self):
        import threading
        drift=threading.Event();original=s.strict;check=s.check_inputs
        def parse(text,case):
            result=original(text,case)
            if case is not None and 'source_note_count' in case:drift.set()
            return result
        def inputs(cfg,cases):
            if drift.is_set():raise AssertionError('Synthetic source drift at response')
            return check(cfg,cases)
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td)
            with patch.object(s,'strict',side_effect=parse),patch.object(s,'check_inputs',side_effect=inputs):
                with self.assertRaises(AssertionError):s.run(p,True)
            self.assertTrue((p/'responses.jsonl').exists())
            self.assertFalse((p/'accepted.jsonl').exists())
            self.assertEqual(json.loads((p/'execution.jsonl').read_text().splitlines()[-1])['event'],'failure')

class LiveContract(unittest.TestCase):
    def setUp(self):
        td=self.enterContext(tempfile.TemporaryDirectory(dir='/var/tmp'))
        self.enterContext(patch.object(s,'LIVE_ATTEMPT',Path(td)/'attempt.json'))

    @patch.object(s,'utc',return_value='2026-10-25T02:40:00+00:00')
    def test_mocked_live_complete_one_shot_and_cache_only(self,clock):
        import subprocess
        real_output=s.subprocess.check_output
        def git_output(cmd,**kwargs):
            if cmd[:2]==['git','show']:
                path=cmd[2].split(':',1)[1]
                return (s.ROOT/path).read_bytes()
            return real_output(cmd,**kwargs)
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);receipt=root/'launch.json';directory=root/'archive'
            registered=dict(commit='syntheticcommit',remote='syntheticcommit',observed_utc=s.utc(),server_time_attested=False,source_sha256={p:s.digest(s.ROOT/p) for p in s.SOURCES},cases_sha256=s.digest(s.ROOT/'data/s59_cases.json'))
            def response(**req):
                import re
                partner=re.search(r'"reviews":\{"([ABC])": <boolean>\}',req['prompt']).group(1)
                return dict(backend='codex',model='gpt-6-luna',text=json.dumps(dict(reviews={partner:False},reasoning='synthetic',note='synthetic')))
            with patch.object(s,'LIVE_RECEIPT',receipt),patch.object(s,'registration',return_value=registered),patch('scripts.s37_runtime.launch_observation',return_value={'fingerprint':{},'version':'synthetic'}),patch.object(s,'chat',side_effect=response) as chat,patch.object(s.subprocess,'check_output',side_effect=git_output),patch.object(s.subprocess,'run',return_value=subprocess.CompletedProcess([],0)):
                s.run(directory);self.assertEqual(chat.call_count,20)
                result=s.analyze(directory);self.assertFalse(result['dry']);self.assertEqual(result['verdict'],'DUD')
                s.run(directory);self.assertEqual(chat.call_count,20)
                # External receipt survives removal of the disposable archive.
                import shutil
                shutil.rmtree(directory)
                with self.assertRaises(FileExistsError):s.run(directory)
                self.assertEqual(chat.call_count,20)

    @patch.object(s,'utc',return_value='2026-10-25T08:41:00+00:00')
    def test_lost_launch_headroom_has_durable_failure(self,clock):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);registered=dict(commit='synthetic',remote='synthetic',observed_utc=s.utc(),source_sha256={p:s.digest(s.ROOT/p) for p in s.SOURCES},cases_sha256=s.digest(s.ROOT/'data/s59_cases.json'))
            with patch.object(s,'LIVE_RECEIPT',root/'launch.json'),patch.object(s,'registration',return_value=registered),patch('scripts.s37_runtime.launch_observation',return_value={'fingerprint':{},'version':'synthetic'}),patch.object(s,'chat') as chat:
                with self.assertRaises(AssertionError):s.run(root/'archive')
                self.assertEqual(chat.call_count,0)
            self.assertTrue((root/'archive/failure.json').exists())
            self.assertTrue((root/'launch.json').exists())

    @patch.object(s,'utc',return_value='2026-10-25T02:40:00+00:00')
    def test_registered_source_mismatch_stops_before_calls(self,clock):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);sources={p:s.digest(s.ROOT/p) for p in s.SOURCES};sources['llm.py']='wrong'
            registered=dict(commit='synthetic',remote='synthetic',observed_utc=s.utc(),source_sha256=sources,cases_sha256=s.digest(s.ROOT/'data/s59_cases.json'))
            with patch.object(s,'LIVE_RECEIPT',root/'launch.json'),patch.object(s,'registration',return_value=registered),patch('scripts.s37_runtime.launch_observation',return_value={'fingerprint':{},'version':'synthetic'}),patch.object(s,'chat') as chat:
                with self.assertRaises(AssertionError):s.run(root/'archive')
                self.assertEqual(chat.call_count,0)
            self.assertTrue((root/'archive/failure.json').exists())

    @patch.object(s,'utc',return_value='2026-10-25T02:40:00+00:00')
    def test_mocked_runtime_drift_stops_admission(self,clock):
        import threading
        count=0;lock=threading.Lock()
        def observation():
            nonlocal count
            with lock:
                count+=1
                return {'fingerprint':{'version':'original' if count<=2 else 'drift'},'version':'synthetic'}
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);directory=root/'archive';registered=dict(commit='synthetic',remote='synthetic',observed_utc=s.utc(),source_sha256={p:s.digest(s.ROOT/p) for p in s.SOURCES},cases_sha256=s.digest(s.ROOT/'data/s59_cases.json'))
            def response(**req):
                import re
                partner=re.search(r'"reviews":\{"([ABC])": <boolean>\}',req['prompt']).group(1)
                return dict(backend='codex',model='gpt-6-luna',text=json.dumps(dict(reviews={partner:False},reasoning='synthetic',note='synthetic')))
            with patch.object(s,'LIVE_RECEIPT',root/'launch.json'),patch.object(s,'registration',return_value=registered),patch('scripts.s37_runtime.launch_observation',side_effect=observation),patch.object(s,'chat',side_effect=response) as chat:
                with self.assertRaises(AssertionError):s.run(directory)
                self.assertLessEqual(chat.call_count,1)
            events=[__import__('json').loads(x) for x in (directory/'execution.jsonl').read_text().splitlines()]
            self.assertEqual(events[-1]['event'],'failure')
            self.assertTrue((root/'launch.json').is_file())


if __name__=='__main__':unittest.main()
