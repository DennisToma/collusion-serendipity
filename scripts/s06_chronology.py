"""Local registration chronology and raw timestamp audit; no server-time claim."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    d=Path('data/s06_denomination');cfg=json.loads((d/'config.json').read_text())
    pre=json.loads(Path('logs/s06_launch_preflight.json').read_text())
    raw=[json.loads(l)['response'] for l in (d/'raw/responses.jsonl').read_text().splitlines()]
    assert not cfg['dry'] and pre['registration_commit']==cfg['registration_commit']==pre['observed_remote_sha']
    first=min(r['call_started_utc'] for r in raw)
    last=max(r['call_completed_utc'] for r in raw)
    assert pre['observed_utc']<first<=last
    epoch=subprocess.check_output(['git','show','-s','--format=%ct',cfg['registration_commit']],text=True).strip()
    assert datetime.fromtimestamp(int(epoch),timezone.utc)<=datetime.fromisoformat(pre['observed_utc'])
    assert pre['source_hashes']==cfg['sources']
    for path,digest in cfg['sources'].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
        original=subprocess.check_output(['git','show',f'{cfg["registration_commit"]}:{path}'])
        assert hashlib.sha256(original).hexdigest()==digest
    out=dict(observed_utc=datetime.now(timezone.utc).isoformat(),registration_commit=cfg['registration_commit'],
             remote_observation_utc=pre['observed_utc'],first_client_call_started_utc=first,
             last_client_call_completed_utc=last,remote_seen_before_first_call=True,
             source_hashes_unchanged=True,server_time_attested=False)
    Path('logs/s06_chronology.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
