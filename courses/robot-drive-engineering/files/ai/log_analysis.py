"""Original tiny synthetic log for checking clocks, units, metrics and deadlines."""
import csv,json,math
from pathlib import Path

ROWS=[(0,0,.003,0,0),(.01,.0105,.014,.01,.008),
      (.02,.020,.023,.02,.018),(.03,.0307,.0412,.03,.027)]

def linear_quantile(values,q):
    s=sorted(values);x=(len(s)-1)*q;i=int(x);j=min(i+1,len(s)-1)
    return s[i]+(s[j]-s[i])*(x-i)

def analyze(rows,nominal_s=.01):
    start=[r[1] for r in rows];dt=[b-a for a,b in zip(start,start[1:])]
    if any(x<=0 for x in dt):raise ValueError('Capture/start timestamps must increase strictly')
    duration=[r[2]-r[1] for r in rows]
    if any(x<0 for x in duration):raise ValueError('End precedes start')
    err=[r[3]-r[4] for r in rows]
    return {'kind':'hand-authored synthetic log, not an instrument measurement',
      'period_ms':[x*1000 for x in dt],
      'work_duration_ms':[x*1000 for x in duration],
      'deadline_misses':sum(r[2]>r[0]+nominal_s for r in rows),
      'rmse_rad':math.sqrt(math.fsum(x*x for x in err)/len(err)),
      'p99_work_ms_linear':linear_quantile(duration,.99)*1000,
      'max_work_ms':max(duration)*1000,'samples':len(rows)}
if __name__=='__main__':
    out=Path(__file__).parent
    with (out/'synthetic-log.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['scheduled_s','started_s','finished_s','reference_rad','position_rad']);w.writerows(ROWS)
    result=analyze(ROWS)
    assert result['deadline_misses']==1
    assert math.isclose(result['rmse_rad'],math.sqrt(17e-6/4))
    assert math.isclose(result['p99_work_ms_linear'],10.29)
    # Optional API cross-check; all analysis above uses only Python's standard library.
    try:
        import numpy as np
    except ImportError:
        pass
    else:
        assert math.isclose(result['p99_work_ms_linear'],float(np.quantile(result['work_duration_ms'],.99,method='linear')))
    (out/'log-analysis-results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
