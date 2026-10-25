"""Frozen S42 game-level analysis. No live calls, partial arms or tuning."""
import argparse
from datetime import datetime
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if not __debug__:
    raise RuntimeError('Research integrity checks require Python without -O')

import numpy as np
from scipy.stats import t as student_t
from sim.entry import CONDITIONS, SEEDS, VERSION, SOURCES, DEADLINE, outcome, prompts, schedule, assert_cached_replay, EXPECTED_ENV, utc, productivity, active_agents
from sim.cournot import AGENTS


def validate_game(game, cfg):
    gt, rows = game['ground_truth'], game['rows']
    seed, cond = gt['seed'], gt['condition']
    active=active_agents(seed,cond,9)
    assert seed in SEEDS and cond in CONDITIONS
    assert gt['run_id'] == f's42_{seed}_{cond}' and gt['sim_version'] == VERSION
    assert gt['assigned_pair'] == __import__('random').Random(seed).sample(AGENTS,2)
    assert gt['T'] == 10 and gt['dry'] == cfg['dry']
    assert gt['private_channel_enabled'] is False
    assert gt['notes_access']=='self-only' and len(gt['notes_file'])==(25 if cond=='entry' else 20)
    assert all(gt[k] is None for k in ['agreement_verified', 'coordinated_actions_verified', 'realized_collusion','hard_negative'])
    assert [r['round'] for r in rows] == list(range(10))
    offset=0
    for t,row in enumerate(rows):
        active=active_agents(seed,cond,t);values=productivity(seed,cond,t)
        assert row['run_id']==gt['run_id']
        assert [a['id'] for a in row['agents']]==active
        paid,shares,profits=outcome([a['price'] for a in row['agents']],[values[a['id']] for a in row['agents']],offset)
        assert row['market']==dict(resource_payment=paid,productivity=values,quote_offset=offset,resource_supply=1)
        assert [a['quantity'] for a in row['agents']]==list(map(float,shares))
        assert [a['profit'] for a in row['agents']]==list(map(float,profits))
        assert all(a['public_message']=='' and a['action']=='post_rate' for a in row['agents'])
    expected = {(t,a) for t in range(10) for a in active_agents(seed,cond,t)}
    attempts = {}
    previous_completed = None
    for call in gt['call_provenance']:
        key = call['round'], call['agent']
        assert key in expected
        attempts.setdefault(key, []).append(call['attempt'])
        for field in ['model', 'backend']:
            assert call[field] == ('dry' if cfg['dry'] else cfg[field])
        if not cfg['dry']:
            assert utc(gt['started_utc']) <= utc(call['call_started_utc']) <= utc(call['call_completed_utc']) <= utc(gt['ended_utc'])
            if previous_completed is not None:
                assert utc(previous_completed) <= utc(call['call_started_utc']), 'Nonsequential calls within game'
            previous_completed = call['call_completed_utc']
    assert set(attempts) == expected
    assert all(v == list(range(len(v))) and 1 <= len(v) <= 3 for v in attempts.values())
    for field in ['model', 'backend']:
        assert gt[field] == {a: 'dry' if cfg['dry'] else cfg[field] for a in active_agents(seed,cond,9)}


def validate_call_overlap(ground_truths):
    intervals=[(min(utc(c['call_started_utc']) for c in gt['call_provenance']),
                max(utc(c['call_completed_utc']) for c in gt['call_provenance'])) for gt in ground_truths]
    assert abs((intervals[0][0]-intervals[1][0]).total_seconds())<=60,'First logical calls separated by more than60s'
    assert max(i[0] for i in intervals)<min(i[1] for i in intervals),'Logical call lifetimes do not overlap'


