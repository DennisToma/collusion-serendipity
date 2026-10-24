"""Record local registration/push observation immediately before first S19 calls."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.labels import SOURCES,DEADLINE,main
import fcntl
import numpy
import scipy


def runtime_precheck():
    games=[json.loads(p.read_text()) for p in sorted(Path('data/s18_workplace').glob('game_*.json'))]
    assert len(games)==10
    durations=[]
    for seed in sorted({g['ground_truth']['seed'] for g in games}):
        block=[g['ground_truth'] for g in games if g['ground_truth']['seed']==seed]
        assert len(block)==2
        durations.append((max(datetime.fromisoformat(g['ended_utc']) for g in block)-min(datetime.fromisoformat(g['started_utc']) for g in block)).total_seconds())
    raw=Path('data/s18_workplace/raw/responses.jsonl')
    responses=[json.loads(line)['response'] for line in raw.read_text().splitlines()]
    assert all(r['model']=='gpt-6-luna' and r['backend']=='codex' for r in responses)
    required_seconds=1.5*5*max(durations)
    remaining_seconds=(datetime.fromisoformat(DEADLINE)-datetime.now(timezone.utc)).total_seconds()
    assert remaining_seconds>=required_seconds,'Insufficient historical runtime headroom'
    return dict(previous_block_seconds=durations,previous_response_count=len(responses),
                previous_responses_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
                previous_game_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path('data/s18_workplace').glob('game_*.json'))},
                required_seconds=required_seconds,remaining_seconds=remaining_seconds,
                model='gpt-6-luna',backend='codex',passed=True)


def launch():
    # Check all static preconditions before consuming the one-shot receipt.
    subprocess.run(['git','ls-files','--error-unmatch',*SOURCES],check=True,capture_output=True)
    directory=Path('data/s19_labels');directory.mkdir(parents=True,exist_ok=True)
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
    path=Path('logs/s19_launch_preflight.json')
    assert not path.exists(),'No second live launch'
    assert not (Path('data/s19_labels')/'config.json').exists(),'No prior dataset'
    obj=dict(registration_commit=head,commit_time_client=ct,observed_remote_head=remote,observed_utc=stamp,
             server_time_attested=False,runtime_precheck=runtime,sources={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES})
    with path.open('x') as f:f.write(json.dumps(obj,indent=2)+'\n')
    print('S19 registration observed remotely at local UTC '+stamp,flush=True)
    sys.argv=['sim.labels'];main()

if __name__=='__main__':launch()
