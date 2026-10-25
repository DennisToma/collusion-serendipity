"""POST-OUTCOME quote-coordinate census; no new inference, labels or promotion.

Added at the supplied-text final critic's request. Frozen scientific sources,
results and summary renderer remain unchanged. Separate raw reconstruction binds
all decisions before this descriptive census. No model calls are allowed.
"""
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s36_independent import verify


def census():
    with patch('sim.common.llm.chat',side_effect=AssertionError('Context census forbids model calls')):
        bound=verify()
    assert bound['passed'] and bound['raw_keys']==200
    r=json.loads(Path('results/s36_grossnet.json').read_text());arms={}
    for condition,offset in [('net',0),('gross',10)]:
        games=[json.loads(p.read_text()) for p in sorted(Path('data/s36_grossnet').glob(f'game_*_{condition}.json'))]
        assert len(games)==5
        rows=[row for g in games for row in g['rows'][2:]]
        quotes=[a['price'] for row in rows for a in row['agents']]
        profiles=Counter(tuple(a['price'] for a in row['agents']) for row in rows)
        assert len(quotes)==80 and len(rows)==40
        mean=Fraction(sum(quotes),len(quotes))
        normalized=Fraction(str(r['metrics']['offered_rate'][condition]['mean']))
        assert mean==normalized+offset
        arms[condition]=dict(primary_decisions=80,primary_rounds=40,quote_offset=offset,
            raw_mean_quote=float(mean),raw_mean_quote_exact=str(mean),
            normalized_mean_offer=float(normalized),normalized_mean_offer_exact=str(normalized),
            quote_counts={str(q):n for q,n in sorted(Counter(quotes).items())},
            raw_profile_counts={','.join(map(str,p)):n for p,n in sorted(profiles.items())})
    return dict(scope='POST-OUTCOME manager descriptive quote census requested by supplied-text final critic;no mechanism,screen,inference or promotion',
        passed=True,scientific_result_sha256=hashlib.sha256(Path('results/s36_grossnet.json').read_bytes()).hexdigest(),
        raw_bound_decisions=bound['notes_and_reasons'],arms=arms)


if __name__=='__main__':
    Path('results/s36_context.json').write_text(json.dumps(census(),indent=2)+'\n')
    print('PASS post-outcome quote-coordinate census;frozen scientific result unchanged')
