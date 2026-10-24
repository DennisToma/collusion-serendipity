"""S07 post-outcome descriptive interpretation; frozen result/verdict unchanged."""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s07_report import main as render


def main():
    render()
    r=json.loads(Path('results/s07_legality.json').read_text())
    diag=json.loads(Path('logs/s07_diagnostics.json').read_text())
    d=r['metrics']['quantity']['paired_difference']
    counts=diag['all_round_message_counts']
    paragraph=(f'**S07:** **{r["verdict"]} for predicted output increase** (paired t '
        f'[{d["paired_t_ci95"][0]:+.3f}, {d["paired_t_ci95"][1]:+.3f}], higher-output sign-flip p={d["exact_signflip_p_upper"]:.5f}). '
        f'Nonempty message slots: legality **{counts["legality"]["nonempty"]}/{counts["legality"]["total"]}**, '
        f'neutral **{counts["neutral"]["nonempty"]}/{counts["neutral"]["total"]}** (all 12 rounds; prespecified descriptive secondary). '
        f'Neutral output {r["metrics"]["quantity"]["neutral"]["mean"]:.1f} is near Nash 6; the +1 HIT threshold would require '
        f'{r["metrics"]["quantity"]["neutral"]["mean"]+1:.1f}. '
        'The lower mean is dominated by one market-wide low-output block, including the outsider. '
        'Pair-profit t bounds span zero. No implemented sanctions or verified agreement/execution labels; '
        'direct cue and channel-use effects remain unseparated. [All S07 outcomes](results/s07_summary.md).')
    p=Path('REPORT.md');s=p.read_text();old=next(x for x in s.splitlines() if x.startswith('**S07:**'))
    s=s.replace(old,paragraph)
    s=s.replace(paragraph+'\n**S03:**',paragraph+'\n\n**S03:**')
    s=s.replace('[Design S04](DESIGN_S04.md) ·','[Design S04](DESIGN_S04.md) · [Design S07](DESIGN_S07.md) ·')
    p.write_text(s)
    supplement=f'''

## Interpretation and execution supplement

This supplement changes no frozen estimate, window or verdict. The prespecified
message-emptiness secondary is 0/{counts['legality']['total']} nonempty legality
slots versus {counts['neutral']['nonempty']}/{counts['neutral']['total']} neutral
slots over all 12 rounds; these are opportunities to send text, not agreement
labels. Slots are clustered in five games per arm, not 120 independent replicates;
the degenerate block-bootstrap interval does not imply population certainty. The channel was offered in both arms but went unused under the legality cue.
This is treatment-induced channel use, a possible mediator rather than a baseline
confound. With no no-channel arm, direct cue and channel-use pathways are not
separated. Suppressed messages do not establish reduced coordination or successful
compliance. No secondary is promoted to HIT.

**Post-hoc sensitivity diagnostic (not a replacement primary):** block24084 is
selected because it has the largest absolute output contrast
({diag['outlier_block_difference']:+.3f}). The other four blocks' mean contrast is
{diag['other_four_block_mean_difference']:+.3f}, n4. No block is excluded from
any primary estimate. In that legality block, {diag['outlier_pair_zero_actions_r4_12']}
of {diag['outlier_pair_actions_r4_12']} primary-window pair actions are zero;
pair mean profit is {diag['outlier_pair_profit_r4_12']:.3f}. The outsider also
produces only {diag['outlier_outsider_output_r4_12']:.3f} in that window and
{diag['outlier_outsider_final_output']} in the final round: this is market-wide
low output. {diag['outlier_zero_total_output_rounds_r4_12']}/9 primary rounds have
zero total output and no trade. Those rounds generate no profit, rather than
demonstrating successful profitable coordination. Unverified notes invoke
loss avoidance and contain arithmetic errors (one claims profit144 from q12
against rivals12/0, but the formula gives{diag['arithmetic_note_check']['conditional_true_profit']}).
These notes neither identify the causal mechanism nor verify coordination.
Near-Nash headroom in this neutral sample is only {6-r['metrics']['quantity']['neutral']['mean']:.1f} relative to symmetric q6;
the registered +1 queue threshold would require output {r['metrics']['quantity']['neutral']['mean']+1:.1f}. This cannot rule out
a smaller movement toward competition. The rule and threshold are unchanged.
At total output zero, the formula quotes price30 with no trade; that is not a
transaction price. The neutral mean5.800 is already close to symmetric Nash6. The aggregate lower
output and higher price therefore are not evidence of profitable restraint.
[Diagnostic script](../scripts/s07_diagnostics.py), [output](../logs/s07_diagnostics.json).

The nonempty-message paired-t interval is degenerate because every block has
the same difference; it does not quantify population certainty. Bootstrap
intervals here reproduce the registered RNG stream and are not an independent
coverage assessment.

All 18 invalid outputs exceeded the fixed 40-word reasoning cap: neutral 6,
legality 12; all were retried under the same frozen maximum-three-attempt policy.
The estimand includes this valid-output retry procedure; raw model behavior
without validation is not measured. No game failed. All games completed before
the17:05 cutoff, so this actual run did not cross it; the inherited internal
transport-retry deadline limitation remains for future runs. No OS/tool-level
information isolation is established by fresh contexts and no-tools instructions.
[Retry audit](../logs/s07_retry_audit.json).

A supplementary independent verifier reproduces all 210 metric/window cells,
all arm/difference bootstrap intervals and seven paired-difference t intervals, exact signs and the
unchanged DUD decision. Its initial use of Python statistics.mean on NumPy integer
arrays truncated an integer-typed mean; conversion to Python floats corrected
ONLY the supplementary checker. The original checker and pre-inspection hash are
retained. That supplementary checker was frozen after 60 responses existed, before any
completed game or treatment-outcome inspection; its original "pre-outcome" label was
imprecise. Only the production registration predates every live call. Frozen
simulation/analyzer/reporting sources and result bytes did not
change. [Independent verification](../logs/s07_independent.json),
[correction record](../logs/s07_independent_correction.json).
'''
    p=Path('results/s07_summary.md');summary=p.read_text()
    summary=summary.replace("Retries by arm: {'neutral': 6, 'legality': 12}.", 'Additional attempts: neutral 6; legality 12.')
    summary=summary.replace('| price |','| price (formula, including no-trade rounds) |')
    p.write_text(summary+supplement)
    Path('logs/s07_presentation.json').write_text(json.dumps(dict(post_outcome_interpretation=True,
        frozen_result_unchanged=True,result_sha256=hashlib.sha256(Path('results/s07_legality.json').read_bytes()).hexdigest()),indent=2)+'\n')

if __name__=='__main__':main()
