"""Regression for reviewer-confirmed worker-to-collector abort gap."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from sim.delay import DelayCache,parse_action
from scripts.s11_safe_run import guarded_call


class Tests(unittest.TestCase):
    def test_terminal_failure_aborts_before_collector(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            cache=DelayCache(Path(td)/'responses.jsonl',True)
            # Keep actual deadline/abort guard, replace only inherited transport.
            def fake(self,system,user,tier,backend,run_id,t,agent,attempt,model):
                return dict(text='{}',model='dry',backend='dry')
            with patch('sim.common.Cache.call',fake):
                # Cache dry adapter requires a JSON object, but schema remains invalid.
                with self.assertRaisesRegex(RuntimeError,'invalid after three attempts'):
                    guarded_call(cache,'s','u','test',0,'A','gpt-6-luna','codex',parse_action,[])
                self.assertTrue(cache.abort.is_set())
                with self.assertRaisesRegex(RuntimeError,'Terminal failure'):
                    cache.call('s','u','cheap','codex','partner',0,'B',0,'gpt-6-luna')

    def test_route_failure_aborts(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
            cache=DelayCache(Path(td)/'responses.jsonl',False)
            response=dict(text=json.dumps(dict(quantity=6,reasoning='',private_message='')),model='wrong',backend='codex')
            with patch('sim.common.llm.chat',return_value=response),patch('sim.delay.now',return_value='2026-10-24T18:00:00+00:00'):
                with self.assertRaisesRegex(RuntimeError,'mismatch'):
                    guarded_call(cache,'s','u','test',0,'A','gpt-6-luna','codex',parse_action,[])
            self.assertTrue(cache.abort.is_set())

if __name__=='__main__':unittest.main()
