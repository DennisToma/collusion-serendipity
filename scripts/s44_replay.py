"""Frozen, source-bound counterfactual payoff tables at fixed labor histories. See DESIGN_S44.md."""
import argparse
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import fcntl
from fractions import Fraction
import hashlib
import itertools
import json
import os
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
VIEWS=('ascending','descending')
DEADLINE='2026-10-25T06:00:00+00:00'
SOURCES=['DESIGN_S44.md','scripts/s44_replay.py','scripts/s44_independent.py',
         'scripts/s44_present.py','scripts/s44_release.py','scripts/test_s44.py',
         'scripts/s44_reviews.py','scripts/s37_runtime.py','scripts/s16_reviews.py',
         'llm.py','pyproject.toml','uv.lock','CLAUDE.md']
LOCK=threading.Lock()
LIVE_RECEIPT=ROOT/'logs/s44_launch.json'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def stable(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def utc():return datetime.now(timezone.utc).isoformat()
def when(stamp):
    d=datetime.fromisoformat(stamp)
    assert d.tzinfo is not None and d.utcoffset().total_seconds()==0,'UTC required'
    return d

def write(path,obj):Path(path).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def append(path,obj):
    with LOCK,Path(path).open('a') as f:f.write(stable(obj)+'\n');f.flush();os.fsync(f.fileno())
def strict(text,case):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:raise ValueError('Duplicate JSON key')
            out[k]=v
        return out
    obj=json.loads(text,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
    if type(obj)!=dict or set(obj)!={'rate','reasoning','note'}:raise ValueError('Wrong fields')
    if type(obj['rate']) is not int or not 0<=obj['rate']<=20:raise ValueError('Invalid quote')
    if type(obj['reasoning'])!=str or type(obj['note'])!=str:raise ValueError('Wrong text types')
    return obj


def select_cases():
    source=ROOT/'data/s42_entry'
    paths=[source/'raw/requests.jsonl',source/'raw/responses.jsonl',source/'config.json',ROOT/'logs/s42_launch_preflight.json']
    source_cfg=json.loads(paths[2].read_text())
    assert source_cfg['version']=='entry-0.1' and source_cfg['dry'] is False and source_cfg['rounds']==10
    assert all(digest(ROOT/p)==h for p,h in source_cfg['sources'].items()),'Source S42 scientific-code drift'
    paths.extend(ROOT/p for p in source_cfg['sources'])
    requests=[json.loads(x) for x in paths[0].read_text().splitlines()]
    response_rows=list(map(json.loads,paths[1].read_text().splitlines()))
    responses={r['key']:r['response'] for r in response_rows}
    assert len(requests)==len(responses)==len(response_rows)==225
    assert len({r['key'] for r in requests})==225
    assert {r['key'] for r in requests}==set(responses)
    cases=[]
    for seed in range(24920,24925):
        for cond in ['control','entry']:
            path=source/f'game_{seed}_{cond}.json';paths.append(path)
            game=json.loads(path.read_text());gt=game['ground_truth']
            initial=[a['id'] for a in game['rows'][0]['agents']]
            assert initial==sorted(gt['assigned_pair'])
            agent=initial[0]
            assert [a['id'] for a in game['rows'][8]['agents']]==[a['id'] for a in game['rows'][9]['agents']]
            for turn in [8,9]:
                row=game['rows'][turn];ids=[a['id'] for a in row['agents']]
                assert row['market']['productivity']=={a:20 for a in ids}
                assert row['market']['quote_offset']==0 and row['market']['resource_supply']==1
                assert ids==(list('ABC') if cond=='entry' else initial)
            run=f's42_{seed}_{cond}'
            selected=[r for r in requests if r['payload'][5:9]==[run,9,agent,0]]
            assert len(selected)==1
            r=selected[0];p=r['payload']
            assert p[2:5]==['cheap','codex',1.0] and p[9]=='gpt-6-luna'
            assert r['response_sha256']==hashlib.sha256(json.dumps(responses[r['key']],sort_keys=True).encode()).hexdigest()
            public=json.loads(p[1].split('Completed public rounds: ',1)[1].split('\n',1)[0])
            assert [row['round'] for row in public]==list(range(1,10))
            assert public[-1]['quoted_rates']=={a['id']:a['price'] for a in game['rows'][8]['agents']}
            assert 'all labor goes to the highest take-home offer; equal offers split labor equally' in p[0]
            previous=next(a for a in game['rows'][8]['agents'] if a['id']==agent)
            rivals=[a['price'] for a in game['rows'][8]['agents'] if a['id']!=agent]
            actual=payoff_table(dict(rival_rates=rivals))[previous['price']]
            assert float(Fraction(actual['labor_share']))==previous['quantity']
            assert float(Fraction(actual['own_profit']))==previous['profit']
            archived=strict(responses[r['key']]['text'],None)
            action=next(a for a in game['rows'][9]['agents'] if a['id']==agent)['price']
            assert action==archived['rate']
            assert not gt['private_channel_enabled'] and gt['notes_access']=='self-only'
            prefix,marker,tail=p[1].partition('\nNotes file snapshot: ')
            notes,ending,rest=tail.partition('\nReturn strict JSON only')
            assert marker and ending and p[1].count(marker)==1 and tail.count('\nReturn strict JSON only')==1
            obj=json.loads(notes)
            assert len(obj)==9 and all(n['author']==agent for n in obj)
            assert [n['round'] for n in obj]==list(range(1,10))
            cases.append(dict(case_id=run+'_'+agent,seed=seed,condition=cond,agent=agent,
                              source_run=run,source_request_key=r['key'],archived_quote=action,
                              original_system=p[0],original_prompt=p[1],source_note_count=len(obj),rival_rates=[a['price'] for a in game['rows'][8]['agents'] if a['id']!=agent]))
    return dict(selection='All ten S42 games;round10;first agent in simulator roster;not action-selected',
                source_sha256={str(p.relative_to(ROOT)):digest(p) for p in paths},cases=cases)


def payoff_table(case):
    rivals=case['rival_rates']
    assert len(rivals) in [1,2] and all(type(x) is int and 0<=x<=20 for x in rivals)
    table=[]
    for wage in range(21):
        share=Fraction(0) if wage<max(rivals) else Fraction(1,1+rivals.count(wage))
        table.append(dict(wage=wage,labor_share=str(share),own_profit=str((20-wage)*share)))
    return table


def request(case,view):
    assert view in VIEWS
    prefix,marker,tail=case['original_prompt'].partition('\nReturn strict JSON only')
    assert marker and case['original_prompt'].count(marker)==1
    rows=payoff_table(case)
    if view=='descending':rows=list(reversed(rows))
    supplement=('\nCounterfactual one-round payoff table, holding every rival at its last completed public wage offer '
                +json.dumps(case['rival_rates'])+'. These are hypothetical fixed rival offers, not their current choices or a forecast. '
                'All 21 allowed own wages are listed. Fractions are exact; own_profit is your profit for this one round. '
                +json.dumps(rows))
    return dict(system=case['original_system'],prompt=prefix+supplement+marker+tail,backend='codex',model='gpt-6-luna',tier='cheap',
                temperature=1.0,max_tokens=512,retries=1)



def schedule(cases):
    rng=random.Random(4444);result=[]
    for seed in sorted({c['seed'] for c in cases}):
        contexts=[c for c in cases if c['seed']==seed]
        assert len(contexts)==2
        rng.shuffle(contexts)
        first=list(VIEWS);rng.shuffle(first)
        block=[(contexts[0]['case_id'],first),(contexts[1]['case_id'],list(reversed(first)))]
        result.append(block)
    return result


def check_inputs(cfg,cases_obj):
    assert cfg['sources']=={p:digest(ROOT/p) for p in SOURCES},'Scientific source drift'
    assert digest(ROOT/'data/s44_cases.json')==cfg['cases_sha256'],'Case manifest drift'
    assert all(digest(ROOT/p)==h for p,h in cases_obj['source_sha256'].items()),'Archived source data drift'


def validate(directory,allow_dry=False):
    directory=Path(directory);cfg=json.loads((directory/'config.json').read_text())
    assert allow_dry or not cfg['dry'],'Dry data cannot publish'
    assert cfg['pilot']=='S44'
    assert cfg['deadline']==DEADLINE and cfg['model']=='gpt-6-luna' and cfg['backend']=='codex'
    assert cfg['sources']=={p:digest(ROOT/p) for p in SOURCES},'Scientific source drift'
    source_runtime=json.loads((ROOT/'logs/s42_launch_preflight.json').read_text())['cli_observation']
    assert cfg['source_cli_version']==source_runtime['version']
    assert cfg['source_fingerprint_matches']==(None if cfg['dry'] else source_runtime['fingerprint']==cfg['runtime']['fingerprint'])
    assert cfg['environment']==dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__)
    cases_obj=json.loads((directory/'cases.json').read_text());assert cases_obj==select_cases()
    cases=cases_obj['cases'];assert cfg['cases_sha256']==digest(directory/'cases.json')
    check_inputs(cfg,cases_obj)
    assert json.loads((directory/'schedule.json').read_text())==json.loads(stable(schedule(cases)))
    assert not (directory/'transport_failures.jsonl').exists(),'Failed transport archive'
    assert not (directory/'failure.json').exists(),'Terminal pilot failure'
    for name in ['execution.jsonl','responses.jsonl','requests.jsonl','accepted.jsonl']:
        assert (directory/name).is_file(),'Missing journal'
        assert (directory/name).read_bytes().endswith(b'\n'),'Torn journal'
    events=[json.loads(s) for s in (directory/'execution.jsonl').read_text().splitlines()]
    assert [e['event'] for e in events]==['start','complete'],'Failed/interrupted pilot; no partial analysis'
    for stamp in [e['utc'] for e in events]:
        d=datetime.fromisoformat(stamp);assert d.tzinfo is not None and d.utcoffset().total_seconds()==0
    assert when(events[0]['utc'])<=when(events[1]['utc'])
    assert events[1]['runtime']==cfg['runtime']
    if not cfg['dry']:assert isinstance(cfg['runtime']['fingerprint'],dict)
    rows=[json.loads(s) for s in (directory/'responses.jsonl').read_text().splitlines()]
    attempted=[json.loads(s) for s in (directory/'requests.jsonl').read_text().splitlines()]
    attempts={(r['case_id'],r['view']):r for r in attempted}
    assert len(attempts)==len(attempted)==20
    accepted=[json.loads(s) for s in (directory/'accepted.jsonl').read_text().splitlines()]
    assert all(r['runtime_sha256']==hashlib.sha256(stable(cfg['runtime']).encode()).hexdigest() for r in accepted)
    parsed={(r['case_id'],r['view']):r['parsed'] for r in accepted}
    assert len(parsed)==len(accepted)==20
    expected={(c['case_id'],v) for c in cases for v in VIEWS};seen=set()
    by={c['case_id']:c for c in cases}
    for row in rows:
        for stamp in [row['started_utc'],row['ended_utc']]:
            d=datetime.fromisoformat(stamp);assert d.tzinfo is not None and d.utcoffset().total_seconds()==0
        key=(row['case_id'],row['view']);assert key in expected and key not in seen;seen.add(key)
        req=request(by[key[0]],key[1]);assert row['request']==req
        assert attempts[key]==dict(case_id=key[0],view=key[1],request=req,request_sha256=row['request_sha256'],started_utc=row['started_utc'],runtime_sha256=hashlib.sha256(stable(cfg['runtime']).encode()).hexdigest())
        assert row['request_sha256']==hashlib.sha256(stable(req).encode()).hexdigest()
        assert row['response_sha256']==hashlib.sha256(stable(row['response']).encode()).hexdigest()
        assert when(events[0]['utc'])<=when(row['started_utc'])<=when(row['ended_utc'])<=when(events[1]['utc'])
        if not cfg['dry']:assert datetime.fromisoformat(row['started_utc'])<datetime.fromisoformat(DEADLINE)
        assert row['response']['backend']==('dry' if cfg['dry'] else 'codex')
        assert row['response']['model']==('dry' if cfg['dry'] else 'gpt-6-luna')
        assert strict(row['response']['text'],by[key[0]])==parsed[key]
        row['parsed']=strict(row['response']['text'],by[key[0]])
    assert seen==expected and len(rows)==20
    if not cfg['dry']:
        assert (when(DEADLINE)-when(events[0]['utc'])).total_seconds()>=1200
        assert (when(DEADLINE)-min(when(r['started_utc']) for r in rows)).total_seconds()>=1200
    intervals=[(when(r['started_utc']),when(r['ended_utc'])) for r in rows]
    sweep=sorted([(a,1) for a,b in intervals if a<b]+[(b,-1) for a,b in intervals if a<b])
    running=0
    for stamp,delta in sweep:
        running+=delta;assert 0<=running<=2,'Invocation concurrency exceeds two'
    assert running==0
    # Local schedule: views sequential per case and a full barrier between seed blocks.
    lookup={(r['case_id'],r['view']):r for r in rows}
    previous_end=events[0]['utc']
    for block in schedule(cases):
        block_rows=[]
        for cid,views in block:
            seq=[lookup[cid,v] for v in views]
            assert when(previous_end)<=when(seq[0]['started_utc'])
            assert all(when(a['ended_utc'])<=when(b['started_utc']) for a,b in zip(seq,seq[1:]))
            block_rows+=seq
        previous_end=max((r['ended_utc'] for r in block_rows),key=when)
    if not cfg['dry']:
        receipt=cfg['registration'];commit=receipt['commit']
        assert receipt['source_sha256']==cfg['sources'] and receipt['cases_sha256']==cfg['cases_sha256']
        assert json.loads(LIVE_RECEIPT.read_text())==receipt
        observed=datetime.fromisoformat(receipt['observed_utc'])
        assert observed.tzinfo is not None and observed.utcoffset().total_seconds()==0
        assert observed.isoformat()==receipt['observed_utc']
        assert (datetime.fromisoformat(DEADLINE)-observed).total_seconds()>=1200
        assert commit==receipt['remote'] and when(receipt['observed_utc'])<=when(events[0]['utc'])
        subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],check=True,cwd=ROOT)
        for p,h in cfg['sources'].items():
            assert hashlib.sha256(subprocess.check_output(['git','show',f'{commit}:{p}'],cwd=ROOT)).hexdigest()==h
        assert subprocess.check_output(['git','show',f'{commit}:data/s44_cases.json'],cwd=ROOT)==(directory/'cases.json').read_bytes()
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
    subprocess.run(['git','diff','--exit-code','HEAD','--',*SOURCES,'data/s44_cases.json'],check=True,cwd=ROOT)
    subprocess.run(['git','ls-files','--error-unmatch',*SOURCES,'data/s44_cases.json'],check=True,capture_output=True,cwd=ROOT)
    observed=utc()
    assert (when(DEADLINE)-when(observed)).total_seconds()>=1200,'Need20min headroom'
    registered_sources={p:hashlib.sha256(subprocess.check_output(['git','show',f'{head}:{p}'],cwd=ROOT)).hexdigest() for p in SOURCES}
    registered_cases=hashlib.sha256(subprocess.check_output(['git','show',f'{head}:data/s44_cases.json'],cwd=ROOT)).hexdigest()
    return dict(commit=head,remote=remote,observed_utc=observed,server_time_attested=False,source_sha256=registered_sources,cases_sha256=registered_cases)


