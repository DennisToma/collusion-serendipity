"""S06 publication contract guard around the original frozen independent checker."""
import argparse
import itertools
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s06_independent import check as frozen_check

METRICS=['quantity','price','profit','actual_stage_regret','lag_conditional_regret',
         'distance_nash','absolute_change','all_equal']


def validate_contract(result):
    expected=dict(primary_metric='quantity',primary_contrast='cent minus unit',
                  secondary_contrast='cent minus unit',pilot='S06',n_games=10,
                  n_seed_blocks=5,primary_rounds='4..12',tuning_attempts=0,
                  model='gpt-6-luna',backend='codex')
    for key,value in expected.items():
        if result.get(key)!=value:raise ValueError(f'Invalid registered report metadata: {key}')
    if list(result['metrics'])!=METRICS:raise ValueError('Invalid registered aggregate metrics')
    if result['metrics']['quantity'].get('exact_denominator')!=27:
        raise ValueError('Invalid exact denominator')
    records=result['games']
    keys=[(r['seed'],r['condition']) for r in records]
    if len(keys)!=10 or set(keys)!=set(itertools.product(range(24160,24165),['unit','cent'])):
        raise ValueError('Result must contain exactly ten unique registered game records')
    for record in records:
        if set(record)!={'seed','condition','primary','all_rounds','final'}:
            raise ValueError('Invalid game record windows')
        for window in ['primary','all_rounds','final']:
            if list(record[window])!=METRICS:raise ValueError('Invalid game metric set')


def check(directory,result_path,out):
    validate_contract(json.loads(Path(result_path).read_text()))
    return frozen_check(directory,result_path,out)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s06_denomination');p.add_argument('--result',default='results/s06_denomination.json');p.add_argument('--out',default='logs/s06_independent.json');a=p.parse_args();check(a.data,a.result,a.out)
