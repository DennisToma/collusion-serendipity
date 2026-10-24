"""Count/routing metadata only; never prints bids, texts or effect estimates."""
from datetime import datetime,timezone
import json
from pathlib import Path


def main():
    d=Path('data/s14_tender');p=d/'raw/responses.jsonl';responses=[]
    if p.exists():
        for line in p.read_bytes().splitlines(keepends=True):
            if not line.endswith(b'\n'):continue
            responses.append(json.loads(line))
    rec=dict(utc=datetime.now(timezone.utc).isoformat(),completed_games=len(list(d.glob('game_*.json'))),responses=len(responses),failures=len(list(d.glob('failure_*.json'))),
             routes=sorted({(r['response']['backend'],r['response']['model']) for r in responses}),
             last_completion=max([r['response'].get('call_completed_utc','') for r in responses],default=None))
    with Path('logs/s14_runtime_checkpoints.jsonl').open('a') as f:f.write(json.dumps(rec)+'\n')
    print(json.dumps(rec))

if __name__=='__main__':main()
