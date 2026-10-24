"""Operational metadata only: no quantities, profits, reasoning or effect peeking."""
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics


def complete_lines(path):
    if not path.exists():
        return []
    raw=path.read_bytes()
    lines=raw.splitlines(keepends=True)
    return [json.loads(line) for line in lines if line.endswith(b'\n')]


def main():
    directory=Path('data/s07_legality')
    responses=complete_lines(directory/'raw/responses.jsonl')
    requests=complete_lines(directory/'raw/requests.jsonl')
    times=[]
    for row in responses:
        response=row['response']
        times.append((datetime.fromisoformat(response['call_completed_utc'])-
                      datetime.fromisoformat(response['call_started_utc'])).total_seconds())
    out=dict(time_utc=datetime.now(timezone.utc).isoformat(),complete_games=len(list(directory.glob('game_*.json'))),
             cached_responses=len(responses),logged_requests=len(requests),
             invalid_output_retries=sum(r['payload'][8]>0 for r in requests),
             model_backend_counts={str(key):sum((r['response']['model'],r['response']['backend'])==key for r in responses)
                                   for key in sorted({(r['response']['model'],r['response']['backend']) for r in responses})},
             mean_call_seconds=statistics.mean(times) if times else None,max_call_seconds=max(times) if times else None)
    with Path('logs/s07_runtime_checkpoints.jsonl').open('a') as handle:
        handle.write(json.dumps(out)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':
    main()
