"""Prospective local CLI-input fingerprint; never provider/effective-config attestation."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def fingerprint():
    launcher=Path(shutil.which('codex')).resolve()
    node=Path(shutil.which('node')).resolve()
    home=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))
    native=sorted(launcher.parent.parent.glob('vendor/*/bin/codex'))
    # Newer npm layouts put the platform binary in a sibling optional package.
    native+=sorted(launcher.parent.parent.glob('node_modules/@openai/codex-*/vendor/*/bin/codex'))
    assert native,'Cannot fingerprint actual candidate native CLI binaries'
    files=[launcher,node,*native,home/'config.toml',home/'AGENTS.md',Path('/etc/codex/config.toml'),Path('/etc/codex/managed_config.toml'),home/'auth.json']
    envnames=['PATH','CODEX_HOME','OPENAI_BASE_URL','OPENAI_API_KEY','OPENAI_ORG_ID','OPENAI_PROJECT_ID','CODEX_API_KEY','CODEX_MANAGED_CONFIG','CODEX_MANAGED_CONFIG_FILE','TMPDIR','HOME','NODE_OPTIONS','HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','NO_PROXY','NODE_EXTRA_CA_CERTS','SSL_CERT_FILE','SSL_CERT_DIR']
    return dict(files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None for p in files},
                environment_sha256={k:hashlib.sha256(os.environ[k].encode()).hexdigest() if k in os.environ else None for k in envnames},
                scope='Known local launcher/node/native/config/routing inputs only; no provider attestation or complete effective-configuration reconstruction')


def launch_observation():
    return dict(fingerprint=fingerprint(),version=subprocess.check_output(['codex','--version'],text=True).strip())
