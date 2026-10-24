# S09 matched private-transcript continuations

Five existing neutral S07 games supply fixed public histories and private chats
for rounds1–6. All five prefixes are used. Ten new continuations generate only
rounds7–12, pinned codex/gpt-6-luna, fresh CLI calls, two concurrent games.
`retain` receives prior transcripts; `erase` removes rounds1–6 received transcripts
from both pair members' prompts. New messages are delivered normally from round8.

`game_*.json` and `trajectories.jsonl` include duplicated source context rows0–5,
with the continuation run_id. These are NOT new observations or independent games.
Call provenance and private reasoning cover only new rows6–11. `private_chat` keeps
original source messages for forensic provenance even in the erase arm; reconstruct
actual prompt exposure using the erase filter in `sim/replay.py` or inspect the full
`raw/requests.jsonl`. Stored message slots include empty text and undelivered final
messages. No verified agreement/execution labels are supplied.

`config.json` binds every scientific source, prefix and independent checker to the
pushed registration commit4474418. Full response and request caches permit offline
replay without paid model calls; all183 response keys must be consumed exactly once.
Three invalid outputs were retried, all in retain; all180 final decisions are valid.
See `logs/s09_retry_audit.json`. Parser/retry differences remain part of the protocol
contrast; no excluded response/game/prefix or outcome-selected replacement.

Run from repository root:

```bash
TMPDIR=/var/tmp uv run python -m sim.replay --out data/s09_replay
uv run python scripts/s09_analyze.py
uv run python scripts/s09_independent.py
uv run python scripts/s09_release.py
```

The analyzer rejects partial arms, source drift, corrupt/truncated raw input,
terminal failures, orphan/duplicate cache keys and inconsistent exports. Source
identity is re-extracted from the original S07 neutral games before analysis.
The release script blocks live calls and requires cached resume to preserve all
input and result bytes. See `DESIGN_S09.md`, `results/s09_summary.md`, and the
independent review files under `logs/s09_*` for inference and isolation limitations.
