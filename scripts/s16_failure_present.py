"""Present the aborted protocol; never estimate a market effect from partial games."""
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    r=json.loads(Path('results/s16_failure.json').read_text());assert r['primary_estimated'] is False
    assert r['rejected_responses_with_valid_bid_and_note_fields']==r['rejected_responses']
    from sim.notes import schedule
    ids=[f's16_{s}_{c}' for s,c in schedule()]
    valid=[r['runs'].get(rid,{}).get('accepted_decisions',0) for rid in ids]
    invalid=[r['runs'].get(rid,{}).get('rejected_responses',0) for rid in ids]
    fig,ax=plt.subplots(figsize=(9,4.5),layout='constrained')
    ax.barh(ids,valid,label='accepted decisions',color='#3479ad')
    ax.barh(ids,invalid,left=valid,label='rejected responses',color='#b55c36')
    ax.axvline(36,ls=':',color='gray',lw=1,label='36 accepted decisions for a complete game')
    ax.invert_yaxis();ax.set(xlabel='Cached responses (includes rejected attempts)',title='S16 aborted: no market effect estimate');ax.legend(fontsize=8)
    fig.savefig('figures/s16_failure.png',dpi=160);plt.close(fig)
    fatal=[x for x in r['rejection_details'] if x['run_id']=='s16_24242_shared' and x['round_zero_based']==2 and x['agent']=='C']
    words=[x['reasoning_words'] for x in fatal]
    lines=['# S16 — Notes-file pilot stopped by its registered output rule','',
        '**FAILED / scientifically unclassified. No payment effect, confidence interval, sign test, profit contrast or note-use treatment comparison is estimated.** The frozen complete-dataset gate rejected the failed run; completed games are retained as evidence, without a selected-subset estimate.', '',
        f"Planned {r['planned_games']} games /5 fresh paired blocks, T12, codex/gpt-6-luna; zero tuning. Started {r['started_games']}, complete {r['complete_games']}, failed/partner-aborted {r['failed_games']}, unstarted {r['unstarted_games']}. {r['responses']} cached responses: {r['accepted_decisions']} accepted decisions and {r['rejected_responses']} rejected responses. All rejections are overlong reasoning (>40 words), not invalid bids or oversized notes.", '',
        f"At seed24242, shared arm, decision round3, firmC (a pair member, partnered withB) returned reasoning of {words} words on its three attempts. The registered policy aborted both games in that block. The self-arm call already in flight completed at {r['last_call_completed_utc']}, after the first failure record at {r['first_failure_recorded_utc']}; it began before that record. No subsequent block started. This is an output-contract failure, not evidence for or against notes affecting procurement behaviour.", '',
        'Both arms name the same designated partner, allow the same note-writing output and retain own notes. Shared adds next-round access to partner notes. The harness provides logical append/snapshot semantics, not an external filesystem-tool capability test. Access wording, delivered content, context length and endogenous writing remain bundled; no agreement/execution labels are verified.', '',
        'Three-supplier tender: common cost6, bids6..20, compulsory purchase of one divisible unit at the lowest bid, equal ties split quantity/revenue/cost. Frozen intended primary is shared−self mean buyer payment r4–12 across all5 blocks. It was never evaluated on this incomplete archive.', '',
        '| Run | Status | Accepted decisions | Rejected responses | Complete rounds |','|---|---|---:|---:|---:|']
    for rid in ids:
        g=r['runs'].get(rid,dict(status='unstarted',accepted_decisions=0,rejected_responses=0,complete_rounds=0))
        lines.append(f"| {rid} | {g['status']} | {g['accepted_decisions']} | {g['rejected_responses']} | {g['complete_rounds']} |")
    lines+=['',
        f"Verification: independent response parsing and rational stage-payoff reconstruction checked all {r['history_requests_checked']} saved public histories and {r['note_snapshot_requests_checked']} file snapshots. Own notes persist in both arms, partner notes appear only in shared, outsiders have no file, and no current-round actions/notes leak. Separate cache-only replay through the original frozen simulator consumes all {r['responses']} keys exactly once: four complete games match all rows/metadata, the three-attempt failure reproduces, and the partner's cached prefix ends at the recorded abort. All16 scientific sources match registration73fe09d and its client-observed prelaunch remote HEAD, local launch chronology, routes, sequential calls, arm overlap and seed barriers pass. Retained evidence is byte-identical. Analysis and live resume both fail closed. [Machine-readable evidence](s16_failure.json).", '',
        f"Rejected responses by arm and role: {json.dumps(r['rejections_by_arm_role'],sort_keys=True)}. These are observed counts with unequal partial exposure, not failure-rate comparisons. The IDEA ledger uses ODD only as a postfailure administrative queue label required by PLAN; the frozen scientific HIT/DUD/ODD screen was not evaluated.", '',
        'The failure auditor was written after the abort, from the frozen protocol and output-validity metadata. It performs no treatment-effect estimation and leaves scientific sources/raw evidence unchanged. Its source and mutation tests are reviewable. No replacement games, fallback model, relaxed parser, excluded block, pooling or secondary promotion. Retry failure cannot distinguish access effects from sampling or verbosity; no arm-specific failure-rate claim is warranted.', '',
        'Operational lesson for future, separately registered work: reconsider treating private-reasoning verbosity as an action-validity requirement when that field is never replayed. Any changed output contract needs fresh seeds and a new registration; this archive remains failed. Tiny samples, one model/shared service, bundled visibility cues, full bid disclosure and deterministic divisible ties limit any future scientific transfer. No sibling headline change.', '',
        '![Protocol completion only](../figures/s16_failure.png)', '',
        '[Design](../DESIGN_S16.md) · [Failure audit code](../scripts/s16_failure_audit.py) · [Reviews](../logs/s16_review_disposition.md) · [Release](../logs/s16_release.json) · [Reproduce](../README.md)']
    Path('results/s16_summary.md').write_text('\n'.join(lines)+'\n')
    report=Path('REPORT.md').read_text().replace('Iteration 8','Iteration 9')
    ls=[x for x in report.splitlines() if not x.startswith('| S16 ·') and not x.startswith('**S16:**')]
    pos=next(i for i,x in enumerate(ls) if x.startswith('| S14 ·'))
    ls.insert(pos+1,f"| S16 · C2, notes-file channel | Aborted under frozen strict-output rule: {r['complete_games']}/10 games complete; {r['responses']} responses, {r['rejected_responses']} overlong-reasoning rejections. No effect estimated. | **FAILED / unclassified** |")
    pos=next(i for i,x in enumerate(ls) if x.startswith('**S14:**'))
    ls.insert(pos,'**S16:** Same pair/writing cues and own-note persistence in both arms; shared adds partner access. Three consecutive >40-word reasoning outputs triggered the registered abort. All173 cached requests replay exactly; incomplete-data analysis and live restart are blocked. No replacement or selected-subset estimate. [Failure evidence and protocol figure](results/s16_summary.md).')
    ls.insert(pos+1,'')
    ls=[('**Next:** Different axis after C2; preregister a less brittle reasoning-output contract on fresh seeds. Favor workplace/labour settings. No secondary-driven promotion.' if x.startswith('**Next:**') else x) for x in ls]
    Path('REPORT.md').write_text(re.sub(r'\n{3,}','\n\n','\n'.join(ls)+'\n'))

if __name__=='__main__':main()
