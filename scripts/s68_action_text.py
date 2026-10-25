"""Verbatim transparency appendix; no intent, honesty or mechanism labels."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s68_replay import validate,VIEWS,decoded


def export(directory='data/s68_polarity',out='results/s68_action_text.md'):
    cfg,cases,rows=validate(directory)
    by={(r['case_id'],r['view']):r for r in rows}
    lines=['# S68 — All returned actions and text','',
           'Verbatim returned JSON for all30fresh decisions,including explanations and notes. Decoded approvals are the scientific outcome; inverted-view raw true means reject and raw false means approve. Historical reviews retain their original encoding. Text is unverified self-report;this appendix assigns no agreement,intent,honesty or mechanism label. Source actions are context only.','']
    for c in cases:
        for v in VIEWS:
            r=by[c['case_id'],v];text=r['response']['text']
            fence='`'*max(3,1+max([len(x) for x in re.findall(r'`+',text)]+[0]))
            lines += [f"## {c['case_id']} · {v} · round{c['turn']+1} · own{c['own_status']}",'',
                      f"Partner {c['partner']} is TYPE-Y;decoded fresh approval={decoded(r['parsed'],c,v)};archived approval={c['archived_approval']} (context).",'',fence+'json',text,fence,'']
    Path(out).write_text('\n'.join(lines)+'\n')
    return dict(passed=True,rows=len(rows),out=out,sha256=hashlib.sha256(Path(out).read_bytes()).hexdigest())


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s68_polarity');p.add_argument('--out',default='results/s68_action_text.md');a=p.parse_args()
    print(json.dumps(export(a.data,a.out),indent=2))
