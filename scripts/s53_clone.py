"""Fresh full-history origin reproduction, reusing the installed frozen venv."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def run():
    root=Path(__file__).resolve().parents[1]
    current=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    origin=subprocess.check_output(['git','remote','get-url','origin'],text=True).strip()
    artifacts=['results/s53_payoffs.json','results/s53_summary.md','figures/s53_payoffs.png',
               'logs/s53_independent.json','logs/s53_release.json','data/s53_registration.json','data/s53_registration_receipt.json']
    records=[]
    with tempfile.TemporaryDirectory(prefix='s53_origin_',dir='/var/tmp') as temp:
        clone=Path(temp)/'repo'
        subprocess.run(['git','clone','--quiet',origin,str(clone)],check=True,timeout=90)
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=clone,text=True).strip()
        if head!=current:raise ValueError('Origin HEAD differs from current results commit')
        commands=[[sys.executable,'scripts/s53_payoffs.py','--release'],
                  [sys.executable,'scripts/s53_independent.py'],
                  [sys.executable,'-m','unittest','scripts.test_s53']]
        for i,command in enumerate(commands):
            p=subprocess.run(command,cwd=clone,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
            records.append(dict(command=command,returncode=p.returncode,output=p.stdout))
            if p.returncode:raise RuntimeError(p.stdout)
        hashes={}
        for name in artifacts:
            if (clone/name).read_bytes()!=(root/name).read_bytes():raise ValueError('Clone bytes differ: '+name)
            hashes[name]=hashlib.sha256((clone/name).read_bytes()).hexdigest()
        status=subprocess.check_output(['git','status','--porcelain'],cwd=clone,text=True)
        if status:raise ValueError('Clone changed: '+status)
    result=dict(passed=True,origin=origin,results_commit=current,full_history_origin_clone=True,
                installed_frozen_venv_reused=True,fresh_dependency_install=False,
                commands=records,byte_identical_artifacts=hashes,clone_git_status=status)
    (root/'logs/s53_remote_clean_clone.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='commands'},indent=2))


if __name__=='__main__':run()
