"""Independent exhaustive wage-grid stage economics, no simulator import."""
from fractions import Fraction as F
import itertools
import json
from pathlib import Path

if not __debug__:raise RuntimeError("No optimized research checks")


def payoff(wages, i):
    return (20-wages[i])/wages.count(wages[i]) if wages[i]==max(wages) else F(0)


def check():
    result={}
    for label,step in [('coarse',F(1)),('fine',F(1,2))]:
        grid=[i*step for i in range(int(20/step)+1)]
        equilibria=[];deviations=0
        for profile in itertools.product(grid,repeat=2):
            profits=[payoff(profile,i) for i in range(2)]
            assert sum(profits)+max(profile)==20
            best=[]
            for i in range(2):
                choices=[payoff(tuple(q if j==i else w for j,w in enumerate(profile)),i) for q in grid]
                deviations+=len(choices);best.append(max(choices))
            if best==profits:equilibria.append([float(w) for w in profile])
        expected=[[18.,18.],[19.,19.],[20.,20.]] if label=='coarse' else [[19.,19.],[19.5,19.5],[20.,20.]]
        assert equilibria==expected
        result[label]=dict(grid_size=len(grid),profiles=len(grid)**2,unilateral_choices=deviations,pure_nash=equilibria)
    return dict(passed=True,grids=result)

if __name__=='__main__':
    r=check();Path('logs/s41_economics.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
