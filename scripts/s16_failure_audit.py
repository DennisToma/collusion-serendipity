"""Audit an aborted S16 archive without estimating any market effect or redrawing."""
import argparse
from collections import Counter
import contextlib
from datetime import datetime
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import platform
import random
import subprocess
import sys
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy
import scipy

if not __debug__:
    raise RuntimeError('Research integrity checks require Python without -O')


def strict_response(text,has_file):
    def unique(pairs):
        obj={}
        for k,v in pairs:
            if k in obj:raise ValueError('duplicate')
            obj[k]=v
        return obj
    def constant(value):raise ValueError(value)
    try:obj=json.loads(text,object_pairs_hook=unique,parse_constant=constant)
    except (ValueError,TypeError):return None,'invalid JSON'
    if not isinstance(obj,dict) or set(obj)!={'bid','reasoning','note'}:return None,'invalid fields'
    if type(obj['bid']) is not int or not 6<=obj['bid']<=20:return None,'invalid bid'
    if not isinstance(obj['reasoning'],str):return None,'invalid reasoning'
    if len(obj['reasoning'].split())>40:return None,'overlong reasoning'
    if not isinstance(obj['note'],str):return None,'invalid note'
    if len(obj['note'].split())>60:return None,'overlong note'
    if not has_file and obj['note']!='':return None,'forbidden outsider note'
    return obj,None


