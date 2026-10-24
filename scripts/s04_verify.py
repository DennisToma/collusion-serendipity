"""S04 independent export arithmetic and complete replay with live calls forbidden."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import statistics
import sys
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.advisor import AdvisorCache, run_game


def main():
    directory=Path('data/s04_advisor')
    cfg=json.loads((directory/'config.json').read_text())
    assert not cfg['dry']
    result=json.loads(Path('results/s04_advisor.json').read_text())
    files=sorted(directory.glob('game_*.json'))
    assert len(files)==10
    games=[json.loads(p.read_text()) for p in files]
    raw=directory/'raw'/'responses.jsonl'
    before=raw.read_bytes()
    # A real request makes verification fail immediately; paid cached calls only.
    with patch('sim.common.llm.chat',side_effect=AssertionError('Uncached live call forbidden')):
        cache=AdvisorCache(raw)
        for original in games:
            gt=original['ground_truth']
            with contextlib.redirect_stdout(io.StringIO()):
                replay=run_game(gt['seed'],gt['condition'],cache,cfg['model'],cfg['backend'],cfg['rounds'])
            assert replay['rows']==original['rows']
            actual=dict(replay['ground_truth']);expected=dict(gt)
            for data in [actual,expected]:
                del data['started_utc'];del data['ended_utc']
            assert actual==expected
    assert raw.read_bytes()==before, 'Replay changed response cache'
    # Independently recompute primary from exports without analysis helpers/numpy.
    trajectory=[json.loads(line) for line in (directory/'trajectories.jsonl').read_text().splitlines()]
    metadata=[json.loads(line) for line in (directory/'ground_truth.jsonl').read_text().splitlines()]
    assert len(metadata)==10 and len(trajectory)==120
    by_id={g['run_id']:g for g in metadata}
    assert len(by_id)==10
    exported={(r['run_id'],r['round']):r for r in trajectory}
    assert len(exported)==120
    sums={}
    for g in games:
        gt=g['ground_truth'];rid=gt['run_id'];pair=set(gt['assigned_pair'])
        assert by_id[rid]==gt
        quantities=[];profits=[]
        for t,row in enumerate(g['rows']):
            assert row==exported[rid,t]
            vals={a['id']:a['quantity'] for a in row['agents']}
            price=max(0,30-sum(vals.values()))
            assert price==row['market']['price']
            for a in row['agents']:
                assert a['profit']==(price-6)*a['quantity']
                if t>=3 and a['id'] in pair:
                    quantities.append(a['quantity']);profits.append(a['profit'])
        sums[gt['seed'],gt['condition']]=(statistics.mean(quantities),statistics.mean(profits))
    differences=[sums[seed,'shared'][0]-sums[seed,'independent'][0] for seed in range(24040,24045)]
    primary=result['metrics']['pair_quantity']
    assert all(abs(a-b)<1e-12 for a,b in zip(differences,primary['seed_differences']))
    assert abs(statistics.mean(differences)-primary['paired_difference']['mean'])<1e-12
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files+[raw,directory/'trajectories.jsonl',directory/'ground_truth.jsonl']}
    check=dict(cache_only_replay_all_games=True,raw_cache_unchanged=True,independent_primary_matches=True,
               exports_match_authoritative_games=True,games=10,rounds=120,
               cached_responses=len(cache.entries),primary_seed_differences=differences,
               primary_mean=statistics.mean(differences),sha256=hashes)
    Path('logs/s04_verification.json').write_text(json.dumps(check,indent=2)+'\n')
    print(json.dumps({k:v for k,v in check.items() if k!='sha256'},indent=2))

if __name__=='__main__':
    main()
