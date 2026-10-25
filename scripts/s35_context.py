"""POST-OUTCOME S35 descriptive rate-profile census; no new inferential tests or promotion.

Added in response to the final interpretation critic. Frozen estimators, sources,
summary renderer and scientific result remain untouched. Every raw action is
bound by the prospectively frozen independent verifier before counting profiles.
"""
import json
from collections import Counter
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s35_independent import verify


def census():
    bound=verify();assert bound['passed']
    out={}
    for condition in ['symmetric','asymmetric']:
        profiles=Counter();blocks=[];nash=0;notes=0
        for path in sorted(Path('data/s35_asymmetry').glob(f'game_*_{condition}.json')):
            game=json.loads(path.read_text());gt=game['ground_truth'];notes+=len(gt['notes_file'])
            wages=[]
            for row in game['rows'][2:10]:
                agents=row['agents']
                if condition=='asymmetric':agents=sorted(agents,key=lambda a:row['market']['productivity'][a['id']])
                rates=tuple(a['price'] for a in agents)
                profiles[','.join(map(str,rates))]+=1;wages.append(max(rates))
                equilibria={(18,18),(19,19),(20,20)} if condition=='symmetric' else {(19,20),(20,20)}
                nash+=rates in equilibria
            blocks.append(dict(seed=gt['seed'],paid_wages=wages,all_paid10=all(w==10 for w in wages)))
        assert sum(profiles.values())==40 and notes==100 and len(blocks)==5
        out[condition]=dict(primary_rounds=40,profiles=dict(sorted(profiles.items())),profile_order='low/high productivity' if condition=='asymmetric' else 'roster order',pure_nash_profile_rounds=nash,notes_written_all_rounds=notes,blocks=blocks)
    return dict(scope='POST-OUTCOME descriptive context census; no inferential CI, causal mechanism, secondary promotion or change to frozen verdict',passed=True,result_sha256=bound['result_sha256'],conditions=out)

if __name__=='__main__':
    result=census();Path('results/s35_context.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
