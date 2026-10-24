"""S32 copy of archived common cache, with one llm.chat transport attempt.
Historical common.py remains untouched. Only codex/gpt-6-luna is allowed live.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import random
import threading
import time
import llm
TEMPERATURE = 1.0
PRICES = list(range(13))
class Cache:
    def __init__(self, path, dry=False):
        self.path, self.dry, self.lock = path, dry, threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.entries = {}
        if path.exists():
            raw = path.read_bytes()
            lines = raw.splitlines(keepends=True)
            offset = 0
            for i, line in enumerate(lines):
                try:
                    row = json.loads(line)
                    self.entries[row['key']] = row['response']
                except (ValueError, KeyError):
                    if i == len(lines) - 1 and not line.endswith(b'\n'):
                        # Preserve evidence and all complete paid responses after a torn append.
                        path.with_suffix(f'.torn.{time.time_ns()}').write_bytes(line)
                        with path.open('r+b') as f:
                            f.truncate(offset)
                        break
                    raise ValueError(f"Damaged cache: {path}")
                offset += len(line)
            else:
                if raw and not raw.endswith(b'\n'):
                    with path.open('ab') as f:
                        f.write(b'\n')

    def call(self, system, prompt, tier, backend, run_id, t, agent, attempt, model=None):
        payload = [system, prompt, tier, backend, TEMPERATURE, run_id, t, agent, attempt]
        if model:  # Phase 2 part C (explicit seller model); omitted otherwise so older cache keys are unchanged
            payload.append(model)
        # Separate fake and real calls even when reusing the same dataset name.
        key = hashlib.sha256(json.dumps([self.dry, payload]).encode()).hexdigest()
        with self.lock:
            if key in self.entries:
                return self.entries[key]
        if self.dry:
            rng = random.Random(key)
            response = dict(text=json.dumps(dict(public_message="Reviewing market prices.",
                            private_message="I am reviewing prices.", reasoning="dry",
                            quantity=rng.choice(list(map(int, PRICES))))),
                            model="dry", backend="dry")
        else:
            if backend!='codex' or model!='gpt-6-luna':raise RuntimeError('S32 transport route pinned')
            called_utc = datetime.now(timezone.utc).isoformat()
            # glm-5.2 (Go) reasons by default and can spend the 512-token default before answering (empty text)
            extra = dict(max_tokens=4000) if (model or '').startswith('glm') else {}
            for wait in ([30, 60, 120, 240, 300, 300, 300] if backend in ('qwen', 'aqueduct') else []) + [None]:
                try:  # Modal qwen endpoint: cold starts / transient 404-429 -> wait instead of failing the game
                    response = llm.chat(prompt, system=system, tier=tier, backend=backend,
                                        temperature=TEMPERATURE, model=model, retries=1, **extra)
                    break
                except RuntimeError:
                    if wait is None:
                        raise
                    time.sleep(wait)
            response = dict(response, call_started_utc=called_utc,
                            call_completed_utc=datetime.now(timezone.utc).isoformat())
        with self.lock:
            with self.path.open('a') as f:
                f.write(json.dumps(dict(key=key, response=response)) + '\n')
                f.flush()
            self.entries[key] = response
        return response
