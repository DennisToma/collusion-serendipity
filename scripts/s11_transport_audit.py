"""Supplementary synthetic checks prompted by methodology critics; no LLM calls."""
import contextlib
from datetime import datetime,timezone
import io
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.advisor import checked_call
from sim.delay import DelayCache,assert_cached_replay,parse_action,run_game


def main():
    obj=dict(quantity=6,reasoning='',private_message='')
    class WrongRoute:
        dry=False
        def call(self,*args):return dict(text=json.dumps(obj),model='wrong',backend='codex')
    try:checked_call(WrongRoute(),'s','u','test',0,'A','gpt-6-luna','codex',parse_action,[])
    except RuntimeError as exc:assert 'mismatch' in str(exc)
    else:raise AssertionError('Wrong route accepted')
    with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
        d=Path(td);cache=DelayCache(d/'raw/responses.jsonl',True)
        with contextlib.redirect_stdout(io.StringIO()):g=run_game(24110,'immediate',cache,'gpt-6-luna','codex')
        cache.call('extra','extra','cheap','codex','orphan',0,'A',0,'gpt-6-luna')
        try:assert_cached_replay(d,[g],dict(dry=True,model='gpt-6-luna',backend='codex'))
        except ValueError as exc:assert 'exactly once' in str(exc)
        else:raise AssertionError('Orphan request accepted')
    with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
        d=Path(td);cache=DelayCache(d/'responses.jsonl',False)
        response=dict(text=json.dumps(obj),model='gpt-6-luna',backend='codex')
        with patch('sim.delay.now',return_value='2026-10-24T18:00:00+00:00'),patch('sim.common.llm.chat',return_value=response):
            first=cache.call('s','u','cheap','codex','test',0,'A',0,'gpt-6-luna')
        before=[p.read_bytes() for p in [cache.path,cache.requests_path]]
        with patch('sim.delay.now',return_value='2099'),patch('sim.common.llm.chat',side_effect=AssertionError('Live call forbidden')):
            again=cache.call('s','u','cheap','codex','test',0,'A',0,'gpt-6-luna')
        assert first==again
        assert before==[p.read_bytes() for p in [cache.path,cache.requests_path]]
    output=dict(observed_utc=datetime.now(timezone.utc).isoformat(),kind='supplementary synthetic protocol audit; no scientific outcomes',
                route_mismatch_refused=True,valid_orphan_cache_key_refused=True,cached_request_after_deadline_allowed=True,
                cache_and_audit_unchanged=True,live_model_calls=0)
    Path('logs/s11_transport_audit.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))

if __name__=='__main__':main()
