"""Postfailure integrity regressions; no effects, new live calls, or raw archive edits."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from scripts.s16_failure_audit import audit


class Tests(unittest.TestCase):
    def test_canonical_failure_reproduces_and_never_calls_metric_or_model(self):
        expected=json.loads(Path('results/s16_failure.json').read_text())
        with patch('sim.common.llm.chat',side_effect=AssertionError('no model')),patch('scripts.s16_analyze.metrics',side_effect=AssertionError('no treatment metrics')):
            self.assertEqual(audit(),expected)
        self.assertFalse(expected['primary_estimated'])
        self.assertEqual(expected['responses'],expected['accepted_decisions']+expected['rejected_responses'])

    def test_rehashed_fatal_response_cannot_be_relabeled_valid(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            d=Path(td)/'data';shutil.copytree('data/s16_tender',d)
            reqpath=d/'raw/requests.jsonl';rawpath=d/'raw/responses.jsonl'
            requests=[json.loads(l) for l in reqpath.read_text().splitlines()]
            raw=[json.loads(l) for l in rawpath.read_text().splitlines()]
            target=next(r for r in requests if r['payload'][5:9]==['s16_24242_shared',2,'C',0])
            response=next(r['response'] for r in raw if r['key']==target['key'])
            obj=json.loads(response['text']);obj['reasoning']='valid';response['text']=json.dumps(obj)
            target['response_sha256']=hashlib.sha256(json.dumps(response,sort_keys=True).encode()).hexdigest()
            for path,rows in [(rawpath,raw),(reqpath,requests)]:path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
            with self.assertRaisesRegex(AssertionError,'Nonsequential'):audit(d)

    def test_duplicate_key_or_completed_journal_rejected(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            d=Path(td)/'data';shutil.copytree('data/s16_tender',d)
            raw=d/'raw/responses.jsonl';old=raw.read_bytes();raw.write_bytes(old+old.splitlines(keepends=True)[0])
            with self.assertRaises(AssertionError):audit(d)
            raw.write_bytes(old)
            journal=d/'raw/execution.jsonl'
            journal.write_text(journal.read_text()+json.dumps(dict(event='complete',utc='2026-10-24T20:00:00+00:00'))+'\n')
            with self.assertRaisesRegex(AssertionError,'interrupted journal'):audit(d)


if __name__=='__main__':unittest.main()
