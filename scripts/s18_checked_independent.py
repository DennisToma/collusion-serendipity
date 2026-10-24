"""Publication contract guard around unchanged, frozen S18 independent arithmetic."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if not __debug__:raise RuntimeError('Publication checks require Python without -O')
from scripts.s18_independent import verify

METRICS={'pair_bad','pair_to_outsider_bad','outsider_to_pair_bad','good','pair_score','outsider_score','organization_loss'}
SUMMARY={'mean','mean_exact','ci95','ci95_exact','paired_t_ci95'}
TAILS={'exact_signflip_p_upper','exact_signflip_p_lower','exact_signflip_p_two_sided'}


def checked_verify(directory,result_path):
    r=json.loads(Path(result_path).read_text())
    assert set(r['metrics'])==METRICS,'Incomplete/extra registered metric set'
    assert r['pilot']=='S18' and r['primary_metric']=='pair_bad' and r['primary_contrast']=='shared minus self'
    assert r['n_games']==10 and r['n_seed_blocks']==5 and r['primary_rounds']=='3..10' and r['tuning_attempts']==0
    assert r['model']=='gpt-6-luna' and r['backend']=='codex'
    assert len(r['games'])==10
    assert {(g['seed'],g['condition']) for g in r['games']}=={(s,c) for s in range(24280,24285) for c in ['self','shared']}
    for g in r['games']:assert set(g['primary'])==METRICS,'Incomplete per-game metrics'
    for key,item in r['metrics'].items():
        assert item['exact_denominator']==(24 if key=='good' else 8),'Wrong registered denominator'
        assert len(item['exact_seed_difference_numerators'])==len(item['seed_differences'])==5
        for arm in ['self','shared','paired_difference']:
            assert set(item[arm])==(SUMMARY|TAILS if arm=='paired_difference' else SUMMARY),'Incomplete/extra summary fields'
            for field in ['ci95','ci95_exact','paired_t_ci95']:assert len(item[arm][field])==2
    root=Path(directory);cfg=json.loads((root/'config.json').read_text())
    assert r['dry']==cfg['dry']
    cache=[json.loads(line) for line in (root/'raw/responses.jsonl').read_text().splitlines()]
    requests=[json.loads(line) for line in (root/'raw/requests.jsonl').read_text().splitlines()]
    assert len(cache)==len(requests)==r['cached_responses']
    assert len({row['key'] for row in cache})==len(cache) and len({row['key'] for row in requests})==len(requests)
    checked=verify(directory,result_path)
    # Frozen verifier checks all three tails for every metric; completeness now required.
    checked['sign_tests']=sum(len(TAILS) for _ in r['metrics'])
    assert checked['bootstrap_intervals']==checked['t_intervals']==3*len(METRICS)
    assert checked['raw_metric_cells']==10*len(METRICS)
    checked['complete_registered_contract']=True
    return checked


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s18_workplace');p.add_argument('--result',default='results/s18_workplace.json');p.add_argument('--out',default='logs/s18_independent.json');a=p.parse_args()
    checked=checked_verify(a.data,a.result);Path(a.out).write_text(json.dumps(checked,indent=2)+'\n');print(json.dumps(checked,indent=2))

if __name__=='__main__':main()
