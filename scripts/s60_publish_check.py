"""Post-outcome publication guard: independently regenerate every displayed artifact.

The registered scientific estimator,source manifest and renderer stay unchanged.
The frozen archive checker alone compares the result and raw replay. This stronger
publication entry additionally compares rendered prose,appendix and figure bytes,
without replacing discrepant originals. No scientific model calls are permitted.
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import subprocess
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

ARTIFACTS=('results/s60_summary.md','results/s60_action_text.md','results/s60_action_text.json','figures/s60_author_bonus.png')
DOCUMENTS=('REPORT.md','REPORT_DETAILS.md','HITS.md','README.md','logs/s60_document_check.json')


def render_expected():
    from scripts.s60_present import main as render
    from matplotlib.figure import Figure
    generated={};real_save=Figure.savefig
    def write_text(path,text,*args,**kwargs):
        name=str(path)
        if name not in ARTIFACTS or name.endswith('.png'):raise AssertionError('Unexpected renderer text write: '+name)
        if name in generated:raise AssertionError('Duplicate renderer write: '+name)
        generated[name]=text.encode(kwargs.get('encoding') or 'utf-8');return len(text)
    with tempfile.TemporaryDirectory(prefix='s60_render_',dir='/var/tmp') as td:
        def savefig(figure,name,*args,**kwargs):
            name=str(name);assert name==ARTIFACTS[-1] and name not in generated
            target=Path(td)/'figure.png'
            real_save(figure,target,*args,**kwargs);generated[name]=target.read_bytes()
        with patch('llm.chat',side_effect=AssertionError('Publication forbids scientific calls')),patch.object(Path,'write_text',new=write_text),patch.object(Figure,'savefig',new=savefig),contextlib.redirect_stdout(io.StringIO()):
            render()
    assert set(generated)==set(ARTIFACTS)
    return generated


def compare_rendered(generated,read_bytes=lambda name:Path(name).read_bytes(),names=ARTIFACTS):
    assert set(generated)==set(names)
    for name,expected in generated.items():
        assert read_bytes(name)==expected,'Displayed artifact differs from frozen renderer: '+name
    return {name:hashlib.sha256(blob).hexdigest() for name,blob in generated.items()}


def render_documents_expected():
    from scripts.s60_integrate import main as integrate
    generated={}
    def capture(path,text,*args,**kwargs):
        name=str(path)
        assert name in DOCUMENTS and name not in generated,'Unexpected document write: '+name
        generated[name]=text.encode(kwargs.get('encoding') or 'utf-8');return len(text)
    with patch('llm.chat',side_effect=AssertionError('Publication forbids scientific calls')),patch.object(Path,'write_text',new=capture),contextlib.redirect_stdout(io.StringIO()):
        integrate(document_capture=True)
    assert set(generated)==set(DOCUMENTS)
    return generated


def document_sections(generated,current):
    """Bind S60-managed text,allowing later pilots to append their own sections."""
    actual={};expected={}
    for name in DOCUMENTS:
        if name=='logs/s60_document_check.json':
            actual[name]=current[name];expected[name]=generated[name];continue
        left=current[name].decode('utf-8');right=generated[name].decode('utf-8')
        if name=='README.md':
            pattern=r'^## S60 — Author approval benefit\n.*?(?=^## |\Z)'
            a=re.findall(pattern,left,re.M|re.S);b=re.findall(pattern,right,re.M|re.S)
            assert len(a)==len(b)==1,'Missing or duplicate S60 README section'
            actual[name]=a[0].rstrip('\n').encode();expected[name]=b[0].rstrip('\n').encode();continue
        marker='summary' if name=='REPORT.md' else 'details' if name=='REPORT_DETAILS.md' else 'handoff'
        pattern=r'<!-- S60 '+marker+r' start -->.*?<!-- S60 '+marker+r' end -->'
        a=re.findall(pattern,left,re.S);b=re.findall(pattern,right,re.S)
        assert len(a)==len(b)==1,'Missing or duplicate S60 document section: '+name
        # Later managers may move the old front summary to its existing details
        # section,as with earlier pilots. They must retain the unchanged row.
        compact='<!-- S60 summary start --><!-- S60 summary end -->'
        if name=='REPORT.md' and a[0]==compact:
            iteration=re.search(r'· Iteration (\d+) ·',left)
            assert iteration and int(iteration[1])>43,'Current S60 summary cannot be erased'
            actual[name]=expected[name]=compact.encode()
        else:actual[name]=a[0].encode();expected[name]=b[0].encode()
        if name=='REPORT.md':
            arow=[line for line in left.splitlines() if line.startswith('| S60 ')]
            brow=[line for line in right.splitlines() if line.startswith('| S60 ')]
            assert len(arow)==len(brow)==1,'Missing or duplicate S60 pilot row'
            actual[name]+=b'\n'+arow[0].encode();expected[name]+=b'\n'+brow[0].encode()
    return expected,actual


def compare_documents(generated,read_bytes=lambda name:Path(name).read_bytes()):
    expected,actual=document_sections(generated,{name:read_bytes(name) for name in DOCUMENTS})
    return compare_rendered(expected,read_bytes=actual.__getitem__,names=DOCUMENTS)


def check():
    before={name:Path(name).read_bytes() for name in (*ARTIFACTS,*DOCUMENTS)}
    hashes=compare_rendered(render_expected())
    document_hashes=compare_documents(render_documents_expected())
    assert all(Path(n).read_bytes()==blob for n,blob in before.items()),'Publication check changed original display artifacts'
    from scripts.s60_release import check as archive_check
    with patch('llm.chat',side_effect=AssertionError('Publication forbids scientific calls')),contextlib.redirect_stdout(io.StringIO()):archive=archive_check()
    receipt=dict(passed=True,scientific_calls_forbidden=True,registered_scientific_sources_unchanged=True,
                 display_originals_unchanged=True,all_display_artifacts_compared=True,
                 regenerated_sha256=hashes,regenerated_s60_document_section_sha256=document_hashes,archive=archive)
    Path('logs/s60_publication.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2));return receipt


def clean_clone():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    remote=subprocess.check_output(['git','remote','get-url','origin'],text=True).strip()
    observed=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],text=True).split()[0]
    assert observed==head,'Push the exact checked release first'
    artifacts=[*ARTIFACTS,*DOCUMENTS,'results/s60_author_bonus.json','logs/s60_independent.json',
               'logs/s60_release.json','logs/s60_publication.json','logs/s60_static_bound.json']
    assert len(artifacts)==len(set(artifacts))==14
    commands=[['scripts/s60_publish_check.py'],['-m','unittest','scripts.test_s60','scripts.test_s60_presentation'],
              ['scripts/s60_independent.py'],['scripts/s60_present.py'],['scripts/s60_static_bound.py']]
    launch_code="""import runpy,sys
