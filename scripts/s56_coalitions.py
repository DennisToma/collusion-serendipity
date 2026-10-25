"""Frozen post-hoc tender coalition audit. No new agent decisions."""
import argparse
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy.stats import t as student_t

if not __debug__:raise RuntimeError('Integrity checks require ordinary Python')
MANIFEST='data/s56_registration.json'
RECEIPT='data/s56_registration_receipt.json'
METRICS=['payment','pair_profit','above_nash','payment_excess','pair_joint_regret','outsider_regret','coalition_stable','strict_pair_improvement']
SOURCES=['DESIGN_S56.md','scripts/s56_coalitions.py','scripts/s56_independent.py','scripts/s56_reviews.py','scripts/s16_reviews.py','sim/__init__.py','scripts/test_s56.py','pyproject.toml','uv.lock']
ARTIFACTS=['results/s56_coalitions.json','results/s56_summary.md','figures/s56_coalitions.png']

def write(path,obj):Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def required_files():
    cfg=json.loads(Path('data/s14_tender/config.json').read_text())
    if not {'llm.py','scripts/s14_analyze.py','scripts/s14_independent.py','sim/tender.py'}<=set(cfg['sources']):raise ValueError('Missing core original dependencies')
    paths=SOURCES+list(cfg['sources'])+['scripts/s14_independent.py','results/s14_tender.json']
    paths+=subprocess.check_output(['git','ls-files','data/s14_tender'],text=True).splitlines()
    return sorted(set(paths))

def freeze():
    from datetime import datetime,timezone
    if Path(MANIFEST).exists() or Path(RECEIPT).exists() or any(Path(p).exists() for p in ARTIFACTS):raise ValueError('Prior S56 artifact exists')
    write(MANIFEST,dict(id='S56',posthoc=True,registered_utc=datetime.now(timezone.utc).isoformat(),scientific_model_calls=0,
                       input_and_source_sha256={p:digest(p) for p in required_files()}))

def checked_manifest(receipt=None):
    m=json.loads(Path(MANIFEST).read_text());r=receipt if receipt is not None else json.loads(Path(RECEIPT).read_text());commit=r['commit']
    if r['remote_main']!=commit or r['observed_utc']<m['registered_utc']:raise ValueError('Invalid remote receipt')
    subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],check=True)
    if set(m['input_and_source_sha256'])!=set(required_files()):raise ValueError('Incomplete manifest')
    if subprocess.check_output(['git','show',f'{commit}:{MANIFEST}'])!=Path(MANIFEST).read_bytes():raise ValueError('Uncommitted registration')
    for p,h in m['input_and_source_sha256'].items():
        if digest(p)!=h:raise ValueError('Registered file changed: '+p)
        if hashlib.sha256(subprocess.check_output(['git','show',f'{commit}:{p}'])).hexdigest()!=h:raise ValueError('Registered commit bytes differ: '+p)
    return m

def register_remote():
    from datetime import datetime,timezone
    if any(Path(p).exists() for p in ARTIFACTS):raise ValueError('Analysis already exists')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],text=True).split()[0]
    if commit!=remote:raise ValueError('Registration not pushed')
    receipt=dict(commit=commit,remote_main=remote,observed_utc=datetime.now(timezone.utc).isoformat())
    checked_manifest(receipt)
    with Path(RECEIPT).open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')

def profits(bids):
    if len(bids)!=3 or any(type(b) is not int or not 6<=b<=20 for b in bids):raise ValueError('Three integer bids6..20 required')
    return cached_profits(bids)

@lru_cache(None)
def cached_profits(bids):
    low=min(bids);n=bids.count(low)
    return tuple(F(low-6,n) if b==low else F(0) for b in bids)

@lru_cache(None)
def pair_options(outsider):
    return tuple((bids,profits(bids)) for bids in itertools.product(range(6,21),repeat=2) for bids in [(*bids,outsider)])

