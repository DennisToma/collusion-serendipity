"""Metadata-only S09 progress; no action or treatment-effect inspection."""
import json
from pathlib import Path
from datetime import datetime,timezone

d=Path('data/s09_replay');p=d/'raw/responses.jsonl'
lines=p.read_text().splitlines() if p.exists() else []
rows=[]
for line in lines:
    try:rows.append(json.loads(line))
    except json.JSONDecodeError:pass
print(json.dumps(dict(time_utc=datetime.now(timezone.utc).isoformat(),
                     complete_games=len(list(d.glob('game_*.json'))),cached_responses=len(rows),
                     failures=[p.name for p in d.glob('failure_*.json')],
                     model_backend_counts={str(k):sum((r['response']['model'],r['response']['backend'])==k for r in rows)
                                           for k in {(r['response']['model'],r['response']['backend']) for r in rows}}),indent=2))
