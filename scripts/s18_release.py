"""Full offline S18 archive reproduction; never permits live calls."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s18_analyze import analyze
from scripts.s18_independent import verify


def main():
    paths=list(Path('data/s18_workplace').rglob('*'))
    original={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file() and p.name!='.writer.lock'}
    with patch('sim.common.llm.chat',side_effect=AssertionError('Release forbids model calls')):
        with contextlib.redirect_stdout(io.StringIO()):result=analyze('data/s18_workplace')
        expected=json.dumps(result,indent=2)+'\n';assert expected==Path('results/s18_workplace.json').read_text()
        independent=verify('data/s18_workplace','results/s18_workplace.json')
        assert independent==json.loads(Path('logs/s18_independent.json').read_text())
        from sim.workplace import main as resume
        with patch.object(sys,'argv',['sim.workplace']),contextlib.redirect_stdout(io.StringIO()):resume()
    for p,digest in original.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest,p
    receipt=dict(passed=True,source_entries=len(result and json.loads(Path('data/s18_workplace/config.json').read_text())['sources']),
                 all_key_replay=True,canonical_result_byte_identical=True,cached_resume_byte_identical=True,
                 independent=independent,result_sha256=hashlib.sha256(expected.encode()).hexdigest())
    Path('logs/s18_release.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