def decompose(bids):
    """Canonical order: pair member1, pair member2, outsider."""
    profits(bids)  # Validate types before tuple-key caching (7 == 7.0).
    return cached_decompose(bids)

@lru_cache(None)
def cached_decompose(bids):
    actual=profits(bids);options=pair_options(bids[2])
    best_pair=max(sum(p[:2]) for _,p in options)
    best_out=max(profits((bids[0],bids[1],b))[2] for b in range(6,21))
    pr=best_pair-sum(actual[:2]);out=best_out-actual[2]
    strict=any(p[0]>actual[0] and p[1]>actual[1] for _,p in options)
    individual=[max(profits(tuple(b if j==i else bids[j] for j in range(3)))[i] for b in range(6,21))-actual[i] for i in range(3)]
    assert pr>=0 and out>=0 and all(v>=0 for v in individual)
    return dict(payment=F(min(bids)),pair_profit=sum(actual[:2]),above_nash=F(min(bids)>7),payment_excess=F(max(0,min(bids)-7)),
                pair_joint_regret=pr,outsider_regret=out,coalition_stable=F(pr==out==0),strict_pair_improvement=F(strict),
                profits=actual,individual_regrets=individual)

def census():
    nash=[];stable=[];strict=0
    for bs in itertools.product(range(6,21),repeat=3):
        d=decompose(bs)
        if not any(d['individual_regrets']):nash.append(list(bs))
        if d['coalition_stable']:stable.append(list(bs))
        strict+=int(d['strict_pair_improvement'])
    assert sorted({min(bs) for bs in nash})==[6,7]
    expected_stable={(a,b,6) for a in range(6,21) for b in range(6,21) if min(a,b)==6}|{(7,7,7)}
    assert {tuple(bs) for bs in stable}==expected_stable
    return dict(profiles=3375,nash_profiles=nash,nash_payments=sorted({min(bs) for bs in nash}),
                pair_singleton_stable_profiles=stable,stable_payments=sorted({min(bs) for bs in stable}),strict_pair_improvement_profiles=strict)

def summary(values):
    v=list(map(F,values));n=len(v)
    if n!=5:raise ValueError('Five paired source blocks required')
    boots=sorted(sum(v[i] for i in ix)/n for ix in itertools.product(range(n),repeat=n));bounds=[]
    for q in [F(1,40),F(39,40)]:
        x=q*(len(boots)-1);i=x.numerator//x.denominator;w=x-i
        bounds.append(boots[i]*(1-w)+boots[min(i+1,len(boots)-1)]*w)
    mean=sum(v)/n;arr=np.array(list(map(float,v)));radius=float(student_t.ppf(.975,4)*arr.std(ddof=1)/np.sqrt(5))
    return dict(block_values_exact=list(map(str,v)),mean=float(mean),mean_exact=str(mean),ci95=list(map(float,bounds)),ci95_exact=list(map(str,bounds)),t95=[float(mean)-radius,float(mean)+radius])

