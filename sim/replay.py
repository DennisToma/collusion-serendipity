"""S09 matched continuation: erase versus retain prior received private messages."""
import argparse
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
import fcntl
import hashlib
import json
from pathlib import Path
import random
import subprocess
import threading

from sim.advisor import checked_call, now, public_history
from sim.common import Cache, TEMPERATURE
from sim.cournot import AGENTS, payoffs, system_prompt

if not __debug__:
    raise RuntimeError('Research integrity checks require Python without -O')

VERSION = 'replay-0.1'
DEADLINE = '2026-10-24T17:48:00+00:00'
CONDITIONS = ['retain', 'erase']
SEEDS = list(range(24080, 24085))
SOURCES = ['sim/replay.py', 'sim/legality.py', 'sim/advisor.py', 'sim/cournot.py', 'sim/common.py',
           'llm.py', 'DESIGN_S09.md', 'scripts/s09_analyze.py', 'scripts/s02_analyze.py',
           'scripts/test_s09.py', 'scripts/s09_snapshot.py', 'scripts/s09_independent.py', 'pyproject.toml', 'uv.lock'] + [f'data/s09_prefix/prefix_{s}.json' for s in SEEDS]



def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('Duplicate JSON key')
        obj[key] = value
    return obj


def reject_constant(value):
    raise ValueError('Nonstandard JSON constant')


def parse_action(text):
    try:
        obj = json.loads(text, object_pairs_hook=unique_object, parse_constant=reject_constant)
        q, reasoning, message = obj['quantity'], obj['reasoning'], obj['private_message']
        if type(q) is not int or not 0 <= q <= 12:
            return None
        if not isinstance(reasoning, str) or len(reasoning.split()) > 40:
            return None
        if not isinstance(message, str) or len(message.split()) > 60:
            return None
        return dict(quantity=q, reasoning=reasoning, private_message=message)
    except (ValueError, KeyError, TypeError):
        return None


class ReplayCache(Cache):
    """Full request audit next to the inherited hash/response cache; fail closed."""
    def __init__(self, path, dry=False):
        if list(path.parent.glob('*.torn.*')):
            raise RuntimeError('Torn-cache recovery is not permitted for S09')
        for raw in [path,path.with_name('requests.jsonl')]:
            if raw.exists() and raw.stat().st_size and not raw.read_bytes().endswith(b'\n'):
                raise RuntimeError('Incomplete raw append; refuse recovery or new calls')
        self.abort = threading.Event()
        super().__init__(path, dry)
        if path.exists():
            assert len(path.read_text().splitlines()) == len(self.entries), 'Duplicate cache keys'
        self.requests_path = path.with_name('requests.jsonl')
        self.requests = {}
        if self.requests_path.exists():
            for line in self.requests_path.read_text().splitlines():
                row = json.loads(line)
                if row['key'] in self.requests:
                    raise ValueError('Duplicate request audit key')
                self.requests[row['key']] = row

    def call(self, system, user, tier, backend, run_id, t, agent, attempt, model=None):
        payload = [system, user, tier, backend, TEMPERATURE, run_id, t, agent, attempt]
        if model:
            payload.append(model)
        key = hashlib.sha256(json.dumps([self.dry, payload]).encode()).hexdigest()
        if self.abort.is_set() and key not in self.entries:
            raise RuntimeError('Partner terminal failure; no new uncached calls')
        if not self.dry and key not in self.entries and now() >= DEADLINE:
            raise RuntimeError('S09 absolute deadline reached; no new uncached requests')
        response = super().call(system, user, tier, backend, run_id, t, agent, attempt, model)
        request = dict(key=key, dry=self.dry, payload=payload,
                       response_sha256=hashlib.sha256(json.dumps(response,sort_keys=True).encode()).hexdigest())
        with self.lock:
            if key in self.requests:
                if self.requests[key] != request:
                    raise RuntimeError('Request audit changed')
            else:
                with self.requests_path.open('a') as handle:
                    handle.write(json.dumps(request)+'\n')
                    handle.flush()
                self.requests[key] = request
        if self.dry:
            # Adapt only the dry dummy for the outsider with no box.
            obj = json.loads(response['text'])
            if 'You have no message box.' in user:
                obj['private_message'] = ''
            return dict(response, text=json.dumps(obj))
        return response


from sim.legality import prompts as original_prompts


def load_prefix(seed):
    return json.loads(Path(f'data/s09_prefix/prefix_{seed}.json').read_text())


