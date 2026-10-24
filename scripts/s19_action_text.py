"""Post-outcome descriptive S19 action/explanation audit; no labels or new windows.

Enumerate EVERY negative-type approval in the registered r3..10 window and bind
it to its accepted raw JSON. Explanations are unverified model outputs. This
supplement changes no parser, metric, exclusion, scientific result or verdict.
"""
import hashlib
import json
from pathlib import Path


def main():
    root=Path('data/s19_labels')
    result_path=Path('results/s19_labels.json')
    result=json.loads(result_path.read_text())
    assert result['pilot']=='S19' and not result['dry']
    raw={r['key']:r['response'] for r in map(json.loads,(root/'raw/responses.jsonl').read_text().splitlines())}
    assert result['invalid_attempt_retries']==dict(normative=0,neutral=0), 'This diagnostic binds the zero-retry archive'
    requests={}
    for r in map(json.loads,(root/'raw/requests.jsonl').read_text().splitlines()):
        payload=r['payload']
        assert r['key']==hashlib.sha256(json.dumps([r['dry'],payload]).encode()).hexdigest()
        assert r['response_sha256']==hashlib.sha256(json.dumps(raw[r['key']],sort_keys=True).encode()).hexdigest()
        requests.setdefault((payload[5],payload[6],payload[7]),[]).append((payload[8],r['key']))
    events=[]
    for path in sorted(root.glob('game_*.json')):
        game=json.loads(path.read_text());gt=game['ground_truth'];pair=gt['assigned_pair']
        for row in game['rows'][2:10]:
            for record in row['agents']:
                for author,approved in record['reviews'].items():
                    if not approved or row['market']['passed'][author]:continue
                    attempts=sorted(requests[gt['run_id'],row['round'],record['id']])
                    assert len(attempts)==1 and attempts[0][0]==0, 'Unexpected attempts in zero-retry archive'
                    attempt,key=attempts[0];response=raw[key];obj=json.loads(response['text'])
                    assert obj['reviews']==record['reviews']
                    reason=next(n['reasoning'] for n in gt['reasoning_notes'] if n['round']==row['round'] and n['agent']==record['id'])
                    assert reason==obj['reasoning']
                    events.append(dict(run_id=gt['run_id'],condition=gt['condition'],round=row['round']+1,
                                       reviewer=record['id'],author=author,partner_edge=record['id'] in pair and author in pair,
                                       structured_approval=True,accepted_attempt=attempt,request_key=key,
                                       response_sha256=hashlib.sha256(json.dumps(response,sort_keys=True).encode()).hexdigest(),
                                       reviews=obj['reviews'],reasoning=reason))
    counts={c:dict(partner=sum(e['condition']==c and e['partner_edge'] for e in events),
                   other=sum(e['condition']==c and not e['partner_edge'] for e in events)) for c in ['normative','neutral']}
    # Tie the descriptive event list back to the unchanged primary/secondary counts.
    assert counts['normative']['partner']==round(result['metrics']['pair_bad']['normative']['mean']*40)
    assert counts['neutral']['partner']==round(result['metrics']['pair_bad']['neutral']['mean']*40)
    assert sum(c['other'] for c in counts.values())==sum(round(result['metrics'][k][c]['mean']*40) for k in ['pair_to_outsider_bad','outsider_to_pair_bad'] for c in counts)
    out=dict(post_outcome_descriptive=True,window='registered primary r3..10',
             scientific_result_sha256=hashlib.sha256(result_path.read_bytes()).hexdigest(),
             event_count=len(events),counts=counts,events=events,
             interpretation='Explanations can conflict with structured actions; no automatic semantic/intention labels, agreement verification or causal mechanism attribution.')
    Path('results/s19_action_text.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    lines=['# S19 post-outcome action/explanation audit','',
           'Descriptive inspection after the frozen analysis, using the same registered rounds3..10. Every observed negative-type approval is listed; no exclusions, new window, semantic classifier, agreement label or metric/verdict change. Structured JSON determines the executed action. Explanations are unverified model outputs.','',
           '| Run | Round | Reviewer → author | Partner edge | Accepted JSON reviews | Explanation verbatim |',
           '|---|---:|---|---|---|---|']
    for e in events:
        reason=e['reasoning'].replace('|','\\|').replace('\n',' ')
        lines.append(f"| {e['run_id']} | {e['round']} | {e['reviewer']} → {e['author']} | {e['partner_edge']} | `{json.dumps(e['reviews'])}` | {reason} |")
    lines+=['','Some explanations describe rejection while the structured action approves. One explanation invokes possible reciprocity. These texts do not independently establish intent, agreement, execution of an agreement, or a framing mechanism. No event is removed and the DUD screen is unchanged.','',
            '[Source-bound event JSON](s19_action_text.json) · [Registered outcomes](s19_summary.md).',
            'Reproduce: `uv run python scripts/s19_action_text.py`.']
    Path('results/s19_action_text.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(event_count=len(events),counts=counts,scientific_result_sha256=out['scientific_result_sha256']),indent=2))

if __name__=='__main__':main()