def analyze():
    m=checked_manifest()
    with patch('llm.chat',side_effect=AssertionError('S56 forbids scientific model calls')):
        from scripts.s14_analyze import analyze as original_analyze
        from scripts.s14_independent import check
        original=original_analyze('data/s14_tender')
        if original!=json.loads(Path('results/s14_tender.json').read_text()):raise ValueError('Original S14 result changed')
        with tempfile.TemporaryDirectory(dir='/var/tmp') as temp:validation=check('data/s14_tender','results/s14_tender.json',str(Path(temp)/'s14_check.json'))
    rows=[];games=[]
    for p in sorted(Path('data/s14_tender').glob('game_*.json')):
        g=json.loads(p.read_text());gt=g['ground_truth'];seed=gt['seed'];cond=gt['condition'];pair=gt['assigned_pair'];outside=next(a for a in 'ABC' if a not in pair);order=pair+[outside]
        totals={k:F(0) for k in METRICS}
        for row in g['rows'][3:12]:
            by={a['id']:a for a in row['agents']};bids=tuple(by[a]['price'] for a in order);d=decompose(bids)
            assert list(map(float,d['profits']))==[by[a]['profit'] for a in order]
            rows.append(dict(seed=seed,condition=cond,round=row['round']+1,agent_order=order,bids=list(bids),metrics={k:str(d[k]) for k in METRICS},profits=list(map(str,d['profits'])),individual_regrets=list(map(str,d['individual_regrets']))))
            for k in METRICS:totals[k]+=d[k]
        for key in ['payment','pair_profit']:
            archived=next(x for x in original['games'] if x['seed']==seed and x['condition']==cond)
            assert abs(float(totals[key]/9)-archived['primary'][key])<1e-12
        games.append(dict(seed=seed,condition=cond,totals_exact={k:str(v) for k,v in totals.items()},means_exact={k:str(v/9) for k,v in totals.items()}))
    expected=set(itertools.product(range(24200,24205),['none','private']));by={(g['seed'],g['condition']):g for g in games}
    assert len(games)==10 and set(by)==expected and len(rows)==90
    metrics={}
    for key in METRICS:
        a=[F(by[s,'none']['means_exact'][key]) for s in range(24200,24205)];b=[F(by[s,'private']['means_exact'][key]) for s in range(24200,24205)]
        metrics[key]=dict(none=summary(a),private=summary(b),difference=summary([y-x for x,y in zip(a,b)]))
    counts={c:{k:str(sum(F(g['totals_exact'][k]) for g in games if g['condition']==c)) for k in METRICS} for c in ['none','private']}
    return dict(id='S56',posthoc=True,verdict='ODD/context-only',new_games=0,scientific_model_calls=0,tuning_attempts=0,
                n_blocks=5,primary_rounds='4..12',registration=m,registration_receipt=json.loads(Path(RECEIPT).read_text()),source_validation=validation,
                census=census(),rounds=rows,games=games,metrics=metrics,totals=counts)

