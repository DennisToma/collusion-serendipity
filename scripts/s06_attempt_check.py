"""Independent supplementary raw-response attempt/count/timestamp check."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    d=Path('data/s06_denomination');report=json.loads(Path('logs/s06_retry_audit.json').read_text())
    cfg=json.loads((d/'config.json').read_text())
    # Existing audit was committed before calls, although outside the13-file manifest.
    source='scripts/s06_retry_audit.py'
    assert Path(source).read_bytes()==subprocess.check_output(['git','show',f'{cfg["registration_commit"]}:{source}'])
    requests=[json.loads(l) for l in (d/'raw/requests.jsonl').read_text().splitlines()]
    responses={r['key']:r['response'] for r in map(json.loads,(d/'raw/responses.jsonl').read_text().splitlines())}
    extra=Counter();bad=Counter();valid=Counter();reasons=Counter()
    for r in requests:
        payload=r['payload'];arm=payload[5].rsplit('_',1)[1];attempt=payload[8]
        if attempt:extra[arm]+=1
        obj=json.loads(responses[r['key']]['text'])
        # Direct raw-schema checks without production parser.
        assert set(obj)=={'quantity','reasoning','private_message'}
        assert type(obj['quantity']) is int and 0<=obj['quantity']<=12
        assert isinstance(obj['reasoning'],str) and obj['private_message']==''
        if len(obj['reasoning'].split())>40:
            bad[arm]+=1;reasons[arm,'reasoning_over_40_words']+=1
        else:valid[arm]+=1
    assert dict(extra)==report['retry_requests']
    assert dict(bad)==report['rejected_responses']
    assert dict(valid)==report['valid_decisions']
    assert {arm:{reason:n for (a,reason),n in reasons.items() if a==arm} for arm in bad}==report['rejection_reasons']
    assert min(r['call_started_utc'] for r in responses.values())==report['first_call_started_utc']
    assert max(r['call_completed_utc'] for r in responses.values())==report['last_call_completed_utc']
    out=dict(independent_raw_responses_checked=len(responses),extra_requests_by_arm=dict(extra),
             rejected_responses_by_arm=dict(bad),valid_actions_by_arm=dict(valid),
             rejection_reasons_verified=True,first_last_timestamps_verified=True,
             original_attempt_auditor_matches_registration=True,
             result_sha256=hashlib.sha256(Path('results/s06_denomination.json').read_bytes()).hexdigest())
    Path('logs/s06_attempt_check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
