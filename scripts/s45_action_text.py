"""Post-outcome S45 transparency census; quotes only,no mechanism/intent labels."""
from datetime import datetime,timezone
import hashlib,json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s45_analyze import analyze
from scripts.s45_independent import verify

def main():
    root=Path('data/s45_reviewring');result=analyze(root)
    assert json.dumps(result,indent=2)+'\n'==Path('results/s45_reviewring.json').read_text()
    verify(root,'results/s45_reviewring.json')
    responses={row['key']:row['response'] for row in map(json.loads,(root/'raw/responses.jsonl').read_text().splitlines())}
    requests=list(map(json.loads,(root/'raw/requests.jsonl').read_text().splitlines()))
    cases=[];decisions=0
    for path in sorted(root.glob('game_*.json')):
        game=json.loads(path.read_text());gt=game['ground_truth']
        for row in game['rows']:
            for rec in row['agents']:
                decisions+=1
                for target,approved in rec['reviews'].items():
                    if not approved or row['market']['passed'][target]:continue
                    attempts=[r for r in requests if r['payload'][5:8]==[gt['run_id'],row['round'],rec['id']]]
                    request=max(attempts,key=lambda r:r['payload'][8]);raw=responses[request['key']]['text'];obj=json.loads(raw)
                    assert obj['reviews']==rec['reviews']
                    assert obj['reasoning']==next(n['reasoning'] for n in gt['reasoning_notes'] if n['round']==row['round'] and n['agent']==rec['id'])
                    assert obj['note']==next(n['text'] for n in gt['notes_file'] if n['round']==row['round']+1 and n['author']==rec['id'])
                    cases.append(dict(run_id=gt['run_id'],seed=gt['seed'],condition=gt['condition'],round_1_based=row['round']+1,primary_window=row['round']>=2,reviewer=rec['id'],target=target,target_supported=False,recommendation=approved,request_key=request['key'],raw_response_text=raw,reasoning=obj['reasoning'],note=obj['note']))
    assert decisions==200
    primary_cases=[c for c in cases if c['primary_window']]
    expected={condition:sum(round(g['primary']['pair_bad']*8) for g in result['games'] if g['condition']==condition) for condition in ['self','shared']}
    assert {condition:sum(c['condition']==condition for c in primary_cases) for condition in ['self','shared']}==expected
    payload=dict(pilot='S45',status='POST-OUTCOME descriptive full census;no labels or secondary promotion',decisions_checked=decisions,cases=cases,case_count=len(cases),primary_cases=len(primary_cases),warmup_cases=len(cases)-len(primary_cases),source_result_sha256=hashlib.sha256(Path('results/s45_reviewring.json').read_bytes()).hexdigest(),raw_response_file_sha256=hashlib.sha256((root/'raw/responses.jsonl').read_bytes()).hexdigest())
    Path('results/s45_action_text.json').write_text(json.dumps(payload,indent=2)+'\n')
    lines=['# S45 — All unsupported recommendations: actions and text','',
           '**Post-outcome descriptive transparency appendix.** This census was added after the primary result was known. It lists every positive recommendation of an UNSUPPORTED product,including warm-up rounds. No semantic,error,intent,agreement or coordination label is assigned. It changes no registered outcome,threshold or verdict.','',
           f'{decisions} archived decisions checked; {len(cases)} unsupported recommendation(s),of which {len(primary_cases)} in primary rounds3–10 and {len(cases)-len(primary_cases)} in warm-up rounds1–2. These are counts,not a prevalence estimate or an additional hypothesis test.','',
           'The commission/audit cost belongs to the reviewer;the8-point sale belongs to the recommended seller. Explanations and notes do not establish why an action occurred. Public actions remain observable in both arms;the self-only arm is not a no-signaling environment.','']
    for case in cases:
        lines += [f"## {case['run_id']} · round {case['round_1_based']} · {case['reviewer']} recommends {case['target']}",'',
                  f"Target quality UNSUPPORTED;submitted recommendation=true;primary window={case['primary_window']}. Request key `{case['request_key']}`. Exact returned JSON:",'']
        fence='`'*max(3,max((len(x) for x in re.findall(r'`+',case['raw_response_text'])),default=0)+1)
        lines += [fence+'json',case['raw_response_text'],fence,'']
    lines += ['[Canonical result](s45_reviewring.json) · [Registered methods](../DESIGN_S45.md) · [Raw responses](../data/s45_reviewring/raw/responses.jsonl) · [Raw requests](../data/s45_reviewring/raw/requests.jsonl) · [Machine-readable census](s45_action_text.json).','Reproduce: `uv run python scripts/s45_action_text.py`.']
    Path('results/s45_action_text.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in payload.items() if k!='cases'},indent=2))

if __name__=='__main__':main()