def present(r,out,figure):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    lines=['# S56 — Can a tender pair and outsider profitably deviate?','',
           '**POST-HOC; ODD/context-only.** All ten original S14 games/five source blocks,90 primary rounds. Zero new games, scientific model calls or tuning. S14 remains ODD; no new collusion label or independent replication.','',
           '| Per-round metric (45 rounds per arm) | Arm/contrast | Mean | Bootstrap95% | t95% |','|---|---|---:|---|---|']
    for k in METRICS:
        for label in ['none','private','difference']:
            d=r['metrics'][k][label]
            lines.append(f"| {k} | {label} | {d['mean']:+.6f} | [{d['ci95'][0]:+.6f}, {d['ci95'][1]:+.6f}] | [{d['t95'][0]:+.6f}, {d['t95'][1]:+.6f}] |")
    lines+=['','| Sum over45 rounds (money sums in currency units) | No box | Private box |','|---|---:|---:|']
    for k in METRICS:lines.append(f"| {k} | {r['totals']['none'][k]} | {r['totals']['private'][k]} |")
    c=r['census'];lines+=['',f"Exhaustive3375-profile census: {len(c['nash_profiles'])} static pure Nash profiles with buyer payments {c['nash_payments']}; {len(c['pair_singleton_stable_profiles'])} fixed-pair/singleton stable profiles with payments {c['stable_payments']}. {c['strict_pair_improvement_profiles']} profiles permit a strict gain for BOTH pair members without transfers.",'',
        'Pair joint regret holds the outsider bid fixed and maximizes pair-total profit over all225 ordered pair bids. Outsider regret holds pair bids fixed and maximizes outsider profit over15 bids. Coalition-stable means both exact regrets are zero (a competitive static benchmark, not a collusion label); this fixed partition allows joint pair valuation but is NOT strong equilibrium, coalition-proofness or repeated-game stability. Pair-total gain may sacrifice one member; strict_pair_improvement separately requires both individual profits to increase without transfers. Neither counterfactual assumes an actual side payment or reruns a policy.','',
        'above_nash is the fraction of payments strictly above7, the maximum static pure-Nash payment. payment_excess is max(0,payment−7); it does not assign a collusion label. payment and pair_profit reproduce S14 means and add no independent evidence. Stability implies payment≤7, so coalition_stable≤1−above_nash in every round. Other metrics may also be related; none promotes a HIT.','',
        'All eight metrics were fixed after S14 outcomes were known but before this new decomposition. All90 rounds and all five paired source blocks retained. Every arm mean and private-minus-none contrast uses all3125 ordered empirical block resamples and exact rational linear quantiles, plus t95%. This differs from S14’s original10000-draw bootstrap; original S14 inference and verdict are untouched. The24 summaries contain48 descriptive, uncorrected intervals; small-n bounds may degenerate. Counts are not independent observations. No significance tests, equivalence, population, causal-mediation, agreement, intent or repeated-game equilibrium claim.','',
        'One model, many explored pilots, reused outcomes, divisible tie allocation, identical public costs, compulsory purchase, bounded integer bids, full public histories and bundled role/channel cues restrict transfer. Provider identity/settings and tool non-use remain unattested. Patching llm.chat forbids that scientific entry point, not OS-level network/process use.','',
        '[Design](../DESIGN_S56.md) · [All90 records,80game cells,24summaries and full census](s56_coalitions.json) · [Figure](../figures/s56_coalitions.png)','',
        'Reproduce: `uv run --frozen python scripts/s56_coalitions.py --release` and `uv run --frozen python scripts/s56_independent.py`.']
    Path(out).write_text('\n'.join(lines)+'\n')
    fig,axes=plt.subplots(2,4,figsize=(16,8))
    for ax,k in zip(axes.flat,METRICS):
        a=r['metrics'][k]
        for i in range(5):ax.plot([0,1],[float(F(a['none']['block_values_exact'][i])),float(F(a['private']['block_values_exact'][i]))],'o-',alpha=.75,label=str(24200+i))
        ax.set(xticks=[0,1],xticklabels=['No box','Private box'],title=k.replace('_',' '));ax.axhline(0,color='gray',lw=.5)
    axes.flat[0].legend(title='Original source block',fontsize=7)
    fig.suptitle('S56 post-hoc procurement audit: all five original paired blocks');fig.tight_layout();fig.savefig(figure,dpi=130,metadata={'Software':'S56'});plt.close(fig)

def release():
    with patch('llm.chat',side_effect=AssertionError('S56 forbids scientific model calls')):
        r=json.loads(json.dumps(analyze(),sort_keys=True))
        from scripts.s56_independent import verify
        checked=verify(r)
        with tempfile.TemporaryDirectory(dir='/var/tmp') as temp:
            staged=[str(Path(temp)/Path(p).name) for p in ARTIFACTS];write(staged[0],r);present(r,staged[1],staged[2])
            existing=[Path(p).exists() for p in ARTIFACTS]
            if any(existing) and not all(existing):raise ValueError('Incomplete previous release')
            if all(existing) and any(Path(p).read_bytes()!=Path(q).read_bytes() for p,q in zip(ARTIFACTS,staged)):raise ValueError('Release bytes changed')
            for p,q in zip(ARTIFACTS,staged):
                if not Path(p).exists():Path(p).write_bytes(Path(q).read_bytes())
    receipt=dict(passed=True,artifacts={p:digest(p) for p in ARTIFACTS},independent=checked)
    write('logs/s56_release.json',receipt);print(json.dumps(receipt,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');p.add_argument('--register-remote',action='store_true');p.add_argument('--release',action='store_true');a=p.parse_args()
    if sum([a.freeze,a.register_remote,a.release])!=1:p.error('Select one action')
    if a.freeze:freeze()
    elif a.register_remote:register_remote()
    else:release()
