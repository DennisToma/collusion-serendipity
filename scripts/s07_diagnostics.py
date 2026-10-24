"""Post-outcome interpretation diagnostics; no refit, new game or verdict change."""
import hashlib
import json
from pathlib import Path


def main():
    root=Path('data/s07_legality')
    result=json.loads(Path('results/s07_legality.json').read_text())
    by={};messages={c:dict(total=0,nonempty=0) for c in ['neutral','legality']}
    for path in root.glob('game_*.json'):
        game=json.loads(path.read_text());gt=game['ground_truth'];by[gt['seed'],gt['condition']]=game
        for m in gt['private_chat']:
            messages[gt['condition']]['total']+=1
            messages[gt['condition']]['nonempty']+=bool(m['text'].strip())
    nums=result['metrics']['quantity']['exact_seed_difference_numerators']
    outlier_seed=24084 # selected post hoc from the plotted largest absolute contrast
    outlier=by[outlier_seed,'legality'];pair=outlier['ground_truth']['assigned_pair']
    pair_actions=[a for row in outlier['rows'][3:] for a in row['agents'] if a['id'] in pair]
    outsider=next(a['id'] for a in outlier['rows'][0]['agents'] if a['id'] not in pair)
    outsider_actions=[a for row in outlier['rows'][3:] for a in row['agents'] if a['id']==outsider]
    clamp_example=outlier['rows'][1]
    diagnostics=dict(review_erratum_clamp_example=dict(seed=outlier_seed,round=2,
        total_output=sum(a['quantity'] for a in clamp_example['agents']),price=clamp_example['market']['price']),
        outlier_outsider_output_r4_12=sum(a['quantity'] for a in outsider_actions)/9,
        outlier_outsider_final_output=next(a['quantity'] for a in outlier['rows'][-1]['agents'] if a['id']==outsider),
        outlier_zero_total_output_rounds_r4_12=sum(sum(a['quantity'] for a in row['agents'])==0 for row in outlier['rows'][3:]),
        primary_window_message_slots_per_arm=5*2*9,
        post_outcome_descriptive=True,primary_verdict_unchanged=result['verdict'],
        all_round_message_counts=messages,largest_absolute_block_selected_post_hoc=outlier_seed,
        outlier_block_difference=nums[-1]/18,other_four_block_mean_difference=sum(nums[:-1])/72,
        outlier_pair_zero_actions_r4_12=sum(a['quantity']==0 for a in pair_actions),
        outlier_pair_actions_r4_12=len(pair_actions),outlier_pair_profit_r4_12=sum(a['profit'] for a in pair_actions)/18,
        arithmetic_note_check=dict(description='Unverified B round2 note claims q12 yields144 if A12/C0 repeat',
                                   conditional_true_profit=(max(0,30-12-12)-6)*12),
        frozen_result_sha256=hashlib.sha256(Path('results/s07_legality.json').read_bytes()).hexdigest())
    Path('logs/s07_diagnostics.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
    print(json.dumps(diagnostics,indent=2))

if __name__=='__main__':main()
