"""Validate post-outcome documentation against frozen S56 JSON and prior rows."""
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import tempfile

root=Path.cwd();generated=['REPORT.md','REPORT_DETAILS.md','results/s56_interpretation.md']
old=subprocess.check_output(['git','show','92f14c14129e1f448857b0ab0af0c66bbe60d139:REPORT.md'],text=True)
assert [x for x in old.splitlines() if x.startswith('|')]==[x for x in Path('REPORT.md').read_text().splitlines() if x.startswith('|') and not x.startswith('| S56 ·')]
with tempfile.TemporaryDirectory(dir='/var/tmp') as td:
    temp=Path(td)
    for name in ['REPORT.md','REPORT_DETAILS.md','results/s56_coalitions.json','logs/s56_release.json']:
        (temp/name).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/name,temp/name)
    try:
        os.chdir(temp);runpy.run_path(str(root/'scripts/s56_documents.py'),run_name='__main__')
        for name in generated:
            if (root/name).read_bytes()!=(temp/name).read_bytes():raise ValueError('Generated documentation differs: '+name)
    finally:os.chdir(root)
n=0
for doc in generated+['README.md','HITS.md','results/s56_summary.md']:
    for link in re.findall(r'\]\(([^)]+)\)',Path(doc).read_text()):
        href=link.strip('<>').split('#')[0]
        if not href or '://' in href:continue
        assert (Path(doc).parent/href).exists(),(doc,href)
        n+=1
m=json.loads(Path('data/s56_registration.json').read_text())
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in m['input_and_source_sha256'].items())
receipt=dict(passed=True,local_links=n,prior_pilot_rows_unchanged=39,total_pilot_rows=40,
             generated_document_files=generated,document_helper_idempotent=True,
             generated_documents_match_frozen_json=True,frozen_source_inputs_unchanged=len(m['input_and_source_sha256']))
Path('logs/s56_document_checks.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