from unittest.mock import patch
args=sys.argv[1:]
with patch('llm.chat',side_effect=AssertionError('Origin check forbids scientific calls')):
 if args[0]=='-m':
  sys.argv=[args[1],*args[2:]];runpy.run_module(args[1],run_name='__main__')
 else:
  sys.argv=args;runpy.run_path(args[0],run_name='__main__')
"""
    with tempfile.TemporaryDirectory(prefix='s60_origin_',dir='/var/tmp') as td:
        clone=Path(td)/'repo'
        subprocess.run(['git','clone','--quiet',remote,str(clone)],check=True)
        subprocess.run(['git','checkout','--quiet',head],cwd=clone,check=True)
        assert not (clone/'.git/shallow').exists()
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1')
        for args in commands:
            subprocess.run([str(root/'.venv/bin/python'),'-c',launch_code,*args],cwd=clone,env=env,check=True)
        status=subprocess.check_output(['git','status','--porcelain'],cwd=clone,text=True)
        assert not status,status
        for name in artifacts:assert (clone/name).read_bytes()==(root/name).read_bytes(),name
        receipt=dict(passed=True,commit=head,observed_origin_head=observed,full_history_origin_clone=True,
                     scientific_calls_forbidden=True,clone_git_status_clean=True,
                     dependency_environment='Existing installed frozen venv;not a fresh dependency installation',
                     byte_identical_artifacts={name:hashlib.sha256((clone/name).read_bytes()).hexdigest() for name in artifacts},
                     commands=commands)
    Path('logs/s60_remote_clean_clone.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS fresh origin clone '+head+':14artifacts byte-identical,32scoped checks,clone clean')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--clean-clone',action='store_true');a=p.parse_args();check()
    if a.clean_clone:clean_clone()
