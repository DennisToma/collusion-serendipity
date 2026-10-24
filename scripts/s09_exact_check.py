"""Post-review analytic resampling/quantity diagnostic; frozen estimates unchanged."""
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np

r=json.loads(Path('results/s09_replay.json').read_text())
nums=r['metrics']['quantity']['exact_seed_difference_numerators']
fork=r['fork_seed_differences']
checks={}
for name,values,denom,reported in [('primary',nums,12,r['metrics']['quantity']['paired_difference']),
                                   ('fork',fork,1,r['fork_quantity_difference'])]:
    means=[sum(Fraction(values[i]) for i in idx)/ (5*denom) for idx in itertools.product(range(5),repeat=5)]
    exact_ci=np.quantile([float(m) for m in means],[.025,.975]).tolist()
    assert exact_ci==reported['ci95']
    distribution={str(k):v for k,v in sorted(Counter(means).items())}
    checks[name]=dict(ordered_resamples=len(means),exact_bootstrap_ci95=exact_ci,
                     frozen_monte_carlo_ci95=reported['ci95'],distribution_counts=distribution)
histograms={cond:Counter() for cond in ['retain','erase']}
pair_histograms={cond:Counter() for cond in ['retain','erase']}
for p in sorted(Path('data/s09_replay').glob('game_*.json')):
    g=json.loads(p.read_text());gt=g['ground_truth'];cond=gt['condition'];pair=gt['assigned_pair']
    for row in g['rows'][6:]:
        for a in row['agents']:
            histograms[cond][a['quantity']]+=1
            if a['id'] in pair:pair_histograms[cond][a['quantity']]+=1
out=dict(posthoc_diagnostic=True,frozen_estimates_changed=False,exact_checks=checks,
         all_agent_quantity_counts={k:dict(sorted(v.items())) for k,v in histograms.items()},
         pair_quantity_counts={k:dict(sorted(v.items())) for k,v in pair_histograms.items()},
         result_sha256=hashlib.sha256(Path('results/s09_replay.json').read_bytes()).hexdigest(),
         inference_limit='Exact empirical bootstrap checks arithmetic under the same resampling assumptions; not independent population validation.')
Path('logs/s09_exact_check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
