"""Deterministic motion models. SI units except explicitly marked qualitative scenes."""
import math
import numpy as np
from scipy.integrate import solve_ivp
G=10.;TH=math.radians(35)
pend=solve_ivp(lambda t,z:[z[1],-G*math.sin(z[0])],[0,2.2],[-TH,0.],rtol=2e-11,atol=1e-12,dense_output=True,max_step=.002)
# First return to the left turning point from elliptic integral, for exact event times.
from scipy.special import ellipk
PEND_PERIOD=4/math.sqrt(G)*ellipk(math.sin(TH/2)**2)
def pendulum(t):
 th,w=pend.sol(t);v=abs(w);tension=G*math.cos(th)+w*w
 return dict(theta=float(th),omega=float(w),v=float(v),T=float(tension),G=G,energy=float(.5*w*w+G*(1-math.cos(th))))
VB=math.sqrt(1.5);BT1=math.sqrt(2)*math.pi/3;BT2=BT1+1/VB;BT3=BT2+math.pi/math.sqrt(2)
def belt(t):
 if t<BT1:
  x=2*(1-math.cos(t/math.sqrt(2)));v=math.sqrt(2)*math.sin(t/math.sqrt(2));a=1-x/2;f=1.;phase=1
 elif t<=BT2:x=1+VB*(t-BT1);v=VB;a=0.;f=x/2;phase=2
 else:
  z=min(t,BT3)-BT2;x=2+math.sqrt(3)*math.sin(z/math.sqrt(2));v=VB*math.cos(z/math.sqrt(2));a=1-x/2;f=1.;phase=3
 return dict(x=x,v=max(0,v),a=a,f=f,spring=x/2,phase=phase)
def power_u(t):
 tau=t/20;lo=0.;hi=1.-1e-13
 for _ in range(55):
  u=(lo+hi)/2
  if -u-math.log1p(-u)<tau:lo=u
  else:hi=u
 u=(lo+hi)/2
 return dict(u=u,v=20*u,s=400*(tau-u*u/2),t=t)
PTEND=20*(-.95-math.log(.05))
KDRAG=.3;EUP=20.;VUP=math.sqrt(2*EUP);HUP=EUP/(G*(1+KDRAG));TUP=VUP/(G*(1+KDRAG));TDOWN=math.sqrt(2*HUP/(G*(1-KDRAG)));THROW_END=TUP+TDOWN
def throw(t):
 if t<=TUP:y=VUP*t-.5*G*(1+KDRAG)*t*t;v=VUP-G*(1+KDRAG)*t;phase='上升'
 else:z=t-TUP;y=HUP-.5*G*(1-KDRAG)*z*z;v=-G*(1-KDRAG)*z;phase='下降'
 return dict(y=max(0,y),v=v,phase=phase,Ep=G*max(0,y),Ek=.5*v*v)
D_GATE=.0024;H_GATE=.5;AGATE=1.;TIN=math.sqrt(2*(H_GATE-D_GATE/2));TOUT=math.sqrt(2*(H_GATE+D_GATE/2));GATE_END=math.sqrt(1.3)
def gate(t):
 s=.5*t*t;v=t;return dict(sA=s,sB=s/2,vA=v,vB=v/2,blocked=TIN<=t<=TOUT,elapsed=max(0,min(t,TOUT)-TIN),F=5.5,mA=.5,mB=22/19)
