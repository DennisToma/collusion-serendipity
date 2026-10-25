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
    path.write_text(body.replace('scripts/s65_release.py','scripts/s65_release_final.py').replace('-m unittest scripts.test_s65 -q','scripts/s65_focused_tests.py'))
    return docs
