"""Independent structure/economics audit of all renamed S61 histories; no LLM calls."""
import json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s61_replay import select_cases,request,write

def check():
    rounds=notes=0;cases=select_cases()['cases'];details=[]
    for c in cases:
        mapping={c['agent']:c['partner'],c['partner']:c['agent']}
        original=request(c,'anchor');renamed=request(c,'swapped')
        assert request(c,'repeat')==original
        def transform(obj):
            if type(obj) is dict:return {mapping.get(k,k):transform(v) for k,v in obj.items()}
            if type(obj) is list:return [transform(v) for v in obj]
            if type(obj) is str:return ''.join(mapping.get(w,w) for w in re.split(r'(\W+)',obj))
            return obj
        def fields(req):
            p=req['prompt']
            return {name:json.loads(p.split(marker,1)[1].split('\n',1)[0]) for name,marker in [('history','Completed public rounds: '),('statuses','Current authoritative statuses: '),('notes','Notes file snapshot: ')]}
        before,after=fields(original),fields(renamed)
        assert transform(before)==after and transform(after)==before
        for h in before['history']:
            ids=list(h['statuses']);assert len(ids)==2
            for who in ids:
                partner=next(x for x in ids if x!=who)
                action=h['reviews'][who][partner];incoming=h['reviews'][partner][who]
                assert type(action) is bool and type(incoming) is bool
                charge=3*int(action and h['statuses'][partner]=='TYPE-Y')
                score=6*incoming+int(action)-charge
                assert h['charges'][who][partner]==charge and h['scores'][who]==score
            rounds+=1
        notes+=len(before['notes'])
        # Original non-ID tokens and all formatting survive one swap.
        for field in ['system','prompt']:
            clean=lambda text:re.sub(r'\b[ABC]\b','<ID>',text)
            assert clean(original[field])==clean(renamed[field])
            assert len(original[field].encode())==len(renamed[field].encode())
        details.append(dict(case_id=c['case_id'],mapping=mapping,history_rounds=len(before['history']),notes=len(before['notes']),system_bytes=len(original['system'].encode()),prompt_bytes=len(original['prompt'].encode())))
    return dict(passed=True,contexts=len(cases),public_round_records=rounds,note_records=notes,independent_primitive_economics=True,structured_transform_roundtrip=True,repeat_request_byte_identical=True,cases=details)

if __name__=='__main__':
    result=check();write('logs/s61_context_audit.json',result);print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
