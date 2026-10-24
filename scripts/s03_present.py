"""Post-outcome S03 interpretation from prespecified metrics; no estimation/tuning.

The pre-run renderer/analysis remain frozen. This adds the observed cycling
interpretation and distinguishes the directional queue verdict from a null claim.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.render_report import main as render_base


def main():
    render_base()
    result=json.loads(Path('results/s03_calculator.json').read_text())
    assert not result['dry']
    metrics=result['metrics'];q=metrics['quantity'];d=q['paired_difference']
    changes=metrics['absolute_change']['paired_difference']
    lag=metrics['lag_conditional_regret'];actual=metrics['actual_stage_regret']
    profit=metrics['profit']['paired_difference'];pt=profit['paired_t_ci95'];qt=d['paired_t_ci95']
    all_means={c:sum(g['all_rounds']['quantity'] for g in result['games'] if g['condition']==c)/5
               for c in ['none','calculator']}
    all_diffs=[]
    for seed in range(24060,24065):
        by={g['condition']:g['all_rounds']['quantity'] for g in result['games'] if g['seed']==seed}
        all_diffs.append(by['calculator']-by['none'])
    n_all_negative=sum(x<0 for x in all_diffs)
    text=(f'**S03:** **{result["verdict"]} for the predicted increase**; controls produced above Nash 6. '
          f'All five **r4–12** differences are negative (t [{qt[0]:+.3f}, {qt[1]:+.3f}], registered higher-output p={d["exact_signflip_p_upper"]:.5f}); '
          f'over all 12 rounds, {n_all_negative}/5 are negative and calculator mean is {all_means["calculator"]:.3f}. '
          f'Paths oscillate: absolute change rises {changes["mean"]:+.3f}; '
          f'lag-conditioned regret falls {lag["none"]["mean"]:.3f}→{lag["calculator"]["mean"]:.3f} (table-adherence check), '
          f'current-rivals regret rises {actual["none"]["mean"]:.3f}→{actual["calculator"]["mean"]:.3f}. '
          'The primary window has an extra low-output phase; price/profit/endpoints are phase-sensitive. '
          f'Profit t [{pt[0]:+.3f}, {pt[1]:+.3f}] spans zero. '
          'Arithmetic, salience and lagged-response cues remain bundled; no collusion claim. '
          '[All S03 outcomes](REPORT_DETAILS.md#s03--exact-conditional-own-profit-calculator).')
    report=Path('REPORT.md').read_text()
    old=next(line for line in report.splitlines() if line.startswith('**S03:**'))
    report=report.replace(old,text)
    report=report.replace(f'| **{result["verdict"]}** |',f'| **{result["verdict"]} for predicted increase** |')
    Path('REPORT.md').write_text(report)
    details=Path('REPORT_DETAILS.md').read_text()
    marker='# S03 — exact conditional own-profit calculator\n'
    all_means={c:sum(g['all_rounds']['quantity'] for g in result['games'] if g['condition']==c)/5
               for c in ['none','calculator']}
    interpretation=f'''
**Observed direction and mechanism diagnostic (post-outcome interpretation,
prespecified metrics):** the predicted increase failed; all five seed contrasts
are negative *in r4–12*. Controls produced above symmetric Nash 6 (mean
6.719 in the primary window), so the proposed removal-of-restraint mechanism
was not present in this baseline. The frozen reverse screen also requires a mean decrease of at
least one unit, so the result remains {result['verdict']} under the unchanged rule.
This label is about the directional hypothesis, not lack of behavioral change.
The plotted quantities oscillate, absolute changes rise {changes['mean']:+.3f},
lag-conditioned stage regret falls to {lag['calculator']['mean']:.3f} (none
{lag['none']['mean']:.3f}), while current-rivals regret rises to
{actual['calculator']['mean']:.3f} (none {actual['none']['mean']:.3f}). This pattern
is consistent with following lagged best responses; it does not identify the
reasoning mechanism or coordinated intent. The primary 9-round window has an
unequal mix of alternating phases. Prespecified all-round quantity means are
none {all_means['none']:.3f}, calculator {all_means['calculator']:.3f}; endpoint and
window interpretations should acknowledge the cycling phase. No window/rule
was changed. All-round seed differences in seed order are
{', '.join(f'{v:+.6f}' for v in all_diffs)}: only {n_all_negative}/5 are negative.
The decrease relative to control reflects both the above-Nash baseline and the
odd window's cycling phase; it does not demonstrate a steady low-output regime.
Lag-conditioned regret is a table-adherence/manipulation check, not independent
evidence of better optimization. Current-rivals regret is a one-stage diagnostic
consistent with simultaneous lagged responses, not a dynamic rationality test.
Primary-window price/profit differences and the final-round row are phase-sensitive;
all five final rounds occur in a low-output phase. Calculator profit is below
static symmetric Nash profit 36 in both the primary window and all rounds.
Secondary outcomes and the reverse-tail p are descriptive, with no
multiplicity adjustment or secondary HIT. No sibling detector was tested here.
The deterministic-cycle/Nash checks reproduce with
`uv run python scripts/s03_economics.py` ([output](logs/s03_economics.json)).
Current rendered interpretation reproduces with `uv run python scripts/s03_present.py`;
the original pre-outcome renderer and all analysis hashes remain unchanged.
'''
    audit=json.loads(Path('logs/s03_execution_audit.json').read_text())
    interpretation+=f'\n**Execution audit:** every one of {audit["cached_responses"]} raw response keys is consumed exactly\nonce; all calls started before the cutoff. Invalid retries: calculator\n{audit["invalid_retries_by_arm"]["calculator"]}, none {audit["invalid_retries_by_arm"]["none"]}; all exceeded the 40-word\nreasoning limit. Invalid attempts remain cached, with no retroactive acceptance.\nRaw files are newline-terminated and unchanged. Reproduce before any replay:\n`uv run python scripts/s03_audit.py`. Frozen Cache recovery can normalize a damaged\nlast line before rejecting mutation, so verify these raw preconditions first.\n[Read-only execution audit](logs/s03_execution_audit.json).\n'
    details=details.replace(marker,marker+interpretation,1)
    details=details.replace('Exploratory attacks on the sibling projects\' price-market findings. Iteration 1,','Historical S01/S02 results from iteration 1; rendering',1)
    details=details.replace('**Next:** cover B, D, E, F and an `own` idea before deepening a prior axis.\nS03 arithmetic-tool idea is queued, not run. Any promotion needs fresh seeds.','**Historical iteration-1 queue:** superseded by the S04 and S03 sections below.\nCurrent remaining axes are D/E/F. Any promotion needs fresh registered seeds.',1)
    Path('REPORT_DETAILS.md').write_text(details)
    provenance=dict(time_utc=datetime.now(timezone.utc).isoformat(),analysis_changed=False,
                    thresholds_changed=False,post_outcome_interpretation=True,
                    inputs=['results/s03_calculator.json','figures/s03_calculator.png','logs/s03_economics.json'])
    Path('logs/s03_presentation.json').write_text(json.dumps(provenance,indent=2)+'\n')


if __name__=='__main__':
    main()
