"""Run the two S65 presentation fixtures against the pre-S65 registration tree.

Only synthetic dry generation within the two named tests observes the original
registration HEAD. Actual archive analysis, publication and live checks are never
patched. This prevents later results commits being used as a pre-pilot baseline.
"""
import argparse,contextlib,json,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_s65,test_s65_publication

@contextlib.contextmanager
def fixture():
    cfg=Path('data/s65_bonus_pooling/config.json')
    reg=json.loads(cfg.read_text())['registration_commit'] if cfg.exists() else subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    real=subprocess.check_output
    def output(cmd,*args,**kwargs):
        if cmd==['git','rev-parse','HEAD']:return (reg+'\n') if kwargs.get('text') else (reg+'\n').encode()
        return real(cmd,*args,**kwargs)
    specs=[(test_s65.PoolingTests,'test_isolated_presentation_idempotent_and_preserves_older_rows'),
           (test_s65_publication.Tests,'test_pilot_table_is_contiguous_and_corrected_render_is_idempotent')]
    with contextlib.ExitStack() as stack:
        for cls,name in specs:
            original=getattr(cls,name)
            def scoped(self,original=original):
                with patch('subprocess.check_output',side_effect=output):return original(self)
            stack.enter_context(patch.object(cls,name,new=scoped))
        yield

def main():
    with fixture():
        suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(m) for m in [test_s65,test_s65_publication])
        result=unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():raise SystemExit(1)
if __name__=='__main__':main()
