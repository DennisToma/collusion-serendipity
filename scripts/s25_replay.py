"""Frozen, source-bound two-order fixed-history decision replay. See DESIGN_S25.md."""
import argparse
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import fcntl
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import random
import platform
import scipy
import subprocess
import sys
import threading

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy.stats import t as student_t
import llm
from llm import chat

if not __debug__: raise RuntimeError('Run without -O')
ROOT=Path(__file__).resolve().parents[1]
VIEWS=('action_first','reason_first')
DEADLINE='2026-10-24T22:50:00+00:00'
SOURCES=['DESIGN_S25.md','scripts/s25_replay.py','scripts/s25_analyze.py',
         'scripts/s25_independent.py','scripts/s25_present.py','scripts/s25_release.py',
         'scripts/test_s25.py','scripts/s21_audit.py',
         'scripts/s21_analyze.py','llm.py','pyproject.toml','uv.lock']
LOCK=threading.Lock()
LIVE_RECEIPT=ROOT/'logs/s25_launch.json'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def stable(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def utc():return datetime.now(timezone.utc).isoformat()
def write(path,obj):Path(path).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def append(path,obj):
    with LOCK,Path(path).open('a') as f:f.write(stable(obj)+'\n');f.flush()
def strict(text,case):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:raise ValueError('Duplicate JSON key')
            out[k]=v
        return out
    obj=json.loads(text,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
    if type(obj)!=dict or set(obj)!={'reviews','reasoning','note'}:raise ValueError('Wrong fields')
    if type(obj['reviews'])!=dict or set(obj['reviews'])!=set(case['reviews']):raise ValueError('Wrong review map')
    if any(type(v)!=bool for v in obj['reviews'].values()):raise ValueError('Reviews not booleans')
    if type(obj['reasoning'])!=str or type(obj['note'])!=str:raise ValueError('Wrong text types')
    if 'You have no notepad; note must be empty.' in case['original_prompt'] and obj['note']!='':raise ValueError('Note without notepad')
    return obj


def select_cases():
    from scripts.s21_audit import select_cases as select_s19
    obj=select_s19()
    reqs={r['key']:r for r in map(json.loads,(ROOT/'data/s19_labels/raw/requests.jsonl').read_text().splitlines())}
    for c in obj['cases']:
        p=reqs[c['source_request_key']]['payload']
        assert p[2:5]==['cheap','codex',1.0] and p[9]=='gpt-6-luna'
        c['original_system']=p[0];c['original_prompt']=p[1]
        assert c['status'][c['author']] in ('FAIL','TYPE-Y')
    return obj


def request(case,view):
    assert view in VIEWS
    original=case['original_prompt']
    prefix,sep,ending=original.partition('Return strict JSON only with exactly these fields: ')
    assert sep and ending.count('. Set each review to true')==1
    suffix='. Set each review to true'+ending.split('. Set each review to true',1)[1]
    reviews='{'+', '.join(json.dumps(a)+': <boolean>' for a in case['reviews'])+'}'
    note='brief notepad entry' if 'Notes file snapshot:' in original else ''
    fields={'reviews':reviews,'reasoning':json.dumps('brief private explanation'),'note':json.dumps(note)}
    order=['reviews','reasoning','note'] if view=='action_first' else ['reasoning','reviews','note']
    schema='{'+','.join(json.dumps(k)+':'+fields[k] for k in order)+'}'
    prompt=prefix+sep+schema+suffix+' Emit the top-level fields in the exact order shown.'
    return dict(system=case['original_system'],prompt=prompt,backend='codex',model='gpt-6-luna',tier='cheap',
                temperature=1.0,max_tokens=1024,retries=1)


def schedule(cases):
    rng=random.Random(2525);result=[]
    for seed in sorted({c['seed'] for c in cases}):
        block=[]
        for c in [c for c in cases if c['seed']==seed]:
            views=list(VIEWS);rng.shuffle(views);block.append((c['case_id'],views))
        rng.shuffle(block);result.append(block)
    return result


def check_inputs(cfg,cases_obj):
    assert cfg['sources']=={p:digest(ROOT/p) for p in SOURCES},'Scientific source drift'
    assert digest(ROOT/'data/s25_cases.json')==cfg['cases_sha256'],'Case manifest drift'
    assert all(digest(ROOT/p)==h for p,h in cases_obj['source_sha256'].items()),'Archived source data drift'


def validate(directory,allow_dry=False):
    directory=Path(directory);cfg=json.loads((directory/'config.json').read_text())
    assert allow_dry or not cfg['dry'],'Dry data cannot publish'
    assert cfg['deadline']==DEADLINE and cfg['model']=='gpt-6-luna' and cfg['backend']=='codex'
    assert cfg['sources']=={p:digest(ROOT/p) for p in SOURCES},'Scientific source drift'
    assert cfg['environment']==dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__)
    cases_obj=json.loads((directory/'cases.json').read_text());assert cases_obj==select_cases()
    cases=cases_obj['cases'];assert cfg['cases_sha256']==digest(directory/'cases.json')
    check_inputs(cfg,cases_obj)
    assert json.loads((directory/'schedule.json').read_text())==json.loads(stable(schedule(cases)))
    events=[json.loads(s) for s in (directory/'execution.jsonl').read_text().splitlines()]
    assert [e['event'] for e in events]==['start','complete'],'Failed/interrupted pilot; no partial analysis'
    assert events[0]['utc']<=events[1]['utc']
    rows=[json.loads(s) for s in (directory/'responses.jsonl').read_text().splitlines()]
    attempted=[json.loads(s) for s in (directory/'requests.jsonl').read_text().splitlines()]
    attempts={(r['case_id'],r['view']):r for r in attempted}
    assert len(attempts)==len(attempted)==20
    accepted=[json.loads(s) for s in (directory/'accepted.jsonl').read_text().splitlines()]
    parsed={(r['case_id'],r['view']):r['parsed'] for r in accepted}
    assert len(parsed)==len(accepted)==20
    expected={(c['case_id'],v) for c in cases for v in VIEWS};seen=set()
    by={c['case_id']:c for c in cases}
    for row in rows:
        key=(row['case_id'],row['view']);assert key in expected and key not in seen;seen.add(key)
        req=request(by[key[0]],key[1]);assert row['request']==req
        assert attempts[key]==dict(case_id=key[0],view=key[1],request=req,request_sha256=row['request_sha256'],started_utc=row['started_utc'])
        assert row['request_sha256']==hashlib.sha256(stable(req).encode()).hexdigest()
        assert row['response_sha256']==hashlib.sha256(stable(row['response']).encode()).hexdigest()
        assert events[0]['utc']<=row['started_utc']<=row['ended_utc']<=events[1]['utc']
        assert row['started_utc']<DEADLINE
        assert row['response']['backend']==('dry' if cfg['dry'] else 'codex')
        assert row['response']['model']==('dry' if cfg['dry'] else 'gpt-6-luna')
        assert strict(row['response']['text'],by[key[0]])==parsed[key]
        row['parsed']=strict(row['response']['text'],by[key[0]])
    assert seen==expected and len(rows)==20
    # Local schedule: views sequential per case and a full barrier between seed blocks.
    lookup={(r['case_id'],r['view']):r for r in rows}
    previous_end=events[0]['utc']
    for block in schedule(cases):
        block_rows=[]
        for cid,views in block:
            seq=[lookup[cid,v] for v in views]
            assert previous_end<=seq[0]['started_utc']
            assert all(a['ended_utc']<=b['started_utc'] for a,b in zip(seq,seq[1:]))
            block_rows+=seq
        previous_end=max(r['ended_utc'] for r in block_rows)
    if not cfg['dry']:
        receipt=cfg['registration'];commit=receipt['commit']
        assert json.loads(LIVE_RECEIPT.read_text())==receipt
        assert commit==receipt['remote'] and receipt['observed_utc']<=events[0]['utc']
        subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],check=True,cwd=ROOT)
        for p,h in cfg['sources'].items():
            assert hashlib.sha256(subprocess.check_output(['git','show',f'{commit}:{p}'],cwd=ROOT)).hexdigest()==h
        assert subprocess.check_output(['git','show',f'{commit}:data/s25_cases.json'],cwd=ROOT)==(directory/'cases.json').read_bytes()
    return cfg,cases,rows


