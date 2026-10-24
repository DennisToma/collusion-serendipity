"""S14 offline publication/release audit and clean-clone reproduction."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))


def check(out='logs/s14_release.json'):
    from sim import tender
    from scripts.s14_analyze import analyze
    from scripts.s14_independent import check as independent
    d=Path('data/s14_tender');result=Path('results/s14_tender.json')
    files=sorted(p for p in d.rglob('*') if p.is_file() and p.name!='.writer.lock')+[result]
    before={str(p):p.read_bytes() for p in files}
    with patch('sim.common.llm.chat',side_effect=AssertionError('No live calls in release')):
        with patch.object(sys,'argv',['sim.tender']):tender.main()
        actual=analyze(d)
    assert (json.dumps(actual,indent=2)+'\n').encode()==before[str(result)]
    assert all(p.read_bytes()==before[str(p)] for p in files)
    with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
        ind=independent(d,result,Path(td)/'ind.json')
    cfg=json.loads((d/'config.json').read_text());assert not cfg['dry']
    subprocess.run(['git','merge-base','--is-ancestor',cfg['registration_commit'],'HEAD'],check=True)
    for name,sha in cfg['sources'].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha
        assert hashlib.sha256(subprocess.check_output(['git','show',f'{cfg["registration_commit"]}:{name}'])).hexdigest()==sha
    requests=[json.loads(l) for l in (d/'raw/requests.jsonl').read_text().splitlines()]
    req={r['key']:r for r in requests};retries={c:0 for c in tender.CONDITIONS};rejected={c:{} for c in tender.CONDITIONS}
    retry_roles={c:{'pair':0,'outsider':0} for c in tender.CONDITIONS}
    responses=[json.loads(l) for l in (d/'raw/responses.jsonl').read_text().splitlines()]
    for r in responses:
        response=r['response'];payload=req[r['key']]['payload'];cond=payload[5].split('_')[-1]
        assert cfg['registration_commit']==json.loads(Path('logs/s14_launch_preflight.json').read_text())['registration_commit']
        assert Path('logs/s14_launch_preflight.json').exists()
        launch=json.loads(Path('logs/s14_launch_preflight.json').read_text())
        assert launch['observed_remote_head']==cfg['registration_commit']
        assert launch['observed_utc']<=response['call_started_utc']<tender.DEADLINE
        assert response['call_started_utc']<=response['call_completed_utc']
        import random
        seed=int(payload[5].split('_')[1]);pair=random.Random(seed).sample(['A','B','C'],2)
        role='pair' if payload[7] in pair else 'outsider'
        if payload[8]>0:
            retries[cond]+=1;retry_roles[cond][role]+=1
        obj=tender.parse_action(response['text'])
        no_box=cond=='none' or role=='outsider'
        if obj is not None and no_box and obj['private_message']!='':
            rejected[cond]['forbidden private message']=rejected[cond].get('forbidden private message',0)+1
        if obj is None:
            try:
                parsed=json.loads(response['text'])
                reason='overlong reasoning' if isinstance(parsed,dict) and isinstance(parsed.get('reasoning'),str) and len(parsed['reasoning'].split())>40 else 'other parser rejection'
            except (ValueError,TypeError):reason='invalid JSON'
            rejected[cond][reason]=rejected[cond].get(reason,0)+1
    assert len(responses)==360+sum(retries.values())==actual['cached_responses']
    links=0
    for doc in ['REPORT.md','README.md','HITS.md','results/s14_summary.md']:
        for link in re.findall(r'\]\(([^)]+)\)',Path(doc).read_text()):
            href=link.strip('<>').split('#')[0]
            if not href or '://' in href:continue
            assert (Path(doc).parent/href).exists() or (Path(doc).parent/href).resolve()==Path(out).resolve(),(doc,href)
            links+=1
    output=dict(cache_only_resume=True,byte_identical_data_result=True,all_key_exact_request_replay=True,
                source_registration_hashes=True,local_prelaunch_remote_observation=True,server_time_attested=False,
                independent=ind,valid_actions=360,responses=len(responses),retries_by_arm=retries,retries_by_arm_role=retry_roles,rejections_by_arm=rejected,
                last_call_completed_utc=max(r['response']['call_completed_utc'] for r in responses),
                links_checked=links,registration_commit=cfg['registration_commit'],
                sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    Path(out).write_text(json.dumps(output,indent=2)+'\n');print('PASS full S14 offline release audit');return output


def clean_clone():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    with tempfile.TemporaryDirectory(prefix='s14_clean_',dir='/var/tmp') as td:
        clone=Path(td)/'repo';subprocess.run(['git','clone','--quiet','--no-local',str(root),str(clone)],check=True)
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1');py=str(root/'.venv/bin/python')
        for command in [['scripts/s14_release.py'],['-m','unittest','scripts.test_s14'],['scripts/s14_independent.py'],['scripts/s14_present.py']]:
            subprocess.run([py,*command],cwd=clone,env=env,check=True)
        artifacts=['results/s14_tender.json','results/s14_summary.md','logs/s14_independent.json','figures/s14_tender.png','REPORT.md']
        assert all((clone/f).read_bytes()==(root/f).read_bytes() for f in artifacts)
        print(f'PASS clean clone {head}: protocol/release checks and {len(artifacts)} byte-identical outputs')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--clean-clone',action='store_true');a=p.parse_args();clean_clone() if a.clean_clone else check()
