"""S25 treatment isolation, output validity, raw order and failed-archive guards."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from scripts.s25_replay import select_cases,request,schedule,strict,run,validate,fixed_model
from scripts.s25_analyze import analyze
from scripts.s25_independent import check


class S25(unittest.TestCase):
    def setUp(self):
        # Synthetic archives only: a future in-memory cutoff keeps mocked/dry
        # regressions useful after the immutable scientific deadline expires.
        self.cutoff=patch('scripts.s25_replay.DEADLINE','2099-01-01T00:00:00+00:00')
        self.cutoff.start();self.addCleanup(self.cutoff.stop)

    def test_selection_source_requests(self):
        from scripts.s21_audit import select_cases as source
        selected=select_cases()['cases'];old=source()['cases']
        self.assertEqual([c['source_request_key'] for c in selected],[c['source_request_key'] for c in old])
        self.assertEqual(sum(c['truth'] for c in selected),4)
        for c in selected:self.assertIn(c['status'][c['author']],['FAIL','TYPE-Y'])
    def test_only_schema_field_order_changes(self):
        for c in select_cases()['cases']:
            a=request(c,'action_first');r=request(c,'reason_first')
            self.assertEqual(a['prompt'],c['original_prompt']+' Emit the top-level fields in the exact order shown.');self.assertEqual(a['system'],c['original_system']);self.assertEqual(r['system'],a['system'])
            self.assertEqual({k:v for k,v in a.items() if k!='prompt'},{k:v for k,v in r.items() if k!='prompt'})
            marker='Return strict JSON only with exactly these fields: '
            ap,asch=a['prompt'].split(marker);rp,rsch=r['prompt'].split(marker)
            self.assertEqual(ap,rp);self.assertEqual(ap,c['original_prompt'].split(marker)[0])
            a_schema,a_tail=asch.split('. Set each review to true');r_schema,r_tail=rsch.split('. Set each review to true')
            self.assertEqual(a_tail,r_tail)
            # Invalid JSON placeholders are normalized identically for structural comparison.
            aj=json.loads(a_schema.replace('<boolean>','true'));rj=json.loads(r_schema.replace('<boolean>','true'))
            self.assertEqual(aj,rj);self.assertEqual(list(aj),['reviews','reasoning','note']);self.assertEqual(list(rj),['reasoning','reviews','note'])
            self.assertEqual(a['model'],'gpt-6-luna');self.assertEqual(a['retries'],1)
    def test_parser_and_order_noncompliance(self):
        c=select_cases()['cases'][0];obj=dict(note='',reasoning='x',reviews=c['reviews'])
        self.assertEqual(list(strict(json.dumps(obj),c)),list(obj))
        bad=[dict(obj,reviews={}),dict(obj,note=1),dict(obj,extra=0),dict(obj,reviews={a:1 for a in c['reviews']})]
        for b in bad:
            with self.assertRaises(ValueError):strict(json.dumps(b),c)
        with self.assertRaises(ValueError):strict('{"reviews":{},"reviews":{},"reasoning":"","note":""}',c)
    def test_schedule(self):
        s=schedule(select_cases()['cases']);self.assertEqual(s,schedule(select_cases()['cases']))
        self.assertEqual(len(s),5);self.assertEqual(len({cid for b in s for cid,v in b}),10)
        self.assertTrue(all(set(v)=={'action_first','reason_first'} for b in s for cid,v in b))
    def test_full_dry_order_roundtrip_independent_and_readonly_resume(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            with patch('scripts.s25_replay.chat',side_effect=AssertionError('Unexpected call')):
                run(td,True);r=analyze(td,True);run(td,True)
            self.assertEqual(r['counts']['action_first']['order_compliant'],10)
            self.assertEqual(r['counts']['reason_first']['order_compliant'],10)
            self.assertEqual(r['contrasts']['approved']['mean'],0)
            f=Path(td)/'result.json';f.write_text(json.dumps(r));self.assertEqual(check(td,f)['summary_checks'],6)
            raw=Path(td)/'responses.jsonl';original=raw.read_text();rows=[json.loads(s) for s in original.splitlines()]
            rows[0]['request']['prompt']+=' tampered';raw.write_text('\n'.join(map(json.dumps,rows))+'\n')
            with self.assertRaises(AssertionError):check(td,f)
            raw.write_text(original)
            with self.assertRaises(AssertionError):analyze(td)
            for mutate in ['case','mean']:
                changed=copy.deepcopy(r)
                if mutate=='case':changed['cases']=[]
                else:changed['contrasts']['approved']['mean']=.1
                f.write_text(json.dumps(changed))
                with self.assertRaises(AssertionError):check(td,f)
    def test_archive_mutations_and_partial(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            run(td,True);f=Path(td)/'responses.jsonl';original=f.read_text()
            rows=[json.loads(s) for s in original.splitlines()];rows[0]['request']['prompt']='tampered'
            f.write_text('\n'.join(map(json.dumps,rows))+'\n')
            with self.assertRaises(AssertionError):validate(td,True)
            f.write_text(original+original.splitlines()[0]+'\n')
            with self.assertRaises(AssertionError):validate(td,True)
            f.write_text(original);cfg=Path(td)/'config.json';c=json.loads(cfg.read_text());c['sources']['llm.py']='bad';cfg.write_text(json.dumps(c))
            with self.assertRaises(AssertionError):validate(td,True)
    def test_failed_parse_archived_and_no_resume(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            with patch('scripts.s25_replay.strict',side_effect=ValueError('synthetic')):
                with self.assertRaises(ValueError):run(td,True)
            self.assertTrue((Path(td)/'responses.jsonl').read_text())
            self.assertEqual(json.loads((Path(td)/'execution.jsonl').read_text().splitlines()[-1])['event'],'failure')
            with self.assertRaises(AssertionError):run(td,True)
    def test_wrong_route_archived(self):
        import scripts.s25_replay as replay
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            receipt=Path(td)/'launch.json'
            with patch.object(replay,'registration',return_value=dict(commit='synthetic')),patch.object(replay,'LIVE_RECEIPT',receipt),patch.object(replay,'chat',return_value=dict(model='wrong',backend='codex',text='{}')):
                with self.assertRaises(AssertionError):run(td)
            self.assertTrue(receipt.exists());self.assertTrue((Path(td)/'responses.jsonl').read_text())
    def test_single_subprocess_no_fallback(self):
        import llm
        with patch('llm.subprocess.run',side_effect=subprocess.CalledProcessError(1,['synthetic'])) as transport,patch('llm.time.sleep'):
            with fixed_model():
                with self.assertRaises(RuntimeError):llm.chat('x',backend='codex',model='gpt-6-luna',tier='cheap',retries=1)
            self.assertEqual(transport.call_count,1)
    def test_data_and_case_drift_before_dispatch(self):
        import scripts.s25_replay as replay
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            run(td,True);cfg=json.loads((Path(td)/'config.json').read_text());cases=select_cases()
            real=replay.digest
            for target in ['data/s25_cases.json',next(iter(cases['source_sha256']))]:
                def changed(path):return 'bad' if Path(path)==replay.ROOT/target else real(path)
                with patch.object(replay,'digest',side_effect=changed):
                    with self.assertRaises(AssertionError):replay.check_inputs(cfg,cases)
    def test_mocked_live_publication_rejects_changed_result(self):
        import scripts.s25_replay as replay
        from scripts.s25_release import release
        from datetime import datetime,timezone
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            receipt=Path(td)/'launch.json';result_path=Path(td)/'result.json';archive=Path(td)/'archive'
            reg=dict(commit='synthetic',remote='synthetic',observed_utc=datetime.now(timezone.utc).isoformat())
            def respond(**req):
                schema=req['prompt'].split('Return strict JSON only with exactly these fields: ')[1].split('. Set each review to true')[0]
                obj=json.loads(schema.replace('<boolean>','true'))
                return dict(text=json.dumps(obj),backend='codex',model='gpt-6-luna')
            with patch.object(replay,'registration',return_value=reg),patch.object(replay,'LIVE_RECEIPT',receipt),patch.object(replay,'chat',side_effect=respond):
                with patch.object(replay.subprocess,'run'),patch.object(replay.subprocess,'check_output') as git:
                    git.side_effect=lambda cmd,**kwargs:Path(cmd[2].split(':',1)[1]).read_bytes()
                    run(archive);result=analyze(archive);result_path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
                    self.assertTrue(release(archive,result_path)['archive_unchanged'])
                    result['verdict']='HIT';result_path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
                    with self.assertRaises(AssertionError):release(archive,result_path)
    def test_canonical_dry_block(self):
        with self.assertRaises(ValueError):run('data/s25_order',True)

if __name__=='__main__':unittest.main()