@contextmanager
def fixed_model():
    # The shared helper deduplicates [requested model, CODEX_CHEAP]. Scope the
    # fallback name to the requested model for this invocation, then restore it.
    original=llm.CODEX_CHEAP
    llm.CODEX_CHEAP='gpt-6-luna'
    try:yield
    finally:llm.CODEX_CHEAP=original


def registration():
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip()
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],text=True,cwd=ROOT).split()[0]
    assert head==remote
    subprocess.run(['git','diff','--exit-code','HEAD','--',*SOURCES,'data/s25_cases.json'],check=True,cwd=ROOT)
    subprocess.run(['git','ls-files','--error-unmatch',*SOURCES,'data/s25_cases.json'],check=True,capture_output=True,cwd=ROOT)
    assert utc()<DEADLINE
    return dict(commit=head,remote=remote,observed_utc=utc(),server_time_attested=False)


def run(directory,dry=False):
    directory=Path(directory)
    if dry and directory.resolve()==(ROOT/'data/s25_order').resolve():raise ValueError('Dry run needs scratch destination')
    directory.mkdir(parents=True,exist_ok=True)
    with (directory/'.writer.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if (directory/'config.json').exists():
            validate(directory,allow_dry=dry);print('Completed archive validated; zero model calls');return
        assert not list(directory.glob('*.jsonl')),'Prior incomplete archive'
        cases_obj=select_cases();cases=cases_obj['cases']
        assert json.loads((ROOT/'data/s25_cases.json').read_text())==cases_obj
        receipt=None
        if not dry:
            receipt=registration()
            # External one-shot receipt survives accidental dataset-directory removal.
            with LIVE_RECEIPT.open('x') as f:f.write(json.dumps(receipt,indent=2)+'\n')
        write(directory/'cases.json',cases_obj);write(directory/'schedule.json',schedule(cases))
        cfg=dict(pilot='S25',dry=dry,deadline=DEADLINE,model='gpt-6-luna',backend='codex',
                 sources={p:digest(ROOT/p) for p in SOURCES},environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),cases_sha256=digest(directory/'cases.json'),registration=receipt)
        write(directory/'config.json',cfg);append(directory/'execution.jsonl',dict(event='start',utc=utc()))
        case_by={c['case_id']:c for c in cases}
        abort=threading.Event()
        admission=threading.Lock()
        def execute(item):
            cid,views=item;c=case_by[cid]
            for view in views:
                req=request(c,view)
                with admission:
                    assert not abort.is_set(),'Prior worker failure'
                    check_inputs(cfg,cases_obj)
                    start=utc();assert start<DEADLINE
                    append(directory/'requests.jsonl',dict(case_id=cid,view=view,request=req,request_sha256=hashlib.sha256(stable(req).encode()).hexdigest(),started_utc=start))
                if dry:
                    obj=dict(reviews=c['reviews'],reasoning='synthetic',note='')
                    if view=='reason_first':obj=dict(reasoning='synthetic',reviews=c['reviews'],note='')
                    response=dict(text=json.dumps(obj),
                                  backend='dry',model='dry')
                else:
                    try:response=chat(**req)
                    except Exception as exc:
                        abort.set()
                        append(directory/'transport_failures.jsonl',dict(case_id=cid,view=view,request=req,started_utc=start,failed_utc=utc(),error=repr(exc)))
                        raise
                end=utc()
                row=dict(case_id=cid,view=view,request=req,request_sha256=hashlib.sha256(stable(req).encode()).hexdigest(),
                         response=response,response_sha256=hashlib.sha256(stable(response).encode()).hexdigest(),
                         started_utc=start,ended_utc=end)
                # Persist every response, including malformed output or route mismatch.
                append(directory/'responses.jsonl',row)
                assert response['backend']==('dry' if dry else 'codex')
                assert response['model']==('dry' if dry else 'gpt-6-luna')
                row['parsed']=strict(response['text'],c)
                append(directory/'accepted.jsonl',dict(case_id=cid,view=view,parsed=row['parsed']))
        def one(item):
            try:execute(item)
            except BaseException:
                abort.set();raise
        try:
            with fixed_model():
                for block in schedule(cases):
                    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(one,block))
            # Bind parsed outputs after complete success without rewriting raw evidence.
            check_inputs(cfg,cases_obj)
            append(directory/'execution.jsonl',dict(event='complete',utc=utc()))
        except BaseException as exc:
            append(directory/'execution.jsonl',dict(event='failure',utc=utc(),error=repr(exc)))
            raise
    validate(directory,allow_dry=dry)
    print('Complete:20 cached decision responses',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s25_order');p.add_argument('--dry',action='store_true');p.add_argument('--select',action='store_true');a=p.parse_args()
    if a.select:write(ROOT/'data/s25_cases.json',select_cases())
    else:run(a.data,a.dry)
