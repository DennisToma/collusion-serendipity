"""Reproduce the committed S09 artifacts in a clean local clone, with no live calls."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    root=Path.cwd();commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    scratch=Path(tempfile.mkdtemp(prefix='s09-clean-',dir='/var/tmp'));clone=scratch/'repo'
    subprocess.run(['git','clone','--quiet','--local','--no-hardlinks',str(root),str(clone)],check=True)
    outputs=['results/s09_replay.json','results/s09_summary.md','figures/s09_replay.png',
             'logs/s09_independent.json','logs/s09_release.json','logs/s09_retry_audit.json','logs/s09_exact_check.json']
    expected={p:digest(root/p) for p in outputs}
    assert expected=={p:digest(clone/p) for p in outputs}
    steps=[['scripts/s09_snapshot.py'],['scripts/s09_analyze.py'],['scripts/s09_independent.py'],
           ['scripts/s09_release.py'],['scripts/s09_retry_audit.py'],['scripts/s09_exact_check.py'],['scripts/s09_present.py'],
           ['-m','unittest','scripts.test_s09','-v']]
    with (root/'logs/s09_clean_check.log').open('w') as log:
        for step in steps:
            proc=subprocess.run([sys.executable,*step],cwd=clone,capture_output=True,text=True,timeout=90)
            log.write('COMMAND: python '+' '.join(step)+'\n'+proc.stdout+proc.stderr+'\n')
            log.flush();assert proc.returncode==0, f'Clean-check failure: {step}'
    actual={p:digest(clone/p) for p in outputs};assert actual==expected, 'Portable artifact mismatch'
    links=0
    for document in ['REPORT.md','HITS.md','README.md','results/s09_summary.md']:
        p=clone/document
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text()):
            if '://' in target or target.startswith('mailto:'):continue
            local=target.split('#',1)[0]
            if local:
                assert (p.parent/local).exists(), f'Missing link {document}: {target}'
                links+=1
    out=dict(commit=commit,clone=str(clone),steps=len(steps),scientific_outputs_byte_identical=True,
             publication_cache_only=True,tests=19,local_file_links=links,sha256=expected)
    (root/'logs/s09_clean_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
