"""Post-run publication guard. Frozen scientific source/estimand stays unchanged."""
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy
import scipy
from scripts.s07_analyze import analyze
from scripts.s07_verify import verify
from sim.legality import SOURCES,DEADLINE


def reject_failed_experiment(root):
    failures=list(Path(root).glob('failure*.json'))
    if failures:
        raise ValueError('Terminal failure marker: no resume or publication allowed')


def validate_registration(root):
    root=Path(root)
    reject_failed_experiment(root)
    cfg=json.loads((root/'config.json').read_text())
    if cfg['dry'] is not False:
        raise ValueError('Live publication refuses synthetic data')
    if not isinstance(cfg.get('registration_commit'),str) or not re.fullmatch('[0-9a-f]{40}',cfg['registration_commit']):
        raise ValueError('Registration must use a full immutable commit id')
    if (type(cfg['temperature_requested']) not in (int,float) or cfg['temperature_requested']!=1
            or type(cfg['workers']) is not int or cfg['workers']!=2 or cfg['deadline_utc']!=DEADLINE):
        raise ValueError('Requested execution configuration mismatch')
    recorded=cfg['environment']
    current=dict(python=platform.python_version(),numpy=numpy.__version__,scipy=scipy.__version__)
    if recorded!=current:
        raise ValueError('Recorded and recomputation environments differ; review before publication')
    if set(cfg['sources'])!=set(SOURCES):raise ValueError('Source manifest mismatch')
    for name,sha in cfg['sources'].items():
        try:blob=subprocess.check_output(['git','show',cfg['registration_commit']+':'+name],stderr=subprocess.PIPE)
        except (KeyError,subprocess.CalledProcessError) as exc:
            raise ValueError('Invalid registration commit') from exc
        if hashlib.sha256(blob).hexdigest()!=sha or hashlib.sha256(Path(name).read_bytes()).hexdigest()!=sha:
            raise ValueError('Registration/current-source hash mismatch')
    return dict(registration_commit=cfg['registration_commit'],recorded_execution_environment=recorded,
                recomputation_environment=current,temperature_requested=cfg['temperature_requested'],
                no_terminal_failure_markers=True,
                caveat='Version records match recomputation; historical backend execution is not independently attested')


def publish(root='data/s07_legality',out='results/s07_legality.json',audit='logs/s07_verification.json'):
    guard=validate_registration(root)
    candidate=analyze(root)
    verification=verify(root,candidate)
    verification['publication_guard']=guard
    output=Path(out);tmp=output.with_suffix('.tmp')
    tmp.write_text(json.dumps(candidate,indent=2)+'\n')
    # No result is released until every registered-source, failure, replay,
    # independent arithmetic, raw-key and export check above has passed.
    tmp.replace(output)
    Path(audit).write_text(json.dumps(verification,indent=2)+'\n')
    print(json.dumps(dict(publication_guard=guard,result_sha256=verification['result_sha256']),indent=2))

if __name__=='__main__':publish()
