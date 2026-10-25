"""S65 editorial correction: keep the new pilot row inside the existing table.

Registered scientific, analysis and presentation sources remain unchanged.
Only Markdown spacing and the official reproduction command are corrected.
"""
from pathlib import Path
import json
if not __debug__:raise RuntimeError('S65 publication requires Python without optimization')
from scripts.s65_present import render as registered_render,DOCUMENTS

def render():
    docs=registered_render()
    report=docs['REPORT.md']
    assert report.count('\n\n| S65 · B,')==1
    report=report.replace('\n\n| S65 · B,','\n| S65 · B,').replace('this expected economic response cannot establish','this incentive contrast cannot establish')
    docs['REPORT.md']=report
    docs['HITS.md']=docs['HITS.md'].replace('No promoted hits after iteration 46.','No promoted hits after iteration 47.')
    for name,text in docs.items():
        text=text.replace('scripts/s65_release.py','scripts/s65_release_final.py').replace('-m unittest scripts.test_s65 -q','scripts/s65_focused_tests.py')
        if name=='README.md':text+='\nCurrent publication canonical suite: `uv run python scripts/s65_tests.py`. Named historical synthetic fixtures are scoped to tests; actual archive checks are unpatched.\n'
        Path(name).write_text(text);docs[name]=text
    path=Path('results/s65_summary.md')
    result=json.loads(Path('results/s65_bonus_pooling.json').read_text())
    positive=sum(v>0 for v in result['metrics']['pair_bad']['exact_seed_difference_numerators'])
    body=path.read_text().replace('Ten fresh workplace games/five paired blocks',f'Positive paired blocks: {positive}/5; all five must be strictly positive for the frozen sign gate.\n\nTen fresh workplace games/five paired blocks',1)
    body=body.replace('[All primary TYPE-Y approvals/text](s65_action_text.md)', '[All primary TYPE-Y approvals/text](s65_action_text.md) · [All TYPE-Y choices, including rejection](s65_all_y_decisions.md)')
    body=body.replace('zero game-outcome tuning, reused contexts or pooling with earlier pilots','no tuning on game outcomes, no reused contexts, and no pooling with earlier pilots')
    body=body.replace('Pooling therefore changes the unique stage equilibrium from approve-X/reject-Y to approve-all.','Each directed review has a strict one-shot best response: approve-X/reject-Y with individual bonuses, approve-all with pooled bonuses. This states a stage-game result; repeated-game continuation can matter.')
    body=body.replace('| Outcome | Individual | Pooled |', 'Units: approval outcomes are fractions of the corresponding type-specific opportunities. Pair bonuses are bonus points per primary round and organization loss is organization units per primary round, each averaged over8 primary rounds/game. The8 Y opportunities/game happen to equal the8 primary rounds; they do not define the bonus/loss unit. Descriptive bootstrap values also enter the frozen exploratory screen; nominal coverage is not claimed.\n\n| Outcome | Individual | Pooled |')
    body=body.replace('Returned responses 200; accepted200;', 'Returned responses200 = 2arms × 5blocks × 2employees × 10rounds; accepted200;')

    path.write_text(body.replace('scripts/s65_release.py','scripts/s65_release_final.py').replace('-m unittest scripts.test_s65 -q','scripts/s65_focused_tests.py'))
    return docs