def audit(data='data/s16_tender'):
    from sim import notes
    d=Path(data);cfg=json.loads((d/'config.json').read_text())
    assert not cfg['dry'] and cfg['version']==notes.VERSION
    assert cfg['rounds']==12 and cfg['n']==5 and cfg['seed0']==24240 and cfg['workers']==2
    assert cfg['model']=='gpt-6-luna' and cfg['backend']=='codex' and cfg['temperature_requested']==1
    assert cfg['deadline_utc']==notes.DEADLINE
    assert cfg['environment']==dict(python=platform.python_version(),numpy=numpy.__version__,scipy=scipy.__version__)
    assert set(cfg['sources'])==set(notes.SOURCES)
    for name,sha in cfg['sources'].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha
        assert hashlib.sha256(subprocess.check_output(['git','show',f'{cfg["registration_commit"]}:{name}'])).hexdigest()==sha
    subprocess.run(['git','merge-base','--is-ancestor',cfg['registration_commit'],'HEAD'],check=True)
    launch=json.loads(Path('logs/s16_launch_preflight.json').read_text())
    assert launch['sources']==cfg['sources'] and launch['registration_commit']==launch['observed_remote_head']==cfg['registration_commit']
    files=sorted(p for p in d.rglob('*') if p.is_file() and p.name!='.writer.lock')
    before={str(p):p.read_bytes() for p in files}
    journal=[json.loads(l) for l in (d/'raw/execution.jsonl').read_text().splitlines()]
    assert len(journal)==1 and journal[0]['event']=='start','Must preserve the interrupted journal'
    assert datetime.fromisoformat(launch['commit_time_client'])<=datetime.fromisoformat(launch['observed_utc'])<=datetime.fromisoformat(journal[0]['utc'])
    failures=[json.loads(p.read_text()) for p in sorted(d.glob('failure_*.json'))];assert failures
    assert not (d/'trajectories.jsonl').exists() and not (d/'ground_truth.jsonl').exists(),'No complete dataset export'
    tasks=notes.schedule();assert json.loads((d/'schedule.json').read_text())==[list(x) for x in tasks]
    planned={f's16_{s}_{c}':(s,c) for s,c in tasks}
    raw=[json.loads(l) for l in (d/'raw/responses.jsonl').read_text().splitlines()]
    request_rows=[json.loads(l) for l in (d/'raw/requests.jsonl').read_text().splitlines()]
    requests={r['key']:r for r in request_rows}
    assert len(raw)==len(requests)==len(request_rows)==len({r['key'] for r in raw})
    groups={};history_checks=0;snapshot_checks=0
    for row in raw:
        req=requests[row['key']];p=req['payload'];response=row['response']
        assert req['dry'] is False and len(p)==10
        system,user,tier,backend,temp,rid,t,agent,attempt,model=p
        assert rid in planned and tier=='cheap' and backend=='codex' and model=='gpt-6-luna' and temp==1
        assert row['key']==hashlib.sha256(json.dumps([False,p]).encode()).hexdigest()
        assert req['response_sha256']==hashlib.sha256(json.dumps(response,sort_keys=True).encode()).hexdigest()
        assert response['model']==model and response['backend']==backend
        assert journal[0]['utc']<=response['call_started_utc']<=response['call_completed_utc']
        assert response['call_started_utc']<notes.DEADLINE
        groups.setdefault(rid,[]).append((p,response))
    complete={g['ground_truth']['run_id']:g for g in [json.loads(p.read_text()) for p in sorted(d.glob('game_*.json'))]}
    assert len(complete)==len(list(d.glob('game_*.json')))
    failed={Path(f['game']).stem.replace('game_','s16_'):f for f in failures}
    assert len(failed)==len(failures) and set(complete).isdisjoint(failed)
    assert set(complete)|set(failed)==set(groups)
    counters={};rejection_details=[];independent_rows={};inflight=[]
    first_failure=min(f['recorded_utc'] for f in failures)
    for rid,items in groups.items():
        seed,cond=planned[rid];pair=random.Random(seed).sample(list('ABC'),2)
        rows=[];entries=[];accepted=[];invalid=[];t=0;ai=0;attempt=0;current={};previous_end=None;terminal=False
        for p,response in items:
            system,user,_,_,_,_,rt,agent,ra,_=p
            assert not terminal and (rt,agent,ra)==(t,'ABC'[ai],attempt),'Nonsequential/extra logical request'
            if previous_end is not None:assert previous_end<=response['call_started_utc']
            previous_end=response['call_completed_utc']
            if response['call_completed_utc']>first_failure:
                assert response['call_started_utc']<=first_failure,'After-failure completion began after first recorded failure'
                inflight.append(dict(run_id=rid,round_zero_based=rt,agent=agent,started=response['call_started_utc'],completed=response['call_completed_utc']))
            prefix=f'Round {t+1}. Completed public rounds: '
            assert user.startswith(prefix)
            observed=json.JSONDecoder().raw_decode(user[len(prefix):])[0]
            expected=[dict(round=i+1,payment=r['market']['payment'],bids={a['id']:a['price'] for a in r['agents']},allocations={a['id']:a['quantity'] for a in r['agents']},profits={a['id']:a['profit'] for a in r['agents']}) for i,r in enumerate(rows)]
            assert observed==expected;history_checks+=1
            if agent in pair:
                partner=next(a for a in pair if a!=agent)
                assert f'You and firm {partner} each have a market notes file.' in system
                assert ('Each file is readable only by its author.' in system)==(cond=='self')
                assert (f"Your file and firm {partner}'s file are both readable by you and by firm {partner}." in system)==(cond=='shared')
                snapshot=json.JSONDecoder().raw_decode(user.split('Notes file snapshot: ',1)[1])[0]
                assert snapshot==[e for e in entries if e['author']==agent or cond=='shared']
                assert all(e['round']<=t for e in snapshot);snapshot_checks+=1
            else:assert 'Notes file snapshot:' not in user and 'market notes file' not in system and 'You have no notes file.' in user
            obj,reason=strict_response(response['text'],agent in pair)
            if reason:
                invalid.append(reason)
                detail=dict(run_id=rid,round_zero_based=t,agent=agent,attempt=attempt,reason=reason,role='pair' if agent in pair else 'outsider')
                try:
                    fields=json.loads(response['text'])
                    detail['reasoning_words']=len(fields['reasoning'].split())
                    detail['note_words']=len(fields['note'].split())
                    detail['economic_and_note_fields_valid']=(type(fields['bid']) is int and 6<=fields['bid']<=20 and isinstance(fields['note'],str) and len(fields['note'].split())<=60 and (agent in pair or fields['note']==''))
                except (ValueError,KeyError,TypeError):pass
                rejection_details.append(detail);attempt+=1
                if attempt==3:terminal=True
                continue
            accepted.append((t,agent));current[agent]=obj;attempt=0;ai+=1
            if ai==3:
                bids=[current[a]['bid'] for a in 'ABC'];low=min(bids);n=bids.count(low)
                shares=[Fraction(1,n) if b==low else Fraction(0) for b in bids]
                records=[dict(id=a,price=current[a]['bid'],public_message='',action='bid',quantity=float(shares[i]),profit=float((low-6)*shares[i])) for i,a in enumerate('ABC')]
                rows.append(dict(run_id=rid,round=t,market=dict(cost=6,payment=low,contract_quantity=1),agents=records))
                entries.extend(dict(round=t+1,author=a,text=current[a]['note']) for a in 'ABC' if a in pair)
                t+=1;ai=0;current={}
        if rid in complete:
            gt=complete[rid]['ground_truth']
            assert journal[0]['utc']<=gt['started_utc']<=items[0][1]['call_started_utc']<=items[-1][1]['call_completed_utc']<=gt['ended_utc'],'Complete-game timestamp bounds'
            later=[rid2 for rid2 in groups if planned[rid2][0]>seed]
            if later:
                assert gt['ended_utc']<=min(groups[rid2][0][1]['call_started_utc'] for rid2 in later),'Complete-game end violates seed barrier'
            assert t==12 and not terminal and complete[rid]['rows']==rows and gt['notes_file']==entries
            assert gt['assigned_pair']==pair and gt['notes_access']==cond
            status='complete'
        else:
            assert t<12 and failed[rid]['recorded_utc']>=items[-1][1]['call_completed_utc']
            if terminal:
                assert failed[rid]['error']==repr(RuntimeError(f'{rid}/{t}/{"ABC"[ai]}: invalid after three attempts'))
                status='invalid-output failure'
            else:
                assert failed[rid]['error']==repr(RuntimeError('Terminal failure; no new requests'))
                status='partner-aborted'
        counters[rid]=dict(status=status,responses=len(items),accepted_decisions=len(accepted),rejected_responses=len(invalid),complete_rounds=t,rejections=dict(Counter(invalid)),first_call_started_utc=items[0][1]['call_started_utc'],last_call_completed_utc=items[-1][1]['call_completed_utc'])
    assert any(x['status']=='invalid-output failure' for x in counters.values())
    started_seeds=sorted({planned[rid][0] for rid in groups})
    assert started_seeds==notes.SEEDS[:len(started_seeds)]
    for seed in started_seeds:
        ids=[f's16_{seed}_{c}' for c in notes.CONDITIONS];assert all(rid in groups for rid in ids)
        start=[datetime.fromisoformat(counters[rid]['first_call_started_utc']) for rid in ids]
        end=[datetime.fromisoformat(counters[rid]['last_call_completed_utc']) for rid in ids]
        assert abs((start[0]-start[1]).total_seconds())<=60 and max(start)<=min(end)
    for a,b in zip(started_seeds,started_seeds[1:]):
        assert max(counters[f's16_{a}_{c}']['last_call_completed_utc'] for c in notes.CONDITIONS)<=min(counters[f's16_{b}_{c}']['first_call_started_utc'] for c in notes.CONDITIONS)
    used=[];replay_status={}
    class PrefixEnd(Exception):pass
    class PrefixCache(notes.TenderCache):
        def call(self,system,user,tier,backend,rid,t,agent,attempt,model=None):
            payload=[system,user,tier,backend,notes.TEMPERATURE,rid,t,agent,attempt]
            if model:payload.append(model)
            key=hashlib.sha256(json.dumps([False,payload]).encode()).hexdigest()
            if key not in self.entries:raise PrefixEnd('End of retained cached prefix; no redraw')
            used.append(key)
            return super().call(system,user,tier,backend,rid,t,agent,attempt,model)
    with patch('sim.common.llm.chat',side_effect=AssertionError('No uncached call in failure audit')):
        cache=PrefixCache(d/'raw/responses.jsonl');cache.cache_only=True
        for seed,cond in tasks:
            rid=f's16_{seed}_{cond}'
            if rid not in groups:continue
            try:
                with contextlib.redirect_stdout(io.StringIO()):replay=notes.run_game(seed,cond,cache,cfg['model'],cfg['backend'])
            except PrefixEnd:
                assert counters[rid]['status']=='partner-aborted';replay_status[rid]='exact cached prefix consumed'
            except RuntimeError as exc:
                assert counters[rid]['status']=='invalid-output failure' and repr(exc)==failed[rid]['error'];replay_status[rid]='registered three-attempt failure reproduced'
            else:
                assert rid in complete and replay['rows']==complete[rid]['rows']
                x,y=dict(replay['ground_truth']),dict(complete[rid]['ground_truth'])
                for obj in [x,y]:obj.pop('started_utc');obj.pop('ended_utc')
                assert x==y;replay_status[rid]='complete game exactly reproduced'
    assert len(used)==len(set(used))==len(raw) and set(used)==set(requests),'Unused/duplicate cached key'
    assert all(p.read_bytes()==before[str(p)] for p in files),'Audit mutated retained evidence'
    for name in ['scripts.s16_analyze','sim.notes']:
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                if name=='scripts.s16_analyze':__import__(name,fromlist=['analyze']).analyze(d)
                else:
                    with patch.object(sys,'argv',['sim.notes','--out',str(d)]):notes.main()
        except (RuntimeError,AssertionError) as exc:
            assert 'Interrupted' in str(exc) or 'Failure marker' in str(exc)
        else:raise AssertionError('Failed archive unexpectedly permits analysis/resume')
    assert all(p.read_bytes()==before[str(p)] for p in files)
    return dict(pilot='S16',status='operational failure; no scientific effect estimate',queue_verdict='ODD',queue_classification_postfailure=True,scientific_verdict=None,primary_estimated=False,
                planned_games=10,started_games=len(groups),complete_games=len(complete),failed_games=len(failed),unstarted_games=10-len(groups),
                responses=len(raw),accepted_decisions=sum(v['accepted_decisions'] for v in counters.values()),rejected_responses=len(rejection_details),
                rejections=dict(Counter(v['reason'] for v in rejection_details)),rejections_by_arm_role={c:{role:sum(x['run_id'].endswith('_'+c) and x['role']==role for x in rejection_details) for role in ['pair','outsider']} for c in ['self','shared']},rejected_responses_with_valid_bid_and_note_fields=sum(v.get('economic_and_note_fields_valid',False) for v in rejection_details),rejection_details=rejection_details,runs=counters,
                first_failure_recorded_utc=first_failure,last_call_completed_utc=max(v['last_call_completed_utc'] for v in counters.values()),
                calls_completing_after_first_failure_record=inflight,history_requests_checked=history_checks,note_snapshot_requests_checked=snapshot_checks,
                exact_all_key_cached_prefix_replay=True,replay_status=replay_status,independent_economics_histories_snapshots=True,
                failed_analysis_and_live_resume_blocked=True,byte_identical_retained_evidence=True,scientific_sources_verified=len(cfg['sources']),
                registration_commit=cfg['registration_commit'],sources=cfg['sources'],model=cfg['model'],backend=cfg['backend'],tuning_attempts=0,
                sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s16_tender');p.add_argument('--out',default='results/s16_failure.json');a=p.parse_args()
    result=audit(a.data);Path(a.out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['sources','sha256','rejection_details','runs','replay_status']},indent=2))
