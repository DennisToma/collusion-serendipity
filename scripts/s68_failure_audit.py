"""Audit the interrupted S68 prefix without computing any behavioral estimate.

Additive post-interruption verifier. The 18 registered scientific sources,
original requests/responses/accepted rows and lone start event stay unchanged.
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import s68_replay as s


def verify(directory='data/s68_polarity'):
    root=Path(directory);cfg=json.loads((root/'config.json').read_text())
    cases_obj=json.loads((root/'cases.json').read_text());cases=cases_obj['cases'];by={c['case_id']:c for c in cases}
    assert cfg['pilot']=='S68' and cfg['dry'] is False and cfg['deadline']==s.DEADLINE
    assert cfg['model']=='gpt-6-luna' and cfg['backend']=='codex'
    assert cfg['sources']=={p:s.digest(s.ROOT/p) for p in s.SOURCES}
    assert json.loads(Path('logs/s68_source_freeze.json').read_text())['sources']==cfg['sources']
    assert cfg['cases_sha256']==s.digest(root/'cases.json')==s.digest(s.ROOT/'data/s68_cases.json')
    assert cases_obj==s.select_cases()
    assert json.loads((root/'schedule.json').read_text())==json.loads(s.stable(s.schedule(cases)))
    receipt=json.loads(s.LIVE_RECEIPT.read_text());assert receipt==cfg['registration']
    assert receipt['commit']==receipt['remote'] and receipt['source_sha256']==cfg['sources']
    assert s.digest(s.LIVE_ATTEMPT)==cfg['attempt_sha256']
    assert json.loads(s.LIVE_ATTEMPT.read_text())['pilot']=='S68'
    assert s.when(json.loads(s.LIVE_ATTEMPT.read_text())['utc'])<=s.when(receipt['observed_utc'])
    subprocess.run(['git','merge-base','--is-ancestor',receipt['commit'],'HEAD'],check=True)
    for path,digest in cfg['sources'].items():
        assert hashlib.sha256(subprocess.check_output(['git','show',f"{receipt['commit']}:{path}"])).hexdigest()==digest
    assert subprocess.check_output(['git','show',f"{receipt['commit']}:data/s68_cases.json"])==(root/'cases.json').read_bytes()
    def journal(name):
        p=root/(name+'.jsonl');assert p.read_bytes().endswith(b'\n')
        return [json.loads(line) for line in p.read_text().splitlines()]
    events=journal('execution');assert len(events)==1 and events[0]['event']=='start'
    requests=journal('requests');responses=journal('responses');accepted=journal('accepted')
    assert len(requests)==30 and len(responses)==len(accepted)==29
    key=lambda r:(r['case_id'],r['view'])
    reqs={key(r):r for r in requests};raw={key(r):r for r in responses};acc={key(r):r for r in accepted}
    expected={(c['case_id'],v) for c in cases for v in s.VIEWS}
    assert len(reqs)==30 and set(reqs)==expected and len(raw)==29 and len(acc)==29 and set(raw)==set(acc)
    missing=expected-set(raw);assert len(missing)==1
    assert s.when(receipt['observed_utc'])<=s.when(events[0]['utc'])
    assert (s.when(s.DEADLINE)-s.when(events[0]['utc'])).total_seconds()>=1200
    runtime_sha=hashlib.sha256(s.stable(cfg['runtime']).encode()).hexdigest()
    assert cfg['runtime']['fingerprint'] is not None
    for r in requests:
        k=key(r);q=s.request(by[k[0]],k[1]);assert r['request']==q
        assert r['request_sha256']==hashlib.sha256(s.stable(q).encode()).hexdigest()
        assert r['runtime_sha256']==runtime_sha
        assert s.when(events[0]['utc'])<=s.when(r['started_utc'])<s.when(s.DEADLINE)
    first=min(s.when(r['started_utc']) for r in requests)
    assert (s.when(s.DEADLINE)-first).total_seconds()>=1200
    # Check bindings only: no decoding/aggregation of approvals or mismatches.
    for k,r in raw.items():
        a=reqs[k]
        assert r['request']==a['request'] and r['request_sha256']==a['request_sha256'] and r['started_utc']==a['started_utc']
        assert r['response_sha256']==hashlib.sha256(s.stable(r['response']).encode()).hexdigest()
        assert s.when(r['started_utc'])<=s.when(r['ended_utc'])
        assert r['response']['backend']=='codex' and r['response']['model']=='gpt-6-luna'
        assert acc[k]['parsed']==s.strict(r['response']['text'],by[k[0]])
        assert acc[k]['runtime_sha256']==runtime_sha
    lookup={key(r):r for r in requests};previous=s.when(events[0]['utc'])
    for block in s.schedule(cases):
        block_ends=[]
        for cid,views in block:
            assert previous<=s.when(lookup[cid,views[0]]['started_utc'])
            for left,right in zip(views,views[1:]):
                assert (cid,left) in raw
                assert s.when(raw[cid,left]['ended_utc'])<=s.when(lookup[cid,right]['started_utc'])
            block_ends.extend(s.when(raw[cid,v]['ended_utc']) for v in views if (cid,v) in raw)
        previous=max(block_ends)
    # Treat the unanswered invocation as open through the local exit observation.
    exit_receipt=json.loads(Path('logs/s68_process_exit.json').read_text())
    assert exit_receipt['exit_code']==143 and exit_receipt['cause']=='unknown'
    observed=s.when(exit_receipt['observed_utc'])
    intervals=[(s.when(r['started_utc']),s.when(raw[k]['ended_utc']) if k in raw else observed) for k,r in reqs.items()]
    sweep=sorted([(a,1) for a,b in intervals if a<b]+[(b,-1) for a,b in intervals if a<b]);running=0
    for stamp,change in sweep:running+=change;assert 0<=running<=2
    assert running==0
    before={str(p.relative_to(root)):s.digest(p) for p in root.rglob('*') if p.is_file() and p.name!='.writer.lock'}
    # Both analysis and resume must reject the incomplete archive without calls.
    for func in [s.validate,s.analyze,s.run]:
        with patch.object(s,'chat',side_effect=AssertionError('Scientific calls forbidden')) as chat:
            try:func(root)
            except AssertionError:pass
            else:raise AssertionError('Incomplete archive accepted by '+func.__name__)
            assert chat.call_count==0
    assert before=={str(p.relative_to(root)):s.digest(p) for p in root.rglob('*') if p.is_file() and p.name!='.writer.lock'}
    assert not list(root.glob('*fail*')),'Original interruption had no harness failure marker'
    prior=json.loads(Path('logs/s68_prior_artifacts.json').read_text())
    assert all(s.digest(path)==digest for path,digest in prior['sha256'].items())
    split=json.loads(Path('logs/s68_split_append.json').read_text())
    old=subprocess.check_output(['git','show',split['baseline_commit']+':data/SPLITS.md'])
    assert hashlib.sha256(old).hexdigest()==split['baseline_sha256']
    assert Path('data/SPLITS.md').read_bytes()==old+split['appended'].encode()
    return dict(pilot='S68',status='FAILED_INTERRUPTED',scientific_verdict=None,behavioral_estimates_computed=False,
                planned_decisions=30,admitted_requests=30,returned_responses=29,accepted_responses=29,logical_retries=0,
                complete_cases=sum(all((c['case_id'],v) in raw for v in s.VIEWS) for c in cases),
                requested_model=cfg['model'],recorded_model=cfg['model'],backend=cfg['backend'],new_games=0,tuning_attempts=0,
                failure_scope='Process exit143;one request has no archived reply;no completion event;no harness-generated terminal marker;cause unknown',
                registration_commit=receipt['commit'],source_hashes_verified=len(cfg['sources']),admission_bindings_verified=len(reqs),returned_response_bindings_verified=len(raw),prefix_bindings_verified=len(raw),
                missing_reply=[dict(case_id=k[0],view=k[1],started_utc=reqs[k]['started_utc']) for k in sorted(missing)],
                first_admission_utc=first.isoformat(),last_archived_return_utc=max(s.when(r['ended_utc']) for r in responses).isoformat(),
                local_exit_observation_utc=observed.isoformat(),interrupted_resume_and_analysis_reject=True,zero_model_calls_in_audit=True,
                raw_archive_sha256=before,prior_scientific_paths_unchanged=prior['selected_artifacts'],exact_prospective_split_append=True,
                process_or_provider_root_cause_attested=False,archived_prefix_intact=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='results/s68_failure.json');a=p.parse_args()
    result=verify();Path(a.out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='raw_archive_sha256'},indent=2))
