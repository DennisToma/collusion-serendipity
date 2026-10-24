"""Archive-only S11 resume with worker-side abort propagation; frozen sources preserved."""
from pathlib import Path
import sys
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim import delay

_ORIGINAL_CHECKED_CALL=delay.checked_call


def guarded_call(cache,*args,**kwargs):
    try:return _ORIGINAL_CHECKED_CALL(cache,*args,**kwargs)
    except BaseException:
        cache.abort.set()
        raise


def main():
    with patch.object(delay,'checked_call',guarded_call),patch('sim.common.llm.chat',side_effect=AssertionError('S11 archive wrapper forbids live calls')):
        delay.main()

if __name__=='__main__':main()
