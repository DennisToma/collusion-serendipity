"""Render the first two pilot results directly from frozen JSON outputs."""
from datetime import datetime, timezone
import json
from pathlib import Path


def fmt(r, signed=False, dp=3):
    spec = f'+.{dp}f' if signed else f'.{dp}f'
    return (f'{r["mean"]:{spec}} [{r["ci95"][0]:{spec}}, '
            f'{r["ci95"][1]:{spec}}]')


def main():
    digits = json.loads(Path('results/s01_digits.json').read_text())
    s02 = json.loads(Path('results/s02_cournot.json').read_text())
    aborted = json.loads(Path('data/s02_cournot/INCOMPLETE.json').read_text())
    a, b = [digits[n] for n in ['llm_v1', 'llm_ds_p2']]
    q = s02['metrics']['pair_quantity']
    price = s02['metrics']['price']
    diff = q['paired_difference']
    secondary_rows = '\n'.join(
        f'| {label} | {fmt(s02["metrics"][metric]["paired_difference"], True)} |'
        for metric, label in [('outsider_quantity', 'Outsider quantity'),
                              ('total_quantity', 'Total quantity'), ('price', 'Market price'),
                              ('pair_profit', 'Pair per-firm profit')])
    final = {c: [x['final']['pair_quantity'] for x in s02['records'] if x['condition'] == c]
             for c in ['none', 'private']}
    all_rounds = {c: sum(x['all_rounds']['pair_quantity'] for x in s02['records']
                        if x['condition'] == c)/s02['n_seeds'] for c in ['none', 'private']}
    benchmark = s02['benchmarks']['pair_as_single_actor_equilibria']
    pair_totals = '/'.join(str(e['pair_profit_total']) for e in benchmark)
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    report = f'''# Serendipity log — Beyond Words

Exploratory attacks on the sibling projects' price-market findings. Iteration 1,
updated {now}. **No hits promoted.** Frozen designs and review amendments:
[DESIGN.md](DESIGN.md). Zero detector tuning attempts; these are discovery results.

| Pilot | Idea → result (descriptive 95% bootstrap interval) | Verdict |
|---|---|---|
| S01 · C, price digits | {a['runs'] + b['runs']} games / {a['rounds'] + b['rounds']:,} rounds scanned; primary channel-game n={a['primary_within_channel']['n']} luna, n={b['primary_within_channel']['n']} deepseek. Assigned-pair-minus-other-pairs prediction improvement: gpt-6-luna **{fmt(a['primary_within_channel'], True, 5)}**, deepseek **{fmt(b['primary_within_channel'], True, 5)}** squared price units. | **DUD** for this digit screen. |
| S02 · A, Cournot quantities | {s02['n_games']} complete games / {s02['n_seeds']} paired seeds, gpt-6-luna/codex. Pair output, rounds 4–12: no channel **{q['none']['mean']:.3f}**, private **{q['private']['mean']:.3f}**; private minus none **{fmt(diff, True)}** units per firm. | **{s02['verdict']}**, heuristic prioritization only. |

**S01: no robust digit-screen gain.** Absolute channel-pair prediction gains:
{fmt(a['channel_gain'], True, 5)} (luna), {fmt(b['channel_gain'], True, 5)} (deepseek).
No-channel control gains are {fmt(a['control_gain'], True, 5)} (luna) and
{fmt(b['control_gain'], True, 5)} (deepseek), consistent with nonlinearity rather
than channel-specific information. The secondary channel-minus-control gain is unresolved:
{fmt(a['secondary_channel_minus_control_gain'], True, 5)} and
{fmt(b['secondary_channel_minus_control_gain'], True, 5)}, respectively.
Every observed price is integer. Digit indicators have zero residual after
projection onto indicators of the exact permitted price. This cannot identify
intentional coding or rule out signaling; a linear-model gain could be price
nonlinearity. Inputs contain only prices/public state; assignments define groups.
Five folds hold out entire games, with training-only scaling/ridge (alpha 10).
No source game excluded. Intervals bootstrap game scores, treating overlapping
cross-fitted models as fixed; they omit refit uncertainty and are descriptive.

**S02: opportunity contrast, not verified collusion.** Three firms choose integer
quantities 0..12; P=max(0,30−total output), cost 6. Static symmetric Nash: q=6,
P=12; all-firm symmetric joint optimum: q=4, P=18 (enumerated in validity checks).
The randomized pair alone can message, delivered next round; no coordination
instruction. Both arms see complete public action/profit history; end round is
undisclosed. Mean market price: none {price['none']['mean']:.3f}, private
{price['private']['mean']:.3f}. Pair-output seed differences:
{', '.join(f'{x:+.3f}' for x in q['seed_differences'])}.
Paired t interval: [{diff['paired_t_ci95'][0]:+.3f}, {diff['paired_t_ci95'][1]:+.3f}];
unpaired bootstrap: [{diff['unpaired_ci95'][0]:+.3f}, {diff['unpaired_ci95'][1]:+.3f}];
one-sided exact sign-flip p={diff['exact_signflip_p_lower']:.3f} (lower output).
Only {s02['n_seeds']} blocks: intervals may under-cover, and minimum exact p=1/8
prevents a HIT under the retained p≤.05 rule. Here the percentile bounds equal
the observed seed range; they are not well-calibrated uncertainty bounds. The
large reduction occurs in seed 24021, where the outsider also reduces output.
No inference from message content,
agreement or realized-collusion label. The channel prompt and delivery are bundled.

**Prespecified secondary outcomes (rounds 4–12; private minus none):**

| Outcome | Descriptive bootstrap bounds |
|---|---|
{secondary_rows}

Pair profit is essentially unchanged. Round-12 pair output, seed order 24020–22:
none {', '.join(f'{x:g}' for x in final['none'])}; private
{', '.join(f'{x:g}' for x in final['private'])}. All-round pair means: none
{all_rounds['none']:.3f}, private {all_rounds['private']:.3f}. Two private games
end at the Nash quantity. The all-firm optimum is not a pair-only benchmark:
enumerating a pair-as-one-actor game gives {len(benchmark)} grid equilibria,
pair-total profits {pair_totals} versus unmerged pair profit 72; the 4/4/8
quantity example pays each pair member 32 versus Nash 36. Lower pair output
alone does not establish profitable coordination.

The original qwen gateway attempt stalled: {aborted['started_game_slots']} started
games, {aborted['cached_calls']} cached decision, {aborted['complete_games']} complete
games. Retained as **incomplete**, not a null outcome; no model pooling.
This runtime deviation changes the planned pinned model and sample size; it
overrides the original no-fallback plan. It was registered before any replacement
outcome, using the remaining six of
ten game slots. Within-seed execution slots randomized before calls. All
{s02['calls']} cached fallback decisions match requested client routing labels;
{s02['invalid_attempts']} invalid-output retries. Model identity is not independently
attested; Codex exposes neither temperature nor API seed (the JSON config's
temperature=1 is requested, not enforced). Failed backend and
changed model/sample size limit portability.

![Cournot trajectories](figures/s02_cournot.png)
*Mean trajectories; shading is the range across games, not a confidence interval.*

**Reproduce:** `uv run python scripts/s01_digits.py`;
`uv run python scripts/s02_analyze.py --data data/s02_cournot_luna`;
`uv run python scripts/render_report.py`;
`uv run python -m unittest scripts.test_research -v`.
Cached generation/resume commands: [README.md](README.md). Frozen outputs:
[S01](results/s01_digits.json), [S02](results/s02_cournot.json).
Independent reviews: [Codex design](logs/design_codex.md),
[Opus design](logs/design_opus.md), [implementation](logs/implementation_codex.md);
[dispositions](logs/review_disposition.md); final claims reviews
[Codex](logs/final_claims_codex.md), [Opus](logs/final_claims_opus.md).

**Next:** cover B, D, E, F and an `own` idea before deepening a prior axis.
S03 arithmetic-tool idea is queued, not run. Any promotion needs fresh seeds.
'''
    Path('REPORT_DETAILS.md').write_text(report.replace('# Serendipity log — Beyond Words', '# Detailed pilot results — iteration 1', 1))
    summary = f'''# Serendipity log — Beyond Words

{now} · Iteration 1 · **No hits promoted.** Discovery pilots; zero tuning attempts.

| Pilot | Result (descriptive 95% bootstrap bounds) | Verdict |
|---|---|---|
| S01 · C, price digits | {a['runs'] + b['runs']} games scanned; primary on {a['primary_within_channel']['n']} luna / {b['primary_within_channel']['n']} deepseek channel games. Pair-minus-other-pairs prediction gain **{fmt(a['primary_within_channel'], True, 5)}** / **{fmt(b['primary_within_channel'], True, 5)}** squared price units. | **DUD** for this screen |
| S02 · A, Cournot quantities | {s02['n_games']} complete games, {s02['n_seeds']} seed blocks, gpt-6-luna. Pair output r4–12: none **{q['none']['mean']:.3f}**, private **{q['private']['mean']:.3f}**; difference **{fmt(diff, True)}** units/firm. | **{s02['verdict']}**, inconclusive |

**S01:** last digits are determined by integer prices; this cannot identify
intentional coding or rule out signaling. Deepseek no-channel gain is
{fmt(b['control_gain'], True, 5)}, consistent with price nonlinearity. Fixed
five-fold game-held-out ridge; bootstrap treats overlapping fitted models as
fixed and omits refit uncertainty. No game excluded.

**S02:** three firms choose quantities 0..12; P=max(0,30−total output), cost 6.
Nash q=6; all-firm optimum q=4. Pair messages arrive next round; no coordination
instruction. Seed differences {', '.join(f'{x:+.3f}' for x in q['seed_differences'])};
exact lower-output p={diff['exact_signflip_p_lower']:.2f}; t interval
[{diff['paired_t_ci95'][0]:+.3f}, {diff['paired_t_ci95'][1]:+.3f}]. With three
blocks, bootstrap bounds equal the observed range; minimum exact p=1/8 prevents
HIT. The largest reduction also includes an outsider output cut.

| Secondary r4–12 outcome | Private minus none (descriptive bounds) |
|---|---|
{secondary_rows}

Pair profit is essentially unchanged. Round-12 pair output: none
{', '.join(f'{x:g}' for x in final['none'])}; private
{', '.join(f'{x:g}' for x in final['private'])}. Lower output alone does not
establish profitable coordination; pair-only coalition benchmarks differ from
the all-firm optimum ([enumeration and full results](REPORT_DETAILS.md)).

**Runtime deviation:** planned Qwen gateway stalled ({aborted['started_game_slots']}
starts, {aborted['cached_calls']} decision, no complete games). Preserved as
incomplete; the amended six-game fallback uses the remaining ten-game budget,
never pooling models. Randomized execution slots; {s02['calls']} cached decisions,
{s02['invalid_attempts']} invalid-output retries. Model labels reflect client
routing; Codex temperature/seed are not controlled. Prompt and delivery are bundled;
agreement/execution labels remain unverified. No confirmatory claim.

![Cournot trajectories](figures/s02_cournot.png)
*Means; shading is the range across games, not a CI.*

[Design](DESIGN.md) · [Full results/methods](REPORT_DETAILS.md) ·
[Reproduce](README.md) · [Reviews and fixes](logs/review_disposition.md).
**Next:** cover B/D/E/F/own before deepening; S03 calculator idea queued, not run.
'''
    Path('REPORT.md').write_text(summary)


if __name__ == '__main__':
    main()
