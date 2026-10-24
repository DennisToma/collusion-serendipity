"""Post-run observations only: does not attest the scientific run's CLI inputs."""
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def observe():
    launcher=Path(shutil.which('codex')).resolve()
    codex_dir=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))
    config=codex_dir/'config.toml'
    # Record hashes only; never output credentials or full inherited environment.
    candidates=[launcher,*sorted(launcher.parent.parent.glob('vendor/*/codex/codex'))]
    cfg=json.loads(Path('data/s31_labor/config.json').read_text())
    games=[json.loads(p.read_text()) for p in sorted(Path('data/s31_labor').glob('game_*.json'))]
    result=json.loads(Path('results/s31_labor.json').read_text())
    counts={c:dict(written=sum(len(g['ground_truth']['notes_file']) for g in games if g['ground_truth']['condition']==c),
                   nonempty=sum(bool(n['text'].strip()) for g in games if g['ground_truth']['condition']==c for n in g['ground_truth']['notes_file'])) for c in ['self','shared']}
    assert counts==result['notes']
    source_current={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in cfg['sources']}
    assert source_current==cfg['sources']
    receipt=dict(observed_utc=datetime.now(timezone.utc).isoformat(),scope='POST-RUN observation only; does not reconstruct or attest execution-time binary, configuration, environment or provider behavior',
                 cli_version=subprocess.check_output([str(launcher),'--version'],text=True).strip(),
                 launcher_path=str(launcher),cli_file_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in candidates if p.is_file()},
                 config_exists=config.exists(),config_sha256=hashlib.sha256(config.read_bytes()).hexdigest() if config.exists() else None,
                 config_path=str(config),effective_configuration_reconstructed=False,configuration_controlled_during_run=False,
                 note_counts_from_game_archives=counts,frozen_scientific_sources_unchanged=True,
                 scientific_result_sha256=hashlib.sha256(Path('results/s31_labor.json').read_bytes()).hexdigest())
    Path('logs/s31_runtime_observation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS post-run observation; scientific sources unchanged; execution-time CLI configuration remains unverified')

if __name__=='__main__':observe()
