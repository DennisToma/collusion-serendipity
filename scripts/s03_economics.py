"""Exhaustive static-game checks for interpretation, independent of LLM outcomes."""
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.cournot import payoffs
from sim.calculator import conditional_table


def main():
    equilibria=[]
    for quantities in itertools.product(range(13),repeat=3):
        _,profits=payoffs(quantities)
        optimal=True
        for agent in range(3):
            best=max(payoffs(list(quantities[:agent])+[q]+list(quantities[agent+1:]))[1][agent] for q in range(13))
            if profits[agent] != best:
                optimal=False
                break
        if optimal:
            equilibria.append(quantities)
    assert len(equilibria)==7 and (6,6,6) in equilibria
    assert all(sum(q)==18 for q in equilibria)
    assert set(equilibria)=={(6,6,6)}|set(itertools.permutations((5,6,7)))
    def best_responses(rival_total):
        table=conditional_table(rival_total)
        maximum=max(r['own_profit'] for r in table)
        return [r['quantity'] for r in table if r['own_profit']==maximum]
    assert best_responses(8)==[8] and best_responses(16)==[4]
    cycle=[4,8,4,8]
    assert sum(cycle)/len(cycle)==6
    out=dict(stage_nash_profiles=equilibria,asymmetric_nash_profiles=len(equilibria)-1,
             nash_total_output=18,symmetric_best_response_cycle=cycle,
             cycle_mean_quantity=6,cycle_absolute_change=4,
             maximum_one_stage_joint_profit=max(sum(payoffs(q)[1]) for q in itertools.product(range(13),repeat=3)))
    Path('logs/s03_economics.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':
    main()
