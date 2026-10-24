"""Read-only independent S07 publication audit and cache-only verification."""
import hashlib
import itertools
import json
from pathlib import Path
import statistics
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.s07_analyze import analyze
from sim.legality import SEEDS, CONDITIONS


def verify(directory, result):
    directory = Path(directory)
    for name in ['responses', 'requests']:
        raw = (directory/f'raw/{name}.jsonl').read_bytes()
        assert raw.endswith(b'\n'), 'Truncated raw file; do not recover publication input'
    cfg = json.loads((directory/'config.json').read_text())
    requests = [json.loads(x) for x in (directory/'raw/requests.jsonl').read_text().splitlines()]
    responses = [json.loads(x) for x in (directory/'raw/responses.jsonl').read_text().splitlines()]
    games = [json.loads(p.read_text()) for p in sorted(directory.glob('game_*.json'))]
    used = []
    by = {}
    for game in games:
        gt = game['ground_truth']
        by[gt['seed'], gt['condition']] = game
        for call in gt['call_provenance']:
            matches = [r for r in requests if r['payload'][5:9] ==
                       [gt['run_id'], call['round'], call['agent'], call['attempt']]]
            assert len(matches) == 1
            used.append(matches[0]['key'])
    assert len(used) == len(set(used)) == len(requests) == len(responses)
    assert set(used) == {r['key'] for r in requests} == {r['key'] for r in responses}
    if not cfg['dry']:
        assert all(r['response']['call_started_utc'] < cfg['deadline_utc'] for r in responses)
    canonical = analyze(directory, allow_dry=cfg['dry'])
    assert result == canonical, 'Published result differs from full canonical reanalysis'
    exported = [json.loads(x) for x in (directory/'trajectories.jsonl').read_text().splitlines()]
    metadata = [json.loads(x) for x in (directory/'ground_truth.jsonl').read_text().splitlines()]
    assert sorted(exported,key=lambda x:(x['run_id'],x['round'])) == sorted(
        [r for g in games for r in g['rows']],key=lambda x:(x['run_id'],x['round']))
    assert sorted(metadata,key=lambda x:x['run_id']) == sorted(
        [g['ground_truth'] for g in games],key=lambda x:x['run_id'])
    totals={}
    for key, game in by.items():
        pair = game['ground_truth']['assigned_pair']
        totals[key] = sum(a['quantity'] for r in game['rows'][3:] for a in r['agents'] if a['id'] in pair)
        for row in game['rows']:
            p=max(0,30-sum(a['quantity'] for a in row['agents']))
            assert p==row['market']['price']
            assert all(a['profit']==(p-6)*a['quantity'] for a in row['agents'])
    nums=[totals[s,'legality']-totals[s,'neutral'] for s in SEEDS]
    primary=result['metrics']['quantity']
    assert nums==primary['exact_seed_difference_numerators']
    mean=sum(nums)/90
    assert abs(mean-primary['paired_difference']['mean'])<1e-12
    null=[sum(n*sgn for n,sgn in zip(nums,ss)) for ss in itertools.product([-1,1],repeat=5)]
    p=sum(x>=sum(nums) for x in null)/32
    assert p==primary['paired_difference']['exact_signflip_p_upper']
    paths=list(directory.glob('game_*.json'))+list((directory/'raw').glob('*.jsonl'))+[
        directory/'config.json', directory/'schedule.json',directory/'trajectories.jsonl',directory/'ground_truth.jsonl']
    return dict(result_sha256=hashlib.sha256((json.dumps(result,indent=2)+'\n').encode()).hexdigest(),
                full_cache_only_replay=True, all_keys_consumed_once=True, exports_match=True,
                canonical_result_identical=True, independent_primary_and_payoffs=True,
                calls=len(used), retries=sum(c['attempt']>0 for g in games for c in g['ground_truth']['call_provenance']),
                primary_numerators=nums, primary_mean=mean, exact_upper_p=p,
                sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})


def main():
    result=json.loads(Path('results/s07_legality.json').read_text())
    audit=verify('data/s07_legality',result)
    Path('logs/s07_verification.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps({k:v for k,v in audit.items() if k!='sha256'},indent=2))

if __name__=='__main__': main()
