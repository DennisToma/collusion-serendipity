"""Post-outcome enumeration of ALL S65 primary TYPE-Y choices, no semantic labels.

This adds a complete descriptive text appendix, not a new metric, window,
exclusion, effect estimate, significance test or classification.
"""
import hashlib,json
from pathlib import Path


def render():
    root=Path('data/s65_bonus_pooling');result=json.loads(Path('results/s65_bonus_pooling.json').read_text())
    assert result['pilot']=='S65' and not result['dry']
    raw={r['key']:r['response'] for r in map(json.loads,(root/'raw/responses.jsonl').read_text().splitlines())}
    requests={}
    for request in map(json.loads,(root/'raw/requests.jsonl').read_text().splitlines()):
        payload=request['payload'];key=request['key']
        assert key==hashlib.sha256(json.dumps([request['dry'],payload]).encode()).hexdigest()
        assert request['response_sha256']==hashlib.sha256(json.dumps(raw[key],sort_keys=True).encode()).hexdigest()
        requests.setdefault((payload[5],payload[6],payload[7]),[]).append(request)
    events=[]
    for path in sorted(root.glob('game_*.json')):
        g=json.loads(path.read_text());gt=g['ground_truth'];condition=gt['condition']
        for row in g['rows'][2:10]:
            for rec in row['agents']:
                author=next(iter(rec['reviews']))
                if row['market']['passed'][author]:continue
                req=max(requests[gt['run_id'],row['round'],rec['id']],key=lambda q:q['payload'][8]);response=raw[req['key']]
                text=response['text'];text=text[8:-4] if text.startswith('```json\n') and text.endswith('\n```') else text
                obj=json.loads(text);assert obj['reviews']==rec['reviews']
                assert obj['reasoning']==next(n['reasoning'] for n in gt['reasoning_notes'] if n['round']==row['round'] and n['agent']==rec['id'])
                assert obj['note']==next(n['text'] for n in gt['notes_file'] if n['round']==row['round']+1 and n['author']==rec['id'])
                events.append(dict(run_id=gt['run_id'],condition=condition,round=row['round']+1,
                                   reviewer=rec['id'],author=author,approved=rec['reviews'][author],
                                   reviewer_final_stage_increment_if_approve=2 if condition=='pooled' else -2,
                                   reasoning=obj['reasoning'],emitted_note=obj['note'],request_key=req['key'],response_sha256=req['response_sha256']))
    assert len(events)==80 and len({(e['run_id'],e['round'],e['reviewer']) for e in events})==80
    for c in ['individual','pooled']:
        selected=[e for e in events if e['condition']==c]
        assert len(selected)==40 and sum(e['approved'] for e in selected)==round(result['metrics']['pair_bad'][c]['mean']*40)
    out=dict(post_outcome_descriptive=True,registered_window='r3..10',event_count=80,
             scientific_result_sha256=hashlib.sha256(Path('results/s65_bonus_pooling.json').read_bytes()).hexdigest(),events=events,
             limits='All primary TYPE-Y choices, including rejection. Returned explanations are unverified; no semantic/intention labels, additional statistical endpoints or mechanism inference. Current notes become visible only after both decisions.')
    Path('results/s65_all_y_decisions.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    lines=['# S65 — All primary TYPE-Y choices','',
           'Post-outcome descriptive appendix: all80 registered-primary TYPE-Y decisions, including rejections. All approved and rejected cases retained. Statements below are unverified model outputs. No semantic labels, mechanism claim, new window, metric, significance test or promotion rule. Final reviewer stage increment if approving is −2 individual, +2 pooled; rejecting yields0. Current emitted notes become visible after both decisions.','',
           '| Run | Round | Reviewer → author | Approve | Final stage increment if approve | Explanation verbatim | Emitted note verbatim |',
           '|---|---:|---|---|---:|---|---|']
    def quote(s):return s.replace('|','\\|').replace('\n',' ')
    for e in events:
        lines.append(f"| {e['run_id']} | {e['round']} | {e['reviewer']} → {e['author']} | {e['approved']} | {e['reviewer_final_stage_increment_if_approve']} | {quote(e['reasoning'])} | {quote(e['emitted_note'])} |")
    lines+=['','[Request-bound JSON](s65_all_y_decisions.json) · [Frozen registered outcomes](s65_summary.md).',
            'Reproduce: `uv run python scripts/s65_decisions.py`.']
    Path('results/s65_all_y_decisions.md').write_text('\n'.join(lines)+'\n')
    print('PASS all80 primary TYPE-Y raw action/reason/note bindings')

if __name__=='__main__':render()
