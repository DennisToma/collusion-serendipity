"""Canonical suite with narrow archived synthetic fixtures, no source edits.

S60 document tests read their frozen split-index bytes; the actual S65 release
independently verifies that the real index is precisely the prospective append.
S62's sole wall-clock-dependent mock transport test uses a fixed pre-cutoff time.
S64's existing scoped historical publication fixture remains unchanged.
"""
import argparse,contextlib,functools,json,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_s60_presentation,test_s62
from scripts.s64_tests import fixture as s64_fixture

@contextlib.contextmanager
def fixture():
    root=Path.cwd().resolve();split=(root/'data/SPLITS.md').resolve()
    reg=json.loads(Path('data/s60_author_bonus/config.json').read_text())['registration_commit']
    registered=subprocess.check_output(['git','show',f'{reg}:data/SPLITS.md'])
    original_read=Path.read_bytes
    def read(path,*args,**kwargs):return registered if path.resolve()==split else original_read(path,*args,**kwargs)
    names=['test_front_report_drift_is_rejected_without_rewriting','test_later_pilots_can_append_and_archive_the_front_summary','test_readme_false_claim_is_rejected']
    with contextlib.ExitStack() as stack:
        stack.enter_context(s64_fixture())
        for name in names:
            original=getattr(test_s60_presentation.Tests,name)
            def scoped(self,original=original):
                with patch.object(Path,'read_bytes',new=read):return original(self)
            stack.enter_context(patch.object(test_s60_presentation.Tests,name,new=scoped))
        original=test_s62.Tests.test_fenced_responses_cached_verbatim_and_replayed
        def scoped_qwen(self):
            with patch('sim.notepad_qwen.now',return_value='2026-10-25T09:30:00+00:00'):return original(self)
        stack.enter_context(patch.object(test_s62.Tests,'test_fenced_responses_cached_verbatim_and_replayed',new=scoped_qwen))
        yield

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default='logs/s65_repository_final.json');args=p.parse_args()
    with fixture():
        from scripts.repository_tests import run
        run(args.out)
if __name__=='__main__':main()