def prompts(agent, partner, condition, rows, chat):
    # The only prompt intervention: erase received messages from rounds 1..6.
    visible = [m for m in chat if condition == 'retain' or m['round'] > 6]
    return original_prompts(agent, partner, 'neutral', rows, visible)


def run_game(seed, condition, cache, model, backend, rounds=12):
    assert condition in CONDITIONS
    started = now()
    pair = random.Random(seed).sample(AGENTS, 2)
    run_id = f's09_{seed}_{condition}'
    prefix = load_prefix(seed)
    assert pair == prefix['assigned_pair']
    rows = [dict(r, run_id=run_id) for r in prefix['rows']]
    notes, calls, chat = [], [], list(prefix['private_chat'])
    for t in range(6, rounds):
        records, pending = [], []
        for agent in AGENTS:
            partner = next((a for a in pair if a != agent), None) if agent in pair else None
            system, user = prompts(agent, partner, condition, rows, chat)
            def parser(text):
                result = parse_action(text)
                if result is not None and partner is None and result['private_message'] != '':
                    return None
                return result
            result = checked_call(cache, system, user, run_id, t, agent,
                                  model, backend, parser, calls)
            notes.append(dict(round=t, agent=agent, reasoning=result['reasoning']))
            if partner:
                pending.append(dict(round=t+1, sender=agent, recipient=partner, text=result['private_message']))
            records.append(dict(id=agent, quantity=result['quantity'], public_message='', action='produce'))
        # Deliver only after every simultaneous action has been chosen.
        chat.extend(pending)
        price, profits = payoffs([a['quantity'] for a in records])
        for agent, profit in zip(records, profits):
            agent['profit'] = profit
        rows.append(dict(run_id=run_id, round=t, market=dict(cost=6, intercept=30, price=price), agents=records))
    gt = dict(run_id=run_id, seed=seed, condition=condition, assigned_pair=pair,
              private_channel_enabled=True, private_chat=chat, prefix_source_sha256=prefix["source_sha256"],
              message_memory_erased=(condition == "erase"), agreement_verified=None,
              coordinated_actions_verified=None, realized_collusion=None, hard_negative=None,
              sim_version=VERSION, T=rounds, dry=cache.dry, reasoning_notes=notes,
              call_provenance=calls, model={a: 'dry' if cache.dry else model for a in AGENTS},
              backend={a: 'dry' if cache.dry else backend for a in AGENTS},
              started_utc=started, ended_utc=now())
    print(f'{run_id} complete {len(calls)} calls', flush=True)
    return dict(rows=rows, ground_truth=gt)


def assert_cached_replay(directory, games, cfg):
    """Prove every action/failed attempt came from its reconstructed cached request."""
    import contextlib
    import io
    from unittest.mock import patch
    raw = Path(directory)/'raw/responses.jsonl'
    request_path = raw.with_name('requests.jsonl')
    original_bytes = [p.read_bytes() for p in [raw, request_path]]
    if any(not data.endswith(b'\n') for data in original_bytes):
        raise ValueError('Truncated raw publication input; no automatic recovery')
    used = []
    class CachedReplay(ReplayCache):
        def call(self, system, user, tier, backend, run_id, t, agent, attempt, model=None):
            payload = [system, user, tier, backend, TEMPERATURE, run_id, t, agent, attempt]
            if model:
                payload.append(model)
            key = hashlib.sha256(json.dumps([self.dry, payload]).encode()).hexdigest()
            if key not in self.entries:
                raise ValueError('Uncached request forbidden during replay')
            used.append(key)
            return super().call(system,user,tier,backend,run_id,t,agent,attempt,model)
    with patch('sim.common.llm.chat',side_effect=AssertionError('Uncached live call forbidden')):
        cache = CachedReplay(raw, dry=cfg['dry'])
        for game in games:
            gt = game['ground_truth']
            with contextlib.redirect_stdout(io.StringIO()):
                replay = run_game(gt['seed'],gt['condition'],cache,cfg['model'],cfg['backend'],12)
            if replay['rows'] != game['rows']:
                raise ValueError('Recorded actions disagree with cached responses')
            a,b = dict(replay['ground_truth']),dict(gt)
            for obj in [a,b]:
                del obj['started_utc'];del obj['ended_utc']
            if a != b:
                raise ValueError('Recorded attempts/provenance/tables disagree with cached replay')
    if len(used) != len(set(used)) or set(used) != set(cache.entries) or set(used) != set(cache.requests):
        raise ValueError('Replay must consume every raw/request key exactly once')
    if [p.read_bytes() for p in [raw, request_path]] != original_bytes:
        raise ValueError('Replay changed the raw cache/request audit')


