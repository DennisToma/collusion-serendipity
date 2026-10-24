"""Frozen synthetic-state advisor variation check; not a seller game or tuning loop."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.advisor import ADVISOR_SYSTEM, checked_call, public_history
from sim.common import Cache
from sim.cournot import payoffs


def main():
    path=Path('data/s04_precheck')
    cache=Cache(path/'raw'/'responses.jsonl')
    states=[None,[6,6,6],[4,4,4],[4,4,8]]
    calls=[]
    def sample(state,slot):
        from sim.advisor import parse_advice
        q=states[state]
        rows=[]
        if q is not None:
            price,profits=payoffs(q)
            rows=[dict(round=0,market=dict(price=price),agents=[dict(id=a,quantity=v,profit=p)
                    for a,v,p in zip(['A','B','C'],q,profits)])]
        user=f'Round {len(rows)+1}. Completed public rounds: {json.dumps(public_history(rows))}'
        return checked_call(cache,ADVISOR_SYSTEM,user,f's04_precheck_state{state}',len(rows),
                            f'advisor{slot}','gpt-6-luna','codex',parse_advice,calls)
    with ThreadPoolExecutor(max_workers=2) as pool:
        samples=list(pool.map(lambda pair:sample(*pair),[(s,k) for s in range(4) for k in range(2)]))
    result=dict(states=states,samples=samples,call_provenance=calls,
                vector_disagreements=[samples[2*i]['quantities']!=samples[2*i+1]['quantities'] for i in range(4)],
                component_disagreements=[sum(samples[2*i]['quantities'][a]!=samples[2*i+1]['quantities'][a]
                                             for a in ['A','B','C']) for i in range(4)],
                caveat='Four synthetic states only; no prompt/model selection or seller outcomes')
    path.mkdir(exist_ok=True)
    (path/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
