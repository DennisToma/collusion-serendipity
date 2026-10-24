"""Independent exhaustive enumeration of S14 static integer-bid equilibria."""
from fractions import Fraction as F
import itertools
import json
from pathlib import Path

if not __debug__:
    raise RuntimeError('Research integrity checks require Python without -O')


def main(out='logs/s14_economics.json'):
    bids=range(6,21)
    def profits(v):
        low=min(v);n=v.count(low)
        return [F(low-6,n) if b==low else F(0) for b in v]
    equilibria=[]
    for v in itertools.product(bids,repeat=3):
        ps=profits(v)
        assert sum(ps)==min(v)-6
        if all(all(profits(list(v[:i])+[b]+list(v[i+1:]))[i]<=ps[i] for b in bids) for i in range(3)):
            equilibria.append(v)
    result=dict(grid=list(bids),profiles_enumerated=15**3,pure_nash_count=len(equilibria),pure_nash_payments=sorted({min(v) for v in equilibria}),pure_nash_profiles=equilibria,
                marginal_cost=6,maximum_feasible_payment=20,all20_profit_per_firm=str(F(14,3)),
                caveat='Static pure strategies only; repeated-game equilibria not classified; no collusion labels')
    assert result['pure_nash_payments']==[6,7]
    Path(out).write_text(json.dumps(result,indent=2)+'\n')
    print({k:v for k,v in result.items() if k!='pure_nash_profiles'})

if __name__=='__main__':main()