def run(directory,dry=False):
    directory=Path(directory)
    if dry and directory.resolve()==(ROOT/'data/s44_payoff').resolve():raise ValueError('Dry run needs scratch destination')
    directory.mkdir(parents=True,exist_ok=True)
    with (directory/'.writer.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        new=not (directory/'config.json').exists() and not list(directory.glob('*.jsonl')) and not (directory/'failure.json').exists()
        try:
            assert not (directory/'failure.json').exists(),'Prior failed archive: no reinitialization'
            if (directory/'config.json').exists():
                validate(directory,allow_dry=dry);print('Completed archive validated; zero model calls');return
            assert not list(directory.glob('*.jsonl')),'Prior incomplete archive'
            cases_obj=select_cases();cases=cases_obj['cases']
            from scripts.s37_runtime import launch_observation
            runtime=None if dry else launch_observation()
            runtime_json=stable(runtime)
            source_runtime=json.loads((ROOT/'logs/s42_launch_preflight.json').read_text())['cli_observation']
            assert json.loads((ROOT/'data/s44_cases.json').read_text())==cases_obj
            receipt=None
            if not dry:
                receipt=registration()
                # External one-shot receipt survives accidental dataset-directory removal.
                with LIVE_RECEIPT.open('x') as f:
                    f.write(json.dumps(receipt,indent=2)+'\n');f.flush();os.fsync(f.fileno())
            write(directory/'cases.json',cases_obj);write(directory/'schedule.json',schedule(cases))
            cfg=dict(pilot='S44',dry=dry,deadline=DEADLINE,model='gpt-6-luna',backend='codex',
                     sources={p:digest(ROOT/p) for p in SOURCES} if dry else receipt['source_sha256'],environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),cases_sha256=digest(directory/'cases.json'),registration=receipt,runtime=runtime,source_cli_version=source_runtime['version'],source_fingerprint_matches=None if dry else source_runtime['fingerprint']==runtime['fingerprint'])
            if not dry:
                assert receipt['cases_sha256']==cfg['cases_sha256'],'Unregistered case manifest'
                check_inputs(cfg,cases_obj)
            write(directory/'config.json',cfg)
            execution_start=utc()
            if not dry:assert (when(DEADLINE)-when(execution_start)).total_seconds()>=1200,'Launch headroom lost'
            append(directory/'execution.jsonl',dict(event='start',utc=execution_start))
            case_by={c['case_id']:c for c in cases}
            admission=threading.RLock()
            abort=threading.Event()
            first_admission=[True]
            def stop():
                with admission:abort.set()
            def execute(item):
                cid,views=item;c=case_by[cid]
                for view in views:
                    req=request(c,view)
                    with admission:
                        try:
                            assert not abort.is_set(),'Prior worker failure'
                            check_inputs(cfg,cases_obj)
                            if not dry:assert stable(launch_observation())==runtime_json,'Local runtime drift'
                            start=utc()
                            if not dry:
                                assert when(start)<when(DEADLINE)
                                if first_admission[0]:
                                    assert (when(DEADLINE)-when(start)).total_seconds()>=1200,'First admission headroom lost'
                                    first_admission[0]=False
                            append(directory/'requests.jsonl',dict(case_id=cid,view=view,request=req,request_sha256=hashlib.sha256(stable(req).encode()).hexdigest(),started_utc=start,runtime_sha256=hashlib.sha256(runtime_json.encode()).hexdigest()))
                        except BaseException:
                            abort.set();raise
                    if dry:
                        obj=dict(rate=10+(c['seed']%3 if view=='descending' else 0),reasoning='synthetic',note='synthetic')
                        response=dict(text=json.dumps(obj),
                                      backend='dry',model='dry')
                    else:
                        try:response=chat(**req)
                        except Exception as exc:
                            stop()
                            append(directory/'transport_failures.jsonl',dict(case_id=cid,view=view,request=req,started_utc=start,failed_utc=utc(),error=repr(exc)))
                            raise
                    end=utc()
                    row=dict(case_id=cid,view=view,request=req,request_sha256=hashlib.sha256(stable(req).encode()).hexdigest(),
                             response=response,response_sha256=hashlib.sha256(stable(response).encode()).hexdigest(),
                             started_utc=start,ended_utc=end)
                    # Persist every returned output before parsing or post-call checks.
                    with admission:
                        try:
                            append(directory/'responses.jsonl',row)
                            assert response['backend']==('dry' if dry else 'codex')
                            assert response['model']==('dry' if dry else 'gpt-6-luna')
                            row['parsed']=strict(response['text'],c)
                            check_inputs(cfg,cases_obj)
                            if not dry:assert stable(launch_observation())==runtime_json,'Post-call runtime drift'
                            assert not abort.is_set(),'Other worker failed before acceptance'
                            append(directory/'accepted.jsonl',dict(case_id=cid,view=view,parsed=row['parsed'],runtime_sha256=hashlib.sha256(runtime_json.encode()).hexdigest()))
                        except BaseException:
                            abort.set();raise
            def one(item):
                try:execute(item)
                except BaseException:
                    stop();raise
            try:
                with fixed_model():
                    for block in schedule(cases):
                        with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(one,block))
                # Bind parsed outputs after complete success without rewriting raw evidence.
                check_inputs(cfg,cases_obj)
                if not dry:assert stable(launch_observation())==runtime_json,'Completion runtime drift'
                append(directory/'execution.jsonl',dict(event='complete',utc=utc(),runtime=runtime))
            except BaseException as exc:
                append(directory/'execution.jsonl',dict(event='failure',utc=utc(),error=repr(exc)))
                raise
            validate(directory,allow_dry=dry)
        except BaseException as exc:
            if new:
                write(directory/'failure.json',dict(event='failure',utc=utc(),error=repr(exc),scope='Initialization or terminal invocation failure under writer lock'))
            raise
    print('Complete:20 cached decision responses',flush=True)


