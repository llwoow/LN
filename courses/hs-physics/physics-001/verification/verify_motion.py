from pathlib import Path
import json,math
import numpy as np
import motion_models as M
R=Path(__file__).parent;checks=[]
def ck(name,condition,detail=''):
 checks.append(dict(name=name,passed=bool(condition),detail=detail));assert condition,(name,detail)
e0=M.pendulum(0)['energy'];ee=[abs(M.pendulum(t)['energy']-e0) for t in np.linspace(0,M.PEND_PERIOD,100)]
ck('摆球机械能与端点回归',max(ee)<1e-8 and abs(M.pendulum(M.PEND_PERIOD)['theta']+M.TH)<1e-8,str(max(ee)))
for t0 in [M.BT1,M.BT2]:
 a,b=M.belt(t0-1e-7),M.belt(t0+1e-7);ck('传送带切换处位置速度连续t='+str(t0),abs(a['x']-b['x'])<1e-6 and abs(a['v']-b['v'])<1e-6)
for t in np.linspace(0,M.BT3,80):
 z=M.belt(t);E=.5*z['v']**2+.25*z['x']**2;target=z['x'] if z['phase']==1 else .75+.25*z['x']**2 if z['phase']==2 else z['x']-.25
 ck('传送带分段受力与功能核验',abs(z['a']-(z['f']-z['spring']))<1e-10 and abs(E-target)<1e-10)
ck('最右端不是平衡',abs(M.belt(M.BT3)['v'])<1e-8 and M.belt(M.BT3)['a']<-.8)
ck('定滑轮两侧等位移与牛顿定律',abs(1.5*10-6-1.5*6)<1e-12)
for t in np.linspace(0,M.GATE_END,30):
 z=M.gate(t);ck('动滑轮绳长约束与两物体动力学',abs(z['sA']-2*z['sB'])<1e-12 and abs(z['F']-z['mA']*10-z['mA']*M.AGATE)<1e-12 and abs(z['mB']*10-2*z['F']-z['mB']*M.AGATE/2)<1e-12)
ck('光电门两边缘实际挡光时长',abs((M.TOUT-M.TIN)-.0024)<1e-8,str(M.TOUT-M.TIN))
for tt in [M.TA,M.TB]:
 p,q=M.track(tt-1e-7),M.track(tt+1e-7);ck('复合轨道接点位置速率连续',abs(p['x']-q['x'])<2e-6 and abs(p['y']-q['y'])<2e-6 and abs(p['v']-q['v'])<2e-6)
for t in np.linspace(M.TA,M.TB,20):
 z=M.track(t);ck('光滑圆弧机械能',abs(.5*z['v']**2+10*z['y']-25)<1e-8)
ck('第18题主要事件顺序',[e['kind'] for e in M.COL['events']]==['撞墙','B停止','互撞','A停止'])
ck('第18题第一次B停间距',abs(M.collision_at(M.COL,1)['xA']-M.collision_at(M.COL,1)['xB']-1.5)<1e-10)
ck('第18题最终间距',abs(M.COL['xa']-M.COL['xb']-1.25)<1e-10)
for model in [M.COL]+M.COL_COMPARE:
 loss=0
 for seg in model['segments']:
  dt=seg['t1']-seg['t0'];sa=seg['va']*dt+.5*seg['aa']*dt*dt;sb=seg['vb']*dt+.5*seg['ab']*dt*dt;loss+=2*abs(sa)+2*model['M']*abs(sb)
  event=next(e for e in model['events'] if abs(e['t']-seg['t1'])<1e-9)
  if event['kind']=='互撞':
   ua=seg['va']+seg['aa']*dt;ub=seg['vb']+seg['ab']*dt;va,vb=event['va'],event['vb'];mass=model['M']
   ck('两物体弹性碰撞动量与动能',abs(ua+mass*ub-va-mass*vb)<1e-8 and abs(ua*ua+mass*ub*ub-va*va-mass*vb*vb)<1e-8)
  if event['kind']=='撞墙':ck('固定墙弹性反射',abs(abs(seg['va']+seg['aa']*dt)-abs(event['va']))<1e-8)
 ck('全程摩擦耗散等于初动能',abs(loss-model['E'])<1e-7,str(loss))
ck('临界以下无互撞',not any(e['kind']=='互撞' for e in M.COL_COMPARE[0]['events']))
ck('临界质量同点静止',abs(M.COL_COMPARE[1]['xa']-M.COL_COMPARE[1]['xb'])<1e-7 and not any(e['kind']=='互撞' for e in M.COL_COMPARE[1]['events']))
ck('临界以上按实际互撞继续',any(e['kind']=='互撞' for e in M.COL_COMPARE[2]['events']))
for t in np.linspace(0,M.PTEND,30):
 z=M.power_u(t);ck('恒功率能量与有限末速',abs(20000*t-(.5*1000*z['v']**2+1000*z['s']))<1e-5 and z['v']<20)
ck('阻力上抛耗散',abs(M.throw(M.THROW_END)['Ek']-20*.7/1.3)<1e-10)
(R/'qa/physics-invariants.json').write_text(json.dumps(dict(checkCount=len(checks),checks=checks),ensure_ascii=False,indent=2));print('passed',len(checks),'physics invariants')
