"""Trusted stdlib entry: execute local scientific modules from captured Git bytes.

Launch with ``uv run python scripts/s54_bootstrap.py`` in the repository root.
The Python process/stdlib, this bootstrap entry, Git and installed dependencies
remain the trusted computing base. This is not OS or provider attestation.
"""
import ast
import hashlib
import importlib.abc
import importlib.machinery
import importlib.util
from pathlib import Path
import subprocess
import sys
import types

if not __debug__:
    raise RuntimeError('Research integrity checks require Python without -O')

MODE='registered-memory-source-v1'
ENTRY='scripts/s54_launch.py'


def _git(root,*args):
    return subprocess.check_output(['git',*args],cwd=root)


def capture_registration(root):
    """Read no working scientific Python before binding the committed manifest."""
    root=Path(root).resolve()
    head=_git(root,'rev-parse','HEAD').decode().strip()
    remote=_git(root,'ls-remote','origin','refs/heads/main').decode().split()[0]
    if head!=remote:raise RuntimeError('Bootstrap requires matching pushed origin/main')
    manifest_bytes=_git(root,'show',f'{head}:sim/opportunities.py')
    tree=ast.parse(manifest_bytes,filename='registered:sim/opportunities.py')
    assignments=[node.value for node in tree.body if isinstance(node,ast.Assign)
                 and any(isinstance(target,ast.Name) and target.id=='SOURCES' for target in node.targets)]
    if len(assignments)!=1:raise RuntimeError('Expected one literal scientific source manifest')
    sources=ast.literal_eval(assignments[0])
    if not isinstance(sources,list) or not all(isinstance(name,str) for name in sources) or len(sources)!=len(set(sources)):
        raise RuntimeError('Malformed scientific source manifest')
    if not {'sim/opportunities.py',ENTRY,'scripts/s54_bootstrap.py'}<=set(sources):
        raise RuntimeError('Bootstrap, entry or simulation absent from source freeze')
    captured={}
    for name in sources:
        relative=Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise RuntimeError('Scientific source path must stay relative to repository')
        registered=_git(root,'show',f'{head}:{name}')
        if (root/name).read_bytes()!=registered:
            raise RuntimeError('Working scientific source differs from captured Git bytes: '+name)
        captured[name]=registered
    if captured['sim/opportunities.py']!=manifest_bytes:
        raise RuntimeError('Captured manifest mismatch')
    hashes={name:hashlib.sha256(blob).hexdigest() for name,blob in captured.items()}
    context=dict(mode=MODE,entrypoint=ENTRY,registration_commit=head,observed_remote_head=remote,
                 sources=hashes,byte_bound_python_sources={name:digest for name,digest in hashes.items() if name.endswith('.py')},
                 compiler='compile(captured_git_bytes); no pyc execution',
                 trusted_computing_base='Bootstrap entry, Python process/stdlib, Git and installed dependencies; no OS/provider attestation')
    return captured,context


class CapturedLoader(importlib.abc.Loader):
    def __init__(self,root,name,source,is_package=False):
        self.root=Path(root);self.name=name;self.source=source;self.is_package=is_package

    def create_module(self,spec):return None

    def exec_module(self,module):
        module.__file__=str(self.root/self.name)
        if self.is_package:module.__path__=[str((self.root/self.name).parent)]
        # Compile the captured bytes directly. Neither changed disk source nor
        # preexisting bytecode can participate in local scientific execution.
        exec(compile(self.source,module.__file__,'exec',dont_inherit=True),module.__dict__)


class NamespaceLoader(importlib.abc.Loader):
    def create_module(self,spec):return None
    def exec_module(self,module):pass


class CapturedSourceFinder(importlib.abc.MetaPathFinder):
    def __init__(self,root,captured):
        self.root=Path(root).resolve();self.modules={};self.namespaces=set()
        for name,blob in captured.items():
            if not name.endswith('.py'):continue
            parts=Path(name).parts
            package=parts[-1]=='__init__.py'
            fullname='.'.join(parts[:-1] if package else [*parts[:-1],Path(parts[-1]).stem])
            self.modules[fullname]=(name,blob,package)
            for i in range(1,len(fullname.split('.'))):
                self.namespaces.add('.'.join(fullname.split('.')[:i]))

    def find_spec(self,fullname,path=None,target=None):
        if fullname in self.modules:
            name,blob,package=self.modules[fullname]
            loader=CapturedLoader(self.root,name,blob,package)
            spec=importlib.util.spec_from_loader(fullname,loader,origin=str(self.root/name),is_package=package)
            if package:spec.submodule_search_locations=[str((self.root/name).parent)]
            return spec
        if fullname in self.namespaces:
            spec=importlib.machinery.ModuleSpec(fullname,NamespaceLoader(),is_package=True)
            spec.submodule_search_locations=[str(self.root/Path(*fullname.split('.')))]
            return spec
        if fullname=='llm' or fullname.split('.')[0] in {'sim','scripts'}:
            raise ImportError('Unregistered local scientific module: '+fullname)
        # Fail closed if an accidental unregistered repository module would be
        # imported outside the scientific namespaces. The installed .venv is TCB.
        spec=importlib.machinery.PathFinder.find_spec(fullname,path)
        if spec is not None and spec.origin not in (None,'built-in','frozen'):
            origin=Path(spec.origin).resolve()
            if origin.is_relative_to(self.root) and not origin.is_relative_to(self.root/'.venv'):
                raise ImportError('Unregistered repository Python import: '+fullname)
        return None


def install_byte_binding(root,captured,context):
    hashes={name:hashlib.sha256(blob).hexdigest() for name,blob in captured.items()}
    if (context.get('mode')!=MODE or context.get('sources')!=hashes
            or context.get('byte_bound_python_sources')!={name:digest for name,digest in hashes.items() if name.endswith('.py')}):
        raise RuntimeError('Captured source context mismatch')
    finder=CapturedSourceFinder(root,captured)
    # sys.modules would otherwise bypass every finder, including this one.
    loaded=[name for name in sys.modules if name in finder.modules or name in finder.namespaces
            or name=='llm' or name.split('.')[0] in {'sim','scripts'}]
    if loaded:raise RuntimeError('Scientific modules loaded before byte binding: '+', '.join(sorted(loaded)))
    sys.meta_path.insert(0,finder)
    sys._s54_bootstrap_context=context
    return finder


def main():
    if len(sys.argv)!=1:raise RuntimeError('S54 bootstrap takes no arguments')
    root=Path(__file__).resolve().parents[1]
    if Path.cwd().resolve()!=root:raise RuntimeError('Run S54 bootstrap from repository root')
    captured,context=capture_registration(root)
    install_byte_binding(root,captured,context)
    module=types.ModuleType('__main__')
    module.__dict__.update(__file__=str(root/ENTRY),__package__='scripts')
    sys.modules['__main__']=module
    exec(compile(captured[ENTRY],str(root/ENTRY),'exec',dont_inherit=True),module.__dict__)


if __name__=='__main__':main()