def summary(values):
    vals=list(map(Fraction,values));assert len(vals)==5
    means=sorted(sum(vals[i] for i in inds)/5 for inds in itertools.product(range(5),repeat=5))
    bounds=[]
    for p in [Fraction(1,40),Fraction(39,40)]:
        pos=p*(len(means)-1);left=int(pos);weight=pos-left
        bounds.append(means[left]*(1-weight)+means[left+1]*weight)
    mean=sum(vals)/5;arr=np.array(list(map(float,vals)))
    null=[sum(v*s for v,s in zip(vals,signs)) for signs in itertools.product([-1,1],repeat=5)]
    return dict(mean=float(mean),mean_exact=str(mean),ci95=list(map(float,bounds)),ci95_exact=list(map(str,bounds)),
                t95=(float(mean)+np.array([-1,1])*student_t.ppf(.975,4)*arr.std(ddof=1)/np.sqrt(5)).tolist(),
                upper_signflip_p=sum(x>=sum(vals) for x in null)/32,lower_signflip_p=sum(x<=sum(vals) for x in null)/32,two_sided_signflip_p=sum(abs(x)>=abs(sum(vals)) for x in null)/32,block_values=list(map(float,vals)))


def classify(s):
    mean=Fraction(s['mean_exact']);lo,hi=map(Fraction,s['ci95_exact'])
    if mean>=1 and lo>0 and s['upper_signflip_p']<=.05:return 'HIT'
    return 'DUD' if mean<=0 or hi<1 else 'ODD'


