"""Replay explicit synthetic arrival times; no inference, no motor and no sleep."""
import csv,json
from pathlib import Path
from command_guard import Guard, packet

def replay(folder):
    folder=Path(folder);folder.mkdir(exist_ok=True)
    g=Guard();g.observe('obs-0',0);g.observe('obs-25',25);g.arm()
    events={20:packet(1),40:packet(2,'obs-25',.3,.4),50:packet(1),
            60:packet(3,'unknown'),75:packet(3,target_rad=4),90:'{bad json}',
            170:packet(3)}
    decisions=[];rows=[]
    for now in range(251):
        if now in events:decisions.append({'at_ms':now,'decision':g.accept(events[now],now)})
        rows.append({'virtual_ms':now,'reference_rad':g.tick(now),'state':g.state})
    with (folder/'synthetic-command-replay.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result={'kind':'deterministic synthetic event replay, not hardware measurement',
            'ticks':len(rows),'decisions':decisions,'final_state':g.state,
            'largest_reference_step_rad':max(abs(b['reference_rad']-a['reference_rad']) for a,b in zip(rows,rows[1:])),
            'timeout_first_ms':next(r['virtual_ms'] for r in rows if r['virtual_ms']>40 and r['state']=='HOLD')}
    (folder/'replay-results.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':print(json.dumps(replay(Path(__file__).parent),indent=2))
