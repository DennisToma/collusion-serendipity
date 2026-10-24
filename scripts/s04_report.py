"""Build S04 report text from frozen JSON; no analysis/model decisions."""
import json
from pathlib import Path


def fmt(r,signed=False):
    spec='+.3f' if signed else '.3f'
    return f'{r["mean"]:{spec}} [{r["ci95"][0]:{spec}}, {r["ci95"][1]:{spec}}]'


def render():
    path=Path('results/s04_advisor.json')
    if not path.exists():
        return ('| S04 · B, shared advisor sample | Registered ten games, five fresh seed blocks, T12. Shared vs independent identical-prompt advisor responses; running, no partial outcome estimate. | **PENDING** |',
                '**S04 running:** seller prompts hide shared identity; both arms sample two advisor responses per round. Low routable advice variation will yield UNINFORMATIVE. This tests common sampling, not a persistent strategic hub.',
                '\n\n# S04 — registered and running\n\nSee [frozen design](DESIGN_S04.md). No partial game outcomes are reported.\n',False)
    r=json.loads(path.read_text());m=r['metrics'];q=m['pair_quantity'];d=q['paired_difference']
    row=(f'| S04 · B, shared advisor sample | {r["n_games"]} games, {r["n_seeds"]} seed blocks. '
         f'Pair output r4–12: independent **{q["independent"]["mean"]:.3f}**, shared **{q["shared"]["mean"]:.3f}**; '
         f'difference **{fmt(d,True)}** units/firm. | **{r["verdict"]}** |')
    exposure=r['routable_disagreement']
    caution=('The exposure gate failed (<25%): little route-dependent advice, so this result cannot test a substantive shared-advisor effect.'
             if exposure<.25 else 'This narrow pilot does not resolve a population effect or test a persistent strategic advisor.')
    short=(f'**S04:** mean routable advice disagreement **{exposure:.1%}** (primary window); '
           f'pair-profit difference **{fmt(m["pair_profit"]["paired_difference"],True)}**. '
           f'{caution} Common advice/action equality is descriptive and can be mechanical; no verified collusion labels. '
           f'[Full S04 results and limitations](REPORT_DETAILS.md#s04--shared-public-information-advisor).')
    table='\n'.join(f'| {key} | {v["independent"]["mean"]:.3f} | {v["shared"]["mean"]:.3f} | {fmt(v["paired_difference"],True)} |' for key,v in m.items())
    by={(x['seed'],x['condition']):x for x in r['records']}
    seedtable='\n'.join(f'| {s} | {by[s,"independent"]["primary"]["pair_quantity"]:.3f} | {by[s,"shared"]["primary"]["pair_quantity"]:.3f} | {delta:+.3f} | '
                         f'{by[s,"independent"]["primary"]["routable_disagreement"]:.1%} / {by[s,"shared"]["primary"]["routable_disagreement"]:.1%} |'
                         for s,delta in zip(range(24040,24045),q['seed_differences']))
    final='\n'.join(f'| {s} | {by[s,"independent"]["final"]["pair_quantity"]:.3f} | {by[s,"shared"]["final"]["pair_quantity"]:.3f} |' for s in range(24040,24045))
    decomposition='\n'.join(f'| {x["seed"]} | {x["price_term"]:+.3f} | {x["quantity_term"]:+.3f} | {x["price_term"]+x["quantity_term"]:+.3f} |' for x in r['profit_decomposition'])
    allround='\n'.join(f'| {metric} | '+ ' | '.join(f'{sum(x["all_rounds"][metric] for x in r["records"] if x["condition"]==c)/r["n_seeds"]:.3f}' for c in ['independent','shared'])+' |' for metric in ['pair_quantity','price','pair_profit'])
    pre=json.loads(Path('data/s04_precheck/results.json').read_text())
    count=sum(pre['vector_disagreements'])
    detail=f'''

# S04 — shared public-information advisor

Iteration 2, axis B; **{r['verdict']}** under the frozen, exposure-gated screen.
{r['n_games']} games / {r['n_seeds']} seed blocks, T12, all exploratory, zero tuning attempts.
Fresh seed range 24040..24044. [Design and pre-outcome amendments](DESIGN_S04.md).
No model pooling with S02, no baseline no-advice arm, no confirmed-collusion label.

The firms use S02's quantity economics: q in 0..12, P=max(0,30-total q), cost 6,
symmetric static Nash q=6, P=12, per-firm profit 36. Two same-model,
identical-prompt advisor calls see only full completed public history; the pair
sees scalar own recommendations. Shared routing uses one vector, independent
routing uses a different vector for each firm; both arms make both calls. Seller
prompts contain no shared-identity cue, private messages or other firm's advice.
Pair ordering and active advisor slot are randomized in advance. Each seed block
finishes before the next begins. This isolates common sampling rather than
branding, persistent advisor memory, private data aggregation or strategic hub
collusion. Same-model calls need not be statistically independent server draws.

## Results (rounds 4–12)

Primary shared-independent pair quantity difference **{fmt(d,True)}**.
Paired t interval [{d['paired_t_ci95'][0]:+.3f}, {d['paired_t_ci95'][1]:+.3f}].
One-sided sign-flip enumeration diagnostic (32 assignments, zeros retained):
{d['exact_signflip_p_lower']:.5f}. Exchangeable slots or symmetric block differences
under a no-effect null are required; backend drift/interference can violate this.
At five blocks the intervals are descriptive and may under-cover.

| Outcome | Independent | Shared | Shared-independent [descriptive 95% bootstrap] |
|---|---|---|---|
{table}

Routable disagreement compares the second pair member's two sampled advice
components within each observed game state (not an observed counterfactual game).
The frozen gate uses its average over BOTH arms and rounds 4–12: {exposure:.1%}.
{caution} Pair quantity/action/advice equality and change product are not pCMI,
do not measure intent, and are not evaluations of either sibling's detector.
Outsider-unshown adoption uses its component in the active first slot; it was
never delivered. Same-model policy can match advice without persuasion.

| Seed | Independent pair q | Shared pair q | Difference | Routable variation independent / shared |
|---|---|---|---|---|
{seedtable}

| Final-round pair quantity | Independent | Shared |
|---|---|---|
{final}

| All-round mean | Independent | Shared |
|---|---|---|
{allround}

## Profit accounting (descriptive, not mediation)

For each paired seed and aligned round/firm, the profit difference equals
(P_shared-P_independent)*q_independent +
(P_shared-6)*(q_shared-q_independent). Average these terms over r4–12 and the pair.
This is an accounting identity with an arbitrary order, not a causal attribution;
price changes can arise from outsider responses. Arithmetic equality is checked.

| Seed | Price term | Quantity term | Pair profit difference |
|---|---|---|---|
{decomposition}

## Instrument, provenance and limits

The separate eight-call synthetic precheck found vector differences at {count}/{len(pre['states'])}
fixed states, with no prompt/model selection. It did not estimate encountered-state
variation or a treatment effect. Raw responses retained in data/s04_precheck.
All {r['calls']} live requests have pinned gpt-6-luna/codex client labels;
{r['invalid_attempts']} invalid-output retries. Labels are not independent model
attestation. Codex exposes no temperature/API seed control. Full per-call
timestamps, sampled vectors (including unused ones), route slots, source SHA256s,
reasoning and authoritative per-game files are retained. Dataset hard-negative
and collusion fields remain null: missing messages do not prove no coordination.

Fewer quantities can reflect unilateral optimization or correction of losses;
profitability and market-wide price/output must be read alongside quantity.
Only five blocks, one model/prompt/market, twelve rounds; no multiplicity correction
for descriptive secondaries, no confirmatory headline. A DUD is only a queue
screen; UNINFORMATIVE means the manipulation had insufficient variation. A HIT
would require independent confirmation, not automatic sibling headline changes.

Reproduce: `uv run python scripts/s04_analyze.py`;
`uv run python scripts/s04_verify.py` (forbids all live calls);
`uv run python -m unittest scripts.test_research scripts.test_s04 -v`.
Run/resume: `uv run python -m sim.advisor`; config/code hashes fail closed on drift.
Independent design reviews: [Codex](logs/s04_design_codex.md),
[Opus](logs/s04_design_opus.md). Final claim-review status/disposition is recorded
in [S04 review disposition](logs/s04_review_disposition.md).

![S04 quantity, price, adoption](figures/s04_advisor.png)
*Means; bands show the observed range across five games, not a confidence interval.*
'''
    return row,short,detail,r['verdict']=='HIT'