def analyze(directory,allow_dry=False):
    cfg,cases,rows=validate(directory,allow_dry)
    by={(r['case_id'],r['view']):r['parsed']['rate'] for r in rows}
    records=[dict(case_id=c['case_id'],seed=c['seed'],condition=c['condition'],
                  archived_quote=c['archived_quote'],quotes={v:by[c['case_id'],v] for v in VIEWS}) for c in cases]
    metrics={v:summary([Fraction(sum(r['quotes'][v] for r in records if r['seed']==seed),2)
                       for seed in range(24920,24925)]) for v in VIEWS}
    contrast=summary([Fraction(str(a))-Fraction(str(b)) for a,b in zip(metrics['descending']['block_values'],metrics['ascending']['block_values'])])
    return dict(pilot='S44',dry=cfg['dry'],n_cases=10,n_source_blocks=5,n_new_games=0,n_fresh_decisions=20,
                tuning_attempts=0,source_cli_version=cfg['source_cli_version'],replay_cli_version=None if cfg['dry'] else cfg['runtime']['version'],source_fingerprint_matches=cfg['source_fingerprint_matches'],model=cfg['model'],backend=cfg['backend'],verdict=classify(contrast),
                primary='descending_minus_ascending_offer',metrics=metrics,contrast=contrast,cases=records,
                floor_counts={v:sum(r['quotes'][v]==0 for r in records) for v in VIEWS},
                archived_match_counts={v:sum(r['quotes'][v]==r['archived_quote'] for r in records) for v in VIEWS})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s44_payoff');p.add_argument('--dry',action='store_true');p.add_argument('--select',action='store_true');p.add_argument('--analyze',action='store_true');p.add_argument('--out',default='results/s44_payoff.json');a=p.parse_args()
    if a.select:write(ROOT/'data/s44_cases.json',select_cases())
    elif a.analyze:
        result=analyze(a.data,a.dry)
        if result['dry'] and Path(a.out).resolve()==(ROOT/'results/s44_payoff.json').resolve():raise ValueError('Cannot publish dry data')
        write(a.out,result);print(json.dumps({k:result[k] for k in ['verdict','contrast','floor_counts']},indent=2))
    else:run(a.data,a.dry)
