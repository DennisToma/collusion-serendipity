"""Metadata-only S18 progress; never reads decisions, notes or treatment metrics."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    root=Path('data/s18_workplace');cfg=json.loads((root/'config.json').read_text())
    rows=[json.loads(line) for line in (root/'raw/responses.jsonl').read_text().splitlines()] if (root/'raw/responses.jsonl').exists() else []
    counts={}
    for r in rows:
        m=r['response'];route=(m['backend'],m['model']);counts[str(route)]=counts.get(str(route),0)+1
    stamp=datetime.now(timezone.utc).isoformat()
    record=dict(utc=stamp,completed_games=len(list(root.glob('game_*.json'))),cached_responses=len(rows),
                failure_markers=len(list(root.glob('failure_*.json'))),routes=counts)
    with Path('logs/s18_runtime_checkpoints.jsonl').open('a') as h:h.write(json.dumps(record)+'\n')
    for p,digest in cfg['sources'].items():
        assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest
        assert hashlib.sha256(subprocess.check_output(['git','show',f'{cfg["registration_commit"]}:{p}'])).hexdigest()==digest
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()