RARC=1.25;MARC=.4;MUARC=math.sqrt(3)/2;HARC=3.75;AARC=2.5*math.sqrt(3);TA=math.sqrt(2)
def arc_event(t,z):return z[0]
arc_event.terminal=True;arc_event.direction=-1
arcsol=solve_ivp(lambda t,z:[-math.sqrt(G*HARC+2*G*RARC*(math.cos(z[0])-.5))/RARC],[0,1.],[math.pi/3],events=arc_event,rtol=1e-12,atol=1e-13,dense_output=True,max_step=.0005)
TB=TA+float(arcsol.t_events[0][0]);ARC_END=TB+.42
ARC_LENGTH=HARC/math.sin(math.pi/3)
def track(t):
 if t<TA:
  s=.5*AARC*t*t;xx=-RARC*math.sin(math.pi/3)-(ARC_LENGTH-s)*.5;yy=RARC/2+(ARC_LENGTH-s)*math.sin(math.pi/3);v=AARC*t;phase='粗糙斜面';phi=None
 elif t<TB:
  phi=float(arcsol.sol(t-TA)[0]);xx=-RARC*math.sin(phi);yy=RARC*(1-math.cos(phi));v=math.sqrt(G*HARC+2*G*RARC*(math.cos(phi)-.5));phase='光滑圆弧'
 else:phi=0.;xx=math.sqrt(50)*(t-TB);yy=0.;v=math.sqrt(50);phase='光滑水平面'
 return dict(x=xx,y=yy,v=v,phase=phase,phi=phi,N_B=20.)
def roots(a,b,c):
 if abs(a)<1e-12:return [-c/b] if abs(b)>1e-12 else []
 disc=b*b-4*a*c
 if disc<-1e-9:return []
 disc=math.sqrt(max(0,disc));return [(-b-disc)/(2*a),(-b+disc)/(2*a)]
def collision_model(M=3.,E=24.):
 p=math.sqrt(2*E/(1+1/M));xa=xb=0.;va=p;vb=-p/M;t=0.;segs=[];events=[]
 for _ in range(40):
  if abs(va)+abs(vb)<1e-8:break
  aa=-math.copysign(2,va) if abs(va)>1e-8 else 0.;ab=-math.copysign(2,vb) if abs(vb)>1e-8 else 0.;candidates=[]
  if aa:candidates.append((abs(va)/2,'A停止'))
  if ab:candidates.append((abs(vb)/2,'B停止'))
  for dt in roots(.5*aa,va,xa-2.75):
   if dt>1e-8 and va+aa*dt>1e-7:candidates.append((dt,'撞墙'))
  for dt in roots(.5*(aa-ab),va-vb,xa-xb):
   if dt>1e-8 and va-vb+(aa-ab)*dt < -1e-7:candidates.append((dt,'互撞'))
  if not candidates:break
  dt,event=min(candidates);segs.append(dict(t0=t,t1=t+dt,xa=xa,xb=xb,va=va,vb=vb,aa=aa,ab=ab));xa+=va*dt+.5*aa*dt*dt;xb+=vb*dt+.5*ab*dt*dt;va+=aa*dt;vb+=ab*dt;t+=dt
  for dd,ee in candidates:
   if abs(dd-dt)<1e-8 and ee=='A停止':va=0.
   if abs(dd-dt)<1e-8 and ee=='B停止':vb=0.
  if event=='撞墙':va=-va;xa=2.75
  if event=='互撞':u,w=va,vb;va=((1-M)*u+2*M*w)/(1+M);vb=(2*u+(M-1)*w)/(1+M);xa=xb=(xa+xb)/2
  events.append(dict(t=t,kind=event,xa=xa,xb=xb,va=va,vb=vb))
 return dict(M=M,E=E,segments=segs,events=events,end=t,xa=xa,xb=xb,va=va,vb=vb,p=p)
def collision_at(model,t):
 # Event frames use post-event velocity; positions are continuous.
 for s in model['segments']:
  if s['t0']<=t<s['t1']:
   z=t-s['t0'];return dict(xA=s['xa']+s['va']*z+.5*s['aa']*z*z,xB=s['xb']+s['vb']*z+.5*s['ab']*z*z,vA=s['va']+s['aa']*z,vB=s['vb']+s['ab']*z)
 return dict(xA=model['xa'],xB=model['xb'],vA=model['va'],vB=model['vb'])
COL=collision_model();COL_COMPARE=[collision_model(M,21.) for M in [1.8,2.1,2.4]]
if __name__=='__main__':
 print('pendulum',PEND_PERIOD,'belt',BT1,BT2,BT3,'gate',TIN,TOUT,'arc',TA,TB,'collision',COL['events'])