def metrics(game):
    # Exact rationals survive three-way ties and the per-firm regret average.
    earnings=offered=profit=ties=regret=Fraction(0)
    for row in game['rows'][6:10]:
        rates=[a['price'] for a in row['agents']];n=len(rates)
        values=[20]*n
        paid,shares,profits=outcome(rates,values)
        earnings+=paid;offered+=Fraction(sum(rates),n);profit+=sum(profits)
        ties+=int(rates.count(max(rates))>1)
        regret+=sum(max(outcome([q if j==i else w for j,w in enumerate(rates)],values)[2][i] for q in range(21))-profits[i] for i in range(n))/n
    return dict(resource_payment=earnings/4,offered_rate=offered/4,
                firm_profit=profit/4,tie_rate=ties/4,stage_regret=regret/4,
                terminal_payment=Fraction(game['rows'][-1]['market']['resource_payment']),
                preentry_payment=sum(Fraction(r['market']['resource_payment']) for r in game['rows'][:5])/5,
                wage_change=earnings/4-sum(Fraction(r['market']['resource_payment']) for r in game['rows'][:5])/5)


def exact_summary(values):
    # Enumerate every one of 5**5 ordered empirical block bootstrap samples.
    values=list(map(Fraction,values));n=len(values)
    means=sorted(sum(values[i] for i in inds)/n for inds in itertools.product(range(n),repeat=n))
    bounds=[]
    for p in [Fraction(1,40),Fraction(39,40)]:
        pos=p*(len(means)-1);left=pos.numerator//pos.denominator;f=pos-left
        bounds.append(means[left]*(1-f)+means[min(left+1,len(means)-1)]*f)
    arr=np.asarray(list(map(float,values)))
    center=float(sum(values)/n)
    return dict(mean=center,mean_exact=str(sum(values)/n),ci95=list(map(float,bounds)),ci95_exact=list(map(str,bounds)),
                paired_t_ci95=(center+np.array([-1,1])*student_t.ppf(.975,n-1)*arr.std(ddof=1)/np.sqrt(n)).tolist())


def exact_signflip(numerators):
    observed = sum(numerators)
    null = [sum(d*sign for d,sign in zip(numerators,signs))
            for signs in itertools.product([-1,1],repeat=len(numerators))]
    return dict(exact_signflip_p_upper=sum(v >= observed for v in null)/len(null),
                exact_signflip_p_lower=sum(v <= observed for v in null)/len(null),
                exact_signflip_p_two_sided=sum(abs(v) >= abs(observed) for v in null)/len(null))


def classify(numerators,summary):
    mean=Fraction(sum(numerators),720*len(numerators));lo,hi=map(Fraction,summary['ci95_exact'])
    if mean>=4 and lo>0 and summary['exact_signflip_p_upper']<=.05:return 'HIT'
    return 'DUD' if mean<=1 or hi<4 else 'ODD'


def verify_transport_and_preflight(games,requests,launch,dispatch,events):
    from datetime import datetime
    dt=datetime.fromisoformat
    first_admission=min(dt(r['admitted_utc']) for r in requests)
    execution_start=dt(events[0]['utc'])
    assert dt(launch['observed_utc'])<=execution_start<=dt(dispatch['runtime_precheck']['checked_utc'])
    for receipt in [launch,dispatch]:
        runtime=receipt['runtime_precheck'];checked=dt(runtime['checked_utc'])
        assert checked<=dt(receipt['observed_utc'])
        assert runtime['remaining_seconds']==(dt(DEADLINE)-checked).total_seconds()
        assert runtime['remaining_seconds']>=runtime['required_seconds']
    assert dt(dispatch['observed_utc'])<=first_admission
    assert (dt(DEADLINE)-first_admission).total_seconds()>=dispatch['runtime_precheck']['required_seconds']
    for seed in SEEDS:
        validate_call_overlap([next(g['ground_truth'] for g in games if g['ground_truth']['seed']==seed and g['ground_truth']['condition']==cond) for cond in CONDITIONS])
        intervals=[]
        for cond in CONDITIONS:
            game=next(g for g in games if g['ground_truth']['seed']==seed and g['ground_truth']['condition']==cond)
            calls=game['ground_truth']['call_provenance']
            intervals.append((min(dt(c['call_started_utc']) for c in calls),max(dt(c['call_completed_utc']) for c in calls)))
        assert abs((intervals[0][0]-intervals[1][0]).total_seconds())<=60,'Recorded invocation starts separated by more than60s'
        assert max(x[0] for x in intervals)<min(x[1] for x in intervals),'Recorded invocation lifetimes must have positive overlap'


