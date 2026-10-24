"""Post-outcome descriptive S27 action/explanation audit; no labels or new windows.

Enumerate EVERY registered-primary partner negative-type approval in the registered r3..10 window and bind
it to its accepted raw JSON. Explanations are unverified model outputs. This
supplement changes no parser, metric, exclusion, scientific result or verdict.
"""
import hashlib
import json
from pathlib import Path


def main():
    root=Path('data/s27_concentration')
    result_path=Path('results/s27_concentration.json')
    result=json.loads(result_path.read_text())
    assert result['pilot']=='S27' and not result['dry']
    raw={r['key']:r['response'] for r in map(json.loads,(root/'raw/responses.jsonl').read_text().splitlines())}
    assert result['invalid_attempt_retries']==dict(three=0,two=0), 'This diagnostic binds the zero-retry archive'
    requests={}
    for r in map(json.loads,(root/'raw/requests.jsonl').read_text().splitlines()):
        payload=r['payload']
        assert r['key']==hashlib.sha256(json.dumps([r['dry'],payload]).encode()).hexdigest()
        assert r['response_sha256']==hashlib.sha256(json.dumps(raw[r['key']],sort_keys=True).encode()).hexdigest()
        requests.setdefault((payload[5],payload[6],payload[7]),[]).append((payload[8],r['key']))
    events=[]
    paths=sorted(root.glob('game_*.json'))
    assert len(paths)==result['n_games']==10
    for path in paths:
        game=json.loads(path.read_text());gt=game['ground_truth'];pair=gt['assigned_pair']
        for row in game['rows'][2:10]:
            for record in row['agents']:
                for author,approved in record['reviews'].items():
                    if not approved or row['market']['passed'][author] or not(record['id'] in pair and author in pair):continue
                    attempts=sorted(requests[gt['run_id'],row['round'],record['id']])
                    assert len(attempts)==1 and attempts[0][0]==0, 'Unexpected attempts in zero-retry archive'
                    attempt,key=attempts[0];response=raw[key];obj=json.loads(response['text'])
                    assert obj['reviews']==record['reviews']
                    reason=next(n['reasoning'] for n in gt['reasoning_notes'] if n['round']==row['round'] and n['agent']==record['id'])
                    assert reason==obj['reasoning']
                    note=next(n['text'] for n in gt['notes_file'] if n['round']==row['round']+1 and n['author']==record['id'])
                    assert note==obj['note']
                    events.append(dict(run_id=gt['run_id'],condition=gt['condition'],round=row['round']+1,
                                       reviewer=record['id'],author=author,partner_edge=record['id'] in pair and author in pair,
                                       structured_approval=True,accepted_attempt=attempt,request_key=key,
                                       response_sha256=hashlib.sha256(json.dumps(response,sort_keys=True).encode()).hexdigest(),
                                       reviews=obj['reviews'],reviewer_charge=row['market']['penalties'][record['id']][author],
                                       reviewer_directed_bonus=1-row['market']['penalties'][record['id']][author],author_directed_bonus=6,reasoning=reason,note=obj['note']))
    counts={c:sum(e['condition']==c for e in events) for c in ['three','two']}
    # Enumerate all and only registered-primary adverse partner decisions.
    for c in counts:assert counts[c]==round(result['metrics']['pair_bad'][c]['mean']*40)
    assert len({(e['run_id'],e['round'],e['reviewer'],e['author']) for e in events})==len(events)
    assert all(e['reviewer_charge']==3 for e in events)
    out=dict(post_outcome_descriptive=True,window='registered primary r3..10',
             scientific_result_sha256=hashlib.sha256(result_path.read_bytes()).hexdigest(),
             event_count=len(events),counts=counts,events=events,
             interpretation='Unverified explanations include reciprocity language and payoff-role confusion; no automatic semantic/intention labels, agreement verification or causal mechanism attribution.')
    Path('results/s27_action_text.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    lines=['# S27 post-outcome action/explanation audit','',
           'Descriptive inspection after the frozen analysis, using the same registered rounds3..10. Every registered-primary partner negative-type approval is listed; no exclusions, new window, semantic classifier, agreement label or metric/verdict change. Structured JSON determines the executed action. Explanations are unverified model outputs.','',
           '| Run | Round | Reviewer → author | Partner edge | Accepted JSON reviews | Reviewer charge | Explanation verbatim | Note verbatim |',
           '|---|---:|---|---|---|---:|---|---|']
    for e in events:
        reason=e['reasoning'].replace('|','\\|').replace('\n',' ')
        lines.append(f"| {e['run_id']} | {e['round']} | {e['reviewer']} → {e['author']} | {e['partner_edge']} | `{json.dumps(e['reviews'])}` | {e['reviewer_charge']} | {reason} | {e['note'].replace(chr(10),' ').replace(chr(124),chr(92)+chr(124))} |")
    lines+=['','The listed outputs include explicit reciprocity language (e.g.24440_two r5) and explanations that misattribute author points or omit the reviewer charge (e.g.24443_two r10). These are post-outcome examples, not verified beliefs or a semantic classifier. Texts do not establish agreement, executed reciprocal deals or a team-size mechanism. No event is removed and the frozen ODD screen is unchanged.','',
            '[Source-bound event JSON](s27_action_text.json) · [Registered outcomes](s27_summary.md).',
            'Reproduce: `uv run python scripts/s27_action_text.py`.']
    Path('results/s27_action_text.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(event_count=len(events),counts=counts,scientific_result_sha256=out['scientific_result_sha256']),indent=2))

if __name__=='__main__':main()
