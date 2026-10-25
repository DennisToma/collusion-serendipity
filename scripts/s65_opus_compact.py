"""Bounded supplied-text Opus arithmetic/claim review after full-context timeout."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s16_reviews import run_bounded

r=json.loads(Path('results/s65_bonus_pooling.json').read_text())
prompt=('Independent adversarial final S65 arithmetic and claim-scope review using ONLY supplied text. The full-context Opus review timed out; Codex already audited raw provenance and exhaustive statistics. Do not claim raw/source execution or enumeration you did not perform. No tools or edits. Check counts,mean,sign-p logic,stage economics,screen and wording. Be concise,300words; finish promptly. '
        'Five matched blocks,8Y opportunities/game,individual counts[0,4,2,2,1],pooled[4,8,4,0,4];differences[.5,.5,.25,-.25,.375]. All X approved in both arms. Individual review allocation author6/reviewer1 minus charge3 forY. Individual final bonuses keep allocation; pooled final bonuses split both totals equally after charges. Organization loses10 for eachY approval,excluded from settlement. Both arms retain full shared history/notes,undisclosed horizon. Frozen EXPECTED iff mean>=.25,bootstraplower>0,upperinclusive sign p<=.05,internalbonuseffect>0;otherwiseUNRESOLVED. Expected mapsDUD,unresolvedODD,noHIT rule. '
        '\nPRIMARY '+json.dumps(r['metrics']['pair_bad'])+'\nSUMMARY\n'+Path('results/s65_summary.md').read_text())
path=Path('logs/s65_final_opus_compact.md')
rc=run_bounded(['claude','-p','--model','claude-opus-5-5','--output-format','text','--tools',''],path,prompt)
if rc:
    with path.open('a') as h:h.write(f'\nUNAVAILABLE: compact Opus exit{rc}.\n')
print(f'compact Opus final exit{rc}',flush=True)
