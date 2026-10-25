"""Verbatim transparency appendix; no intent, honesty or mechanism labels."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.s55_replay import validate,VIEWS


def export(directory='data/s55_visibility',out='results/s55_action_text.md'):
    cfg,cases,rows=validate(directory)
    by={(r['case_id'],r['view']):r for r in rows}
    lines=['# S55 — All returned actions and text','',
           'Verbatim returned JSON for all20fresh decisions,including explanations and notes. Boolean reviews are the scientific outcome. Text is unverified self-report;this appendix assigns no agreement,intent,honesty or mechanism label. Source actions are context only.','']
    for c in cases:
        for v in VIEWS:
            r=by[c['case_id'],v];text=r['response']['text']
            fence='`'*max(3,1+max([len(x) for x in re.findall(r'`+',text)]+[0]))
            lines += [f"## {c['case_id']} · {v} · round{c['turn']+1} · own{c['own_status']}",'',
                      f"Partner {c['partner']} is TYPE-Y;fresh approval={r['parsed']['reviews'][c['partner']]};archived approval={c['archived_approval']} (context).",'',fence+'json',text,fence,'']
    Path(out).write_text('\n'.join(lines)+'\n')
    return dict(passed=True,rows=len(rows),out=out,sha256=hashlib.sha256(Path(out).read_bytes()).hexdigest())


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/s55_visibility');p.add_argument('--out',default='results/s55_action_text.md');a=p.parse_args()
    print(json.dumps(export(a.data,a.out),indent=2))
