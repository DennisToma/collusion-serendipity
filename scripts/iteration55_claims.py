"""Offline table-to-artifact audit, with explicit field bindings for all pilots.

This checks reporting fidelity, not the validity of the original analyses. It
imports no simulation, transport, historical renderer, or LLM module. Artifacts
and original rows are bound to the pre-audit Git revision. All numeric tokens in
bold result spans are checked, plus the two failure rows' unbolded counts.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '88550b12fb796fe4292dd49bc8a05f7dc5adc245'
INDEX = 'results/iteration54_portfolio.json'
OUT = 'results/iteration55_claim_audit.json'
NUM = re.compile(r'[+-]?\d+(?:\.\d+)?')
SOURCE_NAMES = '''s01_digits s02_cournot s04_advisor s03_calculator s07_legality
s09_replay s11_delay s06_denomination s14_tender s16_failure s18_workplace
s19_labels s21_audit s22_enforcement s24_identity s25_order s27_concentration
s29_notepad s28_payoff s31_labor s32_resource s33_leniency s34_salience
s35_asymmetry s36_grossnet s38_horizon s37_policyword s40_memory s42_entry
s43_payoff s41_ticksize s45_reviewring s44_payoff s48_notes s47_example
s50_terminal s51_penalty s53_payoffs s54_opportunities s56_coalitions
s55_visibility s58_history s59_history s60_author_bonus s62_notepad_qwen
s61_identity s64_memory_retention s65_bonus_pooling s67_incentives
s66_payoff_order s69_pooled_enforcement s68_failure s72_temporal
s70_bonus_endowment'''.split()
SOURCES = {name.split('_', 1)[0].upper(): 'results/' + name + '.json' for name in SOURCE_NAMES}
IDEA_APPEND = ('2026-10-25T13:00:00+00:00\tS74-proposal\town\tYoked cross-game decoy notes separate partner-contingent delivery from realistic note framing\tA fresh matched partner-note versus status-matched past-only decoy-note control changes approvals despite similar note style and volume;never include future information\tqueued-not-run\tNew idea iteration55 from table-wide fidelity audit and unresolved channel attribution;requires fresh registration,no calls or estimates\tnot-run\n')


def require(test, message):
    if not test:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def load(name):
    return json.loads((ROOT / name).read_text())


def preserved(baseline):
    """Bind every preexisting non-editorial file to Git, including old code."""
    mutable = {'STATUS.md', 'REPORT.md', 'README.md'}
    count = 0
    for line in git('ls-tree', '-r', baseline).decode().splitlines():
        metadata, name = line.split('\t', 1)
        require(metadata.split()[1] == 'blob', 'Unexpected Git object: ' + name)
        if name == 'IDEAS.tsv':
            require((ROOT / name).read_bytes() == git('show', baseline + ':' + name) + IDEA_APPEND.encode(), 'Idea ledger differs from exact prospective append')
            continue
        if name in mutable:
            continue
        data = (ROOT / name).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == metadata.split()[2], 'Preexisting file changed: ' + name)
        count += 1
    old_log = git('show', baseline + ':STATUS.md').decode().split('## Log\n', 1)[1]
    current_log = (ROOT / 'STATUS.md').read_text().split('## Log\n', 1)[1]
    require(current_log.startswith(old_log), 'Historical STATUS log changed')
    return count


def field(obj, pointer):
    for part in pointer.split('/'):
        obj = obj[int(part)] if isinstance(obj, list) else obj[part]
    return obj


def spec(pointer, scale=1):
    return {'pointer': pointer, 'scale': scale}


def triple(pointer):
    return [spec(pointer + '/mean'), spec(pointer + '/ci95/0'), spec(pointer + '/ci95/1')]


def resolve(s, obj):
    value = field(obj, s['pointer'])
    require(type(value) in (int, float, str), 'Non-numeric scalar: ' + s['pointer'])
    return Fraction(str(value)) * Fraction(str(s['scale']))


def plan(pid, obj):
    """Every displayed bold token has a semantic path, never a value search."""
    metric = obj.get('primary_metric')
    pair = {
        'S02': ('pair_quantity', 'none', 'private'),
        'S04': ('pair_quantity', 'independent', 'shared'),
        'S03': ('quantity', 'none', 'calculator'),
        'S07': ('quantity', 'neutral', 'legality'),
        'S09': ('quantity', 'retain', 'erase'),
        'S11': (metric, 'immediate', 'delayed'),
        'S06': (metric, 'unit', 'cent'),
        'S14': (metric, 'none', 'private'),
        'S18': (metric, 'self', 'shared'),
        'S19': (metric, 'normative', 'neutral'),
        'S22': (metric, 'certain', 'lottery'),
        'S24': (metric, 'human', 'ai'),
        'S27': (metric, 'three', 'two'),
        'S29': (metric, 'self', 'shared'),
        'S28': (metric, 'prose', 'table'),
        'S31': (metric, 'self', 'shared'),
        'S32': (metric, 'human', 'compute'),
        'S33': (metric, 'baseline', 'amnesty'),
        'S34': (metric, 'plain', 'flag'),
        'S35': (metric, 'symmetric', 'asymmetric'),
        'S36': (metric, 'net', 'gross'),
        'S38': (metric, 'hidden', 'known'),
        'S37': (metric, 'coded', 'payroll'),
        'S42': (metric, 'entry', 'control'),
        'S41': (metric, 'fine', 'coarse'),
        'S45': (metric, 'self', 'shared'),
        'S54': (metric, 'alternating', 'synchronized'),
    }
    if pid in pair:
        m, a, b = pair[pid]
        prefix = 'metrics/' + m
        return [spec(prefix + '/' + a + '/mean'), spec(prefix + '/' + b + '/mean')] + triple(prefix + '/paired_difference')
    if pid == 'S01':
        return triple('llm_v1/primary_within_channel') + triple('llm_ds_p2/primary_within_channel')
    if pid == 'S21':
        return [spec('metrics/A/counts/error'), spec('n_cases'), spec('metrics/AT/counts/error'), spec('n_cases')] + triple('contrasts/AT_minus_A_error')
    if pid == 'S25':
        return [spec('counts/action_first/approved'), spec('n_cases'), spec('counts/reason_first/approved'), spec('n_cases')] + triple('contrasts/approved')
    replay = {
        'S40': ('retain', 'erase'), 'S43': ('control', 'table'),
        'S44': ('ascending', 'descending'), 'S48': ('retain', 'erase'),
        'S47': ('low_example', 'high_example'), 'S50': ('hidden', 'final'),
        'S51': ('baseline', 'strong'), 'S55': ('visible', 'masked'),
        'S58': ('retain', 'erase'), 'S59': ('original', 'compact'),
    }
    if pid in replay:
        a, b = replay[pid]
        return [spec('metrics/' + a + '/mean'), spec('metrics/' + b + '/mean')] + triple('contrast')
    counts = {
        'S60': ('high', 'low'), 'S62': ('self', 'shared'),
        'S64': ('persistent', 'reset'), 'S65': ('individual', 'pooled'),
        'S66': ('allocated_first', 'final_first'),
        'S69': ('low_charge', 'high_charge'), 'S70': ('baseline', 'endowed'),
    }
    if pid in counts:
        # Five games, eight Y opportunities each. Verify this denominator below.
        a, b = counts[pid]
        return [spec('metrics/pair_bad/' + a + '/mean', 40), spec('n_games', 4),
                spec('metrics/pair_bad/' + b + '/mean', 40), spec('n_games', 4)] + triple('metrics/pair_bad/paired_difference')
    if pid == 'S61':
        return [spec('mismatch_counts/swap_mismatch'), spec('n_cases'), spec('mismatch_counts/repeat_mismatch'), spec('n_cases')] + triple('contrast')
    if pid == 'S53':
        return [spec('counts/' + arm + '/' + key)
                for key in ['y_approvals', 'missed_x', 'mutual_y_rounds', 'strict_pareto_rounds', 'stage_regret', 'pair_excess']
                for arm in ['self', 'shared']]
    if pid == 'S56':
        return [spec('totals/' + arm + '/' + key)
                for key in ['above_nash', 'coalition_stable', 'strict_pair_improvement']
                for arm in ['none', 'private']] + triple('metrics/coalition_stable/difference')
    if pid == 'S67':
        return [spec('counts/individual/costly_y_approvals'), spec('counts/pooled/costly_y_approvals'),
                spec('counts/pooled/profitable_y_rejections'), spec('counts/pooled/y_opportunities')] + triple('metrics/stage_regret/difference')
    if pid == 'S72':
        return [spec('metrics/full_window_both_gain/self/mean', 5), spec('n_blocks'),
                spec('metrics/full_window_both_gain/shared/mean', 5), spec('n_blocks')] + triple('metrics/full_window_both_gain/difference') + [
                spec('metrics/stage_both_gain/self/mean', 40), spec('n_blocks', 8),
                spec('metrics/stage_both_gain/shared/mean', 40), spec('n_blocks', 8)]
    if pid in ['S16', 'S68']:
        return []
    raise ValueError('Missing explicit mapping: ' + pid)


def check_token(token, value, context):
    # Match the original display precision/sign, including its floating-point
    # formatting convention. No broad tolerance that could hide a last-digit bug.
    if '.' in token:
        precision = len(token.split('.')[1])
        fmt = ('+' if token.startswith('+') else '') + '.' + str(precision) + 'f'
        expected = format(float(value), fmt)
    else:
        require(value.denominator == 1, context + ': expected an integer')
        expected = ('+' if token.startswith('+') and value >= 0 else '') + str(int(value))
    require(token == expected, context + ': displayed ' + token + ', artifact formats as ' + expected)


def category(obj, pid):
    if pid in ['S16', 'S68']:
        require(obj['scientific_verdict'] is None, pid + ': failure gained a verdict')
        return 'FAILED'
    verdict = obj.get('verdict', '')
    if verdict.startswith('DUD'):
        return 'DUD'
    if verdict.startswith('ODD') or verdict in ['UNINFORMATIVE', 'UNRESOLVED']:
        return 'ODD'
    if pid == 'S01':
        # S01 predates the common result envelope; its frozen screen is in DESIGN.
        require('verdict' not in obj, 'Unexpected S01 schema')
        return 'DUD'
    raise ValueError(pid + ': unmapped artifact verdict ' + verdict)


def metadata_claims(cell, obj, pid):
    """Named sample/window fields; source pilot IDs are not sample counts."""
    checks = []
    def check(label, shown, expected, binding):
        require(shown == expected, pid + ': ' + label + ' differs from ' + binding)
        checks.append(dict(label=label, displayed=shown, expected=expected, binding=binding))
    block = re.search(r'(\d+)\s*(?:seed |source |original |time-matched )?(?:blocks|pairs|observed prefixes)', cell)
    expected_blocks = obj.get('n_seed_blocks', obj.get('n_seeds', obj.get('n_source_blocks', obj.get('n_blocks'))))
    if expected_blocks is not None:
        require(block is not None, pid + ': no displayed block count')
        check('blocks', int(block[1]), expected_blocks, 'n_seed_blocks/n_seeds/n_source_blocks/n_blocks')
    if 'n_games' in obj or 'n_cases' in obj or 'n_blocks' in obj:
        leading = re.match(r'\s*(?:All)?(Ten|\d+)', cell)
        require(leading is not None, pid + ': missing leading sample count')
        shown = 10 if leading[1] == 'Ten' else int(leading[1])
        expected = obj.get('n_games', obj.get('n_cases', len(obj.get('games', []))))
        check('games or selected cases', shown, expected, 'n_games/n_cases/len(games)')
    window = re.search(r'r(\d+)[–-](\d+)', cell)
    if window and 'primary_rounds' in obj:
        check('primary rounds', window[1] + '..' + window[2], obj['primary_rounds'], 'primary_rounds')
    fresh = re.search(r'(\d+)\s*fresh decisions', cell)
    if fresh:
        if 'n_fresh_decisions' in obj:
            expected = obj['n_fresh_decisions']
        else:
            expected = sum(len(c['views']) for c in obj['cases'])
        check('fresh decisions', int(fresh[1]), expected, 'n_fresh_decisions or sum(len(case.views))')
    if pid == 'S01':
        counts = [obj['llm_v1']['runs'] + obj['llm_ds_p2']['runs'],
                  obj['llm_v1']['primary_within_channel']['n'], obj['llm_ds_p2']['primary_within_channel']['n']]
        prefix = cell.split('Pair-minus', 1)[0]
        check('scanned and channel samples', list(map(int, NUM.findall(prefix))), counts, 'runs/primary_within_channel.n by dataset')
    if pid == 'S21':
        calls = re.search(r'(\d+) gpt-6.1-sol calls', cell)
        require(calls is not None, 'S21: missing call count')
        check('saved auditor decisions', int(calls[1]), sum(len(c['views']) for c in obj['cases']), 'sum(len(case.views))')
    if pid in ['S53', 'S56']:
        per_arm = re.search(r'(?:over|Counts/)(\d+) rounds', cell)
        require(per_arm is not None, pid + ': missing round count')
        conditions = {r['condition'] for r in obj['rounds']}
        totals = [sum(r['condition'] == c for r in obj['rounds']) for c in conditions]
        require(len(conditions) == 2 and len(set(totals)) == 1, pid + ': imbalanced round arrays')
        check('rounds per arm', int(per_arm[1]), totals[0], 'rounds grouped by condition')
    return checks


def check_row(pilot, obj, row):
    pid = pilot['id']
    require(category(obj, pid) == pilot['category'], pid + ': category differs from artifact')
    cell = row.split('|')[2]
    spans = re.findall(r'\*\*(.*?)\*\*', cell)
    tokens = [token for span in spans for token in NUM.findall(span)]
    specs = plan(pid, obj)
    require(len(tokens) == len(specs), pid + ': numeric coverage mismatch')
    checks = []
    for token, binding in zip(tokens, specs):
        value = resolve(binding, obj)
        check_token(token, value, pid + '/' + binding['pointer'])
        checks.append(dict(display=token, exact_value=str(value), **binding))
    if pid in ['S16', 'S68']:
        require(not spans, pid + ': unexpected highlighted estimate')
        if pid == 'S16':
            extra = ['complete_games', 'planned_games', 'responses', 'rejected_responses']
            require(obj['primary_estimated'] is False, 'S16 gained an estimate')
        else:
            extra = ['accepted_responses', 'planned_decisions', 'admitted_requests']
            require(obj['behavioral_estimates_computed'] is False, 'S68 gained an estimate')
            require('exit143' in obj['failure_scope'], 'S68 exit scope changed')
        failure_tokens = NUM.findall(cell)
        # The exit143 token is bound to failure_scope above, not a numeric field.
        require(len(failure_tokens) == len(extra) + (pid == 'S68'), pid + ': failure coverage')
        for token, pointer in zip(failure_tokens, extra):
            binding = spec(pointer)
            check_token(token, resolve(binding, obj), pid + '/' + pointer)
            checks.append(dict(display=token, exact_value=str(resolve(binding, obj)), **binding))
    # Bind common sample sizes to arrays, rather than trusting n_* metadata alone.
    if 'n_games' in obj:
        games = obj.get('games', obj.get('records'))
        require(len(games) == obj['n_games'], pid + ': n_games versus records')
        seeds = {g['seed'] for g in games}
        require(len(seeds) == obj.get('n_seed_blocks', obj.get('n_seeds')), pid + ': block count')
    if 'n_cases' in obj:
        require(len(obj['cases']) == obj['n_cases'], pid + ': n_cases versus records')
        require(len({c['seed'] for c in obj['cases']}) == obj['n_source_blocks'], pid + ': source blocks')
    if 'n_blocks' in obj:
        require(len({g['seed'] for g in obj['games']}) == obj['n_blocks'], pid + ': posthoc source blocks')
        require(len(obj['games']) == 2 * obj['n_blocks'], pid + ': posthoc game count')
    if pid in ['S60', 'S62', 'S64', 'S65', 'S66', 'S69', 'S70']:
        require(obj['n_games'] == 10 and obj['n_seed_blocks'] == 5 and obj['primary_rounds'] == '3..10', pid + ': rate-to-count assumptions')
        conditions = {g['condition'] for g in obj['games']}
        for cond in conditions:
            games = [g for g in obj['games'] if g['condition'] == cond]
            require(len(games) == 5, pid + ': unequal arms')
            counts = [Fraction(str(g['primary']['pair_bad'])) * 8 for g in games]
            require(all(v.denominator == 1 and 0 <= v <= 8 for v in counts), pid + ': invalid opportunity count')
            require(sum(counts) == Fraction(str(obj['metrics']['pair_bad'][cond]['mean'])) * 40, pid + ': count versus game summaries')
    if pid == 'S72':
        for arm in ['self', 'shared']:
            games = [g for g in obj['games'] if g['condition'] == arm]
            rounds = [r for r in obj['rounds'] if r['condition'] == arm]
            require(len(games) == 5 and len(rounds) == 40, 'S72: scaling denominators')
            require(sum(g['both_gain'] for g in games) == Fraction(str(obj['metrics']['full_window_both_gain'][arm]['mean'])) * 5, 'S72: full-window count')
            require(sum(r['both_gain'] for r in rounds) == Fraction(str(obj['metrics']['stage_both_gain'][arm]['mean'])) * 40, 'S72: stage count')
    return checks, metadata_claims(cell, obj, pid)


def run(objects=None, rows=None):
    baseline = git('rev-parse', BASELINE + '^{commit}').decode().strip()
    protected = preserved(baseline)
    index_bytes = (ROOT / INDEX).read_bytes()
    require(index_bytes == git('show', baseline + ':' + INDEX), 'Inventory changed from pre-audit baseline')
    index = json.loads(index_bytes)
    baseline_rows = [r for r in git('show', baseline + ':REPORT.md').decode().splitlines() if r.startswith('| S')]
    require(baseline_rows == [p['report_row'] for p in index['pilots']], 'Inventory rows differ from baseline REPORT')
    require(set(SOURCES) == {p['id'] for p in index['pilots']}, 'Explicit source coverage mismatch')
    if rows is None:
        rows = [r for r in (ROOT / 'REPORT.md').read_text().splitlines() if r.startswith('| S')]
    require(len(rows) == len(index['pilots']), 'Missing/extra report rows')
    files = {}
    reports = []
    for pilot, row in zip(index['pilots'], rows):
        pid = pilot['id']
        require(row == pilot['report_row'], pid + ': original table row changed')
        path = SOURCES[pid]
        content = (ROOT / path).read_bytes()
        require(content == git('show', baseline + ':' + path), pid + ': scientific artifact changed')
        files[path] = sha(content)
        obj = objects[pid] if objects is not None and pid in objects else json.loads(content)
        checks, metadata = check_row(pilot, obj, row)
        reports.append(dict(id=pid, source=path, source_sha256=files[path], category=pilot['category'],
                            numeric_checks=checks, metadata_checks=metadata,
                            highlighted_spans=len(re.findall(r'\*\*(.*?)\*\*', row.split('|')[2]))))
    return dict(audit='iteration55_table_fidelity', baseline_commit=baseline,
                scope='All highlighted result-cell numeric tokens, failure counts, frozen categories, displayed sample/block counts and available round-window metadata. Entire original rows preserved. Saved-artifact check; no raw-cache replay, re-estimation or independent scientific validation.',
                pilot_entries=len(reports), numeric_tokens_checked=sum(len(p['numeric_checks']) for p in reports),
                metadata_checks=sum(len(p['metadata_checks']) for p in reports),
                unchanged_baseline_files=protected,
                idea_ledger_exact_proposal_append=True,
                categories=index['categories'], index_sha256=sha(index_bytes), source_sha256=sha(Path(__file__).read_bytes()),
                scientific_artifact_hashes=files, pilots=reports,
                limits='Counts for S60/S62/S64/S65/S66/S69/S70 use stored rates times40, with 5games/arm and 8opportunities/game assumed by the registered design and integer game-count checks; opportunity eligibility is not re-read from raw trajectories here. S72 rates use times5 or times40, checked against saved game/round records. UNINFORMATIVE/UNRESOLVED map to ODD. Contextual wording, model names and design thresholds remain protected baseline text, not independently rederived claims. S02/S04 lack primary_rounds metadata; their window labels are preserved only. S01 category is inherited from its frozen design/report; its result envelope has no verdict. No portfolio pooling, hypothesis tests or discovery-rate inference.')


def expected_documents(result):
    n, numbers, metadata = (result[k] for k in ['pilot_entries', 'numeric_tokens_checked', 'metadata_checks'])
    addition = (f'**Complete table audit:** All {n} rows retain their original text and labels; '
                f'{numbers} highlighted numerical values and failure counts match saved JSON fields or documented fixed scalings, '
                f'with {metadata} sample/window metadata checks. [Field-by-field receipt](results/iteration55_claim_audit.json). '
                'This verifies reporting fidelity, not all raw trajectories or scientific validity. Current offline command: '
                '`uv run --frozen python scripts/iteration55_claims.py --check --replay-selected`. '
                'The selected replays cover five pilots; use a full-history clone and existing pinned dependencies. '
                'Their scientific call entry is guarded; no network isolation is claimed. '
                'The archived iteration-54 full-document command requires its pinned revision.\n\n')
    report = git('show', BASELINE + ':REPORT.md').decode()
    report = report.replace('2026-10-25 · Iteration 54 ·', '2026-10-25 · Iteration 55 ·', 1)
    report = report.replace('**Reading guide — iteration 54:**', '**Reading guide — iteration 55:**', 1)
    report = report.replace('<!-- S59 summary start -->', addition + '<!-- S59 summary start -->', 1)
    readme = git('show', BASELINE + ':README.md').decode()
    old_entry = readme.split('\n\n')[1]
    new_entry = ('**Judge / handoff entry:** [concise evidence brief](results/iteration54_brief.md) · '
                 '[complete pilot log](REPORT.md) · [complete table field audit](results/iteration55_claim_audit.json). '
                 'Verify the current handoff offline with `uv run --frozen python scripts/iteration55_claims.py --check --replay-selected`. '
                 'This checks all highlighted table values against saved fields or documented fixed scalings, preserves every original row '
                 'and prior scientific file, and runs five selected scientific reanalyses with their separate checkers. '
                 'It makes no full-portfolio raw-reproduction claim. The command in the archived iteration-54 brief rebuilds its exact '
                 f'full documents at revision `{BASELINE}`; use the current command for this checkout. '
                 'Use a full-history clone: both the audit baseline and selected S72 replay need historical commits. '
                 'Existing installed pinned dependencies are reused. The selected scientific call entry is guarded; this is not network isolation.')
    return {'REPORT.md': report, 'README.md': readme.replace(old_entry, new_entry, 1)}


def check_documents(result, overrides=None):
    overrides = overrides or {}
    for name, expected in expected_documents(result).items():
        actual = overrides.get(name, (ROOT / name).read_text())
        require(actual == expected, 'Editorial document differs from baseline plus explicit overlay: ' + name)


def probes():
    """Isolated mutations never touch the archival files or published report."""
    index = load(INDEX)
    rows = [p['report_row'] for p in index['pilots']]
    tests = []
    for name, edit in [
        ('displayed_value', lambda rs: rs.__setitem__(0, rs[0].replace('+0.00175', '+0.00176'))),
        ('wrong_direction', lambda rs: rs.__setitem__(1, rs[1].replace('-0.481', '+0.481'))),
        ('missing_row', lambda rs: rs.pop()),
        ('failure_gains_estimate', lambda rs: rs.__setitem__(9, rs[9].replace('No effect estimated.', 'Effect +0.5.'))),
    ]:
        changed = rows.copy()
        edit(changed)
        try:
            run(rows=changed)
        except ValueError:
            tests.append('preservation/' + name)
        else:
            raise ValueError('Mutation was accepted: ' + name)
    for pid, pointer, value in [
        ('S70', 'metrics/pair_bad/endowed/mean', 0.075),
        ('S29', 'verdict', 'HIT'),
        ('S68', 'behavioral_estimates_computed', True),
        ('S62', 'n_games', 12),
    ]:
        pilot = next(p for p in index['pilots'] if p['id'] == pid)
        obj = load(SOURCES[pid])
        target = obj
        parts = pointer.split('/')
        for part in parts[:-1]:
            target = target[part]
        target[parts[-1]] = value
        try:
            check_row(pilot, obj, pilot['report_row'])
        except ValueError:
            tests.append('binding/' + pid + '/' + pointer)
        else:
            raise ValueError('Mutation was accepted: ' + pid + '/' + pointer)
    for pid, old, new in [('S01', '+0.00175', '+0.00176'), ('S02', '-0.481', '+0.481'),
                          ('S16', 'No effect estimated.', 'Effect +0.5.')]:
        pilot = next(p for p in index['pilots'] if p['id'] == pid)
        try:
            check_row(pilot, load(SOURCES[pid]), pilot['report_row'].replace(old, new))
        except ValueError:
            tests.append('semantic_without_preservation/' + pid)
        else:
            raise ValueError('Semantic mutation accepted: ' + pid)
    current = (ROOT / 'REPORT.md').read_text()
    for name, changed in [('headline', current.replace('307 highlighted', '308 highlighted', 1)),
                          ('outside_table', current.replace('No hits promoted.', 'One hit promoted.', 1))]:
        require(changed != current, 'Editorial probe did not change text')
        try:
            check_documents(run(), {'REPORT.md': changed})
        except ValueError:
            tests.append('editorial/' + name)
        else:
            raise ValueError('Editorial mutation accepted: ' + name)
    return tests


def selected_replay():
    # Reuse the earlier scientific replay without invoking its frozen full-
    # document renderer/checker, whose exact presentation predates this overlay.
    program = '''import contextlib,io,json
from unittest.mock import patch
with patch('llm.chat',side_effect=AssertionError('No scientific model calls')):
    from scripts.iteration54_handoff import replay
    with contextlib.redirect_stdout(io.StringIO()):
        results=replay()
print(json.dumps(results))
'''
    documents = {name: (ROOT / name).read_bytes() for name in ['STATUS.md', 'REPORT.md', 'README.md']}
    proc = subprocess.run([sys.executable, '-c', program], cwd=ROOT, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240)
    require(proc.returncode == 0, 'Selected historical replay failed: ' + proc.stderr)
    records = json.loads(proc.stdout)
    require([r['pilot'] for r in records] == ['S29', 'S62', 'S69', 'S70', 'S72'], 'Unexpected selected scope')
    require(all(r['reanalysis_matches'] and r['independent']['passed'] for r in records), 'Selected replay mismatch')
    preserved(BASELINE)
    require(all((ROOT / name).read_bytes() == data for name, data in documents.items()), 'Selected replay changed editorial documents')
    return dict(baseline_commit=BASELINE, implementation_sha256=sha(Path(__file__).read_bytes()),
                prior_replay_source_sha256=sha((ROOT / 'scripts/iteration54_handoff.py').read_bytes()),
                scope='Selected scientific reanalyses and separate checkers only. Historical full-document renderer not invoked. llm.chat guard, not network isolation. S72 uses its pinned historical clone.',
                replays=records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default=OUT)
    parser.add_argument('--check', action='store_true', help='Compare saved receipt; do not write')
    parser.add_argument('--replay-selected', action='store_true', help='Also replay the five previously selected pilots and their separate checkers')
    args = parser.parse_args()
    result = run()
    check_documents(result)
    result['rejected_corruption_probes'] = probes()
    data = (json.dumps(result, indent=2, ensure_ascii=False) + '\n').encode()
    target = ROOT / args.out
    if args.check:
        require(target.read_bytes() == data, 'Saved audit differs from current reconstruction')
    else:
        target.write_bytes(data)
    if args.replay_selected:
        receipt = (json.dumps(selected_replay(), indent=2, ensure_ascii=False) + '\n').encode()
        target = ROOT / 'logs/iteration55_selected_replay.json'
        if args.check:
            require(target.read_bytes() == receipt, 'Saved selected replay differs')
        else:
            target.write_bytes(receipt)
    print(json.dumps({k: result[k] for k in ['pilot_entries', 'numeric_tokens_checked', 'metadata_checks', 'categories', 'rejected_corruption_probes']}))


if __name__ == '__main__':
    main()
