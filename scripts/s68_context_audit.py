"""Output-polarity equivalence and unchanged history audit; no simulated calls."""
import itertools,json
from scripts.s68_replay import select_cases,request,decoded,APPROVE_MAPPING,REJECT_MAPPING,HISTORY_NOTE,write,VIEWS
from sim.notepad import outcome

def check():
    cases=select_cases()['cases'];rounds=notes=profiles=0
    for c in cases:
        original=request(c,'anchor');inverted=request(c,'inverted')
        assert original==request(c,'repeat')
        assert original['system']==inverted['system']==c['original_system']
        assert len(original['prompt'])==len(inverted['prompt'])
        assert original['prompt']==c['original_prompt']+HISTORY_NOTE
        assert original['prompt'].count(APPROVE_MAPPING)==1 and original['prompt'].count(REJECT_MAPPING)==0
        assert inverted['prompt'].count(REJECT_MAPPING)==1 and inverted['prompt'].count(APPROVE_MAPPING)==0
        assert inverted['prompt'].replace(REJECT_MAPPING,APPROVE_MAPPING)==original['prompt']
        for marker in ['Completed public rounds: ','Current authoritative statuses: ','Notes file snapshot: ']:
            assert original['prompt'].count(marker)==inverted['prompt'].count(marker)==1
            a=json.loads(original['prompt'].split(marker,1)[1].split('\n',1)[0])
            b=json.loads(inverted['prompt'].split(marker,1)[1].split('\n',1)[0]);assert a==b
            if marker.startswith('Current'):
                assert all(type(v) is str and v in ['TYPE-X','TYPE-Y'] for v in a.values())
            if marker.startswith('Notes'):
                assert all(set(n)=={'round','author','text'} and type(n['round']) is int and type(n['author']) is str and type(n['text']) is str for n in a)
            if marker.startswith('Completed'):rounds+=len(a)
            if marker.startswith('Notes'):notes+=len(a)
        a,b=c['agent'],c['partner'];reverse=dict(c,agent=b,partner=a)
        for ax,bx,ab,ba,view in itertools.product([False,True],[False,True],[False,True],[False,True],VIEWS):
            encode=lambda action:not action if view=='inverted' else action
            fresh={a:{b:decoded(dict(reviews={b:encode(ab)}),c,view)},b:{a:decoded(dict(reviews={a:encode(ba)}),reverse,view)}}
            assert fresh=={a:{b:ab},b:{a:ba}},'Production decoding failed'
            scores,bad,charges=outcome(fresh,{a:ax,b:bx},c['seed'],c['turn'],'shared')
            assert scores=={a:6*int(ba)+int(ab)-3*int(ab and not bx),b:6*int(ab)+int(ba)-3*int(ba and not ax)}
            assert charges=={a:{b:3*int(ab and not bx)},b:{a:3*int(ba and not ax)}}
            assert bad==int(ab and not bx)+int(ba and not ax)
            profiles+=1
    return dict(passed=True,contexts=10,public_round_records=rounds,note_records=notes,decoded_case_view_stage_profiles=profiles,repeat_request_byte_identical=True,history_unchanged=True,production_polarity_decoder_exercised=True)
if __name__=='__main__':
    r=check();write('logs/s68_context_audit.json',r);print(json.dumps(r,indent=2))
