"""Post-outcome presentation-only fix for frozen S25 renderer's one-use anchor.

The immutable renderer consumes an S24 prose anchor it removes on its first run.
Restore that presentation precondition and then render; scientific sources,
raw data, all metrics/thresholds and result JSON remain unchanged. Add the explicit
observed low-exposure caveat and correct the reproduction command in prose.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s25_present import present as frozen_present

ANCHOR=('S24 observed **1/40 partner TYPE-Y approvals in each identity condition**. '
        'Low observed rates and five selected blocks limit sensitivity; DUD is a queue decision, '
        'not evidence that identity cues are equivalent.')
CAVEAT=('Neither fresh arm reproduced any of the four archived adverse approvals used '
        'to enrich the challenge. With no adverse baseline in the fresh action-first arm, '
        'this pilot cannot demonstrate an output-order correction mechanism. '
        'The common extra order instruction and fresh model draws also differ from S19; '
        'their effects are not separated here.')


def present():
    report_path=Path('REPORT.md');original=report_path.read_text()
    report=original
    if not any(x.startswith('S24 observed ') for x in report.splitlines()):
        line=next(x for x in report.splitlines() if x.startswith('S25 uses a deliberately enriched '))
        report=report.replace(line,ANCHOR)
    report_path.write_text(report)
    try:frozen_present()
    except BaseException:
        report_path.write_text(original);raise
    report=report_path.read_text()
    line=next(x for x in report.splitlines() if x.startswith('S25 uses a deliberately enriched '))
    report=report.replace(line,line+' '+CAVEAT)
    report=report.replace('<!-- S25 summary end -->',
        'S25 backend tools were instruction-restricted but not disabled; tool-use transcripts were not retained. '
        'Prompt isolation is verified, actual tool non-use is unverified.\n<!-- S25 summary end -->')
    report_path.write_text(report)
    summary=Path('results/s25_summary.md');text=summary.read_text()
    text=text.replace('scripts/s25_present.py','scripts/s25_present_safe.py')
    text=text.replace('The inclusive n5 sign-flip HIT gate',CAVEAT+'\n\nThe inclusive n5 sign-flip HIT gate')
    text=text.replace('All compliance statistics are descriptive secondary outcomes; no promotion.',
        'All compliance statistics are descriptive secondary outcomes; no promotion. '
        'Per-arm upper p values test a level against zero, not an output-order intervention; '
        'the compliance difference is the relevant cross-arm descriptive contrast. '
        'First-arm counts in the result come from the frozen schedule and were independently '
        'confirmed using raw start timestamps. The separate independent checker reconstructs '
        'decisions, orders and statistics; strict duplicate-key/provenance validation is supplied '
        'by the core publication gate.')
    text=text.replace('Five source blocks are uncertainty units.',
        'Codex tools were discouraged by instructions but not disabled; execution transcripts '
        'were not retained. Read-only sandboxing and an isolated working directory do not '
        'verify absence of filesystem/tool use. Five source blocks are uncertainty units.')
    summary.write_text(text)

if __name__=='__main__':present()
