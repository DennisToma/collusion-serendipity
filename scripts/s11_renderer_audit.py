"""Document presentation chronology separately from the frozen scientific manifest."""
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    cfg=json.loads(Path('data/s11_delay/config.json').read_text());commit=cfg['registration_commit']
    path='scripts/s11_present.py';old=subprocess.check_output(['git','show',f'{commit}:{path}'])
    current=Path(path).read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
    out=dict(registration_commit=commit,initial_renderer_committed_before_client_calls=True,
             initial_renderer_sha256=sha(old),current_renderer_sha256=sha(current),
             renderer_in_frozen_scientific_manifest=path in cfg['sources'],
             post_outcome_presentation_revisions=True,
             scientific_result_sha256=sha(Path('results/s11_delay.json').read_bytes()),
             scope='Renderer formats frozen estimates and adds interpretation; it is not a frozen scientific estimator. Chronology is client-side, not independent server attestation.')
    Path('logs/s11_renderer_provenance.json').write_text(json.dumps(out,indent=2)+'\n')
    diff=subprocess.check_output(['git','diff',commit,'--',path],text=True)
    Path('logs/s11_renderer_changes.patch').write_text(diff)
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
