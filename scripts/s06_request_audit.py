"""Independent parsing of all S06 displayed monetary fields; no prompt helpers."""
import json
from pathlib import Path


def main():
    d=Path('data/s06_denomination')
    req=[json.loads(l) for l in (d/'raw/requests.jsonl').read_text().splitlines()]
    games={g['ground_truth']['run_id']:g for g in [json.loads(p.read_text()) for p in d.glob('game_*.json')]}
    tables=0
    for request in req:
        system,user,_,_,_,rid,t,agent,attempt,model=request['payload']
        g=games[rid];k=1 if rid.endswith('_unit') else 100
        assert f'P = max(0, {30*k} - {k} * (quantity_A + quantity_B + quantity_C))' in system
        assert f'marginal cost is {6*k} accounting units per unit of product' in system
        assert f'profit = (P - {6*k}) * your quantity' in system
        assert f'conversion rate is {k} accounting units per common currency unit' in system
        assert 'private memory beyond the provided completed public rounds' in system
        assert user.startswith(f'Round {t+1}.')
        history=json.loads(user.split('Available completed public rounds: ')[1].split('\n')[0])
        expected=[dict(round=i+1,price=k*r['market']['price'],
                       quantities={a['id']:a['quantity'] for a in r['agents']},
                       profits={a['id']:k*a['profit'] for a in r['agents']}) for i,r in enumerate(g['rows'][:t])]
        assert history==expected
        assert user.endswith('"private_message":""}. You have no message box.')
        if t:
            previous=g['rows'][t-1]['agents'];rivals=sum(a['quantity'] for a in previous if a['id']!=agent)
            assert f'combined {rivals} units in the latest available round ({t})' in user
            text=user.split('not a forecast of their next choices. ')[1].split('\n')[0]
            table=json.loads(text)
            assert table==[dict(quantity=q,own_profit=k*(max(0,30-rivals-q)-6)*q) for q in range(13)]
            assert table==g['ground_truth']['tables'][t]['delivered'][agent]
            tables+=1
        else:assert 'Exact conditional own-profit calculator:' not in user
    out=dict(independent_saved_requests=len(req),independent_actual_tables=tables,
             all_displayed_money_scaled=True,all_history_rounds_and_quantities_unchanged=True,
             conversion_and_formula_cues_verified=True)
    Path('logs/s06_request_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
