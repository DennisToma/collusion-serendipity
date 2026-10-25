"""Post-outcome cache validation closes probe-CLI/chronology coverage gaps.

Read-only; original frozen scientific sources and experimental outcomes unchanged.
Use this entry instead of rerunning the frozen probe CLI. All chronology is local
client evidence, not server attestation.
"""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s62_probe import validate_probe

if not __debug__:raise RuntimeError('Run integrity checks without -O')


def chronology(probe,commit,observed,execution):
    stamps=list(map(datetime.fromisoformat,[probe,commit,observed,execution]))
    assert stamps==sorted(stamps),'Probe must complete before registration and scientific execution'


def check():
    probe=validate_probe()
    cfg=json.loads(Path('data/s62_notepad_qwen/config.json').read_text())
    receipt=json.loads(Path('logs/s62_launch_preflight.json').read_text())
    events=[json.loads(s) for s in Path('data/s62_notepad_qwen/raw/execution.jsonl').read_text().splitlines()]
    commit_time=subprocess.check_output(['git','show','-s','--format=%cI',cfg['registration_commit']],text=True).strip()
    assert datetime.fromisoformat(commit_time)==datetime.fromisoformat(receipt['commit_time_client'])
    chronology(probe['completed_utc'],commit_time,receipt['observed_utc'],events[0]['utc'])
    digest=hashlib.sha256(Path('logs/s62_probe.json').read_bytes()).hexdigest()
    dispatch=json.loads(Path('data/s62_notepad_qwen/raw/dispatch_preflight.json').read_text())
    assert digest==receipt['runtime_precheck']['probe_sha256']==dispatch['runtime_precheck']['probe_sha256']
    for name,expected in cfg['sources'].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==expected,name
    result=dict(passed=True,source_unchanged=True,cached_probe_request_route_bool_validated=True,
                probe_before_registration_and_execution=True,chronology_attestation='Local client UTC/Git only',probe_sha256=digest)
    Path('logs/s62_probe_check.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':print(json.dumps(check(),indent=2))
