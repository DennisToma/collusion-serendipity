"""Exhaustive static wage equilibria; independent of simulator payoff code."""
import itertools,json
from fractions import Fraction as F
from pathlib import Path

def payoff(ws,i):
    return F(20-ws[i],ws.count(ws[i])) if ws[i]==max(ws) else F(0)

def enumerate_nash(n):
    found=[]
    for ws in itertools.product(range(21),repeat=n):
        if all(all(payoff(ws,i)>=payoff(ws[:i]+(q,)+ws[i+1:],i) for q in range(21)) for i in range(n)):
            found.append(ws)
    return found

def check():
    two=enumerate_nash(2);three=enumerate_nash(3)
    assert two==[(18,18),(19,19),(20,20)]
    expected=[p for p in itertools.product(range(21),repeat=3) if p==(19,19,19) or p.count(20)>=2]
    assert three==expected and len(three)==62
    return dict(passed=True,profiles_enumerated={'two':21**2,'three':21**3},nash_profiles={'two':two,'three':three},pure_nash_wage_range={'two':[18,20],'three':[19,20]})
if __name__=='__main__':
    r=check();Path('logs/s42_economics.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='nash_profiles'}))
