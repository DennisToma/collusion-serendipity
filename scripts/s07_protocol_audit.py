"""Synthetic protocol-boundary verification, no LLM or scientific games."""
import contextlib
import io
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.cournot import run_game as old_game
from sim.legality import run_game as new_game

class Probe:
    dry=True
    def __init__(self): self.prompts=[]
    def call(self,system,user,tier,backend,rid,t,agent,attempt,model):
        self.prompts.append((t,agent,user))
        empty=('You have no message box.' in user or 'private_message must be empty' in user)
        return dict(text=json.dumps(dict(quantity=6,reasoning='synthetic protocol probe',
                            private_message='' if empty else f'marker_{t}_{agent}')),model='dry',backend='dry')

def main():
    results={}
    for name,fn,condition in [('S02',old_game,'private'),('S07',new_game,'neutral')]:
        probe=Probe()
        with contextlib.redirect_stdout(io.StringIO()):
            game=fn(24080,condition,probe,'gpt-6-luna','codex',2)
        gt=game[1] if isinstance(game,tuple) else game['ground_truth']
        pair=gt['assigned_pair']
        findings=[]
        for t,agent,user in probe.prompts:
            if t==1:
                partner=next((a for a in pair if a!=agent),None) if agent in pair else None
                findings.append(dict(agent=agent,in_pair=agent in pair,
                                     sees_own_sent_message=f'marker_0_{agent}' in user,
                                     sees_partner_message=f'marker_0_{partner}' in user if partner else False,
                                     sees_any_private_message='marker_' in user))
        assert all(f['sees_partner_message'] for f in findings if f['in_pair'])
        assert not any(f['sees_any_private_message'] for f in findings if not f['in_pair'])
        assert all(f['sees_own_sent_message']==(name=='S02') for f in findings if f['in_pair'])
        results[name]=findings
    results['scientific_inference']='Protocol check only: S02 channel also supplies own-sent-message memory; S07 recipient-only. No behavioral effect estimated.'
    Path('logs/s07_protocol_audit.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