def schedule():
    tasks, rng = [], random.Random(2409)
    for seed in SEEDS:
        order = CONDITIONS.copy()
        rng.shuffle(order)
        tasks.extend((seed, c) for c in order)
    return tasks


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', default='data/s09_replay')
    p.add_argument('--model', default='gpt-6-luna')
    p.add_argument('--backend', default='codex')
    p.add_argument('--workers', type=int, choices=[2], default=2)
    p.add_argument('--dry', action='store_true')
    args = p.parse_args()
    if args.dry and Path(args.out).resolve() == Path('data/s09_replay').resolve():
        raise ValueError('Dry mode requires an explicit separate output directory')
    if args.model != 'gpt-6-luna' or args.backend != 'codex':
        raise ValueError('S09 pins gpt-6-luna/codex before any calls')
    import numpy, scipy
    directory = Path(args.out)
    directory.mkdir(parents=True, exist_ok=True)
    if list(directory.glob('failure_*.json')):
        raise RuntimeError('Terminal failed experiment; no resume or publication')
    lock = (directory / '.writer.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if not args.dry:
        subprocess.run(['git','ls-files','--error-unmatch',*SOURCES],check=True,capture_output=True)
        subprocess.run(['git','diff','--exit-code','HEAD','--',*SOURCES],check=True,capture_output=True)
    sources = {s: hashlib.sha256(Path(s).read_bytes()).hexdigest() for s in SOURCES}
    config = dict(version=VERSION, model=args.model, backend=args.backend, rounds=12, n=5,
                  seed0=SEEDS[0], dry=args.dry, temperature_requested=TEMPERATURE, sources=sources,
                  workers=args.workers, deadline_utc=DEADLINE,
                  transport=dict(temporary_directory_root=__import__('tempfile').gettempdir(),
                                 sandbox_requested='read-only',no_commands_instruction=True,
                                 filesystem_isolation_attested=False),
                  environment=dict(python=platform.python_version(),numpy=numpy.__version__,scipy=scipy.__version__))
    path = directory / 'config.json'
    registration_commit = (json.loads(path.read_text())['registration_commit'] if path.exists() else
                           subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
    if not args.dry:
        for source, digest in sources.items():
            registered = subprocess.check_output(['git','show',f'{registration_commit}:{source}'])
            assert hashlib.sha256(registered).hexdigest() == digest, 'Registration/source mismatch'
    config['registration_commit'] = registration_commit
    if path.exists():
        assert json.loads(path.read_text()) == config, 'Refusing configuration/code drift'
    else:
        path.write_text(json.dumps(config, indent=2)+'\n')
    tasks = schedule()
    (directory / 'schedule.json').write_text(json.dumps(tasks, indent=2)+'\n')
    cache = ReplayCache(directory / 'raw' / 'responses.jsonl', args.dry)
    for seed in SEEDS:
        failures = []
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(run_game, s, c, cache, args.model, args.backend):
                       directory / f'game_{s}_{c}.json' for s, c in tasks if s == seed
                       and not (directory / f'game_{s}_{c}.json').exists()}
            for future in as_completed(futures):
                try:
                    game = future.result()
                except Exception as exc:
                    cache.abort.set()
                    failed = futures[future]
                    details = dict(game=failed.name, error=repr(exc), recorded_utc=now())
                    (directory/f'failure_{failed.stem}.json').write_text(json.dumps(details,indent=2)+'\n')
                    failures.append(details)
                    continue
                path = futures[future]
                tmp = path.with_suffix('.tmp')
                tmp.write_text(json.dumps(game)+'\n')
                tmp.replace(path)
        if failures:
            raise RuntimeError(f'S09 failed block; completed partner preserved, no further blocks: {failures}')
    games = [json.loads((directory / f'game_{s}_{c}.json').read_text()) for s, c in tasks]
    for name, items in [('trajectories', [r for g in games for r in g['rows']]),
                        ('ground_truth', [g['ground_truth'] for g in games])]:
        path = directory / f'{name}.jsonl'
        tmp = path.with_suffix('.tmp')
        tmp.write_text(''.join(json.dumps(x)+'\n' for x in items))
        tmp.replace(path)
    print('S09 all ten games and exports complete', flush=True)
    lock.close()


if __name__ == '__main__':
    main()
