"""Record local registration/push observation immediately before first S14 calls."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.tender import SOURCES,main


def launch():
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],text=True).split()[0]
    assert head==remote
    subprocess.run(['git','diff','--exit-code','HEAD','--',*SOURCES],check=True)
    ct=subprocess.check_output(['git','show','-s','--format=%cI',head],text=True).strip()
    stamp=datetime.now(timezone.utc).isoformat();assert datetime.fromisoformat(ct)<=datetime.fromisoformat(stamp)
    path=Path('logs/s14_launch_preflight.json')
    assert not path.exists(),'No second live launch'
    assert not (Path('data/s14_tender')/'config.json').exists(),'No prior dataset'
    obj=dict(registration_commit=head,commit_time_client=ct,observed_remote_head=remote,observed_utc=stamp,
             server_time_attested=False,sources={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES})
    with path.open('x') as f:f.write(json.dumps(obj,indent=2)+'\n')
    print('S14 registration observed remotely at local UTC '+stamp,flush=True)
    sys.argv=['sim.tender'];main()

if __name__=='__main__':launch()
