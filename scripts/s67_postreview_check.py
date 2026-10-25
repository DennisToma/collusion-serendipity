"""Actual verifier rejection of altered round/game/interval/aggregate records."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.s67_independent import verify
from scripts.s67_audit import checked_manifest


def main():
    manifest = checked_manifest()
    original = Path('results/s67_incentives.json').read_bytes()
    r = json.loads(original)
    verify(r)
    def round_bonus(v):
        d = v['rounds'][0]['final']
        d[next(iter(d))] += .5
    def game_total(v):
        v['games'][0]['totals']['stage_regret'] += .5
    def exact_endpoint(v):
        d = v['metrics']['stage_regret']['difference']['ci95_exact']
        d[0] = str(Fraction(d[0])+Fraction(1, 10**13))
    def aggregate_loss(v):
        v['counts']['individual']['organization_loss'] += 10
    def missing_metric(v):
        del v['metrics']['organization_loss']
    def stage_regret(v):
        d = v['stage_table'][0]['regret_by_agent']
        d[next(iter(d))] += .5
    def opportunity(v):
        v['counts']['individual']['both_y'] += 1
    def pareto_count(v):
        v['counts']['individual']['strict_pareto_rounds'] += 1
    checks = [round_bonus, game_total, exact_endpoint, aggregate_loss, missing_metric, stage_regret, opportunity, pareto_count]
    rejected = []
    for mutate in checks:
        altered = copy.deepcopy(r)
        mutate(altered)
        try:
            verify(altered)
        except AssertionError:
            rejected.append(mutate.__name__)
        else:
            raise AssertionError('Incorrect record accepted: '+mutate.__name__)
    assert Path('results/s67_incentives.json').read_bytes() == original
    baseline = json.loads(Path('data/s67_registration.json').read_text())['older_report_rows']
    report = Path('REPORT.md').read_text()
    def check_rows(text):
        rows = [line for line in text.splitlines() if line.startswith('| S')]
        assert rows[:-1] == baseline and len(rows) == len(baseline)+1
    check_rows(report)
    try:
        check_rows(report.replace(baseline[0], baseline[0]+' fabricated extension', 1))
    except AssertionError:
        pass
    else:
        raise AssertionError('Extended older report row accepted')
    result = dict(passed=True, actual_verifier_rejected=rejected,
                  mutations_in_memory_only=True, original_scientific_bytes_unchanged=True,
                  prior_pilot_rows_exact_line_match=len(baseline), extended_older_row_rejected=True,
                  source_input_hashes_checked=len(manifest['input_and_source_sha256']),
                  older_scientific_paths_checked=len(manifest['older_science_sha256']),
                  unique_frozen_paths=len(set(manifest['input_and_source_sha256']) | set(manifest['older_science_sha256'])))
    Path('logs/s67_postreview_mutations.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