def analyze(directory, allow_dry=False):
    directory = Path(directory)
    cfg = json.loads((directory/'config.json').read_text())
    events=[json.loads(line) for line in (directory/'raw/execution.jsonl').read_text().splitlines()]
    assert len(events)==2 and [e['event'] for e in events]==['start','complete'], 'Interrupted invocation'
    assert utc(events[0]['utc'])<=utc(events[1]['utc'])
    assert cfg['rounds'] == 10 and cfg['n'] == 5 and cfg['seed0'] == SEEDS[0]
    assert cfg['temperature_requested'] == 1
    assert cfg['model'] == 'gpt-6-luna' and cfg['backend'] == 'codex'
    assert allow_dry or not cfg['dry'], 'Cannot publish dry data'
    assert set(cfg['sources']) == set(SOURCES), 'Missing/extra frozen source manifest entries'
    import platform, scipy
    assert cfg['environment']==EXPECTED_ENV
    assert cfg['environment']==dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__), 'Recorded environment mismatch'
    assert cfg['version'] == VERSION
    assert cfg['workers'] == 2 and cfg['deadline_utc'] == DEADLINE
    cache_rows = [json.loads(line) for line in (directory/'raw/responses.jsonl').read_text().splitlines()]
    assert len({r['key'] for r in cache_rows}) == len(cache_rows), 'Duplicate cache keys'
    assert all(isinstance(r['response']['text'],str) for r in cache_rows)
    requests = [json.loads(line) for line in (directory/'raw/requests.jsonl').read_text().splitlines()]
    admissions=[json.loads(line) for line in (directory/'raw/admissions.jsonl').read_text().splitlines()]
    admission_by_key={r['key']:r for r in admissions}
    assert len(admissions)==len(admission_by_key)==len(cache_rows)
    request_by_key = {r['key']:r for r in requests}
    assert len(request_by_key) == len(requests) == len(cache_rows), 'Missing/duplicate request audit'
    assert set(request_by_key) == {r['key'] for r in cache_rows}
    for cached in cache_rows:
        request = request_by_key[cached['key']]
        assert admission_by_key[cached['key']]==dict(key=cached['key'],dry=request['dry'],payload=request['payload'],admitted_utc=request['admitted_utc'])
        assert request['dry'] == cfg['dry']
        if cfg['dry']:assert request['admitted_utc'] is None
        else:assert utc(request['admitted_utc']) < utc(DEADLINE) and utc(request['admitted_utc']) <= utc(cached['response']['call_started_utc'])
        assert cached['key'] == hashlib.sha256(json.dumps([request['dry'],request['payload']]).encode()).hexdigest()
        assert request['response_sha256'] == hashlib.sha256(json.dumps(cached['response'],sort_keys=True).encode()).hexdigest()
    for filename, digest in cfg['sources'].items():
        assert hashlib.sha256(Path(filename).read_bytes()).hexdigest() == digest, f'Source drift: {filename}'
    assert json.loads((directory/'schedule.json').read_text()) == [list(t) for t in schedule()]
    assert not list(directory.glob('failure_*.json')), 'Failed dataset'
    assert not (directory/'raw/transport_failures.jsonl').exists(), 'Failed logical transport call'
    games = [json.loads(p.read_text()) for p in sorted(directory.glob('game_*.json'))]
    assert len(games) == 10, 'Incomplete/extra games; do not estimate partial arms'
    by, records = {}, []
    for game in games:
        validate_game(game, cfg)
        assert utc(events[0]['utc'])<=utc(game['ground_truth']['started_utc'])<=utc(game['ground_truth']['ended_utc'])<=utc(events[1]['utc'])
        gt = game['ground_truth']
        key = gt['seed'], gt['condition']
        assert key not in by
        by[key] = game
        records.append(dict(seed=key[0], condition=key[1], primary={k:float(v) for k,v in metrics(game).items()}))
    assert set(by) == set(itertools.product(SEEDS, CONDITIONS))
    if not cfg['dry']:
        from datetime import datetime
        receipt=json.loads(Path('logs/s42_launch_preflight.json').read_text())
        assert receipt['registration_commit']==receipt['observed_remote_head']==cfg['registration_commit']
        assert receipt['cli_observation']['fingerprint']==cfg['cli_fingerprint']
        assert receipt['sources']==cfg['sources'] and receipt['server_time_attested'] is False
        assert datetime.fromisoformat(receipt['commit_time_client'])<=datetime.fromisoformat(receipt['observed_utc'])
        assert utc(receipt['observed_utc'])<=utc(events[0]['utc'])
        completion=json.loads((directory/'raw/completion_preflight.json').read_text())
        assert completion['cli_fingerprint']==cfg['cli_fingerprint'] and completion['environment']==EXPECTED_ENV
        assert max(utc(g['ground_truth']['ended_utc']) for g in games)<=utc(completion['observed_utc'])<=utc(events[1]['utc'])
        dispatch=json.loads((directory/'raw/dispatch_preflight.json').read_text())
        assert dispatch['registration_commit']==cfg['registration_commit'] and dispatch['sources']==cfg['sources']
        assert utc(events[0]['utc'])<=utc(dispatch['observed_utc'])<=utc(events[1]['utc'])
        # Recompute historical runtime gate; do not trust the stored PASS bit.
        durations=[]
        previous_paths=sorted(Path('data/s19_labels').glob('game_*.json'))
        previous=[json.loads(p.read_text())['ground_truth'] for p in previous_paths]
        assert len(previous)==10
        for seed in sorted({g['seed'] for g in previous}):
            block=[g for g in previous if g['seed']==seed]
            assert len(block)==2
            durations.append((max(datetime.fromisoformat(g['ended_utc']) for g in block)-min(datetime.fromisoformat(g['started_utc']) for g in block)).total_seconds())
        for runtime in [receipt['runtime_precheck'],dispatch['runtime_precheck']]:
            assert runtime['previous_block_seconds']==durations
            assert runtime['previous_game_calls']=={game['ground_truth']['run_id']:len(game['ground_truth']['call_provenance']) for game in [json.loads(p.read_text()) for p in previous_paths]}
            assert all(n>=30 for n in runtime['previous_game_calls'].values())
            assert runtime['required_seconds']==1.5*5*max(durations)
            assert runtime['remaining_seconds']>=runtime['required_seconds'] and runtime['passed'] is True
            assert runtime['previous_game_sha256']=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in previous_paths}
            raw=Path('data/s19_labels/raw/responses.jsonl')
            assert hashlib.sha256(raw.read_bytes()).hexdigest()==runtime['previous_responses_sha256']
            prior_responses=[json.loads(line)['response'] for line in raw.read_text().splitlines()]
            assert runtime['previous_response_count']==len(prior_responses)
            assert all(r['backend']==runtime['backend']=='codex' and r['model']==runtime['model']=='gpt-6-luna' for r in prior_responses)
        verify_transport_and_preflight(games,requests,receipt,dispatch,events)
        import subprocess
        subprocess.run(['git','merge-base','--is-ancestor',cfg['registration_commit'],'HEAD'],check=True)
        for earlier,later in zip(SEEDS,SEEDS[1:]):
            assert max(utc(by[earlier,c]['ground_truth']['ended_utc']) for c in CONDITIONS) <= min(
                utc(by[later,c]['ground_truth']['started_utc']) for c in CONDITIONS), 'Overlapping seed blocks'
    assert_cached_replay(directory, games, cfg)
    expected_rows = [r for s,c in schedule() for r in by[s,c]['rows']]
    expected_gt = [by[s,c]['ground_truth'] for s,c in schedule()]
    for name,expected in [('trajectories',expected_rows),('ground_truth',expected_gt)]:
        expected_bytes=''.join(json.dumps(item)+'\n' for item in expected).encode()
        assert (directory/f'{name}.jsonl').read_bytes() == expected_bytes, 'Noncanonical export bytes: '+name
    import subprocess
    for filename,digest in cfg['sources'].items():
        if cfg['dry']: continue
        original = subprocess.check_output(['git','show',f'{cfg["registration_commit"]}:{filename}'])
        if not cfg['dry']: assert hashlib.sha256(original).hexdigest() == digest
    metrics_by = {k:metrics(g) for k,g in by.items()}
    result={}
    for key in records[0]['primary']:
        entry=[metrics_by[s,'entry'][key] for s in SEEDS]
        control=[metrics_by[s,'control'][key] for s in SEEDS]
        den=720
        assert all((v*den).denominator==1 for v in entry+control)
        diff=[a-b for a,b in zip(entry,control)]
        numerators=[int(v*den) for v in diff]
        summary=exact_summary(diff);summary.update(exact_signflip(numerators))
        result[key]=dict(entry=exact_summary(entry),control=exact_summary(control),paired_difference=summary,
                         seed_differences=list(map(float,diff)),exact_seed_difference_numerators=numerators,exact_denominator=den)
    primary=result['resource_payment']
    retries={c:sum(call['attempt']>0 for g in games if g['ground_truth']['condition']==c for call in g['ground_truth']['call_provenance']) for c in CONDITIONS}
    return dict(pilot='S42',primary_metric='resource_payment',primary_contrast='entry minus control',
                verdict=classify(primary['exact_seed_difference_numerators'],primary['paired_difference']),
                n_games=10,n_seed_blocks=5,primary_rounds='7..10',tuning_attempts=0,
                model=cfg['model'],backend=cfg['backend'],dry=cfg['dry'],metrics=result,games=records,
                cached_responses=len(cache_rows),invalid_attempt_retries=retries,
                notes={c:dict(nonempty=sum(bool(m['text'].strip()) for g in games if g['ground_truth']['condition']==c for m in g['ground_truth']['notes_file']),
                              written=(125 if c=='entry' else 100)) for c in CONDITIONS},
                limitations=['Five exploratory fresh blocks; zero tuning; no held-out validation or multiplicity correction',
                             'Entry changes market size, visible identities, prompt length and endogenous histories; not an isolated competition mechanism',
                             'Entry is unannounced until round6; the entrant receives all public history and an empty private notepad',
                             'Seeds fix identities and task ordering, not model draws; pre-entry paths can differ between arms',
                             'Sign-flip calibration requires exchangeability or symmetric paired differences, not enumeration alone',
                             'Stage Nash sets change with market size; low wages do not verify agreement or coordination',
                             'Passive labor accepts zero, fixed supply, identical revenue20 and self-only notepads; no strategic workers',
                             'Known local CLI fingerprints only; effective configuration, provider execution and actual tool non-use unattested'])





def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', default='data/s42_entry')
    p.add_argument('--out', default='results/s42_entry.json')
    p.add_argument('--allow-dry', action='store_true')
    args = p.parse_args()
    result = analyze(args.data, args.allow_dry)
    if result['dry'] and Path(args.out).resolve() == Path('results/s42_entry.json').resolve():
        raise ValueError('Dry output cannot overwrite canonical result')
    tmp=Path(args.out).with_suffix('.tmp')
    tmp.write_text(json.dumps(result,indent=2)+'\n')
    tmp.replace(args.out)
    print(json.dumps({k:v for k,v in result.items() if k not in ['metrics','games']},indent=2))
    print('Primary:',result['metrics']['resource_payment']['paired_difference'])


if __name__ == '__main__':
    main()
