"""Cache adapted from Q1.4 sim/llm_market.py; source recorded in data/provenance.json.
Only the dry response action grid is changed for the quantity pilot.
"""
import hashlib
import json
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
            for line in path.read_text().splitlines():
                try:
                    row = json.loads(line)
                    self.entries[row['key']] = row['response']
                except (ValueError, KeyError):
                    raise ValueError(f"Damaged cache: {path}")

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
            # glm-5.2 (Go) reasons by default and can spend the 512-token default before answering (empty text)
            extra = dict(max_tokens=4000) if (model or '').startswith('glm') else {}
            for wait in ([30, 60, 120, 240, 300, 300, 300] if backend in ('qwen', 'aqueduct') else []) + [None]:
                try:  # Modal qwen endpoint: cold starts / transient 404-429 -> wait instead of failing the game
                    response = llm.chat(prompt, system=system, tier=tier, backend=backend,
                                        temperature=TEMPERATURE, model=model, **extra)
                    break
                except RuntimeError:
                    if wait is None:
                        raise
                    time.sleep(wait)
        with self.lock:
            with self.path.open('a') as f:
                f.write(json.dumps(dict(key=key, response=response)) + '\n')
                f.flush()
            self.entries[key] = response
        return response

