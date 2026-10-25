"""Scoped post-publication runner; never edits frozen tests/scientific inputs.

Only S64's synthetic publication-mutation test reads the pre-S64 four documents
from registration Git bytes when initially capturing its fixture. All temporary
output reads and real archive release checks remain unpatched.
"""
import argparse,contextlib,functools,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_s64
from scripts.s64_publication_final import baseline,DOCUMENTS

@contextlib.contextmanager
def fixture():
    root=Path.cwd().resolve();registered={(root/n).resolve():baseline(n) for n in DOCUMENTS}
    original_read=Path.read_text;original=test_s64.Tests.test_published_claim_and_older_row_mutations_rejected
    def read(path,*args,**kwargs):
        resolved=path.resolve()
        return registered[resolved] if resolved in registered else original_read(path,*args,**kwargs)
    @functools.wraps(original)
    def scoped(self):
        with patch.object(Path,'read_text',new=read):return original(self)
    with patch.object(test_s64.Tests,'test_published_claim_and_older_row_mutations_rejected',new=scoped):yield

def main():
    p=argparse.ArgumentParser();p.add_argument('--canonical',action='store_true');p.add_argument('--out',default='logs/s64_scoped_tests.json');args=p.parse_args()
    with fixture():
        if args.canonical:
            from scripts.repository_tests import run
            run(args.out)
        else:
            result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromModule(test_s64))
            Path(args.out).write_text(json.dumps(dict(passed=result.wasSuccessful(),tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),fixture='One S64 synthetic publication fixture reads registration Git baseline; real archive/current documents unpatched'),indent=2)+'\n')
            if not result.wasSuccessful():raise SystemExit(1)
if __name__=='__main__':main()
