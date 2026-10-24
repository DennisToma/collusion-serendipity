"""S03 cache-only replay and independent stdlib arithmetic/export verification."""
import contextlib
import hashlib
import io
import itertools
import json
from pathlib import Path
import statistics
import sys
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.calculator import run_game, CalculatorCache
if not __debug__:
    raise RuntimeError('Research integrity checks require Python without -O')


def main():
    directory=Path('data/s03_calculator')
    cfg=json.loads((directory/'config.json').read_text())
    assert not cfg['dry']
    result=json.loads(Path('results/s03_calculator.json').read_text())
    files=sorted(directory.glob('game_*.json'))
    assert len(files)==10
    games=[json.loads(p.read_text()) for p in files]
    raw=directory/'raw/responses.jsonl'
    before=raw.read_bytes()
    request_path=raw.with_name('requests.jsonl')
    before_requests=request_path.read_bytes()
    with patch('sim.common.llm.chat',side_effect=AssertionError('Uncached live call forbidden')):
        cache=CalculatorCache(raw)
        for original in games:
            gt=original['ground_truth']
            with contextlib.redirect_stdout(io.StringIO()):
                replay=run_game(gt['seed'],gt['condition'],cache,cfg['model'],cfg['backend'],12)
            assert replay['rows']==original['rows']
            actual=dict(replay['ground_truth']);expected=dict(gt)
            for data in [actual,expected]:
                del data['started_utc'];del data['ended_utc']
            assert actual==expected
    assert raw.read_bytes()==before
    assert request_path.read_bytes()==before_requests
    trajectory=[json.loads(line) for line in (directory/'trajectories.jsonl').read_text().splitlines()]
    metadata=[json.loads(line) for line in (directory/'ground_truth.jsonl').read_text().splitlines()]
    assert len(metadata)==10 and len(trajectory)==120
    by_id={g['run_id']:g for g in metadata}
    assert len(by_id)==10
    exported={(r['run_id'],r['round']):r for r in trajectory}
    assert len(exported)==120
    totals={};lag_regrets={};actual_regrets={}
    for g in games:
        gt=g['ground_truth'];rid=gt['run_id']
        assert by_id[rid]==gt
        quantities=[];lag=[];actual=[]
        for t,row in enumerate(g['rows']):
            assert row==exported[rid,t]
            vals={a['id']:a['quantity'] for a in row['agents']}
            price=max(0,30-sum(vals.values()))
            assert price==row['market']['price']
            for a in row['agents']:
                assert a['profit']==(price-6)*a['quantity']
                if t>=3:
                    quantities.append(a['quantity'])
                    # Separate formula implementation; do not use production table/payoff helpers.
                    for lagged,storage in [(False,actual),(True,lag)]:
                        previous=g['rows'][t-1] if lagged else row
                        rivals=sum(b['quantity'] for b in previous['agents'] if b['id']!=a['id'])
                        gains=[(max(0,30-rivals-q)-6)*q for q in range(13)]
                        storage.append(max(gains)-gains[a['quantity']])
                table=gt['tables'][t]['delivered'][a['id']]
                if t and gt['condition']=='calculator':
                    rivals=sum(b['quantity'] for b in g['rows'][t-1]['agents'] if b['id']!=a['id'])
                    assert table==[dict(quantity=q,own_profit=(max(0,30-rivals-q)-6)*q) for q in range(13)]
                else:
                    assert table is None
        totals[gt['seed'],gt['condition']]=sum(quantities)
        lag_regrets[gt['seed'],gt['condition']]=statistics.mean(lag)
        actual_regrets[gt['seed'],gt['condition']]=statistics.mean(actual)
    numerators=[totals[s,'calculator']-totals[s,'none'] for s in range(24060,24065)]
    primary=result['metrics']['quantity']
    assert numerators==primary['exact_seed_difference_numerators']
    assert primary['exact_denominator']==27
    assert abs(sum(numerators)/135-primary['paired_difference']['mean'])<1e-12
    null=[sum(d*sign for d,sign in zip(numerators,signs)) for signs in itertools.product([-1,1],repeat=5)]
    p=sum(v>=sum(numerators) for v in null)/32
    assert p==primary['paired_difference']['exact_signflip_p_upper']
    for name,values in [('lag_conditional_regret',lag_regrets),('actual_stage_regret',actual_regrets)]:
        differences=[values[s,'calculator']-values[s,'none'] for s in range(24060,24065)]
        assert all(abs(a-b)<1e-12 for a,b in zip(differences,result['metrics'][name]['seed_differences']))
    for filename,digest in cfg['sources'].items():
        assert hashlib.sha256(Path(filename).read_bytes()).hexdigest()==digest
    freeze=json.loads(Path('logs/s03_analysis_freeze.json').read_text())
    for filename,digest in freeze['sources'].items():
        assert hashlib.sha256(Path(filename).read_bytes()).hexdigest()==digest
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files+[raw,request_path,directory/'trajectories.jsonl',directory/'ground_truth.jsonl']}
    check=dict(cache_only_replay_all_games=True,raw_cache_unchanged=True,independent_primary_matches=True,
               independent_regret_metrics_match=True,exports_match_authoritative_games=True,source_hashes_match=True,
               games=10,rounds=120,cached_responses=len(cache.entries),
               invalid_attempts=sum(c['attempt']>0 for g in games for c in g['ground_truth']['call_provenance']),
               primary_seed_differences=[n/27 for n in numerators],primary_mean=sum(numerators)/135,
               exact_higher_output_signflip_p=p,sha256=hashes)
    Path('logs/s03_verification.json').write_text(json.dumps(check,indent=2)+'\n')
    print(json.dumps({k:v for k,v in check.items() if k!='sha256'},indent=2))


if __name__=='__main__':
    main()
