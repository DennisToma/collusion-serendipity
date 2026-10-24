"""Analytical S11 protocol reference, not LLM data or an experimental contrast."""
from fractions import Fraction
import json
from pathlib import Path
import statistics


def path(lag):
    qs=[]
    for t in range(12):
        if t<lag:q=4  # explicit toy initialization, not an LLM prediction
        else:
            rival_total=2*qs[t-lag]
            vals=[(max(0,30-rival_total-v)-6)*v for v in range(13)]
            q=min(v for v in range(13) if vals[v]==max(vals))
        qs.append(q)
    return qs


def main():
    output=dict(kind='analytical toy reference; not LLM data',initialization='q4 for each firm until first feedback',
                policy='simultaneous symmetric one-step conditional best response; smallest maximizer',arms={})
    for lag,c in [(1,'immediate'),(2,'delayed')]:
        qs=path(lag)
        # Verify exact table-regret zero after feedback, independently of sim helpers.
        for t in range(lag,12):
            rivals=2*qs[t-lag];gains=[(max(0,30-rivals-v)-6)*v for v in range(13)]
            assert gains[qs[t]]==max(gains)
        primary=Fraction(sum(abs(qs[t]-qs[t-1]) for t in range(3,12)),9)
        output['arms'][c]=dict(quantity_path=qs,primary_change=float(primary),primary_exact=str(primary),
                                all_round_mean=statistics.mean(qs),all_round_population_variance=statistics.pvariance(qs))
    a=output['arms'];assert a['immediate']['all_round_population_variance']==a['delayed']['all_round_population_variance']==4
    assert a['immediate']['all_round_mean']==a['delayed']['all_round_mean']==6
    output['primary_reduction_exact']=str(Fraction(a['immediate']['primary_exact'])-Fraction(a['delayed']['primary_exact']))
    output['interpretation']='Consecutive change can fall while mean and full-window variance stay identical. Toy periodicity is not stabilization, learning or collusion.'
    Path('logs/s11_analytical_reference.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))

if __name__=='__main__':main()
