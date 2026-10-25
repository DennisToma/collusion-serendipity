"""Call-forbidden, byte-identical interrupted-prefix release and origin clone."""
import argparse,contextlib,copy,hashlib,io,json,os,re,shutil,subprocess,sys,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s68_failure_audit import verify
from scripts.s68_failure_present import outputs,render,DOCS
from scripts import s68_replay as s

ARTIFACTS=['results/s68_failure.json','results/s68_summary.md',*DOCS]

def check():
    before={p:Path(p).read_bytes() for p in ARTIFACTS}
    raw={str(p):p.read_bytes() for p in Path('data/s68_polarity').rglob('*') if p.is_file() and p.name!='.writer.lock'}
    with patch.object(s,'chat',side_effect=AssertionError('No scientific calls')):
        result=verify();assert json.dumps(result,indent=2)+'\n'==before[ARTIFACTS[0]].decode()
        docs,old,summary,row=outputs(result)
        assert all(before[n].decode()==text for n,text in docs.items())
        assert summary==before[ARTIFACTS[1]].decode()
        rendered=render();assert rendered==result
    assert before=={p:Path(p).read_bytes() for p in ARTIFACTS}
    assert all(Path(p).read_bytes()==blob for p,blob in raw.items())
    assert not Path('results/s68_polarity.json').exists(),'No behavioral analysis may exist'
    assert not Path('figures/s68_polarity.png').exists(),'No behavioral figure may exist'
    old_rows=[line for line in old['REPORT.md'].splitlines() if line.startswith('| S')]
    lines=Path('REPORT.md').read_text().splitlines();report_rows=[l for l in lines if l.startswith('| S')]
    assert report_rows==old_rows+[row]
    indices=[i for i,l in enumerate(lines) if l.startswith('| S')]
    assert indices==list(range(indices[0],indices[0]+len(indices)))
    links=0
    for name in [*DOCS,'results/s68_summary.md']:
        for href in re.findall(r'\]\(([^)]+)\)',Path(name).read_text()):
            if href.startswith(('http:','https:','#')):continue
            assert (Path(name).parent/href.split('#')[0]).exists(),(name,href)
            links+=1
    rejected=[]
    with tempfile.TemporaryDirectory(dir='/var/tmp',prefix='s68_failure_mutations_') as td:
        temp=Path(td)
        for mutation in ['request_count','response_count','response_duplicate','response_hash','accepted_binding','source_manifest','completion_event']:
            directory=temp/mutation;shutil.copytree('data/s68_polarity',directory)
            def read(n):return [json.loads(line) for line in (directory/(n+'.jsonl')).read_text().splitlines()]
            def write(n,rows):(directory/(n+'.jsonl')).write_text(''.join(json.dumps(r)+'\n' for r in rows))
            if mutation=='request_count':write('requests',read('requests')[:-1])
            elif mutation=='response_count':write('responses',read('responses')[:-1])
            elif mutation=='response_duplicate':
                rows=read('responses');rows[-1]=copy.deepcopy(rows[0]);write('responses',rows)
            elif mutation=='response_hash':
                rows=read('responses');rows[0]['response_sha256']='FORGED';write('responses',rows)
            elif mutation=='accepted_binding':
                rows=read('accepted');rows[0]['parsed']['note']='FORGED';write('accepted',rows)
            elif mutation=='source_manifest':
                cfg=json.loads((directory/'config.json').read_text());cfg['sources']['llm.py']='FORGED';(directory/'config.json').write_text(json.dumps(cfg))
            else:write('execution',read('execution')+[dict(event='complete',utc=s.utc())])
            try:verify(directory)
            except AssertionError:rejected.append(mutation)
            else:raise AssertionError('Accepted corrupted prefix '+mutation)
    guards=[]
    with tempfile.TemporaryDirectory(dir='/var/tmp',prefix='s68_failed_doc_guard_') as td:
        temp=Path(td)
        for name,text in docs.items():(temp/name).write_text(text)
        for name in DOCS:
            (temp/name).write_text(docs[name]+'\nUNEXPECTED EDIT\n')
            saved={n:(temp/n).read_bytes() for n in DOCS}
            # Only this isolated publication probe mocks the already-verified audit.
            with contextlib.chdir(temp),patch('scripts.s68_failure_present.verify',return_value=result),patch('scripts.s68_failure_present.outputs',return_value=(docs,old,summary,row)):
                try:render()
                except RuntimeError as exc:assert 'Intervening document change' in str(exc);guards.append(name)
                else:raise AssertionError('Accepted intervening document edit '+name)
            assert saved=={n:(temp/n).read_bytes() for n in DOCS}
            assert not (temp/'results').exists(),'Publication wrote before guard'
            (temp/name).write_text(docs[name])
    receipt=dict(passed=True,status='FAILED_INTERRUPTED',model_calls_forbidden=True,raw_prefix_files_unchanged=len(raw),registered_sources_unchanged=18,
                 no_behavioral_effect_estimate=True,source_prefix_and_metadata_reconstructed=True,corrupt_prefixes_rejected=rejected,
                 prior_report_rows=len(old_rows),current_contiguous_report_rows=len(report_rows),local_links_checked=links,
                 prewrite_document_corruptions_rejected=guards,
                 current_report_rows=len(report_rows),
                 checked_sha256={p:hashlib.sha256(blob).hexdigest() for p,blob in before.items()},
                 existing_venv_reused=True,process_root_cause_unknown=True)
    Path('logs/s68_failure_release.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt

def clean_clone():
    root=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();remote=subprocess.check_output(['git','remote','get-url','origin'],text=True).strip()
    names=[*ARTIFACTS,'logs/s68_failure_release.json']
    with tempfile.TemporaryDirectory(dir='/var/tmp',prefix='s68_failed_origin_') as td:
        clone=Path(td)/'repo';subprocess.run(['git','clone','--quiet',remote,str(clone)],check=True);subprocess.run(['git','checkout','--quiet',head],cwd=clone,check=True)
        commands=[['scripts/s68_failure_audit.py'],['scripts/s68_failure_present.py'],['scripts/s68_failure_release.py'],['-m','unittest','scripts.test_s68']]
        env=dict(os.environ,VIRTUAL_ENV=str(root/'.venv'),TMPDIR='/var/tmp',PYTHONDONTWRITEBYTECODE='1')
        for args in commands:subprocess.run([str(root/'.venv/bin/python'),*args],cwd=clone,env=env,check=True)
        for name in names:assert (clone/name).read_bytes()==(root/name).read_bytes(),name
        assert not subprocess.check_output(['git','status','--porcelain'],cwd=clone,text=True)
        receipt=dict(passed=True,commit=head,clone_source='origin remote',commands=commands,dependency_environment='Existing pinned venv reused;no fresh-install claim',
                     byte_identical_artifacts={p:hashlib.sha256((clone/p).read_bytes()).hexdigest() for p in names},no_behavioral_estimate=True,no_new_scientific_call=True)
    Path('logs/s68_remote_clean_clone.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS interrupted-prefix origin clone '+head)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--clean-clone',action='store_true');a=p.parse_args()
    clean_clone() if a.clean_clone else print(json.dumps(check(),indent=2))
