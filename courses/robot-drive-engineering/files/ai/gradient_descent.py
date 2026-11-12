"""Original scalar regression/gradient check with dimensionless synthetic inputs.
Not a learned robot policy; no framework, downloaded data or hardware access.
"""
import json,math
from pathlib import Path
DATA=[(-1,-.8),(-.5,-.4),(0,0),(.5,.4),(1,.8)]
def loss(w,b):return sum((w*x+b-y)**2 for x,y in DATA)/(2*len(DATA))
def gradient(w,b):return (sum((w*x+b-y)*x for x,y in DATA)/len(DATA),sum(w*x+b-y for x,y in DATA)/len(DATA))
def run():
    w,b,h=0.,.2,1e-6;g=gradient(w,b)
    fd=((loss(w+h,b)-loss(w-h,b))/(2*h),(loss(w,b+h)-loss(w,b-h))/(2*h))
    assert max(abs(a-c) for a,c in zip(g,fd))<1e-9
    history=[{'step':0,'w':w,'b':b,'loss':loss(w,b)}]
    for step in range(1,101):
        dw,db=gradient(w,b);w-=.2*dw;b-=.2*db
        if step in (1,10,100):history.append({'step':step,'w':w,'b':b,'loss':loss(w,b)})
    assert loss(w,b)<1e-9
    return {'evidence':'noise-free synthetic linear regression, not task validation','normalization':'x,y dimensionless for gradient exercise','initial_gradient':g,'central_difference':fd,'history':history,'heldout_x_0p25_prediction':w*.25+b,'target_at_0p25':.2}
if __name__=='__main__':
    result=run();(Path(__file__).parent/'gradient-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
