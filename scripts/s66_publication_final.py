"""Additive post-outcome terminology corrections; frozen science stays unchanged."""
import contextlib,shutil,tempfile
from pathlib import Path
from scripts import s66_present as frozen

ARTIFACTS=['results/s66_summary.md','figures/s66_payoff_order.png','REPORT.md','REPORT_DETAILS.md','HITS.md','README.md']

def polish(text):
    return (text.replace('upper sign p','upper sign-flip p').replace('Upper sign p','Upper sign-flip p')
        .replace('near-ceiling controls can limit detectable increases','near-ceiling controls in some blocks can limit detectable increases')
        .replace('scripts/s66_release.py','scripts/s66_release_final.py'))

def _render_isolated():
    frozen.documents(isolated=True)
    before={n:Path(n).read_bytes() for n in ARTIFACTS}
    p=Path('results/s66_summary.md');s=polish(p.read_text())
    s+='\nThe sign-flip test enumerates signed block differences and compares their mean with the observed mean; it is not a binomial test of positive signs. Frozen scientific sources/results are unchanged; this clarification and the release entry point are post-outcome editorial additions.\n'
    p.write_text(s)
    p=Path('REPORT.md');s=p.read_text();start=s.index('<!-- S66 summary start -->');end=s.index('<!-- S66 summary end -->')
    s=s[:start]+polish(s[start:end])+s[end:];p.write_text(s)
    for name in ['HITS.md','REPORT_DETAILS.md','README.md']:
        p=Path(name);s=p.read_text();start=s.index('## S66 — Equivalent payoff paragraph order')
        s=s[:start]+polish(s[start:])
        if name=='README.md':
            s+='\nS66 reproduction: `uv run python scripts/s66_release_final.py`; focused checks: `uv run python -m unittest scripts.test_s66 -q`. The additive publication helper clarifies sign-flip terminology while preserving all frozen scientific sources, data and estimates.\n'
        p.write_text(s)
    return before,{n:Path(n).read_bytes() for n in ARTIFACTS}

def documents(isolated=False):
    if isolated:
        return _render_isolated()[1]
    root=Path.cwd()
    with tempfile.TemporaryDirectory(dir='/var/tmp',prefix='s66_editorial_') as td:
        temp=Path(td);(temp/'results').mkdir();(temp/'figures').mkdir();(temp/'data').mkdir()
        (temp/'data/s66_payoff_order').symlink_to((root/'data/s66_payoff_order').resolve(),target_is_directory=True)
        shutil.copyfile(root/'results/s66_payoff_order.json',temp/'results/s66_payoff_order.json')
        with contextlib.chdir(temp):before,after=_render_isolated()
    # Reject unexpected bytes observed during validation before starting writes.
    # Requires exclusive writer access; validation and writes are not an atomic transaction.
    for name,expected in after.items():
        if not Path(name).exists() or Path(name).read_bytes() not in (before[name],expected):
            raise RuntimeError('Intervening S66 publication changes: '+name)
    for name,body in after.items():Path(name).write_bytes(body)
    return after

if __name__=='__main__':documents();print('S66 editorial clarification applied; science unchanged')
