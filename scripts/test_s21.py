"""S21 validity: source selection, visibility, strict outputs, exact queue boundaries."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts.s21_audit import select_cases,request,schedule,strict,run,validate,fixed_model,select_target
from scripts.s21_analyze import summary,verdict,analyze


class S21(unittest.TestCase):
    def test_selection(self):
        obj=select_cases();self.assertEqual(len(obj['cases']),10);self.assertEqual(sum(c['truth'] for c in obj['cases']),4)
        for seed in range(24320,24325):self.assertEqual(sum(c['seed']==seed for c in obj['cases']),2)
    def test_visibility(self):
        for case in select_cases()['cases']:
            for v in ['A','T','AT']:
                p=json.loads(request(case,v)['prompt']);self.assertEqual(p['reviewer'],case['reviewer'])
                self.assertEqual(p['target_author'],case['author']);self.assertEqual(p['author_status'],case['status'])
                self.assertEqual(set(p['employee_response']),{'A':{'reviews'},'T':{'reasoning'},'AT':{'reviews','reasoning'}}[v])
                self.assertNotIn('source_run',p);self.assertNotIn('truth',p)
    def test_parser(self):
        for value in [True,False,None]:self.assertIs(strict(json.dumps(dict(approved=value,explanation='x')))['approved'],value)
        for text in ['{"approved":true,"approved":false,"explanation":"x"}','{"approved":1,"explanation":"x"}',
                     '{"approved":true,"explanation":NaN}','{"approved":true,"explanation":"x","extra":0}']:
            with self.assertRaises(ValueError):strict(text)
    def test_exact(self):
        s=summary([Fraction(0),Fraction(1,2),0,0,Fraction(1,2)])
        self.assertEqual(s['mean_exact'],'1/5');self.assertEqual(s['upper_signflip_p'],.25)
        self.assertEqual(verdict(summary([0]*5)),'DUD');self.assertEqual(verdict(summary([Fraction(1,2)]*5)),'HIT')
    def test_schedule(self):
        cases=select_cases()['cases'];s=schedule(cases);self.assertEqual(s,schedule(cases));self.assertEqual(len(s),5)
        self.assertEqual(len({cid for b in s for cid,views in b}),10)
        self.assertTrue(all(set(v)=={'A','T','AT'} for b in s for cid,v in b))
    def test_dry_replay_guards(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            with patch('scripts.s21_audit.chat',side_effect=AssertionError('Unexpected call')):
                run(td,dry=True);r=analyze(td,True);self.assertEqual(r['verdict'],'DUD');run(td,dry=True)
            with self.assertRaises(AssertionError):analyze(td)
            f=Path(td)/'responses.jsonl';original=f.read_text();rows=[json.loads(s) for s in original.splitlines()]
            rows[0]['request']['prompt']='tampered';f.write_text('\n'.join(map(json.dumps,rows))+'\n')
            with self.assertRaises(AssertionError):validate(td,True)
            f.write_text(original)
            event=Path(td)/'execution.jsonl';event.write_text(event.read_text()+json.dumps(dict(event='failure',utc='x'))+'\n')
            with self.assertRaises(AssertionError):validate(td,True)
    def test_failed_output_is_archived_and_cannot_resume(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            with patch('scripts.s21_audit.strict',side_effect=ValueError('Synthetic malformed response')):
                with self.assertRaises(ValueError):run(td,dry=True)
            self.assertTrue((Path(td)/'requests.jsonl').read_text())
            self.assertTrue((Path(td)/'responses.jsonl').read_text())
            events=[json.loads(s)['event'] for s in (Path(td)/'execution.jsonl').read_text().splitlines()]
            self.assertEqual(events,['start','failure'])
            with self.assertRaises(AssertionError):run(td,dry=True)
    def test_canonical_dry_destination_blocked(self):
        with self.assertRaises(ValueError):run('data/s21_audit',dry=True)
    def test_manifest_and_raw_duplicate_guards(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            run(td,dry=True)
            f=Path(td)/'config.json';original=f.read_text();cfg=json.loads(original)
            cfg['sources']['scripts/s21_audit.py']='bad';f.write_text(json.dumps(cfg))
            with self.assertRaises(AssertionError):validate(td,True)
            f.write_text(original)
            raw=Path(td)/'responses.jsonl';raw.write_text(raw.read_text()+raw.read_text().splitlines()[0]+'\n')
            with self.assertRaises(AssertionError):validate(td,True)
    def test_no_fallback_subprocess(self):
        import llm
        import subprocess
        original=llm.CODEX_CHEAP
        with patch('llm.subprocess.run',side_effect=subprocess.CalledProcessError(1,['synthetic'])) as transport, patch('llm.time.sleep'):
            with fixed_model():
                with self.assertRaises(RuntimeError):llm.chat('synthetic',backend='codex',model='gpt-6.1-sol',tier='big',retries=1)
            self.assertEqual(transport.call_count,1)
            self.assertIn('gpt-6.1-sol',transport.call_args.args[0])
        self.assertEqual(llm.CODEX_CHEAP,original)
    def test_live_model_and_parse_failures(self):
        import scripts.s21_audit as audit
        for response in [dict(text='```json invalid```',backend='codex',model='gpt-6.1-sol'),
                         dict(text='{}',backend='codex',model='gpt-6-luna')]:
            with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
                receipt=Path(td)/'launch.json'
                with patch.object(audit,'registration',return_value=dict(commit='synthetic')), patch.object(audit,'LIVE_RECEIPT',receipt), patch.object(audit,'chat',return_value=response):
                    with self.assertRaises((ValueError,AssertionError)):run(td)
                self.assertTrue(receipt.exists())
                self.assertTrue((Path(td)/'requests.jsonl').read_text())
                self.assertTrue((Path(td)/'responses.jsonl').read_text())
                self.assertEqual(json.loads((Path(td)/'execution.jsonl').read_text().splitlines()[-1])['event'],'failure')
    def test_independent_rejects_incomplete_or_changed_mean(self):
        from scripts.s21_independent import check
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            run(td,dry=True);result=analyze(td,True);path=Path(td)/'result.json'
            for field in ['cases','mean']:
                changed=copy.deepcopy(result)
                if field=='cases':changed['cases']=[]
                else:changed['contrasts']['AT_minus_A_error']['mean']=.04
                path.write_text(json.dumps(changed))
                with self.assertRaises(AssertionError):check(td,path)
    def test_explanation_not_selection_feature(self):
        for path in Path('data/s19_labels').glob('game_*.json'):
            game=json.loads(path.read_text());changed=copy.deepcopy(game)
            for note in changed['ground_truth']['reasoning_notes']:note['reasoning']='unrelated replacement'
            self.assertEqual(select_target(game)[:4],select_target(changed)[:4])

if __name__=='__main__':unittest.main()
