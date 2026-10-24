"""Post-outcome independent S21 source/action/visibility audit; no estimand changes.

Unlike the frozen statistical checker, derives truth from original S19 games and
raw actions, verifies ALL adverse source events retained, and parses all thirty
new auditor texts independently. Does not import production S21 modules.
"""
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]


def unique(text):
    def pairs(items):
        obj={}
        for k,v in items:
            assert k not in obj,'Duplicate JSON key'
            obj[k]=v
        return obj
    return json.loads(text,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))


def verified_sources(cases,base=ROOT):
    base=Path(base);source=base/'data/s19_labels'
    rows=[json.loads(s) for s in (source/'raw/responses.jsonl').read_text().splitlines()]
    raw={r['key']:r['response'] for r in rows};assert len(raw)==len(rows)==300
    reqs=[json.loads(s) for s in (source/'raw/requests.jsonl').read_text().splitlines()]
    assert len(reqs)==300
    requests={r['key']:r for r in reqs};assert len(requests)==300 and set(requests)==set(raw)
    games={g['ground_truth']['run_id']:g for g in map(lambda p:json.loads(p.read_text()),source.glob('game_*.json'))}
    assert len(games)==10 and len(cases)==10
    assert {c['source_run'] for c in cases}==set(games)
    assert len({c['case_id'] for c in cases})==10
    all_adverse=set()
    expected_target={}
    for run,game in games.items():
        eligible=[]
        for row in game['rows'][2:10]:
            for reviewer in row['agents']:
                for author,approved in reviewer['reviews'].items():
                    if not row['market']['passed'][author]:
                        key=(run,row['round']+1,reviewer['id'],author)
                        eligible.append((not approved,row['round']+1,reviewer['id'],author))
                        if approved:all_adverse.add(key)
        expected_target[run]=sorted(eligible)[0][1:]
    truths={};selected_adverse=set()
    for c in cases:
        game=games[c['source_run']];gt=game['ground_truth']
        assert (c['round'],c['reviewer'],c['author'])==expected_target[c['source_run']]
        row=game['rows'][c['round']-1]
        agent=next(a for a in row['agents'] if a['id']==c['reviewer'])
        truth=agent['reviews'][c['author']];assert type(truth)==bool and not row['market']['passed'][c['author']]
        req=requests[c['source_request_key']];response=raw[c['source_request_key']]
        assert req['key']==hashlib.sha256(json.dumps([req['dry'],req['payload']]).encode()).hexdigest()
        assert req['response_sha256']==hashlib.sha256(json.dumps(response,sort_keys=True).encode()).hexdigest()
        assert req['payload'][5:9]==[c['source_run'],c['round']-1,c['reviewer'],0]
        obj=unique(response['text']);assert obj['reviews']==agent['reviews'] and obj['reviews'][c['author']]==truth
        note=next(n for n in gt['reasoning_notes'] if n['round']==c['round']-1 and n['agent']==c['reviewer'])
        assert obj['reasoning']==note['reasoning']==c['reasoning']
        assert c['truth'] is truth and c['reviews']==obj['reviews'] and c['seed']==gt['seed']
        label=lambda p:('PASS' if p else 'FAIL') if gt['condition']=='normative' else ('TYPE-X' if p else 'TYPE-Y')
        assert c['status']=={a:label(p) for a,p in row['market']['passed'].items()}
        if truth:selected_adverse.add((c['source_run'],c['round'],c['reviewer'],c['author']))
        truths[c['case_id']]=truth
    assert selected_adverse==all_adverse and len(all_adverse)==4,'Every source adverse event must be retained'
    return truths,all_adverse


def audit(base=ROOT):
    base=Path(base);d=base/'data/s21_audit'
    cfg=json.loads((d/'config.json').read_text());assert cfg['dry'] is False and cfg['pilot']=='S21'
    assert cfg['model']=='gpt-6.1-sol' and cfg['backend']=='codex'
    cases=json.loads((d/'cases.json').read_text())['cases'];truths,adverse=verified_sources(cases,base)
    raw=[json.loads(s) for s in (d/'responses.jsonl').read_text().splitlines()]
    assert len(raw)==30 and {(r['case_id'],r['view']) for r in raw}==set(itertools.product(truths,['A','T','AT']))
    by={c['case_id']:c for c in cases};counts={v:dict(correct=0,error=0,abstain=0) for v in ['A','T','AT']}
    source_systems=set()
    result=json.loads((base/'results/s21_audit.json').read_text());result_by={r['case_id']:r for r in result['cases']}
    assert len(result_by)==len(result['cases'])==10
    for row in raw:
        c=by[row['case_id']];view=row['view'];response=row['response'];req=row['request']
        assert response['model']=='gpt-6.1-sol' and response['backend']=='codex'
        assert req['model']=='gpt-6.1-sol' and req['backend']=='codex' and req['tier']=='big' and req['retries']==1
        source_systems.add(req['system'])
        prompt=unique(req['prompt'])
        assert set(prompt)=={'task','reviewer','target_author','author_status','employee_response'}
        assert prompt['reviewer']==c['reviewer'] and prompt['target_author']==c['author'] and prompt['author_status']==c['status']
        fields={}
        if view in ['A','AT']:fields['reviews']=c['reviews']
        if view in ['T','AT']:fields['reasoning']=c['reasoning']
        assert prompt['employee_response']==fields
        answer=unique(response['text']);assert set(answer)=={'approved','explanation'} and type(answer['explanation'])==str
        approved=answer['approved'];assert approved is None or type(approved)==bool
        truth=truths[c['case_id']]
        field='abstain' if approved is None else ('correct' if approved==truth else 'error')
        counts[view][field]+=1
        reported=result_by[c['case_id']]
        assert reported['truth'] is truth and reported['views'][view]['approved'] is approved
        assert reported['views'][view][field]
    assert len(source_systems)==1
    system=next(iter(source_systems));assert 'reviews records actual review actions' in system and 'Use null' in system
    assert counts=={v:r['counts'] for v,r in result['metrics'].items()}
    return dict(passed=True,post_outcome_verification=True,original_games=10,original_raw_responses=300,
                independently_rebuilt_truths=len(truths),all_source_adverse_events=len(adverse),all_adverse_events_retained=True,
                strict_auditor_texts=30,independent_view_contracts=30,routing_checks=30,counts=counts,
                result_sha256=hashlib.sha256((base/'results/s21_audit.json').read_bytes()).hexdigest())


if __name__=='__main__':
    receipt=audit();(ROOT/'logs/s21_source_audit.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
