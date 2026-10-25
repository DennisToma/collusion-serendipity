"""Prospective local CLI-input fingerprint; never provider/effective-config attestation."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def referenced_inputs():
    """Fail closed on named paths; hash their contents without persisting values."""
    names=['CODEX_MANAGED_CONFIG','CODEX_MANAGED_CONFIG_FILE','NODE_EXTRA_CA_CERTS','SSL_CERT_FILE','SSL_CERT_DIR']
    refs={}
    for name in names:
        value=os.environ.get(name)
        if not value:
            refs[name]=None
            continue
        # OpenSSL directories can be a colon-delimited search path.
        paths=value.split(os.pathsep) if name=='SSL_CERT_DIR' else [value]
        entries=[]
        for item in paths:
            path=Path(item).expanduser().resolve()
            if path.is_dir():
                files=sorted(x for x in path.rglob('*') if x.is_file())
                digest=hashlib.sha256(json.dumps([(str(x.relative_to(path)),hashlib.sha256(x.read_bytes()).hexdigest()) for x in files]).encode()).hexdigest()
            elif path.is_file():digest=hashlib.sha256(path.read_bytes()).hexdigest()
            else:raise RuntimeError('Referenced CLI input unavailable: '+name)
            entries.append(digest)
        refs[name]=entries
    # Nonempty NODE_OPTIONS can import code through several Node syntaxes.
    # Refuse rather than claiming a complete parser/fingerprint of those imports.
    if os.environ.get('NODE_OPTIONS','').strip():
        raise RuntimeError('S41 requires unset or empty NODE_OPTIONS')
    import tempfile
    temp_root=Path(tempfile.gettempdir()).resolve()
    ancestors={}
    for parent in dict.fromkeys([Path.cwd(),*Path.cwd().parents,temp_root,*temp_root.parents]):
        for basename in ['AGENTS.md','CLAUDE.md']:
            p=parent/basename
            ancestors[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    return dict(named_references=refs,ancestor_instructions=ancestors)


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
    return dict(referenced_inputs=referenced_inputs(),files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None for p in files},
                environment_sha256={k:hashlib.sha256(os.environ[k].encode()).hexdigest() if k in os.environ else None for k in envnames},
                scope='Known local launcher/node/native/config/routing inputs only; no provider attestation or complete effective-configuration reconstruction')


def launch_observation():
    return dict(fingerprint=fingerprint(),version=subprocess.check_output(['codex','--version'],text=True).strip())
