"""Post-outcome algebraic clarification only;no observed outcomes or model calls."""
import itertools
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sim.author_bonus import outcome


def verify():
    cases=[]
    for types in itertools.product([False,True],repeat=2):
        x=sum(types);nash={b:(b+1)*x for b in [1,6]}
        for approval_bits in itertools.product([False,True],repeat=2):
            # Bits are indexed by author; a True bit approves that submission.
            nx=sum(a and t for a,t in zip(approval_bits,types))
            ny=sum(a and not t for a,t in zip(approval_bits,types))
            low=2*nx-ny;high=7*nx+4*ny
            statuses=dict(zip(['A','B'],types))
            reviews={'A':{'B':approval_bits[1]},'B':{'A':approval_bits[0]}}
            assert sum(outcome(reviews,statuses,0,0,'low')[0].values())==low
            assert sum(outcome(reviews,statuses,0,0,'high')[0].values())==high
            assert low<=nash[1]
            assert low-nash[1]==-2*(x-nx)-ny
            assert high-nash[6]==-7*(x-nx)+4*ny
            cases.append(dict(author_types=list(types),author_approvals=list(approval_bits),approved_x=nx,approved_y=ny,
                              low_pair_total=low,high_pair_total=high,low_stage_nash_total=nash[1],high_stage_nash_total=nash[6]))
    assert len(cases)==16
    return dict(passed=True,post_outcome_interpretation_only=True,observed_outcomes_read=False,scientific_calls=0,
                status_action_profiles_per_arm=16,payoff_profiles_total=32,low_always_at_most_stage_nash=True,
                low_gap_formula='-2*rejected_X-approved_Y',high_gap_formula='-7*rejected_X+4*approved_Y',cases=cases)


if __name__=='__main__':
    result=verify();Path('logs/s60_static_bound.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS32stage payoff profiles:low pair total never exceeds approve-X/reject-Y benchmark;no observed outcomes read')
