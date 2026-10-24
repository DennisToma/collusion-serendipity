"""Post-run read-only request-use, retry and deadline audit; no scientific tuning."""
from collections import Counter
from datetime import datetime
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.calculator import DEADLINE, parse_action
from scripts.s03_analyze import analyze


def invalid_reason(text):
    try:
        obj=json.loads(text)
    except ValueError:
        return 'non_JSON'
    if not isinstance(obj,dict) or not {'quantity','reasoning','private_message'} <= obj.keys():
        return 'missing_fields_or_object'
    q=obj['quantity']
    if type(q) is not int:
        return 'quantity_type'
    if not 0<=q<=12:
        return 'quantity_range'
    if obj['private_message']!='':
        return 'nonempty_private_message'
    if not isinstance(obj['reasoning'],str):
        return 'reasoning_type'
    if len(obj['reasoning'].split())>40:
        return 'reasoning_word_limit'
    raise ValueError('Response is valid, not an invalid retry')


def check_publication(saved, canonical):
    if saved != canonical:
        raise ValueError('Published results differ from complete canonical reanalysis')
    primary=saved['metrics']['quantity']
    numerators=primary['exact_seed_difference_numerators']
    mean=Fraction(sum(numerators),len(numerators)*primary['exact_denominator'])
    summary=primary['paired_difference']
    if mean>=1 and summary['ci95'][0]>0 and summary['exact_signflip_p_upper']<=.05:
        verdict='HIT'
    elif mean<=-1 and all(v<0 for v in numerators):
        verdict='ODD-reverse'
    elif mean<=Fraction(1,4):
        verdict='DUD'
    else:
        verdict='ODD'
    if verdict!=saved['verdict']:
        raise ValueError('Published verdict differs from independent classification')
    return verdict


def check_consumed(consumed, response_keys, request_keys):
    if consumed!=response_keys or consumed!=request_keys:
        raise ValueError('Unused or missing raw cache/request entries')


def main():
    folder=Path('data/s03_calculator')
    paths=[folder/'raw/responses.jsonl',folder/'raw/requests.jsonl']
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    for p in paths:
        if not p.read_bytes().endswith(b'\n'):
            raise ValueError('Audit requires complete newline-terminated raw files before any replay')
    cached=[json.loads(line) for line in paths[0].read_text().splitlines()]
    responses={r['key']:r['response'] for r in cached}
    requests=[json.loads(line) for line in paths[1].read_text().splitlines()]
    by_id={tuple(r['payload'][5:9]):r for r in requests}
    if len(by_id)!=len(requests) or len(responses)!=len(cached):
        raise ValueError('Duplicate call identity/cache key')
    consumed=set();arm_counts=Counter();reasons={c:Counter() for c in ['none','calculator']};invalid_by_arm=Counter()
    last_start=None;first_start=None
    for path in sorted(folder.glob('game_*.json')):
        gt=json.loads(path.read_text())['ground_truth']
        cond=gt['condition'];rid=gt['run_id']
        if datetime.fromisoformat(gt['ended_utc'])>=datetime.fromisoformat(DEADLINE):
            raise ValueError('Game ended at/after cutoff; transport-retry timing needs review')
        call_groups={}
        for call in gt['call_provenance']:
            identity=(rid,call['round'],call['agent'],call['attempt'])
            request=by_id[identity];key=request['key'];response=responses[key]
            if key in consumed:
                raise ValueError('One response used twice')
            consumed.add(key);arm_counts[cond]+=1
            timestamp=datetime.fromisoformat(response['call_started_utc'])
            if timestamp>=datetime.fromisoformat(DEADLINE):
                raise ValueError('Call started at/after absolute cutoff')
            first_start=min(first_start,timestamp) if first_start else timestamp
            last_start=max(last_start,timestamp) if last_start else timestamp
            call_groups.setdefault((call['round'],call['agent']),[]).append(response)
        for responses_for_action in call_groups.values():
            if parse_action(responses_for_action[-1]['text']) is None:
                raise ValueError('Final accepted action invalid')
            for response in responses_for_action[:-1]:
                if parse_action(response['text']) is not None:
                    raise ValueError('Earlier retry was valid')
                reasons[cond][invalid_reason(response['text'])]+=1
                invalid_by_arm[cond]+=1
    check_consumed(consumed,set(responses),{r['key'] for r in requests})
    result_path=Path('results/s03_calculator.json')
    result_bytes=result_path.read_bytes()
    saved=json.loads(result_bytes)
    canonical=analyze(folder)
    verdict=check_publication(saved,canonical)
    canonical_bytes=(json.dumps(canonical,indent=2)+'\n').encode()
    if result_bytes!=canonical_bytes:
        raise ValueError('Published result bytes differ from canonical reanalysis')
    after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    if before!=after:
        raise ValueError('Read-only audit changed raw files')
    out=dict(raw_files_newline_terminated=True,raw_files_unchanged=True,
             all_cache_entries_consumed_once=True,all_calls_started_before_deadline=True,all_games_ended_before_deadline=True,
             complete_saved_result_matches_canonical=True,independent_classification=verdict,
             result_sha256=hashlib.sha256(result_bytes).hexdigest(),
             cached_responses=len(consumed),calls_by_arm=dict(arm_counts),invalid_retries_by_arm=dict(invalid_by_arm),
             invalid_reasons_by_arm={c:dict(v) for c,v in reasons.items()},
             first_call_started_utc=first_start.isoformat(),last_call_started_utc=last_start.isoformat(),sha256=after)
    Path('logs/s03_execution_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':
    main()
