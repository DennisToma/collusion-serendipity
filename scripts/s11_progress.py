"""Metadata-only S11 generation progress; never computes outcomes."""
from datetime import datetime,timezone
import json
from pathlib import Path


def complete_lines(path):
    if not path.exists():return []
    return [json.loads(line) for line in path.read_bytes().splitlines(keepends=True) if line.endswith(b'\n')]


def main():
    d=Path('data/s11_delay')
    requests=complete_lines(d/'raw/requests.jsonl');responses=complete_lines(d/'raw/responses.jsonl')
    result=dict(observed_utc=datetime.now(timezone.utc).isoformat(),complete_games=len(list(d.glob('game_*.json'))),
                failed_games=len(list(d.glob('failure_*.json'))),cached_responses=len(responses),
                audited_requests=len(requests),retry_requests=sum(r['payload'][8]>0 for r in requests),
                client_routes=sorted({(r['response'].get('model'),r['response'].get('backend')) for r in responses}))
    print(json.dumps(result),flush=True)
    with Path('logs/s11_runtime_checkpoints.jsonl').open('a') as handle:handle.write(json.dumps(result)+'\n')

if __name__=='__main__':main()
