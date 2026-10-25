"""Fresh full-history origin reproduction, using existing pinned installed venv."""
import hashlib,json,os,subprocess,tempfile
from pathlib import Path

def main():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    assert subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],text=True).split()[0]==head
    remote=subprocess.check_output(['git','remote','get-url','origin'],text=True).strip()
    receipt=json.loads(Path('logs/s69_release.json').read_text())
    artifacts=[*receipt['checked_sha256'],'logs/s69_release.json','logs/s69_postcheck.json']
    commands=[['scripts/s69_release.py'],['-m','unittest','scripts.test_s69','-q'],['scripts/s69_independent.py'],['scripts/s69_postcheck.py']]
    with tempfile.TemporaryDirectory(prefix='s69_origin_',dir='/var/tmp') as td:
        clone=Path(td)/'repo';subprocess.run(['git','clone','--quiet',remote,str(clone)],check=True)
        subprocess.run(['git','checkout','--quiet',head],cwd=clone,check=True)
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1')
        for command in commands:subprocess.run([str(root/'.venv/bin/python'),*command],cwd=clone,env=env,check=True)
        for name in artifacts:assert (clone/name).read_bytes()==(root/name).read_bytes(),name
        assert subprocess.check_output(['git','status','--porcelain'],cwd=clone,text=True)==''
        result=dict(passed=True,commit=head,clone_source='origin',full_history=True,clone_clean=True,commands=commands,focused_tests=16,
                    dependency_environment='Existing pinned installed venv;no fresh dependency installation',
                    byte_identical_artifacts={n:hashlib.sha256((clone/n).read_bytes()).hexdigest() for n in artifacts})
    Path('logs/s69_remote_clean_clone.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS clean origin clone '+head)
if __name__=='__main__':main()
