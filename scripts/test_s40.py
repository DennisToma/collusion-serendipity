"""Integrity, parser, intervention, failure and inference checks for S40."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import s40_replay as s


class Protocol(unittest.TestCase):
    def test_selection_and_only_note_difference(self):
        cases=s.select_cases()['cases'];self.assertEqual(len(cases),10)
        for c in cases:
            a=s.request(c,'retain');b=s.request(c,'erase')
            self.assertEqual(a['system'],b['system']);self.assertEqual(a['prompt'],c['original_prompt'])
            prefix,tail=a['prompt'].split('\nNotes file snapshot: ')
            notes,ending=tail.split('\nReturn strict JSON only')
            self.assertEqual(len(json.loads(notes)),9)
            self.assertEqual(b['prompt'],prefix+'\nNotes file snapshot: []\nReturn strict JSON only'+ending)
            self.assertEqual(s.strict(json.dumps(dict(rate=10,reasoning='',note='')),c)['rate'],10)

    def test_reject_invalid_outputs(self):
        for raw in ['{"rate":true,"reasoning":"","note":""}',
                    '{"rate":9,"reasoning":"","note":""}',
                    '{"rate":31,"reasoning":"","note":""}',
                    '{"rate":10.0,"reasoning":"","note":""}',
                    '{"rate":10,"rate":11,"reasoning":"","note":""}',
                    '{"rate":10,"reasoning":null,"note":""}',
                    '{"rate":10,"reasoning":"","note":{},"other":1}',
                    '```json\n{"rate":10,"reasoning":"","note":""}\n```']:
            with self.subTest(raw=raw),self.assertRaises((ValueError,TypeError)):s.strict(raw,None)

    def test_screen_and_degenerate_bounds(self):
        zero=s.summary([0]*5);self.assertEqual(zero['ci95'],[0,0]);self.assertEqual(zero['upper_signflip_p'],1)
        self.assertEqual(s.classify(zero),'DUD')
        self.assertEqual(s.classify(s.summary([2]*5)),'HIT')
        self.assertEqual(s.classify(s.summary([0,3,3,3,3])),'ODD')
        self.assertEqual(s.classify(s.summary([-4]*5)),'DUD')
        self.assertEqual(s.classify(s.summary([1]*5)),'DUD')

    def test_full_dry_and_mutations(self):
        from scripts.s40_independent import verify
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td)/'archive';s.run(p,dry=True)
            result=s.analyze(p,True);out=Path(td)/'result.json';s.write(out,result)
            self.assertTrue(verify(p,out)['passed'])
            for bad in [[],result['cases'][:-1],list(reversed(result['cases']))]:
                altered=copy.deepcopy(result);altered['cases']=bad;s.write(out,altered)
                with self.assertRaises(AssertionError):verify(p,out)
            s.write(out,result)
            with patch('scripts.s40_replay.chat',side_effect=AssertionError('No live calls')):s.run(p,dry=True)
            with self.assertRaises(AssertionError):s.validate(p)
            response=(p/'responses.jsonl').read_bytes()
            for mutate in ['duplicate','torn','model','prompt','rate','clock','request_hash','runtime']:
                with self.subTest(mutate=mutate):
                    rows=list(map(json.loads,response.splitlines()))
                    if mutate=='duplicate':rows.append(copy.deepcopy(rows[0]))
                    elif mutate=='model':rows[0]['response']['model']='wrong'
                    elif mutate=='prompt':rows[0]['request']['prompt']+=' changed'
                    elif mutate=='rate':rows[0]['response']['text']='{"rate":20,"reasoning":"","note":""}'
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
                elif filename=='cases.json':obj['cases'][0]['archived_quote']+=1
                else:obj['sources']['llm.py']='wrong'
                s.write(p/filename,obj)
                with self.assertRaises(AssertionError):s.validate(p,True)
                (p/filename).write_bytes(data)
            with patch('scripts.s40_replay.chat',side_effect=AssertionError('Never live')):
                self.assertEqual(s.analyze(p,True),result)

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

    def test_incomplete_never_resumes(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td);(p/'requests.jsonl').write_text('{}\n')
            with patch('scripts.s40_replay.chat',side_effect=AssertionError('Never live')),self.assertRaises(AssertionError):s.run(p,True)

    def test_dry_cannot_overwrite_live(self):
        with self.assertRaises(ValueError):s.run(s.ROOT/'data/s40_memory',True)

    def test_malformed_response_aborts_without_retry(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            p=Path(td)
            # Force dry generation to create a deliberately malformed synthetic response.
            original=s.strict
            with patch('scripts.s40_replay.strict',side_effect=lambda text,c: original(text,c) if c is None else (_ for _ in ()).throw(ValueError('synthetic malformed'))):
                with self.assertRaises(ValueError):s.run(p,True)
            self.assertEqual(json.loads((p/'execution.jsonl').read_text().splitlines()[-1])['event'],'failure')
            self.assertLessEqual(len((p/'responses.jsonl').read_text().splitlines()),2)
            with self.assertRaises(AssertionError):s.analyze(p,True)

class LiveContract(unittest.TestCase):
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
            registered=dict(commit='syntheticcommit',remote='syntheticcommit',observed_utc=s.utc(),server_time_attested=False,source_sha256={p:s.digest(s.ROOT/p) for p in s.SOURCES},cases_sha256=s.digest(s.ROOT/'data/s40_cases.json'))
            response=dict(backend='codex',model='gpt-6-luna',text='{"rate":10,"reasoning":"synthetic","note":"synthetic"}')
            with patch.object(s,'LIVE_RECEIPT',receipt),patch.object(s,'registration',return_value=registered),patch('scripts.s37_runtime.launch_observation',return_value={'fingerprint':{},'version':'synthetic'}),patch.object(s,'chat',return_value=response) as chat,patch.object(s.subprocess,'check_output',side_effect=git_output),patch.object(s.subprocess,'run',return_value=subprocess.CompletedProcess([],0)):
                s.run(directory);self.assertEqual(chat.call_count,20)
                result=s.analyze(directory);self.assertFalse(result['dry']);self.assertEqual(result['verdict'],'DUD')
                s.run(directory);self.assertEqual(chat.call_count,20)
                # External receipt survives removal of the disposable archive.
                import shutil
                shutil.rmtree(directory)
                with self.assertRaises(FileExistsError):s.run(directory)
                self.assertEqual(chat.call_count,20)

    @patch.object(s,'utc',return_value='2026-10-25T03:11:00+00:00')
    def test_lost_launch_headroom_has_durable_failure(self,clock):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);registered=dict(commit='synthetic',remote='synthetic',observed_utc=s.utc(),source_sha256={p:s.digest(s.ROOT/p) for p in s.SOURCES},cases_sha256=s.digest(s.ROOT/'data/s40_cases.json'))
            with patch.object(s,'LIVE_RECEIPT',root/'launch.json'),patch.object(s,'registration',return_value=registered),patch('scripts.s37_runtime.launch_observation',return_value={'fingerprint':{},'version':'synthetic'}),patch.object(s,'chat') as chat:
                with self.assertRaises(AssertionError):s.run(root/'archive')
                self.assertEqual(chat.call_count,0)
            self.assertTrue((root/'archive/failure.json').exists())
            self.assertTrue((root/'launch.json').exists())

    @patch.object(s,'utc',return_value='2026-10-25T02:40:00+00:00')
    def test_registered_source_mismatch_stops_before_calls(self,clock):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);sources={p:s.digest(s.ROOT/p) for p in s.SOURCES};sources['llm.py']='wrong'
            registered=dict(commit='synthetic',remote='synthetic',observed_utc=s.utc(),source_sha256=sources,cases_sha256=s.digest(s.ROOT/'data/s40_cases.json'))
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
                return {'fingerprint':{'version':'baseline' if count<=2 else 'drift'},'version':'synthetic'}
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            root=Path(td);directory=root/'archive';registered=dict(commit='synthetic',remote='synthetic',observed_utc=s.utc(),source_sha256={p:s.digest(s.ROOT/p) for p in s.SOURCES},cases_sha256=s.digest(s.ROOT/'data/s40_cases.json'))
            response=dict(backend='codex',model='gpt-6-luna',text='{"rate":10,"reasoning":"synthetic","note":"synthetic"}')
            with patch.object(s,'LIVE_RECEIPT',root/'launch.json'),patch.object(s,'registration',return_value=registered),patch('scripts.s37_runtime.launch_observation',side_effect=observation),patch.object(s,'chat',return_value=response) as chat:
                with self.assertRaises(AssertionError):s.run(directory)
                self.assertLessEqual(chat.call_count,1)
            events=[__import__('json').loads(x) for x in (directory/'execution.jsonl').read_text().splitlines()]
            self.assertEqual(events[-1]['event'],'failure')
            self.assertTrue((root/'launch.json').is_file())


if __name__=='__main__':unittest.main()
