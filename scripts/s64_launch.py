"""Record local registration/push observation immediately before first S64 calls."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.memory_retention import SOURCES,DEADLINE,main,check_environment
import fcntl
import numpy
import scipy


def runtime_precheck():
    check_environment()
    # Fixed operational headroom, not a calibrated runtime/power guarantee.
    remaining_seconds=(datetime.fromisoformat(DEADLINE)-datetime.now(timezone.utc)).total_seconds()
    assert remaining_seconds>=3600,'Require at least60minutes before admission cutoff'
    return dict(required_seconds=3600,remaining_seconds=remaining_seconds,passed=True,
                runtime_bound_attested=False)


def launch():
    # Check all static preconditions before consuming the one-shot receipt.
    subprocess.run(['git','ls-files','--error-unmatch',*SOURCES],check=True,capture_output=True)
    directory=Path('data/s64_memory_retention');directory.mkdir(parents=True,exist_ok=True)
    assert not (directory/'raw').exists() and not list(directory.glob('game_*.json'))
    with (directory/'.writer.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    runtime=runtime_precheck()
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],text=True).split()[0]
    assert head==remote
    subprocess.run(['git','diff','--exit-code','HEAD','--',*SOURCES],check=True)
    ct=subprocess.check_output(['git','show','-s','--format=%cI',head],text=True).strip()
    stamp=datetime.now(timezone.utc).isoformat();assert datetime.fromisoformat(ct)<=datetime.fromisoformat(stamp)
    path=Path('logs/s64_launch_preflight.json')
    assert not path.exists(),'No second live launch'
    assert not (Path('data/s64_memory_retention')/'config.json').exists(),'No prior dataset'
    obj=dict(registration_commit=head,commit_time_client=ct,observed_remote_head=remote,observed_utc=stamp,
             server_time_attested=False,runtime_precheck=runtime,sources={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES})
    with path.open('x') as f:f.write(json.dumps(obj,indent=2)+'\n')
    print('S64 registration observed remotely at local UTC '+stamp,flush=True)
    sys.argv=['sim.memory_retention'];main()

if __name__=='__main__':
    with Path('logs/.s64-launch.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        launch()
