"""One cached neutral Aqueduct readiness request; no game or treatment outcomes."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from llm import chat

REQUEST=dict(prompt='Return exactly the JSON object {"ready":true}.',system='You are a JSON formatter.',
             backend='aqueduct',model='qwen-3.6-35b',temperature=1,max_tokens=64,retries=1)


def validate_probe():
    saved=json.loads(Path('logs/s62_probe.json').read_text())
    assert saved['request']==REQUEST and saved['scientific_decisions']==0
    assert saved['response']['model']==REQUEST['model'] and saved['response']['backend']==REQUEST['backend']
    assert ready_text(saved['response']['text'])
    assert datetime.fromisoformat(saved['started_utc'])<=datetime.fromisoformat(saved['completed_utc'])
    return saved


def ready_text(text):
    # Readiness only. Scientific JSON parsing never calls this normalizer.
    if text.startswith('```json\n') and text.endswith('\n```'):
        text=text[len('```json\n'):-len('\n```')]
    from sim.legality import unique_object,reject_constant
    obj=json.loads(text,object_pairs_hook=unique_object,parse_constant=reject_constant)
    return isinstance(obj,dict) and set(obj)=={'ready'} and obj['ready'] is True


def main():
    path=Path('logs/s62_probe.json')
    if path.exists():
        saved=json.loads(path.read_text())
        if 'response' not in saved:raise RuntimeError('Failed probe; no automatic retry')
        print('Cached readiness probe retained');return
    request=dict(REQUEST)
    obj=dict(request=request,scientific_decisions=0,started_utc=datetime.now(timezone.utc).isoformat())
    # Consume a one-shot marker before transport; preserve interrupted calls honestly.
    with path.open('x') as f:f.write(json.dumps(obj,indent=2)+'\n')
    try:obj['response']=chat(**request)
    except BaseException as e:obj['error']=repr(e);raise
    finally:
        obj['completed_utc']=datetime.now(timezone.utc).isoformat()
        path.write_text(json.dumps(obj,indent=2)+'\n')
    assert obj['response']['backend']=='aqueduct' and obj['response']['model']=='qwen-3.6-35b'
    assert ready_text(obj['response']['text'])
    print('Aqueduct/qwen-3.6-35b readiness PASS; zero scientific decisions')

if __name__=='__main__':main()
